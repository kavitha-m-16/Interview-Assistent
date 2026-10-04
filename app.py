# ============================================================
# INTERVAIQ - AI INTERVIEW PREPARATION ASSISTANT
# ============================================================

import streamlit as st
import os
import json

from dotenv import load_dotenv
from groq import Groq

from utils.resume_parser import extract_text_from_pdf
from utils.ai_engine import analyze_resume
from database import (
    init_db,
    create_user,
    verify_user,
    get_user,
    save_resume,
    create_interview,
    save_question_result,
    update_interview_score,
    get_user_interviews,
    get_interview_results,
    get_user_interview_history
)

# Initialize IntervAIQ database
init_db()

# Streamlit page configuration must run before other Streamlit commands.
st.set_page_config(
    page_title="IntervAIQ",
    page_icon="🤖",
    layout="wide"
)

# ============================================================
# INTERVAIQ VISUAL THEME
# ============================================================
# A futuristic AI/interview background is created with CSS so the
# application remains self-contained and does not depend on an
# external image URL.
st.markdown(
    """
    <style>
    /* ---------- APP BACKGROUND ---------- */
    .stApp {
        background:
            radial-gradient(circle at 12% 12%, rgba(64, 120, 255, 0.20), transparent 28%),
            radial-gradient(circle at 88% 18%, rgba(168, 85, 247, 0.17), transparent 25%),
            radial-gradient(circle at 50% 92%, rgba(14, 165, 233, 0.12), transparent 30%),
            linear-gradient(135deg, #050816 0%, #0a1024 48%, #07111f 100%);
        color: #eef4ff;
    }

    /* Subtle neural-network grid / tech pattern */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.22;
        background-image:
            linear-gradient(rgba(96, 165, 250, 0.055) 1px, transparent 1px),
            linear-gradient(90deg, rgba(96, 165, 250, 0.055) 1px, transparent 1px),
            radial-gradient(circle at 18% 30%, rgba(96, 165, 250, 0.35) 0 1px, transparent 2px),
            radial-gradient(circle at 76% 24%, rgba(192, 132, 252, 0.30) 0 1px, transparent 2px),
            radial-gradient(circle at 65% 72%, rgba(56, 189, 248, 0.25) 0 1px, transparent 2px);
        background-size: 54px 54px, 54px 54px, 170px 170px, 230px 230px, 190px 190px;
    }

    /* Keep Streamlit content above the background layer */
    .stApp > header, .stApp [data-testid="stAppViewContainer"] {
        position: relative;
        z-index: 1;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: transparent;
    }

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(7, 13, 31, 0.97), rgba(9, 18, 38, 0.94));
        border-right: 1px solid rgba(96, 165, 250, 0.15);
    }

    section[data-testid="stSidebar"] * {
        color: #e7efff;
    }

    /* ---------- GLASS CARDS ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(10, 18, 39, 0.58);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 18px;
        box-shadow: 0 16px 45px rgba(0, 0, 0, 0.22);
        backdrop-filter: blur(12px);
    }

    /* ---------- HEADINGS ---------- */
    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    h1 {
        text-shadow: 0 0 28px rgba(96, 165, 250, 0.22);
    }

    /* ---------- BUTTONS ---------- */
    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(96, 165, 250, 0.28);
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.82), rgba(124, 58, 237, 0.82));
        color: white;
        font-weight: 650;
        min-height: 44px;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.18);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: rgba(147, 197, 253, 0.70);
        transform: translateY(-1px);
        box-shadow: 0 12px 32px rgba(59, 130, 246, 0.26);
    }

    /* ---------- INPUTS ---------- */
    div[data-baseweb="input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="select"] > div {
        background: rgba(15, 23, 42, 0.72) !important;
        border-color: rgba(148, 163, 184, 0.20) !important;
        border-radius: 12px !important;
    }

    /* ---------- TABS ---------- */
    button[data-baseweb="tab"] {
        color: #b9c7e5;
        font-weight: 600;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #93c5fd;
    }

    /* ---------- FILE UPLOADER ---------- */
    [data-testid="stFileUploader"] section {
        background: rgba(15, 23, 42, 0.58);
        border: 1px dashed rgba(96, 165, 250, 0.34);
        border-radius: 16px;
    }

    /* ---------- METRICS ---------- */
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.52);
        border: 1px solid rgba(148, 163, 184, 0.13);
        border-radius: 16px;
        padding: 14px;
    }

    /* ---------- ALERTS ---------- */
    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    /* ---------- CUSTOM HERO ---------- */
    .intervaiq-hero {
        position: relative;
        overflow: hidden;
        margin: 0.4rem 0 1.4rem 0;
        padding: 3.2rem 2.4rem;
        border-radius: 26px;
        border: 1px solid rgba(96, 165, 250, 0.20);
        background:
            radial-gradient(circle at 78% 25%, rgba(124, 58, 237, 0.28), transparent 24%),
            radial-gradient(circle at 18% 70%, rgba(14, 165, 233, 0.20), transparent 27%),
            linear-gradient(135deg, rgba(10, 18, 39, 0.88), rgba(15, 23, 42, 0.66));
        box-shadow: 0 25px 70px rgba(0,0,0,0.30);
        backdrop-filter: blur(14px);
    }

    .intervaiq-hero::after {
        content: "AI  •  RESUME  •  INTERVIEW  •  FEEDBACK  •  SKILL GAP";
        position: absolute;
        right: 28px;
        bottom: 18px;
        font-size: 10px;
        letter-spacing: 0.16em;
        color: rgba(191, 219, 254, 0.45);
    }

    .intervaiq-badge {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(59, 130, 246, 0.13);
        border: 1px solid rgba(96, 165, 250, 0.25);
        color: #bfdbfe;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
    }

    .intervaiq-title {
        margin: 0.8rem 0 0.3rem 0;
        font-size: clamp(2.2rem, 5vw, 4.6rem);
        line-height: 0.98;
        font-weight: 800;
        background: linear-gradient(90deg, #f8fbff, #93c5fd, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .intervaiq-subtitle {
        max-width: 720px;
        color: #b9c7e5;
        font-size: 1.08rem;
        line-height: 1.65;
    }

    .intervaiq-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 1.2rem;
    }

    .intervaiq-pill {
        padding: 7px 11px;
        border-radius: 10px;
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(148,163,184,0.13);
        color: #dbeafe;
        font-size: 12px;
    }

    /* Compact footer */
    .intervaiq-footer {
        text-align: center;
        color: rgba(191, 219, 254, 0.45);
        font-size: 11px;
        padding: 24px 0 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Authentication Session
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_email" not in st.session_state:
    st.session_state.user_email = ""


def reset_user_session_state():
    """Clear all user-specific in-memory data when switching accounts."""
    defaults = {
        "resume_text": "",
        "resume_analysis": None,
        "candidate_name": "",
        "interview_started": False,
        "interview_questions": [],
        "current_question": 0,
        "answer_evaluation": None,
        "current_hint": None,
        "last_answer": "",
        "selected_company": "",
        "selected_role": "",
        "selected_mode": "",
        "show_model_answer": False,
        "interview_results": [],
        "current_interview_id": None,
        "job_description_text": "",
        "job_match_analysis": None,
        "coach_messages": [],
        "question_reason": None,
        "show_question_reason": False
    }

    for key, value in defaults.items():
        st.session_state[key] = value

def authentication_page():

    st.markdown(
        """
        <div class="intervaiq-hero">
            <span class="intervaiq-badge">✦ AI-POWERED INTERVIEW PLATFORM</span>
            <div class="intervaiq-title">IntervAIQ</div>
            <div class="intervaiq-subtitle">
                Your personalized AI interview coach — analyze your resume,
                practice role-specific interviews, receive instant feedback,
                discover skill gaps, and become interview-ready.
            </div>
            <div class="intervaiq-pills">
                <span class="intervaiq-pill">🧠 Personalized Questions</span>
                <span class="intervaiq-pill">📄 Resume Intelligence</span>
                <span class="intervaiq-pill">🎙️ Voice-to-Text</span>
                <span class="intervaiq-pill">📊 AI Evaluation</span>
                <span class="intervaiq-pill">🎯 Skill Gap Analysis</span>
                <span class="intervaiq-pill">⚡ Adaptive Interviewer</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🚀 Practice Smarter. Perform Better.")

    st.write(
        "Create an account or sign in to start your personalized AI interview experience."
    )

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    # =====================================
    # LOGIN
    # =====================================

    with login_tab:

        st.subheader("Welcome Back 👋")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Please enter both email and password."
                )

            else:

                user = verify_user(
                    email,
                    password
                )

                if user:

                    # Important: remove any previous account's interview/resume state.
                    reset_user_session_state()

                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.user_name = user["name"]
                    st.session_state.user_email = user["email"]

                    st.success(
                        f"Welcome back, {user['name']}! 🎉"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

    # =====================================
    # REGISTER
    # =====================================

    with register_tab:

        st.subheader("Create Your Account 🚀")

        name = st.text_input(
            "Full Name",
            key="register_name"
        )

        email = st.text_input(
            "Email",
            key="register_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if not name or not email or not password:

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success, result = create_user(
                    name,
                    email,
                    password
                )

                if success:

                    st.success(
                        "Account created successfully! 🎉"
                    )

                    st.info(
                        "Please go to the Login tab and sign in."
                    )

                else:

                    st.error(result)

if not st.session_state.logged_in:

    authentication_page()

    st.stop()


st.sidebar.success(
    f"👋 Welcome, {st.session_state.user_name}"
)

st.sidebar.caption(
    st.session_state.user_email
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    reset_user_session_state()

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = ""
    st.session_state.user_email = ""

    st.rerun()

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ GROQ_API_KEY not found in .env file.")
    st.stop()

client = Groq(api_key=api_key)


# ============================================================
# VOICE-TO-TEXT ANSWER SUPPORT
# ============================================================

def transcribe_voice_to_text(audio_file):
    """Convert a recorded interview answer into text using Groq Whisper."""
    try:
        if audio_file is None:
            return ""

        audio_bytes = audio_file.getvalue()

        if not audio_bytes:
            return ""

        transcription = client.audio.transcriptions.create(
            file=("voice_answer.wav", audio_bytes),
            model="whisper-large-v3-turbo",
            response_format="text"
        )

        if isinstance(transcription, str):
            return transcription.strip()

        text_value = getattr(transcription, "text", "")
        return text_value.strip()

    except Exception as e:
        return f"__VOICE_ERROR__:{str(e)}"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 20px;
        margin-bottom: 30px;
    }

    .question-card {
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #444;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .score-card {
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid #444;
        margin: 20px 0;
    }

    .big-score {
        font-size: 55px;
        font-weight: 800;
    }

    .dashboard-card {
        padding: 20px;
        border-radius: 18px;
        border: 1px solid #444;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "resume_analysis" not in st.session_state:
    st.session_state.resume_analysis = None

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "answer_evaluation" not in st.session_state:
    st.session_state.answer_evaluation = None

if "current_hint" not in st.session_state:
    st.session_state.current_hint = None

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if "selected_company" not in st.session_state:
    st.session_state.selected_company = ""

if "selected_role" not in st.session_state:
    st.session_state.selected_role = ""

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = ""

if "show_model_answer" not in st.session_state:
    st.session_state.show_model_answer = False

if "interview_results" not in st.session_state:
    st.session_state.interview_results = []

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "current_interview_id" not in st.session_state:
    st.session_state.current_interview_id = None

if "job_description_text" not in st.session_state:
    st.session_state.job_description_text = ""

if "question_reason" not in st.session_state:
    st.session_state.question_reason = None

if "show_question_reason" not in st.session_state:
    st.session_state.show_question_reason = False

if "job_match_analysis" not in st.session_state:
    st.session_state.job_match_analysis = None


# ============================================================
# GENERATE INTERVIEW QUESTIONS
# ============================================================

def generate_interview_questions(
    resume_text,
    company,
    role,
    mode,
    difficulty,
    number_of_questions,
    job_description=""
):

    prompt = f"""
You are IntervAIQ, an expert AI interview preparation coach.

Create personalized interview questions based on the candidate's
resume, selected company, role, interview mode, and difficulty.

CANDIDATE RESUME:
{resume_text}

COMPANY:
{company}

ROLE:
{role}

INTERVIEW MODE:
{mode}

DIFFICULTY:
{difficulty}

NUMBER OF QUESTIONS:
{number_of_questions}

TARGET JOB DESCRIPTION (optional):
{job_description or "No job description provided."}

Create a balanced interview.

Each question must contain:

- question
- category
- difficulty
- topic

Categories can include:

- HR
- Technical
- Behavioral
- Project
- Coding

Difficulty can be:

- Easy
- Medium
- Hard

Return ONLY valid JSON.

Use exactly this structure:

{{
    "questions": [
        {{
            "question": "",
            "category": "",
            "difficulty": "",
            "topic": ""
        }}
    ]
}}

IMPORTANT:

- Questions should be relevant to the candidate's resume.
- Do not invent technologies that are not in the resume.
- Questions should match the selected role.
- Questions should match the selected difficulty.
- Make questions suitable for a real interview.
- Avoid duplicate questions.
"""

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional interview question "
                        "generator. Always return valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.4,

            response_format={
                "type": "json_object"
            }
        )

        result = response.choices[0].message.content

        data = json.loads(result)

        return data.get("questions", [])

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# RESUME + JOB DESCRIPTION SKILL MATCHING
# ============================================================

def analyze_job_description_match(resume_text, job_description):
    """Compare the candidate resume with a target job description."""

    prompt = f"""
You are IntervAIQ, an AI career and interview preparation analyst.

Compare the candidate resume with the target job description.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Identify the candidate's matching skills, missing skills, strengths,
and practical interview preparation priorities.

Return ONLY valid JSON using exactly this structure:
{{
    "match_percentage": 0,
    "matching_skills": [],
    "missing_skills": [],
    "strengths": [],
    "priority_topics": [],
    "summary": ""
}}

Rules:
- match_percentage must be between 0 and 100.
- Only mention skills supported by the resume or job description.
- Keep lists concise and useful.
- Do not invent experience.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise resume and job description matching analyst. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# ADAPTIVE FOLLOW-UP QUESTION
# ============================================================

def generate_adaptive_followup(question, answer, evaluation, role, category, topic):
    """Generate one interviewer-style follow-up based on the previous answer."""

    prompt = f"""
You are IntervAIQ, conducting a realistic adaptive interview.

ROLE: {role}
CATEGORY: {category}
TOPIC: {topic}

ORIGINAL QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

AI EVALUATION:
Score: {evaluation.get('score', 0)}/100
Technical Accuracy: {evaluation.get('technical_accuracy', 0)}/100
Relevance: {evaluation.get('relevance', 0)}/100
Completeness: {evaluation.get('completeness', 0)}/100
Clarity: {evaluation.get('clarity', 0)}/100
What Went Wrong: {evaluation.get('what_went_wrong', [])}
Improvement Tip: {evaluation.get('improvement_tip', '')}

Generate ONE realistic interviewer follow-up question that probes the
weakest or most interesting part of the candidate's answer.

Rules:
- The follow-up must depend on the candidate's actual answer.
- Do not simply repeat the original question.
- Keep it concise and interview-ready.
- Prefer a deeper why/how/example/trade-off question.
- Return ONLY valid JSON.

Use exactly:
{{
    "question": "",
    "category": "{category}",
    "difficulty": "Medium",
    "topic": "{topic}"
}}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a realistic adaptive interviewer. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        data["is_followup"] = True
        return data
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# EXPLAIN WHY THIS QUESTION WAS ASKED
# ============================================================

def generate_question_reason(
    question,
    resume_text,
    company,
    role,
    mode,
    difficulty,
    category,
    topic,
    job_description=""
):
    """Explain why IntervAIQ selected the current interview question."""

    prompt = f"""
You are IntervAIQ's Explainable AI interview assistant.

Explain clearly why the following interview question was selected.
The explanation must be based ONLY on the information provided below.
Do not claim that a company definitely asks this question unless that
information is explicitly provided. The company is a personalization
context, not proof of a real company interview pattern.

CANDIDATE RESUME:
{resume_text}

SELECTED COMPANY:
{company}

SELECTED ROLE:
{role}

INTERVIEW MODE:
{mode}

DIFFICULTY:
{difficulty}

QUESTION CATEGORY:
{category}

QUESTION TOPIC:
{topic}

INTERVIEW QUESTION:
{question}

JOB DESCRIPTION (if provided):
{job_description or "No job description provided."}

Return ONLY valid JSON using exactly this structure:
{{
    "reason": "",
    "resume_evidence": [],
    "skills_tested": [],
    "interview_context": [],
    "learning_objective": ""
}}

Rules:
- reason should be a short, natural explanation of why this question is relevant.
- resume_evidence should contain 1 to 3 concrete items from the resume that support the question.
- If the resume does not support a specific item, do not invent one.
- skills_tested should list the actual skills or concepts being assessed.
- interview_context should mention relevant selections such as company, role, mode, difficulty, category, or job-description alignment.
- learning_objective should explain what the candidate is expected to demonstrate.
- Keep every list concise and presentation-friendly.
- Never invent work experience, skills, projects, technologies, or company-specific hiring practices.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an explainable AI interview assistant. "
                        "Only use evidence supplied by the user context and "
                        "always return valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        return {
            "reason": data.get("reason", ""),
            "resume_evidence": data.get("resume_evidence", []),
            "skills_tested": data.get("skills_tested", []),
            "interview_context": data.get("interview_context", []),
            "learning_objective": data.get("learning_objective", "")
        }

    except Exception as e:
        return {"error": str(e)}


# ============================================================
# EVALUATE ANSWER
# ============================================================

def evaluate_answer(
    question,
    answer,
    category,
    topic
):

    prompt = f"""
You are IntervAIQ, an expert AI interview evaluator.

Evaluate the candidate's answer to the interview question.

QUESTION:
{question}

CATEGORY:
{category}

TOPIC:
{topic}

CANDIDATE ANSWER:
{answer}

Evaluate the answer based on:

1. Technical accuracy
2. Relevance to the question
3. Completeness
4. Clarity
5. Interview quality

Return ONLY valid JSON using exactly this structure:

{{
    "score": 0,
    "result": "Correct",
    "technical_accuracy": 0,
    "relevance": 0,
    "completeness": 0,
    "clarity": 0,
    "what_went_well": [],
    "what_went_wrong": [],
    "explanation": "",
    "model_answer": "",
    "improvement_tip": ""
}}

IMPORTANT:

- score must be between 0 and 100.
- Each individual score must be between 0 and 100.
- result must be one of:
  "Correct", "Partially Correct", or "Incorrect".
- Do not mark an answer incorrect just because it is short.
- Judge the actual meaning of the answer.
- Do not invent facts about the candidate.
- Give constructive feedback.
- The model answer should be suitable for a real interview.
- Keep feedback clear and practical.
"""

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional technical interview "
                        "evaluator. Always return valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            response_format={
                "type": "json_object"
            }
        )

        result = response.choices[0].message.content

        return json.loads(result)

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# GENERATE AI HINT
# ============================================================

def generate_hint(
    question,
    category,
    topic
):

    prompt = f"""
You are IntervAIQ, an AI interview coach.

Give the candidate a helpful hint for answering this question.

QUESTION:
{question}

CATEGORY:
{category}

TOPIC:
{topic}

IMPORTANT:

- Do NOT provide the complete answer.
- Give only a useful hint.
- Help the candidate remember important points.
- Keep the hint concise.
- The candidate should still think and create their own answer.
"""

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful interview coach."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.4
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"Unable to generate hint: {str(e)}"


# ============================================================
# SAVE CURRENT RESULT
# ============================================================

def save_current_result(
    question_data,
    evaluation,
    answer
):
    """Save the evaluated answer both in memory and in the logged-in user's DB."""

    result_data = {
        "question": question_data.get("question", ""),
        "category": question_data.get("category", "General"),
        "difficulty": question_data.get("difficulty", "Medium"),
        "topic": question_data.get("topic", "General"),
        "answer": answer or "",
        "score": evaluation.get("score", 0),
        "technical_accuracy": evaluation.get("technical_accuracy", 0),
        "relevance": evaluation.get("relevance", 0),
        "completeness": evaluation.get("completeness", 0),
        "clarity": evaluation.get("clarity", 0),
        "result": evaluation.get("result", "Partially Correct"),
        "what_went_well": evaluation.get("what_went_well", []),
        "what_went_wrong": evaluation.get("what_went_wrong", []),
        "explanation": evaluation.get("explanation", ""),
        "model_answer": evaluation.get("model_answer", ""),
        "improvement_tip": evaluation.get("improvement_tip", "")
    }

    st.session_state.interview_results.append(result_data)

    user_id = st.session_state.get("user_id")
    interview_id = st.session_state.get("current_interview_id")

    if user_id and interview_id:
        try:
            save_question_result(
                interview_id,
                user_id,
                result_data
            )
        except Exception as e:
            st.warning(
                f"⚠️ Result was shown in the app, but database saving failed: {e}"
            )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 IntervAIQ</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Personalized AI Interview Coach & Skill-Gap Analyzer'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "Prepare smarter, practice better, and understand exactly "
    "where you need to improve."
)

st.divider()


# ============================================================
# RESUME INTELLIGENCE
# ============================================================

st.markdown(
    """
    <div class="intervaiq-hero">
        <span class="intervaiq-badge">✦ PERSONALIZED AI INTERVIEW WORKSPACE</span>
        <div class="intervaiq-title" style="font-size: clamp(2rem, 4vw, 3.6rem);">
            Train for the interview you actually want.
        </div>
        <div class="intervaiq-subtitle">
            Upload your resume, match it with a job description, choose a company and role,
            then let IntervAIQ build a dynamic interview around your skills and goals.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.header("📄 Resume Intelligence")

st.write(
    "Upload your resume and IntervAIQ will analyze it to "
    "personalize your interview preparation."
)

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF)",
    type=["pdf"]
)


# Optional job description for skill-gap personalization
job_description_file = st.file_uploader(
    "📋 Upload Job Description (Optional PDF)",
    type=["pdf"],
    help="Upload the JD for the role you are targeting. IntervAIQ will compare it with your resume and personalize the interview."
)

if job_description_file is not None:
    st.success(f"Job description uploaded: {job_description_file.name}")

    if st.button("🎯 Analyze Resume ↔ Job Description", key="analyze_jd_button"):
        if not st.session_state.resume_text:
            st.warning("⚠️ Please analyze your resume first.")
        else:
            with st.spinner("🤖 Comparing your resume with the job description..."):
                try:
                    jd_text = extract_text_from_pdf(job_description_file)
                    st.session_state.job_description_text = jd_text
                    match = analyze_job_description_match(
                        st.session_state.resume_text,
                        jd_text
                    )
                    if isinstance(match, dict) and "error" not in match:
                        st.session_state.job_match_analysis = match
                        st.success("✅ Resume and job description matched successfully!")
                    else:
                        st.error(f"❌ JD analysis failed: {match.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Could not process the job description: {e}")

if st.session_state.get("job_match_analysis"):
    match = st.session_state.job_match_analysis
    st.subheader("🎯 Resume ↔ Job Match")

    match_score = int(match.get("match_percentage", 0) or 0)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🎯 Skill Match", f"{match_score}%")
    with c2:
        st.metric("✅ Matching Skills", len(match.get("matching_skills", [])))
    with c3:
        st.metric("⚠️ Missing Skills", len(match.get("missing_skills", [])))

    st.progress(max(0, min(100, match_score)) / 100)

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**✅ Skills You Match**")
        for skill in match.get("matching_skills", [])[:8]:
            st.write(f"• {skill}")
    with m2:
        st.markdown("**⚠️ Skills to Improve**")
        for skill in match.get("missing_skills", [])[:8]:
            st.write(f"• {skill}")

    if match.get("priority_topics"):
        st.info("📚 **Priority Interview Topics:** " + ", ".join(match.get("priority_topics", [])[:6]))

    if match.get("summary"):
        st.caption(match.get("summary"))


# ============================================================
# PROCESS RESUME
# ============================================================

if uploaded_file is not None:

    st.success(
        f"Resume uploaded successfully: {uploaded_file.name}"
    )

    if st.button(
        "🔍 Analyze Resume",
        key="analyze_resume_button"
    ):

        with st.spinner(
            "🤖 IntervAIQ is analyzing your resume..."
        ):

            try:

                resume_text = extract_text_from_pdf(
                    uploaded_file
                )

                st.session_state.resume_text = resume_text

                analysis = analyze_resume(
                    resume_text
                )

                if isinstance(analysis, dict):

                    if "error" in analysis:

                        st.error(
                            f"❌ Resume analysis failed: "
                            f"{analysis['error']}"
                        )

                    else:

                        st.session_state.resume_analysis = analysis

                        # Keep the resume name available to the rest of the app.
                        detected_name = analysis.get("name") if isinstance(analysis, dict) else ""
                        st.session_state.candidate_name = (
                            detected_name or st.session_state.user_name
                        )

                        # Save this resume/profile under the currently logged-in user.
                        try:
                            profile_payload = json.dumps(
                                {
                                    "analysis": analysis,
                                    "resume_text": resume_text
                                },
                                ensure_ascii=False
                            )
                            save_resume(
                                st.session_state.user_id,
                                uploaded_file.name,
                                profile_payload
                            )
                        except Exception as e:
                            st.warning(
                                f"⚠️ Resume analyzed, but database saving failed: {e}"
                            )

                        st.success(
                            "🎉 Resume analyzed successfully and saved to your account!"
                        )

                else:

                    st.session_state.resume_analysis = analysis

            except Exception as e:

                st.error(
                    f"❌ Resume processing failed: {str(e)}"
                )


# ============================================================
# DISPLAY RESUME TEXT
# ============================================================

if st.session_state.resume_text:

    st.subheader("📋 Extracted Resume Content")

    with st.expander(
        "View Extracted Resume Text",
        expanded=False
    ):

        st.text_area(
            "Resume Text",
            st.session_state.resume_text,
            height=300
        )


# ============================================================
# DISPLAY RESUME ANALYSIS
# ============================================================

if st.session_state.resume_analysis:

    analysis = st.session_state.resume_analysis

    if isinstance(analysis, dict):

        st.divider()

        st.header(
            "👤 Your IntervAIQ Candidate Profile"
        )

        # NAME

        if analysis.get("name"):

            st.subheader("👤 Name")

            st.write(
                analysis.get("name")
            )

        # SUMMARY

        if analysis.get(
            "professional_summary"
        ):

            st.subheader(
                "📝 Professional Summary"
            )

            st.write(
                analysis.get(
                    "professional_summary"
                )
            )

        # EDUCATION

        if analysis.get("education"):

            st.subheader(
                "🎓 Education"
            )

            for education in analysis[
                "education"
            ]:

                st.write(
                    f"• {education}"
                )

        # SKILLS AND PROJECTS

        col1, col2 = st.columns(2)

        with col1:

            if analysis.get(
                "technical_skills"
            ):

                st.subheader(
                    "💻 Technical Skills"
                )

                for skill in analysis[
                    "technical_skills"
                ]:

                    st.write(
                        f"• {skill}"
                    )

        with col2:

            if analysis.get(
                "projects"
            ):

                st.subheader(
                    "📁 Projects"
                )

                for project in analysis[
                    "projects"
                ]:

                    st.write(
                        f"• {project}"
                    )

        # EXPERIENCE

        if analysis.get(
            "experience"
        ):

            st.subheader(
                "💼 Experience"
            )

            for experience in analysis[
                "experience"
            ]:

                st.write(
                    f"• {experience}"
                )


# ============================================================
# AI MOCK INTERVIEW
# ============================================================

st.divider()

st.header("🎯 AI Mock Interview")

st.write(
    "Practice personalized interview questions based on "
    "your resume, target company, and role."
)


# ============================================================
# INTERVIEW SETUP
# ============================================================

st.subheader("⚙️ Interview Setup")

col1, col2 = st.columns(2)

# A broad company list so students can practice for both product and service companies.
company_options = [
    "General Placement Interview",
    "Google",
    "Microsoft",
    "Amazon",
    "Apple",
    "Meta",
    "Netflix",
    "Adobe",
    "Salesforce",
    "Oracle",
    "IBM",
    "Cisco",
    "Intel",
    "NVIDIA",
    "Qualcomm",
    "Dell Technologies",
    "HP",
    "SAP",
    "Accenture",
    "Deloitte",
    "EY",
    "KPMG",
    "PwC",
    "Cognizant",
    "Capgemini",
    "TCS",
    "Infosys",
    "Wipro",
    "HCLTech",
    "Tech Mahindra",
    "LTIMindtree",
    "Mphasis",
    "Persistent Systems",
    "Hexaware",
    "Coforge",
    "Zoho",
    "Freshworks",
    "Razorpay",
    "PhonePe",
    "Paytm",
    "Flipkart",
    "Myntra",
    "Swiggy",
    "Zomato",
    "Meesho",
    "Groww",
    "CRED",
    "Zerodha",
    "Dream11",
    "Juspay",
    "BrowserStack",
    "Postman",
    "ServiceNow",
    "Uber",
    "Airbnb",
    "Atlassian",
    "LinkedIn",
    "Goldman Sachs",
    "JPMorgan Chase",
    "Morgan Stanley",
    "Wells Fargo",
    "American Express",
    "Visa",
    "Mastercard",
    "DHL",
    "FedEx",
    "Other / Custom Company"
]

role_options = [
    "Software Engineer",
    "Software Developer",
    "Associate Software Engineer",
    "Software Trainee",
    "Graduate Engineer Trainee",
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "Web Developer",
    "Python Developer",
    "Java Developer",
    "C++ Developer",
    "JavaScript Developer",
    "React Developer",
    "Node.js Developer",
    "AI Engineer",
    "AI/ML Engineer",
    "Machine Learning Engineer",
    "Machine Learning Intern",
    "Deep Learning Engineer",
    "Data Analyst",
    "Data Scientist",
    "Data Engineer",
    "Business Analyst",
    "Product Analyst",
    "Product Manager",
    "SQL Developer",
    "Database Developer",
    "Cloud Engineer",
    "Cloud Support Engineer",
    "DevOps Engineer",
    "Site Reliability Engineer",
    "Cybersecurity Analyst",
    "Security Engineer",
    "QA Engineer",
    "Automation Tester",
    "Manual Tester",
    "Android Developer",
    "Flutter Developer",
    "iOS Developer",
    "UI/UX Designer",
    "Technical Support Engineer",
    "Other / Custom Role"
]

with col1:

    company_choice = st.selectbox(
        "🏢 Select Company",
        company_options,
        key="company_select"
    )

    if company_choice == "Other / Custom Company":
        custom_company = st.text_input(
            "✏️ Enter Company Name",
            placeholder="Example: ABC Technologies",
            key="custom_company"
        ).strip()
        company = custom_company or "Other Company"
    else:
        company = company_choice

with col2:

    role_choice = st.selectbox(
        "💼 Select Role",
        role_options,
        key="role_select"
    )

    if role_choice == "Other / Custom Role":
        custom_role = st.text_input(
            "✏️ Enter Role Name",
            placeholder="Example: Generative AI Intern",
            key="custom_role"
        ).strip()
        role = custom_role or "Other Role"
    else:
        role = role_choice


col1, col2, col3 = st.columns(3)

with col1:

    interview_mode = st.selectbox(
        "🎓 Interview Mode",
        [
            "Mixed Interview",
            "HR Interview",
            "Technical Interview",
            "Behavioral Interview",
            "Project Interview",
            "Coding Interview"
        ]
    )

with col2:

    number_of_questions = st.selectbox(
        "🔢 Number of Questions",
        [5, 10, 15]
    )

with col3:

    difficulty = st.selectbox(
        "📊 Difficulty",
        [
            "Mixed",
            "Easy",
            "Medium",
            "Hard"
        ]
    )


# ============================================================
# START INTERVIEW
# ============================================================

if st.button(
    "🚀 Start AI Mock Interview",
    type="primary",
    use_container_width=True
):

    if not st.session_state.resume_text:

        st.warning(
            "⚠️ Please upload and analyze your resume first."
        )

    else:

        with st.spinner(
            "🤖 Generating your personalized interview..."
        ):

            questions = generate_interview_questions(
                resume_text=st.session_state.resume_text,
                company=company,
                role=role,
                mode=interview_mode,
                difficulty=difficulty,
                number_of_questions=number_of_questions,
                job_description=st.session_state.get("job_description_text", "")
            )

        if isinstance(
            questions,
            dict
        ):

            st.error(
                f"❌ Interview generation failed: "
                f"{questions.get('error')}"
            )

        elif not questions:

            st.error(
                "❌ No interview questions were generated."
            )

        else:

            # Create a separate database interview session for this logged-in user.
            try:
                interview_id = create_interview(
                    st.session_state.user_id,
                    company,
                    role
                )
                st.session_state.current_interview_id = interview_id
            except Exception as e:
                st.error(
                    f"❌ Could not create interview session in database: {e}"
                )
                st.stop()

            st.session_state.interview_questions = questions

            st.session_state.current_question = 0

            st.session_state.interview_started = True

            st.session_state.answer_evaluation = None

            st.session_state.current_hint = None

            st.session_state.last_answer = ""

            st.session_state.show_model_answer = False
            st.session_state.question_reason = None
            st.session_state.show_question_reason = False

            # Clear previous interview results

            st.session_state.interview_results = []

            st.session_state.selected_company = company

            st.session_state.selected_role = role

            st.session_state.selected_mode = interview_mode

            st.success(
                "🎉 Your AI mock interview is ready!"
            )

            st.rerun()


# ============================================================
# INTERACTIVE INTERVIEW
# ============================================================

if (
    st.session_state.interview_started
    and st.session_state.interview_questions
):

    questions = st.session_state.interview_questions

    current = st.session_state.current_question


    # ========================================================
    # FINAL DASHBOARD
    # ========================================================

    if current >= len(questions):

        st.divider()

        st.balloons()

        st.markdown(
            """
            <div class="score-card">

            <h1>🏆 INTERVIEW COMPLETED!</h1>

            <p>
            Great job! Here is your complete
            IntervAIQ performance report.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        results = st.session_state.interview_results


        # ====================================================
        # SAFETY CHECK
        # ====================================================

        if not results:

            st.warning(
                "⚠️ No interview results were recorded."
            )

        else:

            # =================================================
            # OVERALL SCORE
            # =================================================

            total_score = sum(
                item["score"]
                for item in results
            )

            overall_score = round(
                total_score / len(results)
            )

            readiness_score = round(
                (overall_score * 0.50)
                + (sum(item.get("technical_accuracy", 0) for item in results) / len(results) * 0.15)
                + (sum(item.get("relevance", 0) for item in results) / len(results) * 0.15)
                + (sum(item.get("completeness", 0) for item in results) / len(results) * 0.10)
                + (sum(item.get("clarity", 0) for item in results) / len(results) * 0.10)
            )


            # READINESS

            if overall_score >= 80:

                readiness = "🔥 Excellent"

            elif overall_score >= 60:

                readiness = "🟢 Good"

            elif overall_score >= 40:

                readiness = "🟡 Needs Practice"

            else:

                readiness = "🔴 Needs Improvement"


            st.header(
                "🎯 Overall Performance"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "🏆 Overall Score",
                    f"{overall_score}/100"
                )

            with col2:
                st.metric(
                    "🎯 Readiness Score",
                    f"{readiness_score}/100"
                )

            with col3:
                st.metric(
                    "📝 Questions Completed",
                    f"{len(results)}/{len(questions)}"
                )

            with col4:
                st.metric(
                    "💼 Readiness Level",
                    readiness
                )

            st.progress(max(0, min(100, readiness_score)) / 100)
            if readiness_score >= 80:
                st.success("🟢 You are close to interview-ready. Focus on consistency and confidence.")
            elif readiness_score >= 60:
                st.info("🟡 You have a good foundation. Practice your weakest topics before the real interview.")
            else:
                st.warning("🟠 Keep practicing. IntervAIQ has identified areas that need more preparation.")


            st.divider()


            # =================================================
            # PERFORMANCE BREAKDOWN
            # =================================================

            st.header(
                "📊 Performance Breakdown"
            )

            technical = round(
                sum(
                    item["technical_accuracy"]
                    for item in results
                ) / len(results)
            )

            relevance = round(
                sum(
                    item["relevance"]
                    for item in results
                ) / len(results)
            )

            completeness = round(
                sum(
                    item["completeness"]
                    for item in results
                ) / len(results)
            )

            clarity = round(
                sum(
                    item["clarity"]
                    for item in results
                ) / len(results)
            )


            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "🧠 Technical Accuracy",
                    f"{technical}/100"
                )

            with col2:

                st.metric(
                    "🎯 Relevance",
                    f"{relevance}/100"
                )

            with col3:

                st.metric(
                    "📝 Completeness",
                    f"{completeness}/100"
                )

            with col4:

                st.metric(
                    "💬 Clarity",
                    f"{clarity}/100"
                )


            # =================================================
            # PROGRESS BARS
            # =================================================

            st.subheader(
                "📈 Skill Performance"
            )

            st.write(
                f"🧠 Technical Accuracy — {technical}%"
            )

            st.progress(
                technical / 100
            )

            st.write(
                f"🎯 Relevance — {relevance}%"
            )

            st.progress(
                relevance / 100
            )

            st.write(
                f"📝 Completeness — {completeness}%"
            )

            st.progress(
                completeness / 100
            )

            st.write(
                f"💬 Clarity — {clarity}%"
            )

            st.progress(
                clarity / 100
            )


            st.divider()


            # =================================================
            # QUESTION-WISE PERFORMANCE
            # =================================================

            st.header(
                "📋 Question-wise Performance"
            )

            for index, item in enumerate(
                results
            ):

                score = item["score"]

                if score >= 80:

                    icon = "🟢"

                elif score >= 60:

                    icon = "🟡"

                else:

                    icon = "🔴"


                with st.expander(
                    f"{icon} Question {index + 1} — "
                    f"{score}/100"
                ):

                    st.write(
                        f"**Question:** "
                        f"{item['question']}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{item['category']}"
                    )

                    st.write(
                        f"**Topic:** "
                        f"{item['topic']}"
                    )

                    st.write(
                        f"**Difficulty:** "
                        f"{item['difficulty']}"
                    )

                    st.write(
                        f"**Result:** "
                        f"{item['result']}"
                    )

                    st.progress(
                        score / 100
                    )


            st.divider()


            # =================================================
            # TOPIC PERFORMANCE
            # =================================================

            st.header(
                "🎯 Topic Performance"
            )

            topic_scores = {}

            for item in results:

                topic = item["topic"]

                if topic not in topic_scores:

                    topic_scores[topic] = []

                topic_scores[topic].append(
                    item["score"]
                )


            topic_average = {}

            for topic, scores in topic_scores.items():

                topic_average[topic] = round(
                    sum(scores) / len(scores)
                )


            sorted_topics = sorted(
                topic_average.items(),
                key=lambda x: x[1],
                reverse=True
            )


            col1, col2 = st.columns(2)


            # =================================================
            # STRONG AREAS
            # =================================================

            with col1:

                st.subheader(
                    "💪 Strong Areas"
                )

                for topic, score in sorted_topics[:3]:

                    st.success(
                        f"**{topic}** — {score}/100"
                    )


            # =================================================
            # WEAK AREAS
            # =================================================

            with col2:

                st.subheader(
                    "⚠️ Areas to Improve"
                )

                weakest_topics = sorted(
                    topic_average.items(),
                    key=lambda x: x[1]
                )

                for topic, score in weakest_topics[:3]:

                    st.warning(
                        f"**{topic}** — {score}/100"
                    )


            st.divider()

            # =================================================
            # PERSONALIZED IMPROVEMENT PLAN
            # =================================================

            st.header("📚 Personalized Improvement Plan")

            weak_topics = [
                topic for topic, score in weakest_topics[:3]
                if score < 75
            ]

            if weak_topics:
                st.write("Based on your interview performance, focus on:")
                for index, topic in enumerate(weak_topics, start=1):
                    st.write(f"**{index}. {topic}** — practice 3–5 questions and explain your reasoning aloud.")
            else:
                st.write("Your topic scores are balanced. Focus on timed practice and stronger examples.")

            if st.session_state.get("job_match_analysis"):
                priority_topics = st.session_state.job_match_analysis.get("priority_topics", [])
                missing_skills = st.session_state.job_match_analysis.get("missing_skills", [])
                if priority_topics:
                    st.info("🎯 **JD-based priority:** " + ", ".join(priority_topics[:5]))
                if missing_skills:
                    st.warning("📌 **Resume–JD skill gaps:** " + ", ".join(missing_skills[:5]))

            st.divider()


            # =================================================
            # AI ASSESSMENT
            # =================================================

            st.header(
                "🤖 IntervAIQ's Assessment"
            )

            if overall_score >= 80:

                st.success(
                    """
                    🎉 Excellent performance!

                    You demonstrated strong technical
                    understanding, relevance, clarity,
                    and interview skills.

                    You are showing strong interview readiness.
                    Keep practicing to maintain consistency.
                    """
                )

            elif overall_score >= 60:

                st.info(
                    """
                    👍 Good performance!

                    You have a solid foundation, but there
                    are still areas where you can improve.

                    Focus on structured answers, examples,
                    and explaining your reasoning clearly.
                    """
                )

            elif overall_score >= 40:

                st.warning(
                    """
                    💪 You're making progress!

                    Your answers show some understanding,
                    but you need more practice.

                    Review the model answers and retry
                    the weaker questions.
                    """
                )

            else:

                st.error(
                    """
                    📚 More practice is recommended.

                    Focus on understanding the fundamentals
                    and practice explaining your answers
                    clearly and confidently.
                    """ 
                )


            st.divider()


            # =================================================
            # NEXT ACTIONS
            # =================================================

            st.header(
                "🚀 What Would You Like To Do Next?"
            )

            col1, col2 = st.columns(2)


            with col1:

                if st.button(
                    "🔄 Practice Again",
                    type="primary",
                    use_container_width=True,
                    key="practice_again"
                ):

                    try:
                        st.session_state.current_interview_id = create_interview(
                            st.session_state.user_id,
                            st.session_state.selected_company,
                            st.session_state.selected_role
                        )
                    except Exception as e:
                        st.error(f"❌ Could not create new interview session: {e}")
                        st.stop()

                    # Start the retry with the original generated questions;
                    # adaptive follow-ups from the previous attempt are not copied.
                    st.session_state.interview_questions = [
                        q for q in st.session_state.interview_questions
                        if not q.get("is_followup", False)
                    ]

                    st.session_state.current_question = 0

                    st.session_state.answer_evaluation = None

                    st.session_state.current_hint = None

                    st.session_state.last_answer = ""

                    st.session_state.show_model_answer = False

                    st.session_state.interview_results = []

                    st.session_state.interview_started = True

                    st.rerun()


            with col2:

                if st.button(
                    "🏠 Back to Interview Setup",
                    use_container_width=True,
                    key="back_to_setup"
                ):

                    st.session_state.interview_started = False

                    st.session_state.current_question = 0

                    st.session_state.answer_evaluation = None

                    st.session_state.current_hint = None

                    st.session_state.last_answer = ""

                    st.session_state.show_model_answer = False

                    st.session_state.interview_results = []

                    st.rerun()


    # ========================================================
    # ACTIVE INTERVIEW QUESTION
    # ========================================================

    else:

        question_data = questions[current]

        st.divider()


        # ====================================================
        # PROGRESS
        # ====================================================

        st.subheader(
            f"🎯 Question {current + 1} "
            f"of {len(questions)}"
        )

        progress_value = (
            (current + 1) / len(questions)
        )

        st.progress(
            progress_value
        )


        # ====================================================
        # QUESTION CARD
        # ====================================================

        st.markdown(
            f"""
            <div class="question-card">

            <h2>
            🎤 Your Interview Question
            </h2>

            <p style="font-size: 22px;">

            {question_data.get(
                "question",
                "Question unavailable"
            )}

            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # QUESTION INFORMATION
        # ====================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.info(
                f"📂 Category\n\n"
                f"{question_data.get(
                    'category',
                    'General'
                )}"
            )

        with col2:

            st.info(
                f"📊 Difficulty\n\n"
                f"{question_data.get(
                    'difficulty',
                    'Medium'
                )}"
            )

        with col3:

            st.info(
                f"🎯 Topic\n\n"
                f"{question_data.get(
                    'topic',
                    'General'
                )}"
            )


        st.divider()


        # ====================================================
        # EXPLAINABLE AI - WHY THIS QUESTION?
        # ====================================================

        reason_col, _ = st.columns([1, 2])

        with reason_col:

            if st.button(
                "🔍 Why This Question?",
                key=f"why_question_{current}",
                use_container_width=True
            ):

                with st.spinner(
                    "🧠 IntervAIQ is explaining why this question was selected..."
                ):

                    question_reason = generate_question_reason(
                        question=question_data.get("question", ""),
                        resume_text=st.session_state.get("resume_text", ""),
                        company=st.session_state.get("selected_company", ""),
                        role=st.session_state.get("selected_role", ""),
                        mode=st.session_state.get("selected_mode", ""),
                        difficulty=question_data.get("difficulty", "Medium"),
                        category=question_data.get("category", "General"),
                        topic=question_data.get("topic", "General"),
                        job_description=st.session_state.get(
                            "job_description_text",
                            ""
                        )
                    )

                if isinstance(question_reason, dict) and "error" not in question_reason:
                    st.session_state.question_reason = question_reason
                    st.session_state.show_question_reason = True
                    st.rerun()
                else:
                    st.error(
                        "❌ Could not explain this question: "
                        + str(question_reason.get("error", "Unknown error"))
                    )


        if st.session_state.get("show_question_reason") and st.session_state.get("question_reason"):

            reason_data = st.session_state.question_reason

            st.markdown(
                "### 🧠 Why IntervAIQ Asked This Question"
            )

            if reason_data.get("reason"):
                st.info(
                    f"🎯 **Why this question is relevant:** "
                    f"{reason_data.get('reason')}"
                )

            col_a, col_b = st.columns(2)

            with col_a:

                st.markdown("**📄 Resume Evidence**")
                evidence = reason_data.get("resume_evidence", [])

                if evidence:
                    for item in evidence:
                        st.write(f"• {item}")
                else:
                    st.write("• No specific resume evidence was required for this question.")

            with col_b:

                st.markdown("**🧪 Skills / Concepts Being Tested**")
                skills_tested = reason_data.get("skills_tested", [])

                if skills_tested:
                    for item in skills_tested:
                        st.write(f"• {item}")
                else:
                    st.write("• General interview competency")

            context = reason_data.get("interview_context", [])

            if context:
                st.markdown("**🎯 Interview Context**")
                for item in context:
                    st.write(f"• {item}")

            if reason_data.get("learning_objective"):
                st.success(
                    f"📚 **What the interviewer wants to assess:** "
                    f"{reason_data.get('learning_objective')}"
                )

            st.caption(
                "💡 This explanation is generated from your resume and current "
                "interview settings. It does not claim to reveal a company's "
                "private interview process."
            )

        st.divider()


        # ====================================================
        # ANSWER SECTION
        # ====================================================

        if st.session_state.answer_evaluation is None:

            # =================================================
            # VOICE-TO-TEXT
            # =================================================

            with st.expander("🎙️ Voice-to-Text Answer (Optional)", expanded=False):

                st.caption(
                    "Record your answer using your microphone. "
                    "IntervAIQ will convert your speech into text, "
                    "which you can edit before submitting."
                )

                if hasattr(st, "audio_input"):

                    voice_audio = st.audio_input(
                        "🎙️ Record your interview answer",
                        key=f"voice_answer_{current}"
                    )

                    if st.button(
                        "🔄 Convert Voice to Text",
                        key=f"transcribe_{current}",
                        use_container_width=True
                    ):

                        if voice_audio is None:
                            st.warning(
                                "⚠️ Please record an answer first."
                            )
                        else:
                            with st.spinner(
                                "🎧 Converting your voice to text..."
                            ):
                                transcript = transcribe_voice_to_text(
                                    voice_audio
                                )

                            if transcript.startswith("__VOICE_ERROR__:"):
                                st.error(
                                    "❌ Voice transcription failed: "
                                    + transcript.replace(
                                        "__VOICE_ERROR__:", "", 1
                                    )
                                )
                            elif transcript:
                                st.session_state[f"answer_{current}"] = transcript
                                st.success(
                                    "✅ Voice converted to text! "
                                    "You can edit the answer below."
                                )
                                st.rerun()
                            else:
                                st.warning(
                                    "⚠️ No speech was detected. "
                                    "Please record your answer again."
                                )

                else:
                    st.error(
                        "🎙️ Voice recording is not available in your current "
                        "Streamlit version. Please update Streamlit with "
                        "`pip install --upgrade streamlit`."
                    )

            answer = st.text_area(
                "✍️ Your Answer",

                height=220,

                placeholder=(
                    "Type your answer or use Voice-to-Text above...\n\n"
                    "Answer as if you are speaking to a real interviewer."
                ),

                key=f"answer_{current}"
            )


            col1, col2 = st.columns(2)


            # =================================================
            # HINT
            # =================================================

            with col1:

                if st.button(
                    "💡 Get AI Hint",
                    key=f"hint_{current}",
                    use_container_width=True
                ):

                    with st.spinner(
                        "🤖 Thinking of a helpful hint..."
                    ):

                        hint = generate_hint(
                            question_data.get(
                                "question",
                                ""
                            ),

                            question_data.get(
                                "category",
                                "General"
                            ),

                            question_data.get(
                                "topic",
                                "General"
                            )
                        )

                    st.session_state.current_hint = hint

                    st.rerun()


            # DISPLAY HINT

            if st.session_state.current_hint:

                st.info(
                    f"💡 **AI Hint:** "
                    f"{st.session_state.current_hint}"
                )


            # =================================================
            # SUBMIT
            # =================================================

            with col2:

                if st.button(
                    "📤 Submit Answer",
                    type="primary",
                    key=f"submit_{current}",
                    use_container_width=True
                ):

                    if not answer.strip():

                        st.warning(
                            "⚠️ Please enter an answer first."
                        )

                    else:

                        with st.spinner(
                            "🤖 IntervAIQ is evaluating your answer..."
                        ):

                            evaluation = evaluate_answer(
                                question=question_data.get(
                                    "question",
                                    ""
                                ),

                                answer=answer,

                                category=question_data.get(
                                    "category",
                                    "General"
                                ),

                                topic=question_data.get(
                                    "topic",
                                    "General"
                                )
                            )


                        if "error" in evaluation:

                            st.error(
                                f"❌ Evaluation failed: "
                                f"{evaluation['error']}"
                            )

                        else:

                            st.session_state.answer_evaluation = evaluation

                            st.session_state.last_answer = answer

                            st.session_state.current_hint = None

                            st.session_state.show_model_answer = False

                            st.rerun()


        # ====================================================
        # EVALUATION SECTION
        # ====================================================

        else:

            evaluation = (
                st.session_state.answer_evaluation
            )


            # =================================================
            # RESULT
            # =================================================

            result = evaluation.get(
                "result",
                "Partially Correct"
            )

            score = evaluation.get(
                "score",
                0
            )


            if result == "Correct":

                st.success(
                    f"🟢 **Correct! — {score}/100**"
                )

            elif result == "Partially Correct":

                st.warning(
                    f"🟡 **Partially Correct — {score}/100**"
                )

            else:

                st.error(
                    f"🔴 **Incorrect — {score}/100**"
                )


            # =================================================
            # SCORE BREAKDOWN
            # =================================================

            st.header(
                "📊 Your Performance"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "🧠 Technical Accuracy",
                    f"{evaluation.get(
                        'technical_accuracy',
                        0
                    )}/100"
                )

            with col2:

                st.metric(
                    "🎯 Relevance",
                    f"{evaluation.get(
                        'relevance',
                        0
                    )}/100"
                )

            with col3:

                st.metric(
                    "📝 Completeness",
                    f"{evaluation.get(
                        'completeness',
                        0
                    )}/100"
                )

            with col4:

                st.metric(
                    "💬 Clarity",
                    f"{evaluation.get(
                        'clarity',
                        0
                    )}/100"
                )


            st.divider()


            # =================================================
            # WHAT WENT WELL
            # =================================================

            with st.expander(
                "✅ What You Did Well",
                expanded=True
            ):

                what_went_well = evaluation.get(
                    "what_went_well",
                    []
                )

                if what_went_well:

                    for item in what_went_well:

                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        "Your answer addressed the question."
                    )


            # =================================================
            # WHAT TO IMPROVE
            # =================================================

            with st.expander(
                "⚠️ What You Need To Improve",
                expanded=True
            ):

                what_went_wrong = evaluation.get(
                    "what_went_wrong",
                    []
                )

                if what_went_wrong:

                    for item in what_went_wrong:

                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        "Keep improving the depth and clarity "
                        "of your answer."
                    )


            # =================================================
            # EXPLANATION
            # =================================================

            with st.expander(
                "📚 Why Did You Get This Score?",
                expanded=True
            ):

                st.write(
                    evaluation.get(
                        "explanation",
                        "No explanation available."
                    )
                )


            # =================================================
            # MODEL ANSWER
            # =================================================

            st.divider()

            st.subheader(
                "📖 Learn From This Question"
            )

            if st.button(
                "📖 Show Model Answer",
                key=f"model_{current}"
            ):

                st.session_state.show_model_answer = True

                st.rerun()


            if st.session_state.show_model_answer:

                st.success(
                    "💡 Recommended Interview Answer"
                )

                st.write(
                    evaluation.get(
                        "model_answer",
                        "Model answer is not available."
                    )
                )

                st.info(
                    "🎯 Don't memorize the model answer. "
                    "Use it to understand how a strong interview "
                    "answer should be structured."
                )


            # =================================================
            # IMPROVEMENT TIP
            # =================================================

            st.subheader(
                "🚀 Improvement Tip"
            )

            st.warning(
                evaluation.get(
                    "improvement_tip",
                    "Try to provide a more structured and specific answer."
                )
            )


            st.divider()

            # =================================================
            # ADAPTIVE FOLLOW-UP
            # =================================================

            if not question_data.get("is_followup", False):
                st.subheader("🧠 Adaptive Interviewer")
                st.caption(
                    "IntervAIQ can ask a deeper follow-up based on your actual answer, "
                    "just like a real interviewer."
                )

                if st.button(
                    "🧠 Ask Me a Follow-up Question",
                    key=f"adaptive_{current}",
                    use_container_width=True
                ):
                    with st.spinner("🤖 Analyzing your answer and creating a follow-up..."):
                        followup = generate_adaptive_followup(
                            question_data.get("question", ""),
                            st.session_state.get("last_answer", ""),
                            evaluation,
                            st.session_state.get("selected_role", "Software Engineer"),
                            question_data.get("category", "General"),
                            question_data.get("topic", "General")
                        )

                    if isinstance(followup, dict) and "error" not in followup and followup.get("question"):
                        save_current_result(
                            question_data,
                            evaluation,
                            st.session_state.get("last_answer", "")
                        )

                        # Insert the adaptive question immediately after the current question.
                        st.session_state.interview_questions.insert(
                            current + 1,
                            followup
                        )

                        st.session_state.current_question += 1
                        st.session_state.answer_evaluation = None
                        st.session_state.current_hint = None
                        st.session_state.last_answer = ""
                        st.session_state.show_model_answer = False
                        st.session_state.question_reason = None
                        st.session_state.show_question_reason = False

                        st.success("🧠 Follow-up generated! The next question is based on your previous answer.")
                        st.rerun()
                    else:
                        st.error(
                            "❌ Could not generate a follow-up question: "
                            + str(followup.get("error", "Unknown error"))
                        )


            st.divider()


            # =================================================
            # RETRY / NEXT
            # =================================================

            col1, col2 = st.columns(2)


            # =================================================
            # RETRY
            # =================================================

            with col1:

                if st.button(
                    "🔄 Try Again",
                    key=f"retry_{current}",
                    use_container_width=True
                ):

                    st.session_state.answer_evaluation = None

                    st.session_state.current_hint = None

                    st.session_state.last_answer = ""

                    st.session_state.show_model_answer = False
                    st.session_state.question_reason = None
                    st.session_state.show_question_reason = False

                    answer_key = f"answer_{current}"

                    if answer_key in st.session_state:

                        del st.session_state[
                            answer_key
                        ]

                    st.rerun()


            # =================================================
            # NEXT QUESTION
            # =================================================

            with col2:

                if current + 1 < len(questions):

                    if st.button(
                        "➡️ Next Question",
                        type="primary",
                        key=f"next_{current}",
                        use_container_width=True
                    ):

                        # Save current result

                        save_current_result(
                            question_data,
                            evaluation,
                            st.session_state.get("last_answer", "")
                        )

                        # Move forward

                        st.session_state.current_question += 1

                        # Reset evaluation

                        st.session_state.answer_evaluation = None

                        st.session_state.current_hint = None

                        st.session_state.last_answer = ""

                        st.session_state.show_model_answer = False
                        st.session_state.question_reason = None
                        st.session_state.show_question_reason = False

                        st.rerun()


                else:

                    if st.button(
                        "🏆 Finish Interview",
                        type="primary",
                        key="finish_interview",
                        use_container_width=True
                    ):

                        # Save final result

                        save_current_result(
                            question_data,
                            evaluation,
                            st.session_state.get("last_answer", "")
                        )

                        # Persist the final overall score only for this user's interview.
                        current_results = st.session_state.interview_results
                        if current_results and st.session_state.get("current_interview_id"):
                            overall_score = round(
                                sum(item.get("score", 0) for item in current_results)
                                / len(current_results)
                            )
                            try:
                                update_interview_score(
                                    st.session_state.current_interview_id,
                                    st.session_state.user_id,
                                    overall_score
                                )
                            except Exception as e:
                                st.warning(
                                    f"⚠️ Interview completed, but final score could not be saved: {e}"
                                )

                        # Move to dashboard

                        st.session_state.current_question = len(
                            questions
                        )

                        st.session_state.answer_evaluation = None

                        st.session_state.current_hint = None

                        st.session_state.show_model_answer = False
                        st.session_state.question_reason = None
                        st.session_state.show_question_reason = False

                        st.rerun()
# ============================================================
# 📚 SAVED INTERVIEW HISTORY - CURRENT USER ONLY
# ============================================================

st.divider()
st.header("📚 My Interview History")

try:
    user_interviews = get_user_interviews(st.session_state.user_id)
except Exception as e:
    user_interviews = []
    st.warning(f"⚠️ Could not load interview history: {e}")

if not user_interviews:
    st.info("No completed interviews saved for this account yet.")
else:
    for history_item in user_interviews:
        created = history_item.get("created_at", "")
        score = history_item.get("overall_score", 0) or 0
        title = (
            f"{history_item.get('company', 'Company')} — "
            f"{history_item.get('role', 'Role')} — {round(score)}/100"
        )

        with st.expander(f"📝 {title}"):
            st.caption(f"Date: {created}")
            try:
                saved_results = get_interview_results(
                    history_item["id"],
                    st.session_state.user_id
                )
            except Exception:
                saved_results = []

            if not saved_results:
                st.write("No question-level results saved for this interview.")
            else:
                for index, saved in enumerate(saved_results, start=1):
                    st.write(
                        f"**Q{index}. {saved.get('question', '')}** — "
                        f"{saved.get('score', 0)}/100 — {saved.get('result', '')}"
                    )


# ============================================================
# 🤖 AI INTERVIEW COACH - CHAT MODE
# ============================================================

st.divider()

st.header("🤖 AI Interview Coach")

# ------------------------------------------------------------
# CANDIDATE NAME
# ------------------------------------------------------------

candidate_name = st.session_state.get(
    "candidate_name"
) or st.session_state.get(
    "user_name",
    "Candidate"
)

st.caption(
    f"Your personal interview coach, {candidate_name}."
)

# ------------------------------------------------------------
# CHAT HISTORY
# ------------------------------------------------------------

if "coach_messages" not in st.session_state:

    st.session_state.coach_messages = [
        {
            "role": "assistant",
            "content": (
                f"Hi {candidate_name}! 👋\n\n"
                "I've reviewed your interview performance. "
                "Ask me anything about your scores, mistakes, "
                "strong areas, or how to improve."
            )
        }
    ]

# ------------------------------------------------------------
# DISPLAY PREVIOUS CHAT
# ------------------------------------------------------------

for message in st.session_state.coach_messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ------------------------------------------------------------
# GET INTERVIEW RESULTS
# ------------------------------------------------------------

interview_results = st.session_state.get(
    "interview_results",
    []
)

# The coach can use current interview results, or this user's saved history.
if not interview_results:
    try:
        saved_history = get_user_interview_history(
            st.session_state.user_id
        )
        interview_results = [
            item for item in saved_history
            if item.get("question")
        ][-20:]
    except Exception:
        interview_results = []

interview_context = ""

for i, result in enumerate(interview_results):

    interview_context += f"""
Question {i + 1}: {result.get('question', '')}

Category: {result.get('category', '')}

Topic: {result.get('topic', '')}

Score: {result.get('score', 0)}/100

Result: {result.get('result', '')}

Candidate Answer:
{result.get('answer', '')}

Technical Accuracy:
{result.get('technical_accuracy', 0)}/100

Relevance:
{result.get('relevance', 0)}/100

Completeness:
{result.get('completeness', 0)}/100

Clarity:
{result.get('clarity', 0)}/100

What Went Well:
{result.get('what_went_well', [])}

What Needs Improvement:
{result.get('what_went_wrong', [])}

Improvement Tip:
{result.get('improvement_tip', '')}

-------------------------
"""

# ------------------------------------------------------------
# CHAT INPUT
# ------------------------------------------------------------

user_message = st.chat_input(
    "💬 Ask your AI Coach..."
)

# ------------------------------------------------------------
# WHEN USER SENDS MESSAGE
# ------------------------------------------------------------

if user_message:

    # Add user message to chat history
    st.session_state.coach_messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # Display user message immediately
    with st.chat_message("user"):

        st.markdown(user_message)

    # --------------------------------------------------------
    # CREATE CHAT HISTORY FOR AI
    # --------------------------------------------------------

    chat_history = []

    for message in st.session_state.coach_messages:

        chat_history.append(
            {
                "role": message["role"],
                "content": message["content"]
            }
        )

    # --------------------------------------------------------
    # AI COACH PROMPT
    # --------------------------------------------------------

    coach_system_prompt = f"""
You are IntervAIQ, a professional AI interview coach.

Candidate:
{candidate_name}

The candidate has completed an interview.

Here is their interview performance:

{interview_context}

Your job is to help the candidate improve.

IMPORTANT RULES:

1. Keep responses SHORT and easy to read.
2. Maximum 120 words unless the candidate specifically
   asks for a detailed explanation.
3. Do not create large tables.
4. Give practical interview advice.
5. Use the candidate's actual interview scores when relevant.
6. Do not invent candidate information.
7. If the candidate asks about a mistake, explain it simply.
8. If the candidate asks for a better answer, give a
   concise interview-ready answer.
9. If the candidate asks what to practice, recommend
   specific topics based on their performance.
10. Remember the previous messages in the conversation.
11. Continue the conversation naturally.
12. Do not repeatedly introduce yourself.

Be encouraging but honest.
"""

    try:

        with st.chat_message("assistant"):

            with st.spinner("🤖 Thinking..."):

                response = client.chat.completions.create(

                    model="openai/gpt-oss-120b",

                    messages=[
                        {
                            "role": "system",
                            "content": coach_system_prompt
                        },
                        *chat_history
                    ],

                    temperature=0.4
                )

                ai_response = (
                    response
                    .choices[0]
                    .message
                    .content
                )

            st.markdown(ai_response)

        # Save AI response
        st.session_state.coach_messages.append(
            {
                "role": "assistant",
                "content": ai_response
            }
        )

    except Exception as e:

        st.error(
            f"❌ AI Coach error: {str(e)}"
        )