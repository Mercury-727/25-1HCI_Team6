import uuid

from typing import cast
from datetime import timedelta, datetime
from flask import session, request, jsonify, current_app, Blueprint
from pydantic import ValidationError
from openai import OpenAI

from prompt import *
from model import DailyFeedback, UserData, Plan, QuizResult, TaskResult, BookInformation
from core import DoziFlask

DEBUG = False

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/me", methods=["GET", "POST"])
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

            put_db(user_id, "books", BookInformation(textbook="지학사", workbook="쎈"))

            return userdata.model_dump_json()
        except ValidationError as e:
            return jsonify(e.errors(), 400)
    else:
        return ""


@api_bp.route("/me/quiz", methods=["GET", "POST"])
def quiz():
    user_id = get_uuid()

    if request.method == "GET":
        quiz_result = get_db(user_id, "quiz_result", QuizResult(forced=[], likert=[]))

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

@api_bp.route("/me/books", methods=["GET", "POST"])
def books():
    user_id = get_uuid()

    if request.method == "GET":
        book_info = get_db(user_id, "books")

        if not book_info:
            return "No book information: please submit"

        return f'''{{"textbook": "${book_info.textbook}", "workbook": "${book_info.workbook}"}}'''
    elif request.method == "POST":
        try:
            data = request.get_json()
            new_book_info = BookInformation(**data)
            book_info: BookInformation = get_db(user_id, "books", BookInformation(textbook="", workbook=""))

            if new_book_info.textbook:
                book_info.textbook = new_book_info.textbook
            if new_book_info.workbook:
                book_info.workbook = new_book_info.workbook

            if book_info.textbook or book_info.workbook:
                put_db(user_id, "books", book_info)

            return book_info.model_dump_json()
        except ValidationError as e:
            return jsonify(e.errors(), 400)

    return ""


@api_bp.route("/ping")
def ping():
    return "pong"


@api_bp.route("/plan", methods=["GET", "POST"])
def plan():
    user_id = get_uuid()

    if request.method == "GET":
        userdata = get_db(user_id, "userdata")
        if not userdata:
            return "You must provide user data for planning"

        book_info = get_db(user_id, "books")
        if not book_info:
            return "You must provide your book information for planning"

        quiz_result = get_db(user_id, "quiz_result")
        if not quiz_result:
            return "You must provide your learning preferences quiz result"

        current_plan = get_db(user_id, "current_plan", Plan(plan=[]))

        if DEBUG:
            return """{
    "plan": [
        {
            "uuid": "1a2b3c4d-0001-0000-0000-000000000001",
            "emoji": "📖",
            "topic": "교과서 03. 이차함수 y=a(x-p)²+q의 그래프 학습 (114-124쪽)",
            "schedule": {
                "start": "08:00:00Z",
                "duration_minute": 30
            },
            "done": false
        },
        {
            "uuid": "1a2b3c4d-0002-0000-0000-000000000002",
            "emoji": "📖",
            "topic": "교과서 04. 이차함수 y=ax²+bx+c의 그래프 학습 (124-130쪽)",
            "schedule": {
                "start": "08:40:00Z",
                "duration_minute": 25
            },
            "done": false
        },
        {
            "uuid": "1a2b3c4d-0003-0000-0000-000000000003",
            "emoji": "✏️",
            "topic": "워크북 11. 이차함수의 그래프 ⑴ 문제 풀이 (160-164쪽)",
            "schedule": {
                "start": "09:15:00Z",
                "duration_minute": 50
            },
            "done": false
        },
        {
            "uuid": "1a2b3c4d-0004-0000-0000-000000000004",
            "emoji": "✏️",
            "topic": "워크북 11. 이차함수의 그래프 ⑴ 문제 풀이 (165-169쪽)",
            "schedule": {
                "start": "10:15:00Z",
                "duration_minute": 50
            },
            "done": false
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
                    "content": make_knowledge_base(book_info.textbook, book_info.workbook),
                },
                {
                    "role": "user",
                    "content": make_user_input(userdata, data_available=False),
                },
                {
                    "role": "user",
                    "content": make_planning_considerations(quiz_result, current_plan),
                },
                {
                    "role": "user",
                    "content": ADDITIONAL_INSTRUCTIONS,
                }
            ]
        )

        plan_suggestion = response.output_parsed

        if not plan_suggestion:
            return '''{"plan": []}'''

        return plan_suggestion.model_dump_json()

    elif request.method == "POST":
        try:
            data = request.get_json()
            current_plan = Plan(**data)
            put_db(user_id, "current_plan", current_plan)

            return current_plan.model_dump_json()
        except ValidationError as e:
            return jsonify(e.errors(), 400)
    return ""

@api_bp.route("/tasks/complete", methods=["GET", "POST"])
def complete_task():
    user_id = get_uuid()

    if request.method == "GET":
        recent_results: list[TaskResult] = get_db(user_id, "recent_results", [])
        now = datetime.now()
        recent_results = list(
            filter(
                lambda task: now < task.timestamp.replace(tzinfo=None) + timedelta(days=7),
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

@api_bp.route("/feedback/daily")
def daily_feedback():
    user_id = get_uuid()

    quiz_result = get_db(user_id, "quiz_result")

    recent_results: list[TaskResult] = get_db(user_id, "recent_results", [])

    now = datetime.now()
    today_results = list(filter(
        lambda result: now < result.timestamp.replace(tzinfo=None) + timedelta(days=1),
        recent_results,
    ))

    if not (quiz_result and recent_results):
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
                "content": make_learning_preference(quiz_result)
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
