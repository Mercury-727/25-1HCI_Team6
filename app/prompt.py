from model import UserData

SYSTEM_PROMPT = """You are a study planner for self-directed learners.

Your task:
- Generate today's schedule: an array of tasks in Korean.
- Each task includes topic, start time, and duration.
- Use "TEXTBOOK CONTENTS" and "PROBLEM SET CONTENTS" from the KNOWLEDGE BASE to decide the order and scope of study.
- When using problems from the problem set, specify page ranges.
- All content and tasks should be in Korean.
"""

KNOWLEDGE_BASE = """KNOWLEDGE BASE:
**TEXTBOOK CONTENTS**
I. 실수와 그 계산
1. 제곱근과 실수, 10-36pp
01. 제곱근과 그 성질, 12-19pp
02. 무리수와 실수, 20-27pp
03. 근호를 포함한 식의 계산, 28-36pp
중단원 스스로 확인하기, 37-39pp,
창의융합 프로젝트, 40p
수학으로 통하다, 41p
대단원 스스로 마무리하기, 42-45pp
II. 이차방정식
1. 다항식의 곱셈과 인수분해, 46-69pp
01. 다항식의 곱셈, 48-57pp
02. 다항식의 인수분해, 58-69pp
중단원 스스로 확인하기, 70-71pp,
2. 이차방정식, 72-89pp
01. 이차방정식과 그 풀이, 74-79pp
02. 완전제곱식을 이용한 이차방정식의 풀이, 80-89pp
중단원 스스로 확인하기, 90-91pp,
창의융합 프로젝트, 92p
수학으로 통하다, 93p
대단원 스스로 마무리하기, 94p
III. 이차함수
1. 이차함수와 그래프, 98-129pp
01. 이차함수의 뜻, 100-103pp
02. 이차함수 y=ax^2 의 그래프, 104-113pp
03. 이차함수 y=a(x-p)^2+q 의 그래프, 114-123pp
04. 이차함수 y=ax^2+bx+c 의 그래프, 124-129pp
중단원 스스로 확인하기, 130-131pp,
창의융합 프로젝트, 132p
수학으로 통하다, 133p
대단원 스스로 마무리하기, 134p
IV. 삼각비
1. 삼각비, 138-151pp
01. 삼각비의 뜻, 140-144pp
02. 삼각비의 값, 145-151pp
중단원 스스로 확인하기, 152-153p,
2. 삼각비의 활용, 154-163pp
01. 삼각비의 활용, 156-163pp
중단원 스스로 확인하기, 164-165pp,
창의융합 프로젝트, 166p
수학으로 통하다, 167p
대단원 스스로 마무리하기, 168p
V. 원의 성질
1. 원과 직선, 172-183pp
01. 원의 현, 174-178pp
02. 원의 접선, 179-183pp
중단원 스스로 확인하기, 184-185pp,
2. 원주각, 186-201pp
01. 원주각, 188-193pp
02. 원주각의 활용, 194-201pp
중단원 스스로 확인하기, 202-203pp,
창의융합 프로젝트, 204p
수학으로 통하다, 205p
대단원 스스로 마무리하기, 206p
VI. 통계
1. 대푯값과 산포도, 210-225pp
01. 대푯값, 212-219pp
02. 산포도, 220-225pp
중단원 스스로 확인하기, 226-227pp,
2. 상관관계, 228-237pp
01. 상관관계, 230-237pp
중단원 스스로 확인하기, 238-239pp,
창의융합 프로젝트, 240p
수학으로 통하다, 241p
대단원 스스로 마무리하기, 242p

**PROBLEM SET CONTENTS**
I. 제곱근과 실수
01 제곱근의 뜻과 성질, 8-27pp
02 무리수와 실수, 28-37pp
03 근호를 포함한 식의 곱셈과 나눗셈, 38-51pp
04 근호를 포함한 식의 덧셈과 뺄셈, 52-67pp
II. 다항식의 곱셈과 인수분해
05 다항식의 곱셈, 68-87pp
06 다항식의 인수분해, 88-105pp
07 인수분해 공식의 활용, 106-119pp
III. 이차방정식
08 이차방정식의 풀이 ⑴, 120-131pp
09 이차방정식의 풀이 ⑵, 132-141pp
10 이차방정식의 활용, 142-159pp
IV. 이차함수
11 이차함수의 그래프 ⑴, 160-177pp
12 이차함수의 그래프 ⑵, 178-195pp
"""

def make_user_input(userdata: UserData):
    return f"""Please generate a study plan based on the following constraints:

- Total study time must be ≤ {userdata.active_time}.
- Each task's duration must be ≤ {userdata.attention_span}.
- The full plan must satisfy: {userdata.requirement.model_dump_json()}.
- Do not schedule any task during: [{",".join(interval.model_dump_json() for interval in userdata.constraints)}].
- I have studied up to page {userdata.progress} of the textbook.
- I need {userdata.tpp} minutes to solve each page of the problem set.
    """
