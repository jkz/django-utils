import datetime

def timedelta_to_seconds(td):
    return td.days * (60 * 60 * 24) + td.seconds

SECOND = datetime.timedelta(seconds=1)
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
# Inaccurate from here
MONTH = 4 * WEEK
YEAR = 12 * MONTH
DECADE = 10 * YEAR
CENTURY = 10 * DECADE
MILLENIUM = 10 * CENTURY

def is_cooldowned(old, seconds, new=datetime.datetime.now()):
    return new - old > seconds

#TODO is this 1 second off?
def is_cooldowning(timestamp, seconds):
    return not is_cooldowned(timestamp, seconds)

def fuzzy_time(timestamp, now=None):
    now = now or datetime.datetime.now()
    is_history = now > timestamp
    delta = abs(now - timestamp)
    formats = (
            (SECOND, "just now", "right now", "seconds"),
            (MINUTE, "a minute ago", "a minute from now", "minutes"),
            (HOUR, "an hour ago", "an hour from now", "hours"),
            (DAY, "yesterday", "tomorrow", "days"),
            (WEEK, "last week", "next week", "weeks"),
            (MONTH, "last month", "next month", "months"),
            (YEAR, "last year", "next year", "years"),
            (DECADE, "last decade", "next decade", "decades"),
            (CENTURY, "last century", "next century", "centuries"),
            (MILLENIUM, "last millenium", "next millenium", "millenia"),
            (delta,)
    )

    for idx, val in enumerate(formats):
        if delta < 2 * val[0]:
            return val[1] if is_history else val[2]
        if delta < formats[idx + 1][0]:
            return " ".join((
                    str(int(timedelta_to_seconds(delta) / timedelta_to_seconds(val[0]))),
                    val[3],
                    "ago" if is_history else "from now"))

