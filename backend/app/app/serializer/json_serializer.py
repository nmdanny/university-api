import json
from typing import List, Mapping, Optional, Union, Type

from app.core.config import settings
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.base_class import Translations, ExtraData

from app.models import (
    University, Course, Track, Department, Faculty, Term, DegreeType
)

Item = Union[University, Course, Track, Department, Faculty, Term]
ItemType = Union[Type[University], Type[Course], Type[Track], Type[Department], Type[Faculty], Type[Term]]

key_mapper = {
    "name": "name_translations",
    "degreeType": "degree",
    "extraData": "extra_data",
    "credits": "course_credits"
}

type_generator_mapper = {
    "departments": Department,
    "faculties": Faculty,
    "tracks": Track,
    "courses": Course
}


class JsonSerializer:
    def __init__(self, input_path: str):
        self.input: dict = self.load_input(input_path)
        self.db: Session = SessionLocal()
        self.remove_all()
        # must be configured before serializing
        self.university: University = self.create_item(University, self.input["university"])

        self.populate_db()

    def populate_db(self):
        del self.input["university"]
        self._serialize_item_map(self.input)

    @staticmethod
    def load_input(input_path) -> dict:
        with open(input_path, "r") as js_file:
            return json.load(js_file, encoding="utf8")

    def create_university(self,
                          name_translations: Translations,
                          extra_data: Optional[ExtraData],
                          university_id: int) -> University:
        return self._get_or_create_item(University, name_translations=name_translations,
                                        extra_data=extra_data,
                                        id=university_id)

    def get_or_create_term(self, term_map: dict):
        return self._get_or_create_item(Term, **term_map)

    @staticmethod
    def convert_map_keys(item_map: dict):
        return {k if k not in key_mapper else key_mapper[k]: v for k, v in item_map.items()}

    def create_item(self, item_type: ItemType, item_map: dict) -> Item:
        return self._get_or_create_item(item_type, **item_map)

    def create_course(self, course_map):
        return self.create_item(Course, course_map)

    def create_courses(self):
        for course in self.input['courses']:
            self.create_course(course)

    def _serialize_item_map(self, item_mapping: dict):
        return {
            k: v if k not in type_generator_mapper else self._serialize_list_items(
                k, v) for k, v in item_mapping.items()
        }

    @staticmethod
    def _map_json_keys(item_mapping: dict):
        return {
            k if k not in key_mapper else key_mapper[k]: v for k, v in item_mapping.items()
        }

    def _serialize_list_items(self, key, list_items):
        return [self.create_item(type_generator_mapper[key], {**item, "university": self.university}) for item in
                list_items]

    def _get_or_create_item(self, cls: ItemType, **kwargs) -> Item:
        kwargs = self._serialize_item_map(self._map_json_keys(kwargs))
        cached_item = self.get_item(cls, kwargs["name_translations"], item_id=kwargs.get("id"))
        if cached_item is not None:
            print(f"{cls.__name__} already exists")
            return cached_item

        item = cls(**kwargs)
        print(f"Created new {cls.__name__} with id={item.id}")

        self.db.add(item)
        self.db.commit()

        return item

    def get_item(self, cls, name_translations, item_id=None) -> Optional[Item]:
        items_filter = self.db.query(cls).filter(cls.name_translations["en"].astext == name_translations["en"])
        if item_id is not None:
            items_filter = items_filter.filter(cls.id == item_id)

        items = items_filter.all()
        if len(items) > 0:
            return items[0]

        return None

    def remove_all(self):
        tables = ["track", "course", "department", "faculty", "term", "university"]
        for table in tables:
            self.db.execute(f"delete from {table};")
        self.db.commit()


if __name__ == '__main__':
    serializer = JsonSerializer(settings.INPUT_PATH + "/sample.json")

    serializer.create_courses()
    # serializer.create_courses()

    print("all:")
    print(serializer.db.execute("select * from department;").all())
    serializer.remove_all()
    # print(db.get("university", "1").all())
