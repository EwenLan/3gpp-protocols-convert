import logging
from os import supports_bytes_environ
import typing
from common import TransformIdentifier
from interface import SchemaBase, TypeInfo
from log import Log
from property import ObjectProperty, PropertyRefType

log: logging.Logger = Log(__name__).getLogger()


class EnumTypeSchema(SchemaBase):
    enumValue: typing.List[str]

    def __init__(self, typeName: str, schema: dict) -> None:
        super().__init__(typeName)
        self.enumValue = []
        anyOf = schema.get("anyOf", None)
        for i in anyOf:
            enumValue: list = i.get("enum", [])
            for j in enumValue:
                self.enumValue.append(str(j))
        log.debug("get %d options in %s schema", len(self.enumValue), typeName)


class SimpleTypeSchema(SchemaBase):
    originType: str

    def __init__(self, typeName: str, schema: dict) -> None:
        super().__init__(typeName)
        t: str = schema.get("type", "")
        if t == "":
            log.error("unable to get type from schema, use string as default")
            self.originType = "string"
            return
        self.originType = t
        log.debug("get simple type %s with essential type %s", typeName, t)


class ComplexTypeSchema(SchemaBase):
    properties: typing.List[ObjectProperty]

    def __init__(self, typeName: str, schema: dict) -> None:
        super().__init__(typeName)
        self.properties = []
        required = schema.get("required", [])
        log.debug("type %s has %d required properties",
                  typeName, len(required))
        properties: list = schema.get("properties", [])
        for i in properties:
            self.properties.append(ObjectProperty(
                TransformIdentifier(i), i in required, properties[i]))
        log.debug("type %s has %d properties and %d required properties",
                  typeName, len(self.properties), len(required))


class ArrayTypeSchema(SchemaBase):
    elementType: TypeInfo

    def __init__(self, typeName: str, schema: dict) -> None:
        super().__init__(typeName)
        item: dict = schema.get("items", {})
        self.elementType = PropertyRefType(item)
