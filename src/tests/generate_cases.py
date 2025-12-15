"""
Used to generate test cases for the benchmark_cases.json file.
"""

import json

# Load the simple key-value dataset we made earlier
input_file = "benchmark_data.json"
output_file = "benchmark_cases.json"

def generate_sarif_case(id, rule_id, snippet, path, method_type):
    return {
        "id": id,
        "type": method_type,
        "description": f"Test case for {method_type} detection",
        "payload": {
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "gitleaks",
                            "rules": [
                                {
                                    "id": rule_id,
                                    "name": rule_id.replace("-", " ").title()
                                }
                            ]
                        }
                    },
                    "results": [
                        {
                            "ruleId": rule_id,
                            "message": {
                                "text": snippet
                            },
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {
                                            "uri": path
                                        },
                                        "region": {
                                            "startLine": 15,
                                            "snippet": {
                                                "text": f"some_var = '{snippet}'"
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

def main():
    try:
        with open(input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please regenerate it.")
        return

    cases = []
    for idx, item in enumerate(data):
        # Generate a unique Rule ID for clear distinction
        rule_id = f"test-rule-{item['Rule']}"
        case = generate_sarif_case(
            id=item["Rule"],
            rule_id=rule_id,
            snippet=item["Snippet"],
            path=item["Path"],
            method_type=item["Type"]
        )
        cases.append(case)

    with open(output_file, "w") as f:
        json.dump(cases, f, indent=2)
    
    print(f"Successfully generated {len(cases)} SARIF test cases in '{output_file}'.")

if __name__ == "__main__":
    main()
