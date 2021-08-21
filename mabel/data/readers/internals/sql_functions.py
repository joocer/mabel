def get_year(input):
    import dateutil.parser
    import datetime

    if isinstance(input, str):
        input = dateutil.parser.parse(input)
    if isinstance(input, (datetime.date, datetime.datetime)):
        return input.year
    return None  #


def get_month(input):
    import dateutil.parser
    import datetime

    if isinstance(input, str):
        input = dateutil.parser.parse(input)
    if isinstance(input, (datetime.date, datetime.datetime)):
        return input.month
    return None


def get_day(input):
    import dateutil.parser
    import datetime

    if isinstance(input, str):
        input = dateutil.parser.parse(input)
    if isinstance(input, (datetime.date, datetime.datetime)):
        return input.day
    return None


def get_date(input):
    import dateutil.parser
    import datetime

    if isinstance(input, str):
        input = dateutil.parser.parse(input)
    if isinstance(input, (datetime.date, datetime.datetime)):
        return input.date
    return None


FUNCTIONS = {
    "YEAR": get_year,
    "MONTH": get_month,
    "DAY": get_day,
    "DATE": get_date,
    "UCASE": lambda x: x.upper(),
    "LCASE": lambda x: x.lower(),
    "LEN": len,
    "ROUND": round,
}
