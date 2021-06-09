from .course import Course
from pydantic import Field
from .track import Track
from typing import List


class TrackWithCourses(Track):
    courses: List[Course] = Field(..., description="List of courses within this track")
