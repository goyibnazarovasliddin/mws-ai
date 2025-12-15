"""
ML Pipeline and Business Logic.

Description:
- Core orchestration layer that receives findings from the parser and pushes them through the analysis chain:
  1) rule_filter: Fast heuristic checks (FP detection).
  2) ml.features & ml.predict: Machine Learning model prediction.
  3) llm_client: Deep analysis using OpenAI for complex cases.
  4) storage: Saves the final annotated findings to the database.

Connections:
- Integrates all core logical components: parser, rule_filter, llm_client, ml/*, and storage.
"""

from sqlalchemy.orm import Session
from app.services import parser, rule_filter, storage, llm_client
from app.ml import features, predict
from app.models.pydantic_schemas import FindingSchema

from typing import Union, List, Any

def process_report(db: Session, tool: str, report_data: Union[dict, list], report_id: str):
    """
    Main processing function for a security report.
    Iterates through findings and applies the 3-layer analysis funnel.
    """
    
    # 1. Parse Report
    # -------------
    # Convert raw JSON/SARIF into a standardized list of FindingSchema objects.
    parsed_findings = parser.normalize_report(tool, report_data)
    
    analyzed_findings = []
    stats = {"total": len(parsed_findings), "filtered_fp": 0, "remaining_tp": 0}
    
    for finding in parsed_findings:
        # 2. Heuristic Filter (Layer 1)
        # -----------------------------
        # Checks for obvious false positives (e.g., test files, 'example' keywords).
        # Very fast, no cost.
        is_fp_heuristic, reason_h, conf_h = rule_filter.check_is_false_positive(
            finding.file_path, finding.secret_snippet
        )
        
        if is_fp_heuristic:
            finding.is_false_positive = True
            finding.ai_verdict = f"Heuristic: {reason_h}"
            finding.confidence = conf_h
            stats["filtered_fp"] += 1
        else:
            # 3. ML Prediction (Layer 2)
            # --------------------------
            # Extracts probability features (entropy, string length, etc.) and runs 
            # against the trained Random Forest model.
            feats = features.extract_features(finding)
            is_fp_ml, conf_ml = predict.predict(feats)
            
            if is_fp_ml:
                finding.is_false_positive = True
                finding.ai_verdict = "ML Model classified as FP"
                finding.confidence = conf_ml
                stats["filtered_fp"] += 1
            else:
                # 4. LLM Verification (Layer 3)
                # -----------------------------
                # If Rules and ML both think it MIGHT be real, we ask the LLM for a 
                # human-like verdict. This is the most expensive but most accurate step.
                llm_result = llm_client.analyze_with_llm({
                    "file_path": finding.file_path,
                    "secret_snippet": finding.secret_snippet,
                    "rule_id": finding.rule_id
                })
                
                finding.is_false_positive = llm_result.get("is_false_positive", False)
                finding.ai_verdict = llm_result.get("reason", "LLM Analysis")
                finding.confidence = llm_result.get("confidence", 0.5)

                if not finding.is_false_positive:
                    stats["remaining_tp"] += 1
                else:
                    stats["filtered_fp"] += 1
        
        analyzed_findings.append(finding)
        
    # 5. Save Results
    # ---------------
    # Persist the fully analyzed findings and update report status.
    storage.save_findings(db, report_id, analyzed_findings)
    storage.update_report_status(db, report_id, "completed", stats)
    
    return stats

