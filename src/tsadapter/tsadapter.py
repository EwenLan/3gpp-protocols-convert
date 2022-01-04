from _typeshed import Self
from abc import abstractclassmethod
import logging
from interface import TypeInfo
from log import Log
import copy
import typing
from schema import ObjectProperty
import common
import typeinfo

log: logging.Logger = Log(__name__).getLogger()

spaceIndent: int = 4
blankRowsBetweenExpressions = 2


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


class TsObjectProperty:
    propertyName: str
    required: bool
    typeInfo: typeinfo.TsTypeInfo

    def __init__(self, propertyName: str, typeInfo: typeinfo.TsTypeInfo, required: bool = False) -> None:
        self.propertyName = propertyName
        self.typeInfo = typeInfo
        self.required = required

    def ToString(self) -> str:
        if self.required:
            return "{}: {}".format(self.propertyName, self.typeInfo.ToString())
        return "{}?: {}".format(self.propertyName, self.typeInfo.ToString())

    def GetImportFrom(self) -> str:
        return self.importFrom

    def GetTypeNames(self) -> typing.List[str]:
        if self.typeInfo == None:
            log.error("type info of property %s is none")
            return ""
        return self.typeInfo.get


class InterfaceExpression(TsExpression):
    typeName: str
    properties: typing.List[TsObjectProperty]

    def __init__(self, typeName: str, properties: typing.List[TsObjectProperty]) -> None:
        super().__init__()
        self.typeName = typeName
        self.properties = copy.deepcopy(properties)

    def ToString(self) -> str:
        ans: str = "export interface {} {{\n".format(self.typeName)
        for i in self.properties:
            ans += " " * spaceIndent
            ans += i.ToString()
            ans += "\n"
        ans += "}"
        return ans


class TsFileWritter:
    importExpressions: typing.List[ImportExpression]
    expressions: typing.List[TsExpression]

    def __init__(self) -> None:
        self.importExpressions = []
        self.expressions = []

    def Import(self, typeName: str, importedFile: str) -> None:
        if importedFile == "":
            return
        for i in self.importExpressions:
            if i.CheckIfImportedFileEqual(importedFile):
                i.AddImportType(typeName)
                log.debug("import file %s exists, append type %s",
                          importedFile, typeName)
                return
        self.importExpressions.append(
            ImportExpression([typeName], importedFile))
        log.debug("import file %s not exists, add new import with type %s",
                  importedFile, typeName)

    def MappedType(self, typeName: str, originType: typeinfo.TsTypeInfo):
        self.expressions.append(
            MappedTypeExpression(typeName, originType))

    def MappedArrayType(self, typeName: str, elementType: str):
        self.expressions.append(
            MappedArrayTypeExpression(typeName, elementType))

    def Enum(self, typeName: str, enumValues: typing.List[str]):
        self.expressions.append(EnumExpression(
            typeName, copy.deepcopy(enumValues)))

    def Interface(self, typeName: str, properties: typing.List[TsObjectProperty]):
        self.expressions.append(InterfaceExpression(
            typeName, copy.deepcopy(properties)))

    def ToString(self) -> str:
        ans: str = ""
        combinedExpressions: typing.List[TsExpression] = self.importExpressions + \
            self.expressions
        if len(combinedExpressions) > 0:
            ans += combinedExpressions[0].ToString()
        for i in range(1, len(combinedExpressions), 1):
            ans += "\n" * blankRowsBetweenExpressions
            ans += combinedExpressions[i].ToString()
        return ans


def ConvertTsImportPath(filename: str):
    if filename == "":
        return ""
    return "./" + ".".join(filename.split(".")[:-1])


def convertToTsObjectProperty(property: ObjectProperty) -> TsObjectProperty:
    typeInfo: TypeInfo = property.GetTypeInfo()
    if typeInfo == None:
        log.error("fail to get type info, property %s",
                  property.GetPropertyName())
        return None
    return TsObjectProperty(property.GetPropertyName(), , property.GetRequired())


class TsAdapter:
    simpleType: dict
    enumType: dict
    objectType: dict

    tsWritter: TsFileWritter

    def __init__(self) -> None:
        self.simpleType = {}
        self.enumType = {}
        self.objectType = {}
        self.tsWritter = TsFileWritter()
        pass

    def AddSimpleTypeDefine(self, typeName: str, originType: str) -> None:
        self.tsWritter.MappedType(typeName, originType)

    def AddEnumTypeDefine(self, typeName: str, enumValues: typing.List[str]) -> None:
        self.tsWritter.Enum(typeName, enumValues)

    def AddObjectTypeDefine(self, typeName: str, properties: typing.List[ObjectProperty]) -> None:
        tsProperties: typing.List[TsObjectProperty] = [
            convertToTsObjectProperty(i) for i in properties if i != None]
        for i in tsProperties:
            self.tsWritter.Import(i.GetTypeName(), i.GetImportFrom())
        self.tsWritter.Interface(typeName, tsProperties)

    def AddArrayTypeDefine(self, typeName: str, elementType: str) -> None:
        self.tsWritter.MappedArrayType(typeName, elementType)

    def Save(self, path: str):
        f = open(path, "w", encoding="utf-8")
        f.write(self.tsWritter.ToString())
        f.close()
