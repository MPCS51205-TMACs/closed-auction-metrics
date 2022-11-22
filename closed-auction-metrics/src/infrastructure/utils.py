import pytz
import datetime

TIME_ZONE = pytz.timezone("UTC")
TIME_PARSE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

def toSQLTimestamp6Repr(aDatetime: datetime.datetime) -> str:
    return aDatetime.strftime(TIME_PARSE_FORMAT)

def toDatetimeFromStr(aStrDatetime: str) -> datetime.datetime:
    return TIME_ZONE.localize(datetime.datetime.strptime(aStrDatetime,TIME_PARSE_FORMAT))
