from model import TaskResult, UserData

SYSTEM_PROMPT = """You are a study planner for self-directed learners.

Your task:
- Generate today's schedule as an array of tasks in Korean.
- Each task should include topic, start time, and duration.
- Use "TEXTBOOK CONTENTS" and "WORKBOOK CONTENTS" from the KNOWLEDGE BASE to decide the order and scope of study.
- When assigning workbook problems, specify the exact page ranges.
- All content and tasks should be in Korean.
- Insert break times between tasks(do not include breaks in the schedule).
"""

KNOWLEDGE_BASE = """KNOWLEDGE BASE:
**TEXTBOOK CONTENTS**
| 단원 | 페이지 |
| I. 실수와 그 계산 | - |
| 1. 제곱근과 실수 | 10 |
| 01. 제곱근과 그 성질 | 12 |
| 02. 무리수와 실수 | 20 |
| 03. 근호를 포함한 식의 계산 | 28 |
| 중단원 스스로 확인하기 | 37 |
| 창의융합 프로젝트 | 40 |
| 수학으로 통하다 | 41 |
| 대단원 스스로 마무리하기 | 42 |
| II. 이차방정식 | - |
| 1. 다항식의 곱셈과 인수분해 | 46 |
| 01. 다항식의 곱셈 | 48 |
| 02. 다항식의 인수분해 | 58 |
| 중단원 스스로 확인하기 | 70 |
| 2. 이차방정식 | 72 |
| 01. 이차방정식과 그 풀이 | 74 |
| 02. 완전제곱식을 이용한 이차방정식의 풀이 | 80 |
| 중단원 스스로 확인하기 | 90 |
| 창의융합 프로젝트 | 92 |
| 수학으로 통하다 | 93 |
| 대단원 스스로 마무리하기 | 94 |
| III. 이차함수 | - |
| 1. 이차함수와 그래프 | 98 |
| 01. 이차함수의 뜻 | 100 |
| 02. 이차함수 y=ax^2 의 그래프 | 104 |
| 03. 이차함수 y=a(x-p)^2+q 의 그래프 | 114 |
| 04. 이차함수 y=ax^2+bx+c 의 그래프 | 124 |
| 중단원 스스로 확인하기 | 130 |
| 창의융합 프로젝트 | 132 |
| 수학으로 통하다 | 133 |
| 대단원 스스로 마무리하기 | 134 |
| IV. 삼각비 | - |
| 1. 삼각비 | 138 |
| 01. 삼각비의 뜻 | 140 |
| 02. 삼각비의 값 | 145 |
| 중단원 스스로 확인하기 | 152 |
| 2. 삼각비의 활용 | 154 |
| 01. 삼각비의 활용 | 156 |
| 중단원 스스로 확인하기 | 164 |
| 창의융합 프로젝트 | 166 |
| 수학으로 통하다 | 167 |
| 대단원 스스로 마무리하기 | 168 |
| V. 원의 성질 | - |
| 1. 원과 직선 | 172 |
| 01. 원의 현 | 174 |
| 02. 원의 접선 | 179 |
| 중단원 스스로 확인하기 | 184 |
| 2. 원주각 | 186 |
| 01. 원주각 | 188 |
| 02. 원주각의 활용 | 194 |
| 중단원 스스로 확인하기 | 202 |
| 창의융합 프로젝트 | 204 |
| 수학으로 통하다 | 205 |
| 대단원 스스로 마무리하기 | 206 |
| VI. 통계 | - |
| 1. 대푯값과 산포도 | 210 |
| 01. 대푯값 | 212 |
| 02. 산포도 | 220 |
| 중단원 스스로 확인하기 | 226 |
|2. 상관관계 | 228 |
| 01. 상관관계 | 230 |
| 중단원 스스로 확인하기 | 238 |
| 창의융합 프로젝트 | 240 |
| 수학으로 통하다 | 241 |
| 대단원 스스로 마무리하기 | 242 |

**WORKBOOK CONTENTS**
| 단원 | 페이지 |
| I. 제곱근과 실수 | - |
| 01 제곱근의 뜻과 성질 | 8 |
| 02 무리수와 실수 | 28 |
| 03 근호를 포함한 식의 곱셈과 나눗셈 | 38 |
| 04 근호를 포함한 식의 덧셈과 뺄셈 | 52 |
| II. 다항식의 곱셈과 인수분해 | - |
| 05 다항식의 곱셈 | 68 |
| 06 다항식의 인수분해 | 88 |
| 07 인수분해 공식의 활용 | 106 |
| III. 이차방정식 | - |
| 08 이차방정식의 풀이 ⑴ | 120 |
| 09 이차방정식의 풀이 ⑵ | 132 |
| 10 이차방정식의 활용 | 142 |
| IV. 이차함수 | - |
| 11 이차함수의 그래프 ⑴ | 160 |
| 12 이차함수의 그래프 ⑵ | 178 |
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

def make_user_input(userdata: UserData) -> str:
    return f"""Please generate a study plan based on the following constraints:

- Total study time must be ≤ {userdata.active_time}.
- Each task's duration must be ≤ {userdata.attention_span}.
- The plan must satisfy: {userdata.requirement.model_dump_json()}.
- Do not schedule any task during: [{",".join(interval.model_dump_json() for interval in userdata.constraints)}].
- I have studied up to page {userdata.progress} of the textbook.
    """

def _make_learning_preference(answers: list[bool]) -> str:
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

def _make_recent_results(results: list[TaskResult]) -> str:
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

    prompt.append(_make_learning_preference(answers))
    prompt.append(_make_recent_results(results))

    return "\n".join(prompt)
