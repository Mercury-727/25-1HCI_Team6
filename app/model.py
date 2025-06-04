from datetime import time
from pydantic import BaseModel

class TimeBlock(BaseModel):
    start: time
    duration_minute: int

class Task(BaseModel):
    id: int
    emoji: str
    topic: str
    schedule: TimeBlock

class Plan(BaseModel):
    plan: list[Task]

class UserData(BaseModel):
    active_time: int
    attention_span: int
    requirement: TimeBlock
    constraints: list[TimeBlock]
    progress: int
    tpp: float

class QuizResult(BaseModel):
    answers: list[bool]
