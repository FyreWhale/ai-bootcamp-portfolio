"""
prompts.py — all 8 system prompts used by analyzer.py.

Task 3 of the lab (Track A).
Study material references:
  §3.3 Schema-First Prompt Design
  §6.1 Extraction Prompts
  §6.2 Evaluation Prompts
  §6.3 Feedback-Only Principle
"""

# ---------------------------------------------------------------------------
# Extraction prompts
# ---------------------------------------------------------------------------

RESUME_PROFILE_PROMPT = """
INSTRUCTION
Extract a structured candidate profile from the plain résumé text provided. Extract only what is literally present — never invent or paraphrase information.

CONTEXT
You are an objective data extraction engine. Your task is to map raw résumé text into a standardized structured format for downstream analysis.

CONSTRAINTS
- Copy what is literally present in the text.
- Never invent, hallucinate, or infer missing information.
- Never rewrite or paraphrase descriptions.
- If a field is absent or no relevant data is found, you must still include the key but return an empty array `[]` (for lists) or an empty string `""` (for strings). Do not omit any keys from the schema.

OUTPUT
{
  "name": "string",
  "contact": {
    "email": "string", "phone": "string", "linkedin": "string",
    "github": "string", "portfolio": "string"
  },
  "summary": "string",
  "education": [{"school": "string", "degree": "string",
                 "graduation_date": "string", "courses": ["string"]}],
  "projects":  [{"title": "string", "date": "string", "bullets": ["string"]}],
  "experience":[{"title": "string", "company": "string",
                 "date": "string", "bullets": ["string"]}],
  "skills": {
    "languages": ["string"], "frameworks": ["string"], "tools": ["string"],
    "concepts": ["string"], "platforms": ["string"]
  }
}

Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


JD_PROFILE_PROMPT = """
INSTRUCTION
Extract a structured Job Description (JD) profile from the free-form job posting text provided. Extract only what is literally present — never invent or paraphrase.

CONTEXT
You are an objective data extraction engine mapping job requirements into a standardized structured format to evaluate candidate fit.

CONSTRAINTS
- Extract only what is literally present in the text.
- Never invent, hallucinate, or infer requirements that are not explicitly stated.
- If a field is absent, you must still include the key but return an empty array `[]` or an empty string `""`. Do not omit any keys.

OUTPUT
{
  "job_title": "string",
  "company": "string",
  "location": "string",
  "experience_level": "string",
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "tools_technologies": ["string"],
  "responsibilities": ["string"],
  "soft_skills": ["string"],
  "buzzwords": ["string"],
  "deal_breakers": ["string"]
}

Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


# ---------------------------------------------------------------------------
# Evaluation prompts
# ---------------------------------------------------------------------------

KEYWORD_MATCH_PROMPT = """
INSTRUCTION
Compare the provided résumé profile keywords against the JD profile requirements and calculate a keyword match score. Identify present and missing keywords.

CONTEXT
You will receive a parsed RÉSUMÉ PROFILE and a parsed JD PROFILE in JSON format. 
Scoring formula: 100 * (required_skills found in résumé) / max(1, total required_skills).

CONSTRAINTS
- The résumé and JD profiles are always provided in full, even when they share zero keywords. This is a normal, valid input.
- You must return the requested JSON schema even if there is a total mismatch. An empty "present" array is a correct result in this scenario. Do not ask for clarification or claim no résumé was given.
- The `why_it_matters` field must be diagnostic only (25 words max) and never rewrite or generate résumé content.

OUTPUT
{
  "present": [{"keyword": "string", "category": "language|framework|tool|concept|soft_skill|buzzword",
               "found_in": "summary|projects|experience|education|skills", "exact_match": true}],
  "missing": [{"keyword": "string", "category": "language|framework|tool|concept|soft_skill|buzzword", "importance": "required|preferred",
               "suggested_section": "skills|projects|experience|summary",
               "why_it_matters": "string (25 words max — diagnostic only)"}],
  "keyword_match_score": 0
}

Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


BULLET_QUALITY_PROMPT = """
INSTRUCTION
Score each résumé bullet point against the Action → Technology → Impact (ATI) rubric and calculate an average quality score.

CONTEXT
A strong résumé bullet follows the ATI rubric: it names the action taken, the specific technology/tool used, and a measurable impact.
- L1_OK: Action only (e.g., "Developed web application.")
- L2_BETTER: Action + Technology (e.g., "Developed web application using React and Node.js.")
- L3_BEST: Action + Technology + Impact (e.g., "Developed web application using React and Node.js, increasing user retention by 20%.")
Scoring formula: round(100 * sum(level_score) / (3 * count)) where L1=1, L2=2, L3=3.

CONSTRAINTS
- Evaluate the bullets exactly as written.
- The `what_is_missing` field must be diagnostic only (20 words max) identifying what ATI components are absent.
- You must never suggest a rewritten bullet or generate new phrasing.

OUTPUT
{
  "bullets": [{"source": "projects|experience", "parent_title": "string",
               "bullet_text": "string (verbatim)", "has_action_verb": true,
               "has_specific_technology": true, "has_measurable_impact": false,
               "level": "L1_OK|L2_BETTER|L3_BEST",
               "what_is_missing": "string (20 words max — diagnose only)"}],
  "bullet_quality_avg": 0
}

Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


JARGON_AUDIT_PROMPT = """
INSTRUCTION
Dynamically compare résumé terminology against JD terminology to flag equivalent but differently worded terms and calculate a jargon penalty score.

CONTEXT
Applicant Tracking Systems (ATS) and recruiters do semantic matching. You must identify where the résumé uses terminology that means the same thing as the JD but might fail an exact keyword match.
Severity scoring rules:
- high: The JD uses no equivalent language at all for the term in the résumé.
- medium: There is partial overlap between the résumé term and JD terminology.
- low: The JD already uses matching or highly adjacent terminology.
Scoring formula: max(0, 100 - (10 * high_count) - (5 * medium_count) - (2 * low_count)).

CONSTRAINTS
- Do not use a static translation table; compare the specific inputs provided dynamically.
- The `suggested_translation` must identify the JD term it maps to; it is a diagnostic tool, not a rewrite of the résumé bullet.

OUTPUT
{
  "flags": [{"bullet_text": "string (verbatim)", "term_used": "string",
             "suggested_translation": "string", "severity": "low|medium|high"}],
  "jargon_score": 0
}

Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


STRUCTURE_AUDIT_PROMPT = """
INSTRUCTION
Audit the provided résumé text for general ATS-parseability and standard formatting conventions, and generate a structure score.

CONTEXT
Evaluate the text against general ATS-parseability rules:
1. Single-column layout.
2. Standard section headers (e.g., Summary, Experience, Education, Skills).
3. Reverse-chronological order for experience and education.
4. Appropriate length (typically 1-2 pages).
5. Contact info placed at the top.
6. No images, tables, or complex graphics.
Structure score should be between 0 and 100 based on adherence to these conventions.

CONSTRAINTS
- Base your analysis solely on the provided résumé text.
- Do not correct or rewrite the layout. Note issues in the `ats_red_flags` diagnostic field only.

OUTPUT
{
  "page_count_estimate": 1,
  "single_column_likely": true,
  "section_headings_present": ["string"],
  "section_headings_missing": ["string"],
  "reverse_chronological_likely": true,
  "contact_info_at_top": true,
  "length_appropriate": true,
  "no_images_or_graphics": true,
  "ats_red_flags": [{"issue": "string", "evidence": "string"}],
  "structure_score": 0
}

Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content.
"""


DEGREE_ALIGNMENT_PROMPT = """\
You are a degree-alignment checker. You are given a JD profile JSON and the
student's degree program code. You check whether the JD job title is on the
suggested-titles list for the student's degree.

Degree-Aligned Job Title Lists
===============================
RTIS (Real-Time Interactive Simulation):
  Game Engine Developer, Systems Engineer, Site Reliability Engineer (SRE),
  DevOps Engineer, AI/ML Engineer, Data Analyst / Data Scientist,
  Full Stack Developer, Cybersecurity Engineer, Simulation Engineer,
  Graphics Programmer, Technical Product Manager, Technical Project Manager

IMGD (Interactive Media & Game Development):
  Game Developer, Systems Engineer, Full Stack Developer, Data Engineer,
  Infrastructure Engineer, DevOps Engineer, Cybersecurity Engineer,
  AI/ML Engineer, Technical Designer, Technical Artist,
  Gameplay Programmer, Tools Engineer,
  Technical Product Manager, Technical Project Manager

UXGD (User Experience & Game Design):
  App Developer, UI/UX Designer, Product Designer, Product Manager,
  Product Operations Manager, Project Manager, Marketing & Design Specialist,
  Process Architect, Technical Designer, Technical Artist,
  UX Researcher, UX Engineer

BFA (Digital Art and Animation):
  Technical Artist, UI/UX Designer, Creative Designer, Unreal Engine Artist,
  3D Graphic Artist, Production Assistant, Project Manager, Project Operations

Matching rule:
- title_on_suggested_list is true if the JD title matches an entry exactly OR
  is a clear variant (e.g. "Junior Systems Engineer" matches "Systems Engineer").
- If false, set degree_alignment_score to 50-70 with fit_commentary explaining
  the mismatch. Never invent a match.

JSON schema:

{
  "student_degree": "string",
  "jd_title": "string",
  "title_on_suggested_list": true,
  "matched_against": "string",
  "fit_commentary": "string (40 words or fewer)",
  "degree_alignment_score": 100
}

Output ONLY a valid JSON object matching the schema above. No prose. No
markdown fences. Never rewrite or generate résumé content.
"""


# ---------------------------------------------------------------------------
# Synthesis prompt
# ---------------------------------------------------------------------------

OVERALL_SUMMARY_PROMPT = """
INSTRUCTION
Produce a 3-bullet plain Markdown executive summary from the provided full analysis report.

CONTEXT
You will be provided with a JSON report containing evaluated scores and flags (keyword match, bullet quality, jargon, structure, and background fit). 

CONSTRAINTS
- Output exactly 3 bullet points in plain Markdown.
- The summary must be diagnostic only, focusing on strengths, weaknesses, and alignment.
- Never rewrite or generate new résumé content.
- DO NOT output JSON. Do not include markdown fences (```).

OUTPUT
* First bullet summarizing key strengths and fit.
* Second bullet summarizing primary gaps or missing requirements.
* Third bullet summarizing formatting, bullet quality, or structural observations.
"""