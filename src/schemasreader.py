import typing
from common import TransformIdentifier
from define import TypeCategory
from log import Log
from schema import ArrayTypeSchema, EnumTypeSchema, ComplexTypeSchema, SimpleTypeSchema
import logging

log: logging.Logger = Log(__name__).getLogger()


class Schemas:
    objectTypeSchemas: typing.List[ComplexTypeSchema]
    enumTypeSchemas: typing.List[EnumTypeSchema]
    simpleTypeSchemas: typing.List[SimpleTypeSchema]
    arrayTypeSchemas: typing.List[ArrayTypeSchema]

    def __init__(self, schemasPart: dict) -> None:
        self.objectTypeSchemas = []
        self.enumTypeSchemas = []
        self.simpleTypeSchemas = []
        self.arrayTypeSchemas = []
        for i in schemasPart:
            legalIdentifier = TransformIdentifier(i)
            currCategory = GetSchemaTypeCategory(schemasPart[i])
            log.debug("%s with identifier %s has type category %s",
                      i, legalIdentifier, currCategory)
            if currCategory == TypeCategory.enumType:
                self.enumTypeSchemas.append(
                    EnumTypeSchema(legalIdentifier, schemasPart[i]))
                continue
            if currCategory == TypeCategory.complexType:
                self.objectTypeSchemas.append(
                    ComplexTypeSchema(legalIdentifier, schemasPart[i]))
                continue
            if currCategory == TypeCategory.arrayType:
                self.arrayTypeSchemas.append(
                    ArrayTypeSchema(legalIdentifier, schemasPart[i]))
                continue
            self.simpleTypeSchemas.append(
                SimpleTypeSchema(legalIdentifier, schemasPart[i]))
        log.debug("get schemas of object type %d, simple type %d, enum type %d", len(
            self.objectTypeSchemas), len(self.simpleTypeSchemas), len(self.enumTypeSchemas))


def GetSchemasPart(d: dict) -> dict:
    componentsPart: dict = d.get("components", None)
    if componentsPart == None:
        log.error("dict object does not have component part")
        return {}
    schemasPart: dict = componentsPart.get("schemas", None)
    if schemasPart == None:
        log.error("dict object does not have schemas part")
        return {}
    return schemasPart


def GetSchemaTypeCategory(schema: dict) -> str:
    a: dict = schema.get("anyOf", None)
    t: str = schema.get("type", "")
    if t == "object":
        log.debug("dict has type object indicator")
        return TypeCategory.complexType
    if t == "array":
        log.debug("dict has type array indicator")
        return TypeCategory.arrayType
    if not a == None:
        log.debug("dict has anyOf component, assert as enum type")
        return TypeCategory.enumType
    if not t == "":
        log.debug("dict has type indicator %s", t)
        return TypeCategory.simpleType
    log.error("dict does not have valid type indicator, get object type as default")
    return TypeCategory.complexType
