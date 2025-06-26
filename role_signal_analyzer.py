import json
import re

def score_job_description(text):
    score = {
        "SDS": 0,
        "flags": [],
        "suggested_title": "Unknown",
        "visibility_risk": "Low",
        "OFI": 0  # Ontology Flag Index
    }

    # Normalize case
    text = text.lower()

    # Baseline scoring based on title keywords
    if re.search(r"\b(vice president|svp|chief|executive director)\b", text):
        score["SDS"] += 20
        score["flags"].append("Senior title language detected")
        score["OFI"] += 1

    # Ghost authorship detection
    if re.search(r"support[s]? senior leadership", text) and "external engagement" in text:
        score["SDS"] += 40
        score["flags"].append("Ghost authorship detected")
        score["suggested_title"] = "SVP or Chief Strategy Role"
        score["visibility_risk"] = "High"
        score["OFI"] += 1

    # Executive misnaming
    if re.search(r"manag(es|ing) managers", text) and "liaison to regulators" in text:
        score["SDS"] += 45
        score["flags"].append("Misnamed executive responsibilities")
        if score["suggested_title"] == "Unknown":
            score["suggested_title"] = "Compliance Executive"
        score["visibility_risk"] = "High"
        score["OFI"] += 1

    # Fallback heuristics if no strong match
    if score["suggested_title"] == "Unknown":
        if "project manage" in text:
            score["suggested_title"] = "Program Manager"
            score["OFI"] += 1
        elif "coordinate" in text or "facilitate" in text:
            score["suggested_title"] = "Operations Coordinator"
            score["OFI"] += 1
        else:
            score["suggested_title"] = "General Staff Role"

    return score

if __name__ == "__main__":
    with open("input_example.txt", "r") as f:
        jd_text = f.read()

    result = score_job_description(jd_text)

    with open("output_summary.json", "w") as out:
        json.dump(result, out, indent=2)
