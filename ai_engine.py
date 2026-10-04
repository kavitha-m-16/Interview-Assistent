import os
import json
from dotenv import load_dotenv
from groq import Groq


# -----------------------------------------
# Load environment variables
# -----------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Please add it to your .env file."
    )


# -----------------------------------------
# Create Groq Client
# -----------------------------------------

client = Groq(
    api_key=GROQ_API_KEY
)


# -----------------------------------------
# Analyze Resume
# -----------------------------------------

def analyze_resume(resume_text: str):

    prompt = f"""
You are IntervAIQ, an AI-powered interview preparation coach.

Analyze the following candidate resume and create a structured
candidate profile.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "name": "",
    "professional_summary": "",
    "education": [],
    "technical_skills": [],
    "projects": [],
    "certifications": [],
    "experience": [],
    "strengths": [],
    "areas_to_improve": []
}}

IMPORTANT RULES:

1. Extract information only from the resume.
2. Do not invent qualifications, companies, projects, or skills.
3. If information is not available, return an empty list.
4. Identify technical skills clearly.
5. Identify projects clearly.
6. Identify certifications if present.
7. Identify internships or professional experience if present.
8. Suggest reasonable areas to improve based on the candidate's
   profile.
9. Keep the professional summary concise.

RESUME:

{resume_text}
"""

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI interview preparation "
                        "assistant. Always return valid JSON."
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

        profile = json.loads(result)

        return profile

    except Exception as e:

        raise Exception(
            f"Groq resume analysis failed: {str(e)}"
        )
# --------------------------------
# Generate Interview Questions
# --------------------------------

def generate_interview_questions(resume_text, company, role, mode, num_questions=5):

    prompt = f"""
You are IntervAIQ, an AI-powered interview preparation coach.

Generate {num_questions} interview questions for the candidate.

Candidate Resume:
{resume_text}

Target Company:
{company}

Target Role:
{role}

Interview Mode:
{mode}

Create a balanced interview consisting of:
- HR questions
- Technical questions
- Role-specific questions
- Behavioral questions
- Coding questions when relevant to the role

IMPORTANT RULES:

1. Questions must be relevant to the selected role.
2. Use the candidate's resume to personalize questions.
3. Do not invent anything that is not present in the resume.
4. Questions should have different difficulty levels.
5. If the role is technical, include technical questions.
6. Include coding questions for software/technical roles.
7. In Learning Mode, questions should help the candidate learn.
8. Return ONLY valid JSON.
9. Do not add markdown or explanations outside the JSON.

Return the following structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "category": "Technical",
            "difficulty": "Medium",
            "topic": "Python"
        }}
    ]
}}
"""

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI interview coach."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        result = response.choices[0].message.content

        return result

    except Exception as e:

        return {
            "error": str(e)
        }
# --------------------------------
# Evaluate Interview Answer
# --------------------------------

def evaluate_answer(question, answer, category, topic):

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
"""

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional technical "
                        "interview evaluator. Always return valid JSON."
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

def get_hint(question, category, topic):
    prompt = f"""
You are IntervAIQ, an AI interview coach.

Give the candidate a helpful hint for answering the following interview question.

Question:
{question}

Category:
{category}

Topic:
{topic}

Rules:
1. Do NOT give the complete answer.
2. Give only a useful hint.
3. Help the candidate understand what points they should include.
4. Keep it concise.
5. Do not reveal the final answer.

Return only the hint.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return {
            "error": str(e)
        }