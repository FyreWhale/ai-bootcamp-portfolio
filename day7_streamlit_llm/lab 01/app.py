import streamlit as st
from dotenv import load_dotenv

from parse import read_resume_pdf
from analyzer import (
    extract_resume_profile, extract_jd_profile, analyse_keyword_match,
    analyse_bullets, analyse_jargon, analyse_structure,
    analyse_degree_alignment, summarise_overall, compute_overall_score,
)

ATS_PASS_THRESHOLD = 60

load_dotenv()
VALID_DEGREES = ["RTIS", "IMGD", "UXGD", "BFA"]

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description", height=250)
degree = st.selectbox("Select Degree", VALID_DEGREES)
run = st.button("Analyze Resume")

if run:
    if not resume_file or not jd_text:
        st.error("Please upload resume and paste job description.")
        st.stop()

    print("[1/8] Loading documents...")
    resume_text = read_resume_pdf(resume_file)

    print("[2/8] Analyzing resume...")
    resume_profile = extract_resume_profile(resume_text)

    print("[3/8] Analyzing job description...")
    jd_profile = extract_jd_profile(jd_text)

    print("[4/8] Analyzing keyword match...")
    keyword_match = analyse_keyword_match(resume_profile, jd_profile)

    print("[6/8] Analyzing bullets...")
    bullets = analyse_bullets(resume_profile)

    print("[6/8] Analyzing jargon...")
    jargon = analyse_jargon(resume_profile, jd_profile)

    print("[7/8] Analyzing structure...")
    structure = analyse_structure(resume_text)

    print("[8/8] Analyzing degree alignment...")
    background_fit = analyse_degree_alignment(resume_profile, jd_profile)
    
    report = {
        "resume_profile": resume_profile,
        "jd_profile": jd_profile,
        "keyword_match": keyword_match,
        "bullets": bullets,
        "jargon": jargon,
        "structure": structure,
        "background_fit": background_fit,
    }

    print("Computing overall score...")
    overall_score = compute_overall_score(report)
    report["overall_score"] = overall_score
    report["passes_ats_threshold"] = overall_score >= ATS_PASS_THRESHOLD
    verdict = "PASS" if report["passes_ats_threshold"] else "FAIL"

    print("Generating summary...")
    summary = summarise_overall(report)

    st.warning(f"Overall Score: {overall_score} - {verdict}")
    st.write(summary)
