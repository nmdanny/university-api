from abc import ABC
from typing import Mapping, Union

class Serializer(ABC):
    def __init__(self, input_path: str):
        self.input: Mapping[str, Union[str, dict, int]] = self.load_input(input_path)

    @staticmethod
    def load_input(file_path) -> Mapping[str, Union[str, dict, int]]:
        raise NotImplementedError()

    def serialize(self, parsed_input):
        raise NotImplementedError()

    def populate_db(self):
        raise NotImplementedError()
