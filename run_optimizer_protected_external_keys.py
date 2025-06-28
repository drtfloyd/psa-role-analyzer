
import sys
import os

# PSA™ License Enforcement Block (external file-based key loading)
def load_authorized_keys(file_path="authorized_keys.txt"):
    try:
        with open(file_path, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print("⚠️ License key file not found. No keys loaded.")
        return set()

AUTHORIZED_KEYS = load_authorized_keys()

def check_license_key():
    license_key = os.getenv("PSA_LICENSE_KEY")
    if not license_key:
        print("🆓 Running in Freemium Mode – Limited Output Enabled")
        return "free"
    elif license_key not in AUTHORIZED_KEYS:
        print("\n🚫 Invalid PSA™ License Key")
        print("🔒 Full access requires a valid key.")
        print("📩 Contact: toolset.ranker-28@icloud.com")
        sys.exit(1)
    else:
        print("✅ License Key Valid – Full Mode Enabled")
        return "pro"

# Run the license check before executing any logic
mode = check_license_key()

def load_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading file: {e}"

def basic_signal_score(resume_text, jd_text):
    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())
    match_score = len(resume_words.intersection(jd_words)) / max(len(jd_words), 1)
    mli_score = min(1.0, len(resume_text) / 3000)
    return round(match_score * 100, 2), round(mli_score * 100, 2)

def generate_report(match_score, mli_score):
    report = f"""
    Resume Signal Optimizer™ Report

    ✅ Architecture Match Score: {match_score}%
    ✅ Machine Legibility Index (MLI): {mli_score}%

    Recommendations:
    - Ensure title and role language matches the job description.
    - Enhance legibility with action verbs and ontology-aligned phrasing.
    - Target clarity over fluff: presence is more than padding.
    """
    return report

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_optimizer.py [resume.txt] [job_description.txt]")
        return

    resume_path = sys.argv[1]
    jd_path = sys.argv[2]

    resume_text = load_file(resume_path)
    jd_text = load_file(jd_path)

    if "Error" in resume_text or "Error" in jd_text:
        print("There was an error loading one of the files.")
        return

    match_score, mli_score = basic_signal_score(resume_text, jd_text)

    if mode == "free":
        print(f"📉 Freemium Output: Match Score = {match_score}%")
    elif mode == "pro":
        report = generate_report(match_score, mli_score)

        output_path = os.path.join("outputs", "signal_report.txt")
        os.makedirs("outputs", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(report)
        print(f"Full report saved to: {output_path}")

if __name__ == "__main__":
    main()
