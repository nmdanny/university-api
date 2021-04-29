# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.item import Item  # noqa
from app.models.user import User  # noqa
from app.models.university import University  # noqa
from app.models.faculty import Faculty  # noqa
from app.models.department import Department  # noqa
from app.models.track import Track, DegreeType  # noqa
from app.models.term import Term  # noqa
from app.models.course import Course  # noqa
from app.models.track_department import track_department  # noqa
from app.models.course_set import CourseSet, CourseSetMembership  # noqa