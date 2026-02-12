import json
import os
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Daily Self-Reflection Q&A for Parents")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "questions.json"

# Vercel serverless has a read-only filesystem except /tmp
_is_vercel = bool(os.environ.get("VERCEL"))
ANSWERS_FILE = Path("/tmp/answers.json") if _is_vercel else BASE_DIR / "answers.json"


def load_questions() -> list[dict]:
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_answers() -> list[dict]:
    if not ANSWERS_FILE.exists():
        return []
    with open(ANSWERS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_answers(answers: list[dict]):
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=2)


def get_today_question() -> dict:
    """Pick a question based on the day of the year so it rotates daily."""
    questions = load_questions()
    day_index = date.today().timetuple().tm_yday % len(questions)
    return questions[day_index]


class AnswerRequest(BaseModel):
    question_id: int
    question_text: str
    answer: str


@app.get("/api/today")
def today_question(offset: int = 0):
    """Return today's reflection question, with optional offset for follow-up questions."""
    questions = load_questions()
    day_index = date.today().timetuple().tm_yday % len(questions)
    q = questions[(day_index + offset) % len(questions)]
    today_str = date.today().isoformat()
    answers = load_answers()
    existing = next(
        (a for a in answers if a["date"] == today_str and a["question_id"] == q["id"]),
        None,
    )
    return {
        "date": today_str,
        "question": q,
        "existing_answer": existing,
        "offset": offset,
    }


@app.post("/api/answer")
def submit_answer(req: AnswerRequest):
    """Save or update today's answer."""
    if not req.answer.strip():
        raise HTTPException(status_code=400, detail="답변을 입력해주세요.")

    today_str = date.today().isoformat()
    answers = load_answers()

    existing = next(
        (
            a
            for a in answers
            if a["date"] == today_str and a["question_id"] == req.question_id
        ),
        None,
    )

    if existing:
        existing["answer"] = req.answer.strip()
        existing["updated_at"] = datetime.now().isoformat()
    else:
        answers.append(
            {
                "date": today_str,
                "question_id": req.question_id,
                "question_text": req.question_text,
                "answer": req.answer.strip(),
                "created_at": datetime.now().isoformat(),
            }
        )

    save_answers(answers)
    return {"status": "ok", "message": "저장되었습니다."}


@app.get("/api/history")
def get_history(limit: int = 30):
    """Return past answers, newest first."""
    answers = load_answers()
    answers.sort(key=lambda a: a["date"], reverse=True)
    return answers[:limit]


@app.get("/", response_class=HTMLResponse)
def index():
    html_path = BASE_DIR / "static" / "index.html"
    return html_path.read_text(encoding="utf-8")
