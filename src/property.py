from common import TransformIdentifier
from define import PropertyCategory
import logging
from interface import TypeInfo
from log import Log

log: logging.Logger = Log(__name__).getLogger()
simpleTypeWhiteList = ["string", "number", "boolean"]


class PropertyRefType(TypeInfo):
    importedFile: str

    def __init__(self, schema: dict) -> None:
        ref: str = schema.get("$ref")
        self.importedFile, pathPart = ref.split("#")
        typeName = TransformIdentifier(pathPart.split("/")[-1])
        super().__init__(typeName)
        log.debug("get ref remote file %s, type %s",
                  self.importedFile, self.typeName)

    def GetImportFrom(self) -> str:
        return self.importedFile


class PropertySimpleType(TypeInfo):
    def __init__(self, schema: dict) -> None:
        super().__init__(schema.get("type", ""))


class PropertyArrayType(PropertyRefType):
    def __init__(self, schema: dict) -> None:
        items: dict = schema.get("items", "")
        super().__init__(items)


def GetPropertyCategory(schema: dict) -> PropertyCategory:
    typeName = schema.get("type", "")
    if typeName in simpleTypeWhiteList:
        return PropertyCategory.simpleType
    if typeName == "array":
        return PropertyCategory.arrayType
    ref = schema.get("$ref", "")
    if not ref == "":
        return PropertyCategory.refType
    return PropertyCategory.unknown


class ObjectProperty:
    propertyName: str
    required: bool
    typeInfo: TypeInfo

    def __init__(self, propertyName: str, required: bool, schema: dict) -> None:
        self.propertyName = propertyName
        self.required = required
        self.typeInfo = None
        category = GetPropertyCategory(schema)
        log.debug("category of property %s is %s", propertyName, category)
        if category == PropertyCategory.refType:
            self.typeInfo = PropertyRefType(schema)
        elif category == PropertyCategory.simpleType:
            self.typeInfo = PropertySimpleType(schema)
        elif category == PropertyCategory.arrayType:
            self.typeInfo = PropertyArrayType(schema)
        else:
            log.error("not support property %s yet", propertyName)
        log.debug("property %s is required %s", propertyName, required)

    def GetPropertyName(self) -> str:
        return self.propertyName

    def GetTypeInfo(self) -> TypeInfo:
        return self.typeInfo

    def GetRequired(self) -> bool:
        return self.required
