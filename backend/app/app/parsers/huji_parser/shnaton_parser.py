import os

os.environ["DJANGO_SETTINGS_MODULE"] = "Coursist.settings"
import re
import urllib
from datetime import datetime
from typing import Optional, List
from urllib import request
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from logic.errors import ShnatonParserError, FetchRawDataError, HtmlFormatError

from utils.logger import log, wrap

SHNATON_URL = "https://shnaton.huji.ac.il/index.php/"
CHARSET = "windows-1255"

# Edge cases:
# 34209 - Has comments
# 96203 - Has date מועדים מיוחדים
# 71080 - Has verbose מועדים מיוחדים
# 34209 - Has two teachers for the same group, one for a lesson.

SEMESTERS_DICT = {"A": {
    "he": "א",
    "en": "a"
}, "B": {
    "he": "ב",
    "en": "b"
}, "SUMMER": {
    "he": "קיץ",
    "en": "summer"
}, "YEARLY": {
    "he": "שנתי",
    "en": "yearly"
}}


def parse_course_semester(semester: str) :
    if semester == "סמסטר א' או/ו ב'":
        return [SEMESTERS_DICT["A"], SEMESTERS_DICT["B"]]
    elif semester == "סמסטר א'":
        return [SEMESTERS_DICT["A"]]
    elif semester == "סמסטר ב'":
        return [SEMESTERS_DICT["B"]]
    elif semester == "קיץ" or semester == "סמסטר קיץ":
        return [SEMESTERS_DICT["SUMMER"]]
    elif semester == "שנתי":
        return [SEMESTERS_DICT["YEARLY"]]
    raise NotImplementedError(f"Unrecognized course semester: {semester}")


def parse_general_course_info(source, year, course):
    general_course_info = source.find_all(class_="courseTD")
    course_tab_info = source.find_all(class_="courseTab")
    if course_tab_info[5].contents:
        course["extraData"] = {"syllabus": SHNATON_URL + str(course_tab_info[5].contents[1].attrs['href']).split("'")[-2]}
    else:
        course["extraData"] = {}
    course["courseId"] = str(re.sub("[^0-9]", "", general_course_info[2].string))
    name = general_course_info[1].string.replace("_", "")
    try:
        name_en = general_course_info[0].string.title()
        course["courseName"] = {"he": name, "en": name_en}
    except Exception as e:
        course["courseName"] = {"he": name}

    term = general_course_info[7].string
    course["terms"] = parse_course_semester(term)
    course["credits"] = int(re.sub("[^0-9]", "", general_course_info[6].string))
    return course


def parse_faculty(source, course):
    faculty_container = source.find(class_="courseTitle")
    if len(faculty_container) == 0:
        raise HtmlFormatError("Faculty / department not found")
    # maxsplit = 1 because some faculties have more than one colon
    data = faculty_container.string.split(":", maxsplit=1)
    if len(data) != 2:
        raise HtmlFormatError(f"Faculty / department bad formatting: {data}")
    faculty = data[0].strip(" :\t")
    department = data[1].strip(" :\t")
    course["faculties"] = [{"name": {"he": faculty}}]
    course["departments"] = [{"name": {"he": department}}]
    return course


def get_degree_type(maslul_name):
    if "בוגר" in maslul_name:
        return "BA"
    elif "מוסמך" in maslul_name:
        return "MA"
    elif "דוקטורט" in maslul_name:
        return "PHD"
    else:
        return "BA"


def parse_maslulim(source_maslulim, course):
    course["tracks"] = []
    maslulimInfo = source_maslulim.find_all(class_="link")
    for maslul_info in maslulimInfo[1:]:
        maslul_name = maslul_info.contents[0].contents[0]
        degree_type = get_degree_type(maslul_name)
        course["tracks"].append({"degreeType": degree_type, "name": {"he": maslul_name}})
    return course


def parse_kedem(a):
    cleanKedemArray = []
    for i in range(len(a) - 3):
        if len(a[i]) > 3 and a[i].isnumeric():
            cleanKedemArray.append(a[i])
            cleanKedemArray.append(a[i + 3])
    return cleanKedemArray


def get_kedem_json(kedem_array):
    kedem_json = {'AND': []}
    i = 0
    if len(kedem_array) == 2:
        kedem_json['AND'].append({"courseId": kedem_array[0]})
    if len(kedem_array) > 2 and kedem_array[1] == 'וגם   ':
        kedem_json['AND'].append({"courseId": kedem_array[0]})
    while i < len(kedem_array) - 1:
        if kedem_array[i + 1] == 'וגם   ':
            kedem_json['AND'].append({"courseId": kedem_array[i + 2]})
            i += 2
        elif kedem_array[i + 1] == 'או':
            or_dict = dict()
            or_dict['OR'] = [{"courseId": kedem_array[i]}, {"courseId": kedem_array[i + 2]}]
            i += 2
            while i + 1 < len(kedem_array) and kedem_array[i + 1] == "או":
                or_dict['OR'].append({"courseId": kedem_array[i + 2]})
                i += 2
            kedem_json['AND'].append(or_dict)
        elif kedem_array[i + 1] == 'וגם  יש לבחור אחד מהקורסים הבאים ':
            or_dict = dict()
            or_dict['OR'] = [{"courseId": kedem_array[i + 2]}, {"courseId": kedem_array[i + 4]}]
            i += 4
            while i + 1 < len(kedem_array) and kedem_array[i + 1] == "או":
                or_dict['OR'].append({"courseId": kedem_array[i + 2]})
                i += 2
            kedem_json['AND'].append(or_dict)
        else:
            i += 1
    if not kedem_json['AND']:
        return {}
    return kedem_json


class ShnatonParser:
    def __init__(
            self, shnaton_url: str = SHNATON_URL
    ):
        self.shnaton_url = shnaton_url

    def get_course_html(self, year: int, course_number: int):
        log.info("Read course html's from shnaton")
        data = urllib.parse.urlencode(
            {"peula": "Simple", "maslul": "0", "shana": "0", "year": year, "course": course_number}
        ).encode("utf-8")
        data_kedem = urllib.parse.urlencode(
            {"peula": "CourseD", "maslul": "0", "year": year, "course": course_number, "detail": "kedem"}
        ).encode("utf-8")
        data_maslulim = urllib.parse.urlencode(
            {"peula": "CourseD", "maslul": "0", "year": year, "course": course_number, "detail": "tochniot"}
        ).encode("utf-8")
        response_kedem = urllib.request.urlopen(url=self.shnaton_url, data=data_kedem)
        response_maslulim = urllib.request.urlopen(url=self.shnaton_url, data=data_maslulim)
        response = urllib.request.urlopen(url=self.shnaton_url, data=data)
        html = response.read().decode(response.headers.get_content_charset())
        html_kedem = response_kedem.read().decode(response_kedem.headers.get_content_charset())
        html_maslulim = response_maslulim.read().decode(response_maslulim.headers.get_content_charset())

        return html, html_kedem, html_maslulim

    def extract_data_from_shnaton(self, year: int, course_number: int) -> Optional[dict]:
        course_dict = {}
        html, html_kedem, html_maslulim = self.get_course_html(year, course_number)
        source = BeautifulSoup(html, "html.parser")
        source_kedem = BeautifulSoup(html_kedem, "html.parser")
        kedem_text = source_kedem.getText().split("\n")
        kedem_array = parse_kedem(kedem_text)
        kedem_json = get_kedem_json(kedem_array)
        course_dict["parentDependencies"] = kedem_json
        source_maslulim = BeautifulSoup(html_maslulim, "html.parser")
        if len(source.find_all(class_="courseTD")) == 0:
            raise HtmlFormatError(f"Course number {course_number} not found")
        course_dict = parse_faculty(source, course_dict)
        course_dict = parse_maslulim(source_maslulim, course_dict)

        course_dict = parse_general_course_info(source, year, course_dict)
        return course_dict

    def _fetch_course(self, course_number: int, year: int):
        log.info(f"Fetch course called for number {wrap(course_number)} and year {wrap(year)}")
        if not isinstance(course_number, int):
            course_number = int(course_number)

        course = self.extract_data_from_shnaton(year, course_number)
        if course is None:
            raise FetchRawDataError("No raw data could be parsed")

        raw_course_number = int(course["courseId"])
        if raw_course_number != course_number:
            raise ShnatonParserError(
                f"Course numbers mismatch: given {wrap(course_number)}, parsed {wrap(raw_course_number)}"
            )

        return course

    def fetch_course(self, course_number: int, year: int = None):
        """
        Fetch course from Shnaton, add it to the database and return it.
        :param course_number: The course number to search.
        :param year: The year to look for in the shnaton.
        :return: The course model object of the fetched course and its classes,
         or None if the course wasn't found.
        """
        if not year:
            now = datetime.now()
            year = now.year
            if now.month >= 8:
                year += 1
        try:
            return self._fetch_course(course_number, year)
        except ShnatonParserError:
            raise
        except Exception as e:
            raise ShnatonParserError(f"Failed to parse course {wrap(course_number)} for year {wrap(year)}") from e
