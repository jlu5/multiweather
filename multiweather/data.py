"""Data types to represent a weather response"""

from dataclasses import dataclass, field
import datetime

from multiweather.log import logger

class _WeatherUnit():
    __slots__ = ()
    def __bool__(self):
        for slot in self.__slots__:
            if getattr(self, slot) is not None:
                return True
        return False

    def __eq__(self, other):
        for slot in self.__slots__:
            if getattr(self, slot) != getattr(other, slot):
                return False
        return True

# pylint: disable=too-few-public-methods
class Temperature(_WeatherUnit):
    """Represents a temperature value"""
    __slots__ = ("c", "f")
    def __init__(self, c=None, f=None):
        if c is not None and f is not None:
            raise ValueError("Exactly one of 'c' and 'f' can be specified")
        if c is not None:
            self.c = float(c)
            self.f = self.c * 9/5 + 32
        elif f is not None:
            self.f = float(f)
            self.c = (self.f - 32) * 5/9
        else:
            self.c = None
            self.f = None

    def __repr__(self):
        return f'<Temperature {self.c}C / {self.f}F>'

class Distance(_WeatherUnit):
    """Represents a distance value (visibility, etc.)"""
    __slots__ = ("km", "mi")
    def __init__(self, km=None, mi=None):
        if km is not None and mi is not None:
            raise ValueError("Exactly one of 'km', 'mi' can be specified")
        if km is not None:
            self.km = float(km)
            self.mi = self.km / 1.609
        elif mi is not None:
            self.mi = float(mi)
            self.km = self.mi * 1.609
        else:
            self.mi = None
            self.km = None

    def __repr__(self):
        return f'<Distance {self.km}km / {self.mi}mi>'

class Speed(_WeatherUnit):
    """Represents a speed value (wind speed, etc.)"""
    __slots__ = (
        # kilometers per hour
        "kph",
        # miles per hour
        "mph",
        # meters per second
        "ms"
    )
    def __init__(self, kph=None, mph=None, ms=None):
        if len(list(filter(lambda x: x is not None, (kph, mph, ms)))) > 1:
            raise ValueError("Exactly one of 'kph', 'mph' and 'ms' can be specified")
        if kph is not None:
            self.kph = float(kph)
            self.mph = self.kph / 1.609
            self.ms = self.kph / 3.6
        elif mph is not None:
            self.mph = float(mph)
            self.kph = self.mph * 1.609
            self.ms = self.kph / 3.6
        elif ms is not None:
            self.ms = float(ms)
            self.kph = self.ms * 3.6
            self.mph = self.kph / 1.609
        else:
            self.kph = None
            self.mph = None
            self.ms = None

    def __repr__(self):
        return f'<Speed {self.kph}kph / {self.mph}mph / {self.ms}m/s>'

class Precipitation(_WeatherUnit):
    """Represents a precipitation value (amount and percentage)"""
    __slots__ = ("percentage", "mm", "inches")
    def __init__(self, percentage=None, mm=None, inches=None):
        if percentage is not None and not 0 <= percentage <= 100:
            raise ValueError(f"Invalid percentage value {percentage}")
        self.percentage = percentage

        if mm is not None and inches is not None:
            raise ValueError("Exactly one of 'mm', 'inches' can be specified")
        if mm is not None:
            self.mm = float(mm)
            self.inches = self.mm / 25.4
        elif inches is not None:
            self.inches = float(inches)
            self.mm = self.inches * 25.4
        else:
            self.mm = None
            self.inches = None

    def __repr__(self):
        return f'<Precipitation {self.mm}mm / {self.inches}in {self.percentage}%>'

@dataclass
class WindConditions:
    """Represents wind conditions (speed, gust, and direction)"""
    # Wind speed
    speed: Speed
    # Wind gust
    gust: Speed | None
    # Direction in meteorological angles
    direction: float

def make_wind(direction, speed_mph=None, speed_kph=None, gust_mph=None, gust_kph=None,
              speed_ms=None, gust_ms=None) -> WindConditions | None:
    """Convenience method to create a WindConditions, or None if the data is missing"""
    if direction is None:
        logger.debug("missing wind angle")
        return None
    direction = float(direction)
    if speed_mph is not None:
        return WindConditions(
            speed=Speed(mph=speed_mph),
            gust=Speed(mph=gust_mph) if gust_mph is not None else None,
            direction=direction,
        )
    if speed_kph is not None:
        return WindConditions(
            speed=Speed(kph=speed_kph),
            gust=Speed(kph=gust_kph) if gust_kph is not None else None,
            direction=direction,
        )
    if speed_ms is not None:
        return WindConditions(
            speed=Speed(ms=speed_ms),
            gust=Speed(ms=gust_ms) if gust_ms is not None else None,
            direction=direction,
        )
    logger.debug("missing wind amount")
    return None

# pylint: disable=too-many-instance-attributes
@dataclass
class WeatherConditions:
    """Represents the weather conditions for some time period"""
    # Human readable summary of weather conditions (e.g. "Sunny")
    summary: str | None
    # Weather code (API specific)
    weather_code: str | int | None
    # Icon URL representing weather conditions, if available
    icon: str | None
    # Time associated with this weather report (timezone-aware date)
    time: datetime.datetime

    # Temperature
    temperature: Temperature | None
    # Feels like / apparent temperature
    feels_like: Temperature | None
    # Dew point:
    dew_point: Temperature | None
    # Humidity (stored as values between 0 and 100)
    humidity: float | None
    # Atmospheric pressure (hPa)
    pressure: float | None

    # Precipitation
    precipitation: Precipitation | None
    # Cloud coverage percentage (stored as values between 0 and 100)
    cloud_cover: float | None

    wind: WindConditions | None

    # UV index
    uv_index: float | None

    # Visibility
    visibility: Distance | None

    # Sunrise, sunset times
    sunrise: datetime.datetime | None
    sunset: datetime.datetime | None

    # Low & high temperatures (for forecasts)
    low_temperature: Temperature | None
    high_temperature: Temperature | None
    low_feels_like: Temperature | None
    high_feels_like: Temperature | None

@dataclass
class WeatherResponse:
    """Represents a combined weather response (current conditions and daily forecasts)"""
    # Current conditions
    current: WeatherConditions

    # Weather backend name & URL of the weather report (for attribution purposes)
    name: str
    url: str | None

    # Daily forecasts
    daily_forecast: list[WeatherConditions] = field(default_factory=list)

__all__ = [
    'Temperature',
    'Distance',
    'Speed',
    'Precipitation',
    'WindConditions',
    'WeatherConditions',
    'WeatherResponse'
]
