from typing import Optional
from datetime import time, datetime
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

class QuizResult(BaseModel):
    answers: list[bool]

class TaskResult(BaseModel):
    topic: str
    timestamp: datetime
    duration_minute: int
    completion_rate: int

class DailyFeedback(BaseModel):
    analysis: str
    suggestion: str
    encouragement: str

class BookInformation(BaseModel):
    textbook: Optional[str]
    workbook: Optional[str]
