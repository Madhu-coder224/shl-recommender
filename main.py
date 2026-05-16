import os
import json
import logging
from typing import Literal

import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SHL Assessment Recommender", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY must be set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

SYSTEM_PROMPT = """You are an expert SHL assessment consultant chatbot. Your role is to help HR professionals and hiring managers identify the most appropriate SHL assessments for their job roles and hiring needs.

SHL Assessment Catalog (name | url | best for):
- Verify G+ | https://www.shl.com/solutions/products/assessments/cognitive-assessments/verify-g-plus/ | General ability: numerical, verbal, and inductive reasoning. Professional and managerial roles.
- Verify Numerical Reasoning | https://www.shl.com/solutions/products/assessments/cognitive-assessments/verify-numerical-reasoning/ | Interpreting numerical data and making decisions. Finance, data, and analyst roles.
- Verify Verbal Reasoning | https://www.shl.com/solutions/products/assessments/cognitive-assessments/verify-verbal-reasoning/ | Understanding written information and drawing conclusions. Roles requiring strong communication.
- Verify Inductive Reasoning | https://www.shl.com/solutions/products/assessments/cognitive-assessments/verify-inductive-reasoning/ | Logical thinking and pattern recognition. Technical, engineering, and analytical roles.
- Verify Deductive Reasoning | https://www.shl.com/solutions/products/assessments/cognitive-assessments/verify-deductive-reasoning/ | Applying rules and drawing logical conclusions. Legal, compliance, and policy roles.
- Occupational Personality Questionnaire (OPQ32) | https://www.shl.com/solutions/products/assessments/personality-assessments/opq32/ | 32 dimensions of work style and personality. Leadership, management, and graduate hiring.
- Motivation Questionnaire (MQ) | https://www.shl.com/solutions/products/assessments/personality-assessments/motivation-questionnaire-mq/ | What energizes and motivates individuals at work. Senior roles, culture fit, retention risk.
- Customer Contact Styles Questionnaire (CCSQ) | https://www.shl.com/solutions/products/assessments/personality-assessments/customer-contact-styles-questionnaire/ | Customer service behavioral styles. Customer-facing roles, contact center hiring.
- Situational Judgement Test (SJT) | https://www.shl.com/solutions/products/assessments/situational-judgment-tests/ | Realistic work scenarios to assess judgment. Specific job families, graduate programs.
- Work Safety Questionnaire (WSQ) | https://www.shl.com/solutions/products/assessments/personality-assessments/work-safety-questionnaire/ | Safety awareness and risk behaviors. Operational, manufacturing, and field roles.
- Graduate and Managerial Assessment (GMA) | https://www.shl.com/solutions/products/assessments/cognitive-assessments/graduate-and-managerial-assessment/ | Advanced reasoning battery. Graduate schemes and leadership pipelines.
- Dependability and Safety Instrument (DSI) | https://www.shl.com/solutions/products/assessments/personality-assessments/dependability-and-safety-instrument/ | Reliability, integrity, and safety orientation. Frontline, logistics, and operational roles.
- Technology Professional Assessment | https://www.shl.com/solutions/products/assessments/technology-solutions/ | Technical aptitude and problem solving. Software engineers and IT professionals.
- Sales Solution Assessment | https://www.shl.com/solutions/products/assessments/sales-solutions/ | Commercial acumen, persuasion, and customer orientation. B2B and B2C sales roles.

Instructions:
1. Ask clarifying questions about the job role, level (entry/mid/senior/executive), volume of hiring, and key competencies required if not provided.
2. Recommend the most relevant SHL assessments with clear justifications.
3. Limit recommendations to 1-5 assessments unless the user asks for more.
4. Keep the conversation focused and professional.
5. Indicate end_of_conversation as true only when the user has received their recommendations and signals they are done (e.g., says "thanks", "that's all", "perfect", "goodbye").

IMPORTANT: You MUST respond ONLY with a valid JSON object in this exact format. Do not include any text outside the JSON:
{
  "reply": "Your conversational response here",
  "recommendations": [
    {
      "name": "Assessment Name",
      "description": "Why this assessment fits the role",
      "url": "https://www.shl.com/..."
    }
  ],
  "end_of_conversation": false
}

The "recommendations" list should be empty [] if you are still gathering information. Always include the exact URL from the catalog above for each recommended assessment."""

SYSTEM_ACK = json.dumps({
    "reply": "I understand. I am an expert SHL assessment consultant ready to help you identify the right assessments for your hiring needs.",
    "recommendations": [],
    "end_of_conversation": False
})


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class Recommendation(BaseModel):
    name: str
    description: str
    url: str


class ChatResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation]
    end_of_conversation: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages list cannot be empty")

    contents = [
        {"role": "user", "parts": [{"text": f"[SYSTEM INSTRUCTIONS]\n{SYSTEM_PROMPT}\n\nAcknowledge you understand and are ready to help."}]},
        {"role": "model", "parts": [{"text": SYSTEM_ACK}]},
    ]

    for msg in request.messages:
        role = "model" if msg.role == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg.content}]})

    try:
        response = model.generate_content(
            contents,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=2048,
            ),
        )
        raw_text = response.text or ""
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[-1]
        raw_text = raw_text.rsplit("```", 1)[0].strip()

    try:
        data = json.loads(raw_text)
        return ChatResponse(
            reply=data.get("reply", ""),
            recommendations=[
                Recommendation(
                    name=r["name"],
                    description=r["description"],
                    url=r.get("url", "https://www.shl.com/solutions/products/product-catalog/"),
                )
                for r in data.get("recommendations", [])
                if isinstance(r, dict) and "name" in r and "description" in r
            ],
            end_of_conversation=bool(data.get("end_of_conversation", False)),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning(f"Failed to parse structured response: {e}\nRaw: {raw_text}")
        return ChatResponse(
            reply=raw_text,
            recommendations=[],
            end_of_conversation=False,
        )
