"""Data types to represent a weather response"""

from dataclasses import dataclass, field
import datetime
import string

from multiweather.log import logger

class _WeatherUnit():
    __slots__ = ()
    _DEFAULT_TEMPLATE = None
    _NULL_VALUE_DISPLAY = '<null>'

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

    def _format_attrs(self, decimal_places):
        attrs = {}
        for attr in self.__slots__:
            value = getattr(self, attr)
            if isinstance(value, (int, float)):
                attrs[attr] = f'{value:.{decimal_places}f}'
            else:
                attrs[attr] = value
        return attrs

    def format(self, template_str=None, decimal_places=1):
        """
        Format the weather unit using template_str (or the class' default
        template string), with any float values fixed to decimal_places decimal
        places.
        """
        if not self:
            return self._NULL_VALUE_DISPLAY
        if template_str is None:
            if self._DEFAULT_TEMPLATE is None:
                raise ValueError("Template string missing")
            template_str = self._DEFAULT_TEMPLATE
        tmpl = string.Template(template_str)
        attrs = self._format_attrs(decimal_places=decimal_places)
        return tmpl.substitute(attrs)

    __str__ = format

    def __repr__(self):
        return f'{self.__class__.__name__}({self.format()})'

# pylint: disable=too-few-public-methods
class Temperature(_WeatherUnit):
    """Represents a temperature value"""
    __slots__ = ("c", "f")
    _DEFAULT_TEMPLATE = "${c}C / ${f}F"

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

class Distance(_WeatherUnit):
    """Represents a distance value (visibility, etc.)"""
    __slots__ = ("km", "mi")
    _DEFAULT_TEMPLATE = "${km}km / ${mi}mi"

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
    _DEFAULT_TEMPLATE = "${kph}kph / ${mph}mph / ${ms}m/s"

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

class Precipitation(_WeatherUnit):
    """Represents a precipitation value (amount and percentage)"""
    __slots__ = ("percentage", "mm", "inches")

    @property
    def _DEFAULT_TEMPLATE(self):  # pylint: disable=invalid-name
        tmpl = "${mm}mm / ${inches}in"
        if self.percentage is not None:
            tmpl += " (${percentage}%)"
        return tmpl

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

class Direction(_WeatherUnit):
    """Represents a direction, input as meterological angles"""
    __slots__ = ("angle", "direction")
    _DEFAULT_TEMPLATE = "$direction"

    def __init__(self, angle=None):
        self.angle = angle
        if angle is not None:
            self.angle = angle % 360
        self.direction = self._get_direction()

    def _get_direction(self):
        """Returns wind direction (N, W, S, E, etc.) given an angle."""
        directions = (
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
        )
        if self.angle is None:
            return directions[0]

        assert 0 <= self.angle < 360  # angle is already normalized
        angle_step = 360.0 / len(directions)
        idx = round(self.angle / angle_step)
        return directions[idx % len(directions)]

@dataclass
class WindConditions:
    """Represents wind conditions (speed, gust, and direction)"""
    # Wind speed
    speed: Speed
    # Wind gust
    gust: Speed | None
    # Direction in meteorological angles
    direction: Direction

def make_wind(direction, speed_mph=None, speed_kph=None, gust_mph=None, gust_kph=None,
              speed_ms=None, gust_ms=None) -> WindConditions | None:
    """Convenience method to create a WindConditions, or None if the data is missing"""
    if direction is None:
        logger.debug("missing wind angle")
        return None
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
