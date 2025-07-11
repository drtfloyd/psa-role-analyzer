
import streamlit as st
import re

# ---------- Core Scoring Logic ----------
def score_job_description(text: str) -> dict:
    """
    Lightweight role-signal scorer.

    Returns:
        dict: keys = SDS, flags, suggested_title, visibility_risk, OFI
    """
    score = {
        "SDS": 0,
        "flags": [],
        "suggested_title": "Unknown",
        "visibility_risk": "Low",
        "OFI": 0  # Ontology Flag Index
    }

    text = text.lower()

    # Senior-title language
    if re.search(r"\b(vice president|svp|chief|executive director)\b", text):
        score["SDS"] += 20
        score["flags"].append("Senior title language detected")
        score["OFI"] += 1

    # Ghost authorship
    if re.search(r"support[s]? senior leadership", text) and "external engagement" in text:
        score["SDS"] += 40
        score["flags"].append("Ghost authorship detected")
        score["suggested_title"] = "SVP or Chief Strategy Role"
        score["visibility_risk"] = "High"
        score["OFI"] += 1

    # Executive mis-naming
    if re.search(r"manag(?:es|ing) managers", text) and "liaison to regulators" in text:
        score["SDS"] += 45
        score["flags"].append("Misnamed executive responsibilities")
        if score["suggested_title"] == "Unknown":
            score["suggested_title"] = "Compliance Executive"
        score["visibility_risk"] = "High"
        score["OFI"] += 1

    # Fallback heuristics
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

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Role Signal Analyzer", layout="wide")

st.markdown(
    """
    <style>
        .stTextArea textarea {height: 250px;}
        .stButton button {width: 100%; border-radius: 5px;}
        .badge {display:inline-block;padding:5px 10px;border-radius:15px;color:#fff;margin-right:5px;}
        .badge-high {background-color:#dc3545;}
        .badge-low  {background-color:#28a745;}
        .badge-flag {background-color:#ffc107;color:#000;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🤖 Role Signal Analyzer")
st.write(
    "Paste any job description and surface hidden seniority signals, "
    "ghost-authorship clues, and mis-named executive roles."
)

col1, col2 = st.columns([2, 1])

with col1:
    example_text = (
        "The individual will support senior leadership with strategy formulation "
        "and external engagement.\nThey will manage managers across regions and "
        "serve as a liaison to regulators and compliance boards."
    )
    jd_text = st.text_area("📝 Job description", value=example_text, height=250)
    analyze_btn = st.button("Analyze Job Description")

with col2:
    st.subheader("Analysis Results")
    if analyze_btn and jd_text.strip():
        res = score_job_description(jd_text)

        st.metric("Suggested Title", res["suggested_title"])
        risk_badge = f"<span class='badge badge-{ 'high' if res['visibility_risk']=='High' else 'low'}'>{res['visibility_risk']}</span>"
        st.markdown(f"**Visibility Risk:** {risk_badge}", unsafe_allow_html=True)
        st.metric("Signal Detection Score (SDS)", res["SDS"])

        st.write("**Detected Flags:**")
        if res["flags"]:
            st.markdown(
                " ".join(f"<span class='badge badge-flag'>{flag}</span>" for flag in res["flags"]),
                unsafe_allow_html=True,
            )
        else:
            st.write("No specific flags detected.")
    elif analyze_btn:
        st.warning("Please enter a job description first.")
    else:
        st.info("→ Paste text and click **Analyze**.")

with st.expander("How this works"):
    st.markdown(
        """
        The analyzer scans for three main pattern groups:

        1. **Senior titles** – explicit high-rank keywords (e.g., “Chief”, “SVP”).
        2. **Ghost authorship** – language hinting the role writes or orchestrates on behalf of leadership.
        3. **Mis-named executive roles** – tasks like *managing managers* or *regulator liaison* that usually belong to director-plus positions.

        Each hit boosts the **SDS** (Signal Detection Score). Heuristics back-fill a likely title when signals are weak.
        """
    )
