"""
Created on 2023-12-08, Extended on 2023-16-12

@author: wf, ChatGPT

Prompts for the development and extension of the 'YamlAble' class within the 'yamable' module:
1. Develop a Python class named 'YamAble' in a module called 'yamable'. This class should be useable as a mixin with a focus on converting dataclass instances to YAML format, specifically for use in object-oriented programming.
2. Implement methods in the 'YamAble' class for formatting multi-line string attributes using YAML block scalar style and excluding attributes with None values from the YAML output.
3. Add a method to handle multi-line strings in the 'YamlAble' class, ensuring they are formatted as block scalars in the YAML output.
4. Include functionality to recursively remove None values from dataclass instances before conversion in the 'YamAble' class.
5. The 'YamlAble' class should only process dataclass instances, with error handling to raise a ValueError for non-dataclass objects.
6. Write a comprehensive test suite for the 'YamlAble' class within the context of the 'ngwidgets.basetest' framework. The tests should verify correct block scalar formatting, omission of None values, and general accuracy of the YAML conversion.
7. Emphasize the use of Google-style docstrings, comprehensive comments, and type hints throughout the 'YamAble' class and its test suite.
8. Adhere strictly to the provided instructions, and if there are any assumptions or uncertainties, seek clarification before proceeding.
"""
import json
import urllib.request
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from typing import Any, Generic, Type, TypeVar

import yaml
from dacite import from_dict
from dataclasses_json import dataclass_json

T = TypeVar("T")


def lod_storable(cls):
    """
    Decorator to make a class LoDStorable by
    inheriting from YamlAble.
    This decorator also ensures the class is a
    dataclass and has JSON serialization/deserialization
    capabilities.
    """
    cls = dataclass(cls)  # Apply the @dataclass decorator
    cls = dataclass_json(cls)  # Apply the @dataclass_json decorator

    class LoDStorable(YamlAble, cls):
        """
        decorator class
        """

        pass

    LoDStorable.__name__ = cls.__name__
    LoDStorable.__doc__ = cls.__doc__

    return LoDStorable


class DateConvert:
    """
    date converter
    """

    @classmethod
    def iso_date_to_datetime(cls, iso_date: str) -> datetime.date:
        date = datetime.strptime(iso_date, "%Y-%m-%d").date() if iso_date else None
        return date


class YamlAble(Generic[T]):
    """
    An extended YAML handler class for converting dataclass objects to and from YAML format,
    and handling loading from and saving to files and URLs.
    """

    def _yaml_setup(self):
        """
        Initializes the YamAble handler, setting up custom representers and preparing it for various operations.
        """
        if not is_dataclass(self):
            raise ValueError("I must be a dataclass instance.")
        if not hasattr(self, "_yaml_dumper"):
            self._yaml_dumper = yaml.Dumper
            self._yaml_dumper.ignore_aliases = lambda *_args: True
            self._yaml_dumper.add_representer(type(None), self.represent_none)
            self._yaml_dumper.add_representer(str, self.represent_literal)
            self._yaml_dumper.add_representer(tuple, self.represent_tuple)

    def represent_none(self, _, __) -> yaml.Node:
        """
        Custom representer for ignoring None values in the YAML output.
        """
        return self._yaml_dumper.represent_scalar("tag:yaml.org,2002:null", "")

    def represent_literal(self, dumper: yaml.Dumper, data: str) -> yaml.Node:
        """
        Custom representer for block scalar style for strings.
        """
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    def to_yaml(
        self,
        ignore_none: bool = True,
        ignore_underscore: bool = True,
        allow_unicode: bool = True,
        sort_keys: bool = False,
    ) -> str:
        """
        Converts this dataclass object to a YAML string, with options to omit None values and/or underscore-prefixed variables,
        and using block scalar style for strings.

        Args:
            ignore_none: Flag to indicate whether None values should be removed from the YAML output.
            ignore_underscore: Flag to indicate whether attributes starting with an underscore should be excluded from the YAML output.
            allow_unicode: Flag to indicate whether to allow unicode characters in the output.
            sort_keys: Flag to indicate whether to sort the dictionary keys in the output.

        Returns:
            A string representation of the dataclass object in YAML format.
        """
        obj_dict = asdict(self)
        self._yaml_setup()
        clean_dict = self.remove_ignored_values(
            obj_dict, ignore_none, ignore_underscore
        )
        yaml_str = yaml.dump(
            clean_dict,
            Dumper=self._yaml_dumper,
            default_flow_style=False,
            allow_unicode=allow_unicode,
            sort_keys=sort_keys,
        )
        return yaml_str

    @classmethod
    def from_yaml(cls: Type[T], yaml_str: str) -> T:
        """
        Deserializes a YAML string to a dataclass instance.

        Args:
            yaml_str (str): A string containing YAML formatted data.

        Returns:
            T: An instance of the dataclass.
        """
        data: dict[str, Any] = yaml.safe_load(yaml_str)
        instance: T = cls.from_dict(data)
        return instance

    @classmethod
    def load_from_yaml_file(cls: Type[T], filename: str) -> T:
        """
        Loads a dataclass instance from a YAML file.

        Args:
            filename (str): The path to the YAML file.

        Returns:
            T: An instance of the dataclass.
        """
        with open(filename, "r") as file:
            yaml_str: str = file.read()
        instance: T = cls.from_yaml(yaml_str)
        return instance

    @classmethod
    def load_from_yaml_url(cls: Type[T], url: str) -> T:
        """
        Loads a dataclass instance from a YAML string obtained from a URL.

        Args:
            url (str): The URL pointing to the YAML data.

        Returns:
            T: An instance of the dataclass.
        """
        yaml_str: str = cls.read_from_url(url)
        instance: T = cls.from_yaml(yaml_str)
        return instance

    def save_to_yaml_file(self, filename: str):
        """
        Saves the current dataclass instance to a YAML file.

        Args:
            filename (str): The path where the YAML file will be saved.
        """
        yaml_content: str = self.to_yaml()
        with open(filename, "w") as file:
            file.write(yaml_content)
            
    @classmethod
    def from_json2(cls: Type[T], json_str: str) -> T:
        """
        Deserializes a JSON string to a dataclass instance.

        Args:
            json_str (str): A string containing JSON formatted data.

        Returns:
            T: An instance of the dataclass.
        """
        data: dict[str, Any] = json.loads(json_str)
        instance: T = cls.from_dict(data)
        return instance

    @classmethod
    def load_from_json_file(cls: Type[T], filename: str) -> T:
        """
        Loads a dataclass instance from a JSON file.

        Args:
            filename (str): The path to the JSON file.

        Returns:
            T: An instance of the dataclass.
        """
        with open(filename, "r") as file:
            json_str: str = file.read()
        instance: T = cls.from_json(json_str)
        return instance

    @classmethod
    def load_from_json_url(cls: Type[T], url: str) -> T:
        """
        Loads a dataclass instance from a JSON string obtained from a URL.

        Args:
            url (str): The URL pointing to the JSON data.

        Returns:
            T: An instance of the dataclass.
        """
        json_str: str = cls.read_from_url(url)
        instance: T = cls.from_json(json_str)
        return instance

    def save_to_json_file(self, filename: str):
        """
        Saves the current dataclass instance to a JSON file.

        Args:
            filename (str): The path where the JSON file will be saved.
        """
        json_content: str = self.to_json()
        with open(filename, "w") as file:
            file.write(json_content)

    @classmethod
    def read_from_url(cls, url: str) -> str:
        """
        Helper method to fetch content from a URL.
        """
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return response.read().decode()
            else:
                raise Exception(f"Unable to load data from URL: {url}")

    @staticmethod
    def remove_ignored_values(
        value: Any, ignore_none: bool = True, ignore_underscore: bool = False
    ) -> Any:
        """
        Recursively removes specified types of values from a dictionary or list.
        By default, it removes keys with None values. Optionally, it can also remove keys starting with an underscore.

        Args:
            value: The value to process (dictionary, list, or other).
            ignore_none: Flag to indicate whether None values should be removed.
            ignore_underscore: Flag to indicate whether keys starting with an underscore should be removed.
        """
        if isinstance(value, dict):
            return {
                k: YamlAble.remove_ignored_values(v, ignore_none, ignore_underscore)
                for k, v in value.items()
                if (not ignore_none or v is not None)
                and (not ignore_underscore or not k.startswith("_"))
            }
        elif isinstance(value, list):
            return [
                YamlAble.remove_ignored_values(v, ignore_none, ignore_underscore)
                for v in value
            ]
        return value

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        """
        Creates an instance of a dataclass from a dictionary, typically used in deserialization.
        """
        if not data:
            return None
        instance = from_dict(data_class=cls, data=data)
        return instance
