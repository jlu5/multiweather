"""Data types to represent a weather response"""

from dataclasses import dataclass, field
import datetime

from multiweather.log import logger

# pylint: disable=too-few-public-methods
class Temperature:
    """Represents a temperature value"""
    __slots__ = ("c", "f")
    def __init__(self, c=None, f=None):
        if len(list(filter(None, (c, f)))) != 1:
            raise ValueError("Exactly one of 'c' and 'f' must be specified")
        if c is not None:
            self.c = float(c)
            self.f = self.c * 9/5 + 32
        else:
            self.f = float(f)
            self.c = (self.f - 32) * 5/9

    def __repr__(self):
        return f'<Temperature {self.c}C / {self.f}F>'

    def __eq__(self, other):
        return self.c == other.c and self.f == other.f

def make_temperature(f=None, c=None) -> Temperature | None:
    """Convenience method to create a Temperature, or None if the data is missing"""
    if f is not None:
        return Temperature(f=f)
    if c is not None:
        return Temperature(c=c)
    return None

class Distance:
    """Represents a distance value (visibility, etc.)"""
    __slots__ = ("km", "mi")
    def __init__(self, km=None, mi=None):
        if len(list(filter(None, (km, mi)))) != 1:
            raise ValueError("Exactly one of 'km', 'mi' must be specified")
        if km is not None:
            self.km = float(km)
            self.mi = self.km / 1.609
        else:
            self.mi = float(mi)
            self.km = self.mi * 1.609

    def __repr__(self):
        return f'<Distance {self.km}km / {self.mi}mi>'

    def __eq__(self, other):
        return self.km == other.km and self.mi == other.mi

def make_distance(mi=None, km=None) -> Distance | None:
    """Convenience method to create a Distance, or None if the data is missing"""
    if mi is not None:
        return Distance(mi=mi)
    if km is not None:
        return Distance(km=km)
    return None

class Speed:
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
        if len(list(filter(None, (kph, mph, ms)))) != 1:
            raise ValueError("Exactly one of 'kph', 'mph' and 'ms' must be specified")
        if kph is not None:
            self.kph = float(kph)
            self.mph = self.kph / 1.609
            self.ms = self.kph / 3.6
        elif mph is not None:
            self.mph = float(mph)
            self.kph = self.mph * 1.609
            self.ms = self.kph / 3.6
        else:
            self.ms = float(ms)
            self.kph = self.ms * 3.6
            self.mph = self.kph / 1.609

    def __repr__(self):
        return f'<Speed {self.kph}kph / {self.mph}mph / {self.ms}m/s>'

    def __eq__(self, other):
        return self.kph == other.kph and self.mph == other.mph and self.ms == other.ms

class Precipitation:
    """Represents a precipitation value (amount and percentage)"""
    __slots__ = ("percentage", "mm", "inches")
    def __init__(self, percentage, mm=None, inches=None):
        if not 0 <= percentage <= 1:
            raise ValueError(f"Invalid percentage value {percentage}")
        self.percentage = percentage

        if len(list(filter(None, (mm, inches)))) != 1:
            raise ValueError("Exactly one of 'mm', 'inches' must be specified")
        if mm is not None:
            self.mm = float(mm)
            self.inches = self.mm / 25.4
        else:
            self.inches = float(inches)
            self.mm = self.inches * 25.4

    def __repr__(self):
        return f'<Precipitation {self.mm}mm / {self.inches}in>'

    def __eq__(self, other):
        return self.percentage == other.percentage and self.mm == other.mm and self.inches == other.inches

def make_precipitation(percentage, mm=None, inches=None) -> Precipitation | None:
    """Convenience method to create a Precipitation, or None if the data is missing"""
    if percentage is None:
        logger.debug("missing precipitation percentage")
        return None
    if mm:
        return Precipitation(percentage, mm=mm)
    if inches:
        return Precipitation(percentage, inches=inches)
    logger.debug("missing precipitation amount")
    return None

@dataclass
class WindConditions:
    """Represents wind conditions (speed, gust, and direction)"""
    # Wind speed
    speed: Speed
    # Wind gust
    gust: Speed
    # Direction in meteorological angles
    direction: float

def make_wind(direction, speed_mph=None, speed_kph=None, gust_mph=None, gust_kph=None) -> WindConditions | None:
    """Convenience method to create a WindConditions, or None if the data is missing"""
    if direction is None:
        logger.debug("missing wind angle")
        return None
    direction = float(direction)
    if speed_mph and gust_mph:
        return WindConditions(
            speed=Speed(mph=speed_mph),
            gust=Speed(mph=gust_mph),
            direction=direction,
        )
    if speed_kph and gust_kph:
        return WindConditions(
            speed=Speed(kph=speed_kph),
            gust=Speed(kph=gust_kph),
            direction=direction,
        )
    logger.debug("missing wind amount")
    return None

# pylint: disable=too-many-instance-attributes
@dataclass
class WeatherConditions:
    """Represents the weather conditions for some time period"""
    # Summary text of weather conditions (e.g. "Sunny")
    summary: str | None
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
    # Humidity (percentage value between 0 and 1)
    humidity: float | None
    # Atmospheric pressure (hPa)
    pressure: float | None

    # Precipitation
    precipitation: Precipitation | None
    # Cloud coverage percentage
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
    """Represents the overall weather response"""
    # Current conditions
    current: WeatherConditions

    # Pretty URL of the weather request
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
