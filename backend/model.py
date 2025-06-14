from typing import Optional
from datetime import time, datetime
from uuid import UUID
from pydantic import BaseModel

class TimeBlock(BaseModel):
    start: time
    duration_minute: int

class Task(BaseModel):
    uuid: UUID
    emoji: str
    topic: str
    schedule: TimeBlock
    done: bool

class Plan(BaseModel):
    plan: list[Task]

class UserData(BaseModel):
    weekday_study_time: int
    weekend_study_time: int
    weekday_requirement: TimeBlock
    weekend_requirement: TimeBlock
    progress: str

class QuizResult(BaseModel):
    forced: list[bool]
    likert: list[int]

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
