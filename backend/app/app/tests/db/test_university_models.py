from sqlalchemy.orm import Session
from app.models import (
    University,
    Term,
    Faculty,
    Department,
    Track,
    DegreeType,
    Course,
    CourseSet,
    CourseSetMembership,
    DAGNode, CourseSetNode, ORNode, singleton_course_node, DAGRootNode
)


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
    tracks = [
        Track(
            university=uni,
            id="23010",
            degree=DegreeType.Bachelors,
            name_translations={"he": 'מדמ"ח חד חוגי מורחב'},
            departments=[dep],
        ),
        Track(
            university=uni,
            id="125860",
            degree=DegreeType.Bachelors,
            name_translations={"he": "הנדסת חשמל ומחשבים עם התחמות בהנדסת מחשבים"},
            departments=[dep2],
        ),
    ]

    course_names = [
        "Infi1", "Infi2", "LinAlg1", "LinAlg2", "Probability", "IML", "Logic1", "LogicCS", "Intro2CS"
    ]

    courses = {
        name: Course(
            university=uni,
            id=f"C_{name.upper()}",
            name_translations={
                "en": name
            },
            term=terms[0],
            course_credits=1337
        ) for name in course_names
    }

    db.add_all(courses.values())

    infi1 = singleton_course_node(courses["Infi1"])
    infi2 = singleton_course_node(courses["Infi2"])
    infi1.children.append(infi2)

    lin1 = singleton_course_node(courses["LinAlg1"])
    lin2 = singleton_course_node(courses["LinAlg2"])
    lin1.children.append(lin2)

    prob = singleton_course_node(courses["Probability"])
    prob.parents.append(lin2)

    iml = singleton_course_node(courses["IML"])
    logic1 = singleton_course_node(courses["Logic1"])
    logic_cs = singleton_course_node(courses["LogicCS"])
    intro = singleton_course_node(courses["Intro2CS"])

    logic_cs.parents.append(intro)
    iml.parents.extend([prob, infi2, lin2])

    or_node = ORNode()
    or_node.university = uni
    or_node.children.extend([logic1, logic_cs])

    cs_extended_root = DAGRootNode()
    cs_extended_root.track = tracks[0]
    cs_extended_root.university = uni
    cs_extended_root.children.extend([
        infi1, lin1, or_node, intro
    ])

    db.add(cs_extended_root)

    db.commit()

