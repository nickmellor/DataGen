class RandomContactException(BaseException):
    """
    base exception for any exception in the RandomPerson class
    """
    pass


class NameLookupException(RandomContactException):
    """error in name/popularity input file"""
    pass


class RandomNameException(BaseException):
    pass


class MissingPopularityException(RandomNameException):
    """missing or malformed popularity field contents"""
    pass


class NegSampleSizeException(RandomContactException):
    """
    Negative or zero sample size passed to .save_csv
    """
    pass


