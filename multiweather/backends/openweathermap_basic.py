"""OpenWeatherMap weather v2.5 backend (current conditions only)"""

import datetime
import urllib.parse

from multiweather.backends.basebackend import BaseJSONWeatherBackend
from multiweather.data import (
    Distance,
    Precipitation,
    Temperature,
    make_wind,
    WeatherConditions,
    WeatherResponse,
)
from multiweather.exceptions import GeocodeAPIError

class OpenWeatherMapBackend(BaseJSONWeatherBackend):
    SUPPORTS_NATIVE_GEOCODE = True
    def __init__(self, api_key, base_url='https://api.openweathermap.org/data/2.5/weather'):
        """Instantiates the OpenWeatherMap API client"""
        self.api_key = api_key
        self.base_url = base_url

    def _get_json_request_url(self, location, forecast_days=0):
        lat, lon = location
        return f'{self.base_url}?' + urllib.parse.urlencode({
            'appid': self.api_key,
            'lat': lat,
            'lon': lon,
            'units': 'metric', # default is Kelvin
        })

    def _format_weather(self, location, data):
        lat, lon = location
        pretty_url = 'https://openweathermap.org/weathermap?' + urllib.parse.urlencode({
            'lat': lat,
            'lon': lon,
            'zoom': 12
        })
        precipitation = Precipitation(percentage=None, mm=0)
        if rain := data.get('rain'):
            if rain1h := rain.get('1h'):
                precipitation = Precipitation(percentage=None, mm=rain1h)
            elif rain3h := rain.get('3h'):
                precipitation = Precipitation(percentage=None, mm=rain3h)
        elif snow := data.get('snow'):
            if snow1h := snow.get('1h'):
                precipitation = Precipitation(percentage=None, mm=snow1h)
            elif snow3h := snow.get('3h'):
                precipitation = Precipitation(percentage=None, mm=snow3h)

        tz = datetime.timezone(datetime.timedelta(seconds=data['timezone']))
        icon = f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
        current_out = WeatherConditions(
            summary=data['weather'][0]['main'],
            weather_code=data['weather'][0]['id'],
            icon=icon,
            time=datetime.datetime.fromtimestamp(data['dt'], tz),
            temperature=Temperature(c=data['main']['temp']),
            feels_like=Temperature(c=data['main']['feels_like']),
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure'],
            precipitation=precipitation,
            cloud_cover=data['clouds']['all'],
            wind=make_wind(data['wind']['deg'], speed_ms=data['wind']['speed'], gust_ms=data['wind'].get('gust')),
            visibility=Distance(km=data['visibility']/1000),
            sunrise=datetime.datetime.fromtimestamp(data['sys']['sunrise'], tz),
            sunset=datetime.datetime.fromtimestamp(data['sys']['sunset'], tz),
            # For large areas
            low_temperature=Temperature(c=data['main'].get('temp_min')),
            high_temperature=Temperature(c=data['main'].get('temp_high')),
            # Not available
            dew_point=None,
            uv_index=None,
            # Not applicable
            low_feels_like=None,
            high_feels_like=None,
        )
        resp = WeatherResponse(
            name='OpenWeatherMap',
            url=pretty_url,
            current=current_out,
        )
        return resp

    def _get_json_geocode_url(self, location):
        args = {
            'q': location,
            'limit': 1,
            'appid': self.api_key
        }
        return f'http://api.openweathermap.org/geo/1.0/direct?{urllib.parse.urlencode(args)}'

    def _parse_geocode(self, location, data):
        if not data:
            raise GeocodeAPIError(f'No results for {location!r}')
        return (data[0]['lat'], data[0]['lon'])
