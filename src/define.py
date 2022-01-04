from enum import Enum


class TypeCategory(Enum):
    complexType: str = "COMPLEX TYPE"
    simpleType: str = "SIMPLE DATA TYPE"
    enumType: str = "Enumerations"
    structuredType: str = "STRUCTURED DATA TYPE"
    arrayType: str = "ARRAY TYPE"


class PropertyCategory(Enum):
    unknown: int = 0
    refType: int = 1
    simpleType: int = 2
    arrayType: int = 3
