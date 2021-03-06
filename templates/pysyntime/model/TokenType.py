from enum import Enum


class TokenType(Enum):
    """
    Token type enum.
    """

    YEAR = 0
    YEAR_MID = 1
    YEAR_YEAR = 2
    MONTH = 3
    MONTH_ABBR = 4
    MONTH_MID = 5
    MONTH_MONTH = 6
    YEAR_MONTH = 7
    WEEK = 8
    WEEK_ABBR = 9
    WEEK_WEEK = 10
    DATE = 11
    TIME = 12
    TIME_TIME = 13
    DAY_TIME = 14
    SEASON = 15
    TIMELINE = 16
    PERIOD = 17
    DECADE = 18
    HALFDAY = 19
    HALFDAY_HALFDAY = 20
    TIME_UNIT = 21
    DURATION = 22
    DURATION_DURATION = 23
    HOLIDAY = 24
    TIME_ZONE = 25
    ERA = 26
    PREFIX = 27
    SUFFIX = 28
    LINKAGE = 29
    BASIC_NUMBER = 30
    BASIC_NUMBER_NUMBER = 31
    ORDINAL = 32
    ORDINAL_ORDINAL = 33
    DIGIT = 34
    DIGIT_DIGIT = 35
    NUMERAL = 36
    NUMERAL_NUMERAL = 37
