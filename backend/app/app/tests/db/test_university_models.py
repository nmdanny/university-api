from sqlalchemy.orm import Session
from app.models import University, Term, Faculty, Track, DegreeType, Course


def test_can_create_uni(db: Session) -> None:
    uni = University(name_translations={"en": "Test Uni", "he": "אוני בדיקה"})

    terms = [
        Term(id=1, name_translations={"en": "Semester 1"}),
        Term(id=2, name_translations={"en": "Semester 2"}),
    ]

    fac = Faculty(university=uni, name_translations={"en": "CS", "he": 'מדמ"ח'})

    courses = [
        Course(
            university=uni,
            id="67310",
            term=terms[0],
            name_translations={
                "he": "מבוא למשאבי הספרייה",
                "en": "Introduction to library resources",
            },
        )
    ]

    tracks = [
        Track(
            faculty=fac,
            degree=DegreeType.Bachelors,
            name_translations={"he": "חד חוגי מורחב"},
            courses=courses,
        )
    ]

    db.add_all(tracks)
    db.commit()
