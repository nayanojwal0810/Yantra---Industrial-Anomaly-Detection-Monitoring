"""
Script to analyze label semantics and fault distribution across all runs.
"""
import json

def analyze():
    with open("reports/audit/audit_inventory_results.json") as f:
        data = json.load(f)

    files = data["files"]
    print(f"{'Filename':<42} | {'Scenario':<22} | {'Rows':<5} | {'Norm':<5} | {'Fault':<5} | {'Fault%':<7} | {'Distinct Anomaly Codes'}")
    print("-" * 115)
    
    code_to_scenarios = {}
    
    for item in files:
        dist_str = ", ".join(f"{k}:{v}" for k, v in item['anomaly_dist'].items())
        pct = f"{item['fault_ratio']*100:.1f}%" if item['fault_ratio'] is not None else "N/A"
        norm = item['normal_rows'] if item['normal_rows'] is not None else "N/A"
        fault = item['fault_rows'] if item['fault_rows'] is not None else "N/A"
        
        for k in item['anomaly_dist'].keys():
            if k != "0":
                code_to_scenarios.setdefault(k, set()).add(item['scenario'])

        print(f"{item['filename']:<42} | {item['scenario']:<22} | {item['row_count']:<5} | {norm:<5} | {fault:<5} | {pct:<7} | {dist_str}")

    print("\n--- Code to Scenario Mapping ---")
    for code in sorted(code_to_scenarios.keys(), key=int):
        print(f"Code {code}: {sorted(list(code_to_scenarios[code]))}")

if __name__ == "__main__":
    analyze()
