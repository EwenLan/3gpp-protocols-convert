import logging
from expression import EnumExpression, ImportExpression, MappedTypeExpression, TsExpression
from interface import TypeInfo
from log import Log
import copy
import typing
from schema import ObjectProperty
import typeinfo

log: logging.Logger = Log(__name__).getLogger()

spaceIndent: int = 4
blankRowsBetweenExpressions = 2


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
    return TsObjectProperty(property.GetPropertyName(), typeinfo.TsSimpleTypeInfo(typeinfo.TsType(typeInfo.GetImportFrom(), typeInfo.GetTypeName())), property.GetRequired())


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
