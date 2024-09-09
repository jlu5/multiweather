import datetime
import urllib.parse
import zoneinfo

from multiweather.backends.basebackend import BaseJSONWeatherBackend
from multiweather.data import (
    make_precipitation,
    make_temperature,
    make_wind,
    WeatherConditions,
    WeatherResponse,
)
from multiweather.exceptions import APIError

class PirateWeatherBackend(BaseJSONWeatherBackend):
    def __init__(self, api_key, base_url='https://api.pirateweather.net/forecast'):
        """Instantiates the Pirate Weather (Dark Sky compatible) API client"""
        self.api_key = api_key
        self.base_url = base_url

    def _get_json_request_url(self, location, forecast_days=0):
        lat, lon = location
        exclude = ['minutely', 'hourly', 'alerts'] # not used by this library yet
        if not forecast_days:
            exclude.append('daily')

        args = {
            # Default units are US imperial, but this library converts units by itself anyways
            'units': 'us',
            'exclude': ','.join(exclude),
        }
        return f'{self.base_url}/{self.api_key}/{lat},{lon}?{urllib.parse.urlencode(args)}'

    def _format_weather_inner(self, data, tz):
        sunrise = None
        if sunrise_ts := data.get('sunriseTime'):
            sunrise = datetime.datetime.fromtimestamp(sunrise_ts, tz)

        sunset = None
        if sunset_ts := data.get('sunsetTime'):
            sunset = datetime.datetime.fromtimestamp(sunset_ts, tz)

        return WeatherConditions(
            summary=data.get('summary'),
            # TODO: icons are provided as names, need to find a URL for them
            icon=None,
            weather_code=data['icon'],
            time=datetime.datetime.fromtimestamp(data['time'], tz),

            temperature=make_temperature(f=data.get('temperature')),
            feels_like=make_temperature(f=data.get('apparentTemperature')),
            dew_point=make_temperature(f=data.get('dewPoint')),
            humidity=data.get('humidity'),
            pressure=data.get('pressure'),
            precipitation=make_precipitation(
                percentage=data.get('precipProbability'),
                inches=data.get('precipIntensity')
            ),
            cloud_cover=data.get('cloud_cover'),
            wind=make_wind(
                direction=data.get('windBearing'),
                speed_mph=data.get('windSpeed'),
                gust_mph=data.get('windGust')),
            uv_index=data.get('uvIndex'),
            visibility=data.get('visibility'),

            # Only available for forecasts
            sunrise=sunrise,
            sunset=sunset,
            low_temperature=make_temperature(f=data.get('temperatureLow')),
            high_temperature=make_temperature(f=data.get('temperatureHigh')),
            low_feels_like=make_temperature(f=data.get('apparentTemperatureLow')),
            high_feels_like=make_temperature(f=data.get('apparentTemperatureHigh')),
        )

    def _format_weather(self, location, data):
        lat, lon = location
        url = f'https://merrysky.net/forecast/{lat},{lon}'

        if error := data.get('message'):
            raise APIError(error)

        tz = zoneinfo.ZoneInfo(data['timezone'])

        current = self._format_weather_inner(data['currently'], tz)
        forecasts = []
        if 'daily' in data:
            for forecast_data in data['daily']['data']:
                forecasts.append(self._format_weather_inner(forecast_data, tz))

        resp = WeatherResponse(
            name='Pirate Weather',
            url=url,
            current=current,
            daily_forecast=forecasts,
        )
        return resp
