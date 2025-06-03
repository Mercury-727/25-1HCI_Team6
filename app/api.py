import secrets
import uuid

from flask import Flask, session, request, jsonify
from pydantic import ValidationError
from openai import OpenAI

from prompt import SYSTEM_PROMPT, KNOWLEDGE_BASE, make_user_input
from model import UserData, Plan

app = Flask(__name__)
app.secret_key = secrets.token_bytes()

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

@app.route("/ping")
def ping():
    return "pong"

@app.route("/plan")
def plan():
    if "userdata" not in session:
        return "You must provide user data for planning"

    userdata = UserData.model_validate_json(session["userdata"])

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
                "content": make_user_input(userdata)
            },
        ]
    )

    if not response.output_parsed:
        return '''{"plan": []}'''

    return response.output_parsed.model_dump_json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
