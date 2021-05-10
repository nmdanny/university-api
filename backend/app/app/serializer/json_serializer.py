import sys

print(sys.path)

import json
from typing import List, Mapping, Optional, Union, Type

from app.core.config import settings
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.base_class import Translations, ExtraData

from app.models import (
    University, Course, Track, Department, Faculty, Term, DegreeType
)

from base_serializer import Serializer


class JsonSerializer(Serializer):
    def __init__(self, input_path: str):
        super().__init__(input_path)
        self.db: Session = SessionLocal()
        self.remove_all()
        self.university: University = self.create_university(self.input["universityName"],
                                                             self.input.get("extraData"),
                                                             university_id=self.input.get("universityId"))

    @staticmethod
    def load_input(input_path) -> Mapping[str, object]:
        with open(input_path, "r") as js_file:
            return json.load(js_file, encoding="utf8")

    def create_university(self, name_translations: Translations,
                          extra_data: Optional[ExtraData],
                          university_id: int):
        university = University(name_translations=name_translations,
                                extra_data=extra_data,
                                id=university_id)
        self.db.add(university)
        self.db.commit()
        print(f"Created new University with ID={university.id}")

        return university

    def get_or_create_term(self, name_translations: Translations):
        return self.get_or_create_item(Term, name_translations=name_translations)

    def get_or_create_track(self,
                            track_id: int,
                            name_translations: Translations,
                            degree: DegreeType,
                            extra_data: Optional[ExtraData]):
        return self.get_or_create_item(Track, name_translations=name_translations, degree=degree, id=track_id,
                                       university=self.university, extra_data=extra_data)

    def get_or_create_department(self,
                                 track_id: int,
                                 name_translations: Translations,
                                 extra_data: Optional[ExtraData]):
        return self.get_or_create_item(Department, name_translations=name_translations, id=track_id,
                                       university=self.university, extra_data=extra_data)

    def create_course(self, course_map):
        term = self.get_or_create_term(course_map["term"])
        tracks = [self.get_or_create_track(track_map["id"],
                                           track_map["name"],
                                           DegreeType[track_map["degreeType"]],
                                           extra_data=track_map.get("extraData"))
                  for track_map in course_map["tracks"]]
        departments = [self.get_or_create_department(department_map["id"],
                                                     department_map["name"],
                                                     extra_data=department_map.get("extraData"))
                       for department_map in course_map["departments"]]

    def create_courses(self):
        for course in self.input['courses']:
            self.create_course(course)

    def get_or_create_item(self, cls: Union[Type[Course], Type[Track], Type[Department], Type[Faculty], Type[Term]],
                           **kwargs):
        cached_item = self.get_item(cls, kwargs["name_translations"], item_id=kwargs.get("id"))
        if cached_item is not None:
            print(f"{cls.__name__} already exists")
            return cached_item

        print(f"Creating {cls.__name__}")
        item = cls(**kwargs)

        self.db.add(item)
        self.db.commit()

        return item

    def get_item(self, cls, name_translations, item_id=None) -> Optional[Union[Type[Course],
                                                                               Type[Track],
                                                                               Type[Department],
                                                                               Type[Faculty],
                                                                               Type[Term]]]:
        items_filter = self.db.query(cls).filter(cls.name_translations["en"].astext == name_translations["en"])
        if item_id is not None:
            items_filter = items_filter.filter(cls.id == item_id)

        items = items_filter.all()
        if len(items) > 0:
            return items[0]

        return None

    @staticmethod
    def where_clause_generator(*args: Union[str, bool]):
        return "where " + " and ".join(filter(bool, args)) if len(args) > 0 else ""

    def remove_all(self):
        tables = ["track", "course", "department", "faculty", "term", "university"]
        for table in tables:
            self.db.execute(f"delete from {table};")
        self.db.commit()

    @staticmethod
    def compare_obj_fields(field1, field2):
        return hash(str(field1)) == hash(str(field2))


if __name__ == '__main__':
    serializer = JsonSerializer(settings.INPUT_PATH + "/sample.json")

    serializer.create_courses()
    # serializer.create_courses()

    print("all:")
    print(serializer.db.execute("select * from department;").all())
    serializer.remove_all()
    # print(db.get("university", "1").all())
