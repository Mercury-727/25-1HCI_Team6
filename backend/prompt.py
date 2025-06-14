from typing import Optional
from datetime import datetime

from model import TaskResult, UserData, QuizResult, Plan
from knowledge_base import KnowledgeBase

PLAN_SYSTEM_PROMPT = """You are a study planner for self-directed learners.

Your task:
- Generate today's schedule as an array of tasks in Korean.
- Each task should include topic, start time, and duration(multiple of 5min).
- Use "TEXTBOOK CONTENTS" and "WORKBOOK CONTENTS" from the KNOWLEDGE BASE to decide the order and scope of study.
- When assigning workbook problems, specify the exact page ranges.
- All content and tasks should be in Korean.
- Consider attention span. Each task's duration should not be too long.
- Insert break times between tasks(do not include breaks in the schedule).
"""

FEEDBACK_SYSTEM_PROMPT = """You are an AI math learning coach.
Given a user's learning preferences and recent study data, generate concise daily feedback with three parts:
1. Learning Analysis: Briefly analyze today's study using the provided data and learning preference. Highlight strengths and areas for improvement.
2. Actionable Suggestion: Give one practical, specific suggestion for tomorrow's study, tailored to the user's style and recent performance.
3. Encouragement: Add a short, positive message to motivate the user.
All content should be in Korean.
"""

ADDITIONAL_INSTRUCTIONS = """
Additional Instructions:
- Analyze the user's current plan.
- Keep all tasks already marked as "done" unchanged in the schedule.
- For tasks not yet completed (not marked as "done"), adjust their start time and duration appropriately, considering the overall flow and the user's recent pace and learning preferences.
- When creating new tasks, always start from where the last relevant task in the current plan was completed.
- Explicitly state the page ranges for each workbook task, and ensure the workload is appropriate for the user's current ability.
- Reflect the user's progress and preferences in all scheduling decisions.

Respond only with the final schedule in Korean.
"""

def make_knowledge_base(textbook: str, workbook: str) -> str:
    kb = KnowledgeBase()

    prompt = ["KNOWLEDGE BASE:"]
    prompt.append(kb.get_textbook_contents(textbook))
    prompt.append(kb.get_workbook_contents(workbook))

    return "\n".join(prompt)


def make_user_input(userdata: UserData, data_available=False) -> str:
    is_weekday = datetime.today().weekday() < 5

    prompt = f"""Please generate a study plan based on the following constraints:

- Total study time must be ≤ {userdata.weekday_study_time if is_weekday else userdata.weekend_study_time}.
- The plan must satisfy: {userdata.weekday_requirement.model_dump_json() if is_weekday else userdata.weekend_requirement.model_dump_json()}.
    """

    if not data_available:
        prompt += f"- I'm currently studying chapter {userdata.progress} of the textbook.\n"

    return prompt

def make_learning_preference(result: Optional[QuizResult]) -> str:
    preferences = [
        "- The user's following learning preferences extracted from a quiz:",
    ]

    if not result:
        return preferences[0]

    preferences.append("conceptual approach: " + ("holistic" if result.forced[0] else "detail_focused"))
    preferences.append("motivation type: " + ("extrinsic" if result.forced[1] else "intrinsic"))
    preferences.append("study time allocation: " + ("preference based" if result.forced[2] else "plan based"))

    preferences.append("self regulation: " + (
        ("strong" if result.likert[0] >= 4 else (
            "weak" if result.likert[0] <= 2 else "moderate"
        ))
    ))
    preferences.append("achievement motivation: " + (
        ("high" if result.likert[0] >= 4 else (
            "low" if result.likert[0] <= 2 else "medium"
        ))
    ))
    preferences.append("mood based study: " + (
        ("frequent" if result.likert[0] >= 4 else (
            "rare" if result.likert[0] <= 2 else "sometimes"
        ))
    ))

    preferences.append("Adapt the schedule to match these preferences.")

    return "\n".join(preferences)

def make_recent_results(results: list[TaskResult]) -> str:
    if not results:
        return "I take 10min to solve a page of workbook."

    recent_results = [
        "- The user's recent task results (topic, completion rate, actual duration):",
    ]

    for result in results:
        recent_results.append(f"{result.topic}: {result.completion_rate}%, {result.duration_minute}min")

    return "\n".join(recent_results)

def make_current_plan(current_plan: Plan) -> str:
    plans = [
        "- The user's current plans (uuid, topic, schedule)"
    ]

    if not current_plan.plan:
        plans.append("No tasks planned")

    for task in current_plan.plan:
        plans.append(f"{task.uuid} {task.topic} {task.schedule.model_dump_json()}{' done' if task.done else ''}")

    return "\n".join(plans)


def make_planning_considerations(quiz_result: QuizResult, current_plan: Plan):
    prompt = [
        "For planning, consider:",
    ]

    prompt.append(make_learning_preference(quiz_result))
    prompt.append(make_current_plan(current_plan))
    prompt.append("I take 10min to solve a page of workbook")

    return "\n".join(prompt)
