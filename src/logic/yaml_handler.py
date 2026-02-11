# yaml_handler.py
import yaml


class YamlParser:
    @staticmethod
    def parse(stream) -> dict:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
