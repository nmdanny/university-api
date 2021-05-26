import random
import datetime
import sentry_sdk
import json

from shnaton_parser import ShnatonParser
from utils.logger import wrap, log

DEFAULT_SRC_FILE = "courses_2021.json"
DEFAULT_LIMIT = 100


def parse_shnaton(src_file=DEFAULT_SRC_FILE, limit=DEFAULT_LIMIT, shuffle=False):
    university_json = {}
    log.info(f"Fetching courses from {src_file} with limit: {limit}, shuffle: {shuffle}")
    with open(src_file, encoding="utf8") as file:
        courses = json.load(file)
    if shuffle:
        random.shuffle(courses)
    else:
        courses.sort(key=lambda c: c["id"])
    fail_count = 0
    log.info(f"Total {wrap(len(courses))} courses found")
    university_json["universityName"] = {"he": "האוניברסיטה העברית", "en": "The Hebrew University of Jerusalem"}
    university_json["parseDate"] = str(datetime.date.today())
    university_json["extraData"] = {}
    parser = ShnatonParser()
    limit = min(limit, len(courses))
    courses_list = []
    for i, course in enumerate(courses):
        if i >= limit:
            break
        course_number = course["id"]
        log.info(f"Course {wrap(i + 1)} out of {wrap(limit)} is {wrap(course_number)}")
        try:
            courses_list.append(parser.fetch_course(course_number))
        except Exception as e:
            log.error(f"Could'nt fetch course {course_number}: {e}")
            sentry_sdk.capture_exception(e)
            fail_count += 1
    log.info(f"Fail count: {wrap(fail_count)} out of {wrap(limit)}")
    university_json["courses"] = courses_list
    with open('C:/Users/USER/Desktop/data.json', 'w', encoding="utf-8") as fp:
        json.dump(university_json, fp, ensure_ascii=False)


if __name__ == '__main__':
    parse_shnaton()
