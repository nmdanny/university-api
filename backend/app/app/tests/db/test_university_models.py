from sqlalchemy.orm import Session
from app.models import University, Term, Faculty, Department, Track, DegreeType, Course


def test_can_create_uni(db: Session) -> None:
    uni = University(name_translations={"en": "Test Uni", "he": "אוני בדיקה"})

    terms = [
        Term(id=1, name_translations={"en": "Semester 1"}),
        Term(id=2, name_translations={"en": "Semester 2"}),
        Term(id=3, name_translations={"en": "Semester 1/2"}),
    ]

    fac = Faculty(
        university=uni,
        id="facCSE",
        name_translations={
            "en": "Computer Science and Engineering",
            "he": 'ביה"ס להנדסה ולמדעי המחשב',
        },
    )
    dep = Department(
        faculty=fac,
        id="521",
        name_translations={"en": "Computer Science", "he": "מדעי המחשב"},
    )
    dep2 = Department(
        faculty=fac,
        id="583",
        name_translations={
            "en": "Electrical & Computer Engineering",
            "he": "הנדסת חשמל ומחשבים",
        },
    )
    courses = [
        Course(
            university=uni,
            id="67101",
            term=terms[2],
            course_credits=7,
            name_translations={
                "he": "מבוא למדעי המחשב",
                "en": "Introduction to Computer Science",
            },
            tracks=[
                Track(
                    university=uni,
                    id="23010",
                    degree=DegreeType.Bachelors,
                    name_translations={"he": 'מדמ"ח חד חוגי מורחב'},
                    departments=[dep]
                ),
                Track(
                    university=uni,
                    id="125860",
                    degree=DegreeType.Bachelors,
                    name_translations={
                        "he": "הנדסת חשמל ומחשבים עם התחמות בהנדסת מחשבים"
                    },
                    departments=[dep2]
                ),
            ],
        )
    ]

    # will also add all associated entries
    db.add_all(courses)
    db.commit()
