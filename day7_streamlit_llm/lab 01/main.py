"""
main.py — CLI entry point for the Résumé x JD Analyzer.

Task 5 of the lab (Track A).
Study material reference: §4 The Multi-Stage Pipeline

Your job is to write the main() function. The argument parser is already
provided — do not modify parse_args().
"""

import argparse
import json
import sys
import os
from datetime import datetime
from pathlib import Path

from parse import read_resume_pdf, read_jd_text
from analyzer import (
    extract_resume_profile,
    extract_jd_profile,
    analyse_keyword_match,
    analyse_bullets,
    analyse_jargon,
    analyse_structure,
    analyse_degree_alignment,
    summarise_overall,
    compute_overall_score,
)
from report import render_markdown


ATS_PASS_THRESHOLD = 60


def parse_args(argv: list[str]) -> tuple[str, str]:
    """
    Parse command-line arguments. Pre-provided — do not modify.

    Usage:
        python main.py path/to/resume.pdf path/to/job_description.txt
    """
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Résumé x JD Analyzer — diagnostic feedback only.",
    )
    parser.add_argument("resume", metavar="resume.pdf", help="Path to the PDF résumé.")
    parser.add_argument("job", metavar="job.txt", help="Path to the plain-text job description.")
    args = parser.parse_args(argv[1:])
    return args.resume, args.job


def main() -> int:
    """
    Orchestrate the full analysis pipeline. Return 0 on success, 1 on error.

    Steps to implement:
      [1/8] Parse CLI arguments (call parse_args(sys.argv)).
      [2/8] Load documents — call read_resume_pdf() and read_jd_text();
            catch ValueError and print to stderr, then return 1.
      [3/8] Extract structured profiles — call extract_resume_profile() and
            extract_jd_profile(); print progress as "[3/8] Extracting profiles…".
      [4/8] Run the 5 evaluations in order:
              analyse_keyword_match(resume_profile, jd_profile)
              analyse_bullets(resume_profile)
              analyse_jargon(resume_profile, jd_profile)
              analyse_structure(resume_text)
              analyse_background_fit(resume_profile, jd_profile)
            Print a [4/8]…[8/8] progress line for each.
      [9/9] Assemble the report dict:
              {
                "resume_profile":  resume_profile,
                "jd_profile":      jd_profile,
                "keyword_match":   keyword_match,
                "bullets":         bullets,
                "jargon":          jargon,
                "structure":       structure,
                "background_fit":  background_fit,
              }
            Compute overall_score with compute_overall_score(report).
            Add to report:
              report["overall_score"]       = overall_score
              report["passes_ats_threshold"] = overall_score >= ATS_PASS_THRESHOLD
              report["summary"]             = summarise_overall(report)

            Build a timestamped filename:
              ts = datetime.now().strftime("%Y%m%d_%H%M%S")
              json_path = Path("outputs") / f"match_report_{ts}.json"
              md_path   = Path("outputs") / f"match_report_{ts}.md"

            Save JSON: json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            Save Markdown: render_markdown(report, out_path=md_path)

            Print the final verdict and the 3-bullet summary.
            Return 0.
    """
    resume_path, job_path = parse_args(sys.argv)

    model = os.getenv("MODEL", "Unknown")
    print(f"Using model: {model}")
    
    try:
        print(f"[1/8] Parsing résumé: {resume_path}")
        resume_text = read_resume_pdf(resume_path)

        print(f"[2/8] Reading JD: {job_path}")
        jd_text = read_jd_text(job_path)

    except ValueError as e:
        print(f"Error reading files: {e}", file=sys.stderr)
        return 1

    try:
        print("[3/8] Extracting résumé profile (LLM)...")
        resume_profile = extract_resume_profile(resume_text)

        print("[4/8] Extracting JD profile (LLM)...")
        jd_profile = extract_jd_profile(jd_text)

        print("[5/8] Keyword match (LLM)...")
        keyword_match = analyse_keyword_match(resume_profile, jd_profile)

        print("[6/8] Bullet audit (LLM)...")
        bullets = analyse_bullets(resume_profile)

        print("[7/8] Jargon, structure, degree alignment (LLM x3)...")
        jargon = analyse_jargon(resume_profile, jd_profile)
        structure = analyse_structure(resume_text)
        background_fit = analyse_degree_alignment(resume_profile, jd_profile)

    except RuntimeError as e:
        print(f"LLM Error: {e}", file=sys.stderr)
        return 1
    
    report = {
        "meta": {
            "resume_path": resume_path,
            "job_path": job_path,
            "model": model,
            "timestamp": datetime.now().isoformat()
        },
        "resume_profile": resume_profile,
        "jd_profile": jd_profile,
        "keyword_match": keyword_match,
        "bullets": bullets,
        "jargon": jargon,
        "structure": structure,
        "background_fit": background_fit,
    }

    overall_score = compute_overall_score(report)
    report["overall_score"] = overall_score
    report["passes_ats_threshold"] = overall_score >= ATS_PASS_THRESHOLD

    print("[8/8] Final summary (LLM)...")
    try:
        report["summary"] = summarise_overall(report)
    except RuntimeError as e:
        print(f"LLM Error during summary: {e}", file=sys.stderr)
        return 1
    
    Path("outputs").mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = Path("outputs") / f"match_report_{ts}.json"
    md_path = Path("outputs") / f"match_report_{ts}.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    render_markdown(report, out_path=md_path)

    verdict = "PASS" if report["passes_ats_threshold"] else "FAIL"

    print(f"\nScore: {overall_score}/100  ({verdict} 60% ATS threshold)")
    print(f"JSON:  {json_path}")
    print(f"MD:    {md_path}\n")
    print(report["summary"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
