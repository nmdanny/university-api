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
    "courses": Course,
    "term": Term
}

child_to_parent_mapper = {
    "departments": "courses",
    "faculties": "courses",
    "tracks": "courses",
    "courses": "university"
}


class JsonSerializer:
    def __init__(self, input_path: str):
        self.input: dict = self.load_input(input_path)
        self.db: Session = SessionLocal()
        self.remove_all()
        # must be configured before serializing
        # self.university: University = self.create_item(University, self.input["university"])
        self.campaign_context = None  # current campaign context
        self.course_cache = {}

        self.populate_db()

    def populate_db(self):


        # del self.input["university"]
        self.serialize_json(self.input)

    @staticmethod
    def load_input(input_path) -> dict:
        with open(input_path, "r") as js_file:
            return json.load(js_file, encoding="utf8")

    def create_university(self,
                          name_translations: Translations,
                          extra_data: Optional[ExtraData],
                          university_id: int) -> University:
        return self._get_or_create_item(University,
                                        name_translations=name_translations,
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

    # def create_courses(self):
    #     for course in self.input['courses']:
    #         self.create_course(course)

    def serialize_json(self, json_dict: dict):
        university_dependencies = ["courses"]
        json_dict = json_dict["university"]
        university = self.create_item(University, {k: json_dict[k] for k in json_dict.keys() if k not in university_dependencies})
        # self.create_courses(item_mapping["courses"], university)

    def serialize_mapping(self, item_mapping):
        for key in [_ for _ in item_mapping if _ in type_generator_mapper]:
            parent_item = self._get_or_create_item(type_generator_mapper[key],
                                                   **{k: v for k, v in item_mapping[key].items() if
                                                      k not in type_generator_mapper[key].course_sub_keys})

    def _serialize(self, item_mapping, key, parent=None):
        item_mapping = self._map_json_keys(item_mapping)
        item_cls = type_generator_mapper[key]
        kwargs = {k: v for k, v in item_mapping.items() if k not in item_cls.course_sub_keys}
        if key in child_to_parent_mapper:
            kwargs[child_to_parent_mapper[key]] = parent

        current_item = self._get_or_create_item(item_cls, **kwargs)
        for key in [_ for _ in item_mapping if _ in type_generator_mapper]:
            value = item_mapping[key]
            if type(value) is list:
                [self._serialize(item, key, current_item) for item in value]
            else:
                self._serialize(item_mapping[key], key, current_item)

    def create_courses(self, courses, university):
        course_dependencies = ["departments", "faculties", "tracks"]
        for course_map in courses:
            course = self.create_item(Course, {key: course_map[key] for key in course_map.keys() if
                                               key not in course_dependencies})
            if course.id not in self.course_cache:
                self.course_cache[course.id] = course
            for course_dependency in course_dependencies:
                self._serialize_list_items(course_dependency, course_map[course_dependency],
                                           {"course": course, "university": university})

    @staticmethod
    def _map_json_keys(item_mapping: dict):
        return {k if k not in key_mapper else key_mapper[k]: v for k, v in item_mapping.items()}

    def _serialize_list_items(self, key, list_items, item_extension={}):
        return [self.create_item(type_generator_mapper[key], {**item, **item_extension}) for item in list_items]

    def _get_or_create_item(self, cls: ItemType, **kwargs) -> Item:
        kwargs = self._map_json_keys(kwargs)
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

    # serializer.create_courses()

    print("all:")
    print(serializer.db.execute("select * from department;").all())
    serializer.remove_all()
    # print(db.get("university", "1").all())
