import secrets
import uuid

from flask import Flask, session, request, jsonify
from pydantic import ValidationError
from openai import OpenAI

from prompt import SYSTEM_PROMPT, KNOWLEDGE_BASE, make_learning_preference, make_user_input
from model import UserData, Plan, QuizResult

app = Flask(__name__)
app.secret_key = secrets.token_bytes()

DEBUG = True

@app.route("/me", methods=["GET", "POST"])
def me():
    if request.method == "GET":
        if "userdata" in session:
            return session["userdata"]
        else:
            return "No user data submitted"
    elif request.method == "POST":
        if "uuid" not in session:
            session["uuid"] = uuid.uuid4()

        try:
            data = request.get_json()
            validated = UserData(**data)
            session["userdata"] = validated.model_dump_json()
            return session["userdata"]
        except ValidationError as e:
            return jsonify(e.errors(), 400)
    else:
        return ""


@app.route("/quiz", methods=["POST"])
def quiz():
    if "uuid" not in session:
        session["uuid"] = uuid.uuid4()

    try:
        data = request.get_json()
        validated = QuizResult(**data)
        session["quiz_result"] = validated.model_dump_json()
        return session["quiz_result"]
    except ValidationError as e:
        return jsonify(e.errors(), 400)


@app.route("/ping")
def ping():
    return "pong"


@app.route("/plan")
def plan():
    if "userdata" not in session:
        return "You must provide user data for planning"

    userdata = UserData.model_validate_json(session["userdata"])

    if "quiz_result" in session:
        validated = QuizResult.model_validate_json(session["quiz_result"])
        answers = validated.answers
    else:
        answers = []

    if DEBUG:
        return """{
    "plan": [
        {
            "id": 1,
            "emoji": "📗",
            "topic": "이차방정식 복습: 핵심 개념 정리(p74-79)",
            "schedule": {
                "start": "15:30:00-05:00",
                "duration_minute": 40
            }
        },
        {
            "id": 2,
            "emoji": "📝",
            "topic": "문제 세트 08: 이차방정식 풀이① - 내신 대비 문제(p120-124)",
            "schedule": {
                "start": "16:20:00-05:00",
                "duration_minute": 37
            }
        },
        {
            "id": 3,
            "emoji": "💪",
            "topic": "문제 세트 09: 이차방정식 풀이② - 자신감 향상(p132-135)",
            "schedule": {
                "start": "18:00:00-05:00",
                "duration_minute": 30
            }
        }
    ]
}"""

    client = OpenAI()

    response = client.responses.parse(
        model="o4-mini-2025-04-16",
        text_format=Plan,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": KNOWLEDGE_BASE,
            },
            {
                "role": "user",
                "content": make_user_input(userdata),
            },
            {
                "role": "user",
                "content": make_learning_preference(answers)
            },
        ]
    )

    if not response.output_parsed:
        return '''{"plan": []}'''

    return response.output_parsed.model_dump_json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
