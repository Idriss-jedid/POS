from enum import Enum


class UnitType(str, Enum):
    """Unit of measurement types"""
    PIECE = "PIECE"
    KG = "KG"
    GRAM = "GRAM"
    LITER = "LITER"
    ML = "ML"
    METER = "METER"
    CM = "CM"
    BOX = "BOX"
    PACK = "PACK"
    DOZEN = "DOZEN"
