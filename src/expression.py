from abc import abstractclassmethod
import typing
import copy
import typeinfo
from log import Log
import logging
import common

spaceIndent: int = 4

log: logging.Logger = Log(__name__).getLogger()


class TsExpression(object):
    @abstractclassmethod
    def ToString(self) -> str:
        return ""


class ImportExpression(TsExpression):
    importedFile: str
    typeNames: typing.List[str]

    def __init__(self, typeNames: typing.List[str], importedFile: str) -> None:
        super().__init__()
        self.importedFile = importedFile
        self.typeNames = copy.deepcopy(typeNames)

    def CheckIfImportedFileEqual(self, importedFile: str) -> bool:
        return self.importedFile == importedFile

    def AddImportType(self, typeName: str):
        if not typeName in self.typeNames:
            self.typeNames.append(typeName)

    def ToString(self) -> str:
        ans: str = "import {"
        if len(self.typeNames) > 0:
            ans += "{}".format(self.typeNames[0])
        for i in range(1, len(self.typeNames), 1):
            ans += ", {}".format(self.typeNames[i])
        ans += "}} from \"{}\"".format(self.importedFile)
        return ans


class TypeDefineExpression(TsExpression):
    typeName: str

    def __init__(self, typeName: str) -> None:
        super().__init__()
        self.typeName = typeName


class MappedTypeExpression(TypeDefineExpression):
    originType: typeinfo.TsTypeInfo

    def __init__(self, typeName: str, originType: typeinfo.TsTypeInfo) -> None:
        super().__init__(typeName)
        self.originType = originType

    def ToString(self) -> str:
        return "export type {} = {}".format(self.typeName, self.originType.ToString())


class EnumExpression(TypeDefineExpression):
    enumValues: typing.List[str]

    def __init__(self, typeName: str, enumValues: typing.List[str]) -> None:
        super().__init__(typeName)
        self.enumValues = copy.deepcopy(enumValues)

    def ToString(self) -> str:
        log.debug("export enum type %s, options num %d",
                  self.typeName, len(self.enumValues))
        ans: str = "export enum {} {{\n".format(self.typeName)
        for i in self.enumValues:
            ans += " " * spaceIndent
            ans += "{} = \"{}\",\n".format(
                common.TransformIdentifier(i), i)
        ans += "}"
        return ans
