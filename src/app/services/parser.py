"""
A module that normalizes the format of SARIF and various scanners (gitleaks, trufflehog, etc.).

Task:
- Converts various report formats into a single `Finding` list of objects:
{ rule_id, file_path, snippet, original_location, raw_result }

Linkage:
- endpoints/analyze.py calls this function.
- normalized payload is stored in storage.py.
"""

from typing import List, Dict, Any
from app.models.pydantic_schemas import FindingSchema

def normalize_sarif(report: Dict[str, Any]) -> List[FindingSchema]:
    findings = []
    runs = report.get("runs", [])
    for run in runs:
        results = run.get("results", [])
        rules = {r["id"]: r for r in run.get("tool", {}).get("driver", {}).get("rules", [])}
        
        for res in results:
            rule_id = res.get("ruleId", "unknown")
            message = res.get("message", {}).get("text", "")
            
            locations = res.get("locations", [])
            file_path = "unknown"
            snippet = ""
            start_line = 0
            
            if locations:
                phys_loc = locations[0].get("physicalLocation", {})
                file_path = phys_loc.get("artifactLocation", {}).get("uri", "unknown")
                region = phys_loc.get("region", {})
                snippet = region.get("snippet", {}).get("text", "")
                start_line = region.get("startLine", 0)

            # Fallback for snippet if message contains the secret (common in some tools)
            # But usually SARIF snippet is in region.
            if not snippet and message:
                 snippet = message # Be careful here, message might be description
            
            finding = FindingSchema(
                rule_id=rule_id,
                file_path=file_path,
                secret_snippet=snippet,
                is_false_positive=False, # Default
                confidence=0.0,
                ai_verdict="",
                original_location={"line": start_line}
            )
            findings.append(finding)
    return findings

def normalize_gitleaks(report: Any) -> List[FindingSchema]:
    # Gitleaks JSON is usually a list of dicts
    findings = []
    if isinstance(report, dict) and "runs" in report: 
        # It's SARIF format even if tool says gitleaks
        return normalize_sarif(report)
        
    items = report if isinstance(report, list) else [report]
    
    for item in items:
        # Gitleaks JSON format fields
        # "RuleID", "File", "Secret", "StartLine"
        finding = FindingSchema(
            rule_id=item.get("RuleID", "unknown"),
            file_path=item.get("File", "unknown"),
            secret_snippet=item.get("Secret", ""),
            is_false_positive=False,
            confidence=0.0,
            ai_verdict="",
            original_location={"line": item.get("StartLine", 0), "commit": item.get("Commit", "")}
        )
        findings.append(finding)
    return findings

def normalize_report(tool: str, report: Any) -> List[FindingSchema]:
    if tool.lower() == "sarif" or (isinstance(report, dict) and "runs" in report):
        return normalize_sarif(report)
    elif tool.lower() == "gitleaks":
        return normalize_gitleaks(report)
    else:
        # Fallback: try SARIF structure or empty
        if isinstance(report, dict) and "runs" in report:
            return normalize_sarif(report)
        return []

