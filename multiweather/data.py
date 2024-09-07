"""Data types to represent a weather response"""

from dataclasses import dataclass, field
import datetime

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

class Precipitation:
    """Represents a precipitation amount value"""
    __slots__ = ("mm", "inches")
    def __init__(self, mm=None, inches=None):
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

@dataclass
class WindConditions:
    """Represents wind conditions (speed, gust, and direction)"""
    # Wind speed
    speed: Speed
    # Wind gust
    gust: Speed
    # Direction in meteorological angles
    direction: float

# pylint: disable=too-many-instance-attributes
@dataclass
class WeatherConditions:
    """Represents the overall weather conditions at a specific time"""
    # Summary text of current conditions (e.g. "Sunny")
    condition_summary: str
    # Icon URL representing the condition, if available
    condition_icon: str | None

    # Temperature
    temperature: Temperature
    # Feels like / apparent temperature
    feels_like: Temperature | None
    # Dew point:
    dew_point: Temperature | None
    # Humidity (percentage value between 0 and 1)
    humidity: float | None
    # Atmospheric pressure (hPa)
    pressure: float | None

    # Precipitation amount
    precipitation: Precipitation | None
    # Percentage of precipitation
    precipitation_prob: float | None
    # Cloud coverage percentage
    cloud_cover: float | None

    wind: WindConditions | None

    # UV index
    uv_index: float | None

    # Visibility
    visibility: Distance | None

    # Current, sunrise, sunset times (seconds since Unix epoch)
    time: float | None
    sunrise: float | None
    sunset: float | None

@dataclass
class WeatherResponse:
    """Represents the overall weather response"""
    # Current condition
    current: WeatherConditions
    # Daily forecast. Key is a timezone *aware* datetime, in the timezone of the requested weather location
    daily_forecast: dict[datetime.datetime, WeatherConditions] = field(default_factory=dict)

    def __post_init__(self):
        for key in self.daily_forecast:
            if key.tzinfo is None:
                raise ValueError("Keys to WeatherResponse.daily_forecast should be timezone aware")

__all__ = [
    'Temperature',
    'Distance',
    'Speed',
    'Precipitation',
    'WindConditions',
    'WeatherConditions',
    'WeatherResponse'
]
