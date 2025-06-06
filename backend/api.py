import uuid

from typing import cast
from datetime import timedelta, datetime
from flask import session, request, jsonify, current_app, Blueprint
from pydantic import ValidationError
from openai import OpenAI

from prompt import *
from model import DailyFeedback, UserData, Plan, QuizResult, TaskResult
from core import DoziFlask

DEBUG = False

bp = Blueprint("main", __name__)

@bp.route("/me", methods=["GET", "POST"])
def me():
    user_id = get_uuid()

    if request.method == "GET":
        userdata = get_db(user_id, "userdata")

        if userdata:
            return userdata.model_dump_json()
        else:
            return "No user data: please submit"

    elif request.method == "POST":
        try:
            data = request.get_json()
            userdata = UserData(**data)
            put_db(user_id, "userdata", userdata)

            return userdata.model_dump_json()
        except ValidationError as e:
            return jsonify(e.errors(), 400)
    else:
        return ""


@bp.route("/me/quiz", methods=["GET", "POST"])
def quiz():
    user_id = get_uuid()

    if request.method == "GET":
        quiz_result = get_db(user_id, "quiz_result", QuizResult(answers=[]))

        return quiz_result.model_dump_json()

    elif request.method == "POST":
        try:
            data = request.get_json()
            quiz_result = QuizResult(**data)
            put_db(user_id, "quiz_result", quiz_result)

            return quiz_result.model_dump_json()
        except ValidationError as e:
            return jsonify(e.errors(), 400)

    return ""


@bp.route("/ping")
def ping():
    return "pong"


@bp.route("/plan")
def plan():
    user_id = get_uuid()

    userdata = get_db(user_id, "userdata")

    if not userdata:
        return "You must provide user data for planning"

    quiz_result = get_db(user_id, "quiz_result", QuizResult(answers=[]))

    recent_results: list[TaskResult] = get_db(user_id, "recent_results", [])
    now = datetime.now()
    recent_results = list(
        filter(
            lambda task: now < task.timestamp + timedelta(days=7),
            recent_results,
        )
    )
    put_db(user_id, "recent_results", recent_results)

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
                "content": PLAN_SYSTEM_PROMPT,
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
                "content": make_planning_considerations(quiz_result.answers, recent_results),
            },
            {
                "role": "user",
                "content": ADDITIONAL_INSTRUCTIONS,
            }
        ]
    )

    if not response.output_parsed:
        return '''{"plan": []}'''

    return response.output_parsed.model_dump_json()

@bp.route("/tasks/complete", methods=["GET", "POST"])
def complete_task():
    user_id = get_uuid()

    if request.method == "GET":
        recent_results: list[TaskResult] = get_db(user_id, "recent_results", [])
        now = datetime.now()
        recent_results = list(
            filter(
                lambda task: now < task.timestamp + timedelta(days=7),
                recent_results,
            )
        )
        put_db(user_id, "recent_results", recent_results)

        return f'{{"recent_results": [{",".join(result.model_dump_json() for result in recent_results)}]}}'
    elif request.method == "POST":
        try:
            data = request.get_json()
            task_result = TaskResult(**data)

            recent_results: list[TaskResult] = get_db(user_id, "recent_results", [])
            recent_results.append(task_result)
            put_db(user_id, "recent_results", recent_results)

            return task_result.model_dump_json()
        except ValidationError as e:
            return jsonify(e.errors(), 400)

    return ""

@bp.route("/feedback/daily")
def daily_feedback():
    user_id = get_uuid()

    quiz_result = get_db(user_id, "quiz_result", QuizResult(answers=[]))
    answers = quiz_result.answers

    recent_results: list[TaskResult] = get_db(user_id, "recent_results", [])

    now = datetime.now()
    today_results = list(filter(
        lambda result: now < result.timestamp + timedelta(days=1),
        recent_results,
    ))

    if not (answers and recent_results):
        return ""

    client = OpenAI()

    response = client.responses.parse(
        model="o4-mini-2025-04-16",
        text_format=DailyFeedback,
        input=[
            {
                "role": "system",
                "content": FEEDBACK_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": make_learning_preference(answers)
            },
            {
                "role": "user",
                "content": make_recent_results(today_results),
            },
        ]
    )

    if not response.output_parsed:
        return '''{"analysis": "", "suggestion": "", "encouragement": ""}'''

    return response.output_parsed.model_dump_json()


def get_uuid():
    if "uuid" not in session:
        session["uuid"] = uuid.uuid4()

    return session["uuid"]


def get_db(user_id, key, default=None):
    value = cast(DoziFlask, current_app).db.get(user_id, key, default)
    return value

def put_db(user_id, key, value):
    cast(DoziFlask, current_app).db.put(user_id, key, value)
