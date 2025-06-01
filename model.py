from pydantic import BaseModel

class TimeInterval(BaseModel):
    start: int
    end: int

class Task(BaseModel):
    topic: str
    schedule: TimeInterval

class Plan(BaseModel):
    plan: list[Task]

class UserData(BaseModel):
    active_time: int
    attention_span: int
    requirement: TimeInterval
    constraints: list[TimeInterval]
    progress: int
    tpp: float
