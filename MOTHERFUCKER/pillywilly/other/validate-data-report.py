#!/usr/bin/env python3
"""Validate a data report JSON against the standardized schema.

Usage:
    python3 scripts/validate-data-report.py data/reports/<report-file>.json

Exit code: 0 if all gates pass, 1 if any fail.
"""

import json
import sys
import os

def load_json(path):
    with open(path) as f:
        return json.load(f)

def check(condition, message, gates, key):
    gates[key] = {"status": "PASS" if condition else "FAIL", "detail": message}
    return condition

def validate_report(report_path):
    report = load_json(report_path)
    schema = load_json("data/SCHEMA.json")
    gates = {}

    all_pass = True

    # Check required top-level fields
    for field in schema["required"]:
        ok = check(field in report, f"Top-level field '{field}' present", gates, f"SCH_{field}")
        all_pass = all_pass and ok

    # Report metadata
    report_section = report.get("report", {})
    for field in schema["report"]["required"]:
        ok = check(field in report_section, f"report.{field} present", gates, f"RPT_{field}")
        all_pass = all_pass and ok

    if "type" in report_section:
        valid_types = schema["report"]["type_enum"]
        ok = check(report_section["type"] in valid_types,
                   f"report.type is '{report_section['type']}' (valid: {valid_types})",
                   gates, "RPT_type_valid")
        all_pass = all_pass and ok

    # Method section
    method = report.get("method", {})
    for field in schema["method"]["required"]:
        ok = check(field in method, f"method.{field} present", gates, f"MTH_{field}")
        all_pass = all_pass and ok

    if "parameters" in method:
        params = method["parameters"]
        for field in schema["method"]["parameters"]["required"]:
            ok = check(field in params, f"method.parameters.{field} present", gates, f"PAR_{field}")
            all_pass = all_pass and ok

    if "formulas" in method:
        formulas = method["formulas"]
        for field in schema["method"]["formulas"]["required"]:
            ok = check(field in formulas, f"method.formulas.{field} present", gates, f"FRM_{field}")
            all_pass = all_pass and ok

    # API usage section
    api_usage = report.get("api_usage", {})
    for field in schema["api_usage"]["required"]:
        ok = check(field in api_usage, f"api_usage.{field} present", gates, f"API_{field}")
        all_pass = all_pass and ok

    if "endpoints" in api_usage:
        for endpoint in api_usage["endpoints"]:
            for field in schema["api_usage"]["endpoints"]["items"]["required"]:
                ok = check(field in endpoint, f"api_usage.endpoint.{field} present", gates, f"EP_{field}_{endpoint.get('name', 'unknown')}")
                all_pass = all_pass and ok

    # Verification gates section
    verification = report.get("verification", {})
    for field in schema["verification"]["required"]:
        ok = check(field in verification, f"verification.{field} present", gates, f"VER_{field}")
        all_pass = all_pass and ok

    if "gates" in verification:
        report_gates = verification["gates"]
        # Derive stage from report type, not next_stage
        type_to_stage = {
            "underserved_claim_test": "stage_1",
            "channel_curation": "stage_2",
            "video_harvest": "stage_3",
            "feature_extraction": "stage_4",
            "gap_map": "stage_5",
        }
        report_type = report.get("report", {}).get("type", "unknown")
        current_stage = type_to_stage.get(report_type, "unknown")
        required_gates_key = f"{current_stage}_required"
        if required_gates_key in schema["verification"]["gates"]:
            for gate_name in schema["verification"]["gates"][required_gates_key]:
                ok = check(gate_name in report_gates,
                           f"Gate '{gate_name}' present",
                           gates, f"GATE_{gate_name}")
                all_pass = all_pass and ok
                if ok:
                    gate_ok = check(report_gates[gate_name].get("status") == "PASS",
                                    f"Gate '{gate_name}': {report_gates[gate_name].get('detail', '')}",
                                    gates, f"GATE_{gate_name}_pass")
                    all_pass = all_pass and gate_ok
        else:
            # Check all gates pass
            for gate_name, gate_data in report_gates.items():
                gate_ok = check(gate_data.get("status") == "PASS",
                                f"Gate '{gate_name}': {gate_data.get('detail', '')}",
                                gates, f"GATE_{gate_name}")
                all_pass = all_pass and gate_ok

    # Data section
    data_section = report.get("data", {})
    if "summary" in data_section:
        for field in schema["data"]["summary"]["required"]:
            ok = check(field in data_section["summary"], f"data.summary.{field} present", gates, f"SUM_{field}")
            all_pass = all_pass and ok

    # Print results
    print(f"\nValidation Report: {os.path.basename(report_path)}")
    print(f"Schema version: {schema.get('schema_version', 'unknown')}")
    print(f"{'='*60}")
    for gate_name in sorted(gates.keys()):
        gate = gates[gate_name]
        icon = "PASS" if gate["status"] == "PASS" else "FAIL"
        print(f"  [{icon}] {gate_name}: {gate['detail']}")
    print(f"{'='*60}")
    print(f"Overall: {'ALL GATES PASS' if all_pass else 'SOME GATES FAIL'}")
    print()

    # Update verification section in report
    verification["gates"].update(gates)
    verification["all_pass"] = all_pass
    report["verification"] = verification

    # Write updated verification back
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return all_pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate-data-report.py <report.json>")
        sys.exit(1)

    result = validate_report(sys.argv[1])
    sys.exit(0 if result else 1)
