from model import TaskResult, UserData
from knowledge_base import KnowledgeBase

PLAN_SYSTEM_PROMPT = """You are a study planner for self-directed learners.

Your task:
- Generate today's schedule as an array of tasks in Korean.
- Each task should include topic, start time, and duration(multiple of 5min).
- Use "TEXTBOOK CONTENTS" and "WORKBOOK CONTENTS" from the KNOWLEDGE BASE to decide the order and scope of study.
- When assigning workbook problems, specify the exact page ranges.
- All content and tasks should be in Korean.
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
- Analyze the user's recent task results—especially completion rate and actual duration—to estimate their current learning level and pace.
- For both the textbook and workbook, determine the current progress based on the most recently completed tasks (e.g., last studied page).
- When creating new tasks, always start from where the last task was completed.
- When scheduling workbook tasks, dynamically adjust the number of pages per task based on recent performance:
    - If the completion rate for recent workbook tasks is low or the actual duration exceeded the planned time, reduce the number of pages for the next workbook task.
    - If the completion rate is high and the actual duration was within the planned time, you may slightly increase the number of pages.
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
    prompt = f"""Please generate a study plan based on the following constraints:

- Total study time must be ≤ {userdata.active_time}.
- Each task's duration must be ≤ {userdata.attention_span}.
- The plan must satisfy: {userdata.requirement.model_dump_json()}.
- Do not schedule any task during: [{",".join(interval.model_dump_json() for interval in userdata.constraints)}].
    """

    if not data_available:
        prompt += f"- I have studied up to page {userdata.progress} of the textbook.\n"

    return prompt

def make_learning_preference(answers: list[bool]) -> str:
    preferences = [
        "- The user's following learning preferences extracted from a quiz:",
    ]

    if not answers:
        return preferences[0]

    answer_len = len(answers)

    if answer_len >= 4 and any(answers[:4]):
        preferences.append("- Has internal motivation to learn math.")
    else:
        preferences.append("- Shows low intrinsic interest  in learning math.")

    if answer_len >= 6 and any(answers[4:6]):
        preferences.append("- Understands the value of math in life or grades.")

    if answer_len >= 9 and any(answers[6:9]):
        preferences.append("- Studies math to gain recognition or enter a good school.")

    if answer_len >= 10 and answers[9]:
        preferences.append("- Feels stressed about math test scores.")
    else:
        preferences.append("- Shows little stress about math tests.")

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

def make_planning_considerations(answers: list[bool], results: list[TaskResult]):
    prompt = [
        "For planning, consider:",
    ]

    prompt.append(make_learning_preference(answers))
    prompt.append(make_recent_results(results))

    return "\n".join(prompt)
