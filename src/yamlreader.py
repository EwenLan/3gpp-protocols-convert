import typing
import yaml


class YamlReader:
    yamlContent: typing.Dict[str, dict]

    def __init__(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            self.yamlContent = yaml.load(f, yaml.FullLoader)

    def GetDictContent(self) -> dict:
        return self.yamlContent
