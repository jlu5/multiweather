import datetime
import urllib.parse
import zoneinfo

from multiweather.backends.basebackend import BaseJSONWeatherBackend
from multiweather.consts import get_summary_for_wmo_code
from multiweather.data import (
    Distance,
    Precipitation,
    Temperature,
    make_wind,
    WeatherConditions,
    WeatherResponse,
)
from multiweather.exceptions import APIError, GeocodeAPIError

class OpenMeteoBackend(BaseJSONWeatherBackend):
    SUPPORTS_NATIVE_GEOCODE = True
    def __init__(self, api_key=None, base_url=None, fill_current_with_hourly=True):
        """Instantiates the Open-Meteo API client"""
        self.api_key = api_key
        default_base_url = 'https://customer-api.open-meteo.com/v1/forecast' if api_key \
            else 'https://api.open-meteo.com/v1/forecast'
        self.base_url = base_url or default_base_url
        self.fill_current_with_hourly = fill_current_with_hourly

    def _get_json_request_url(self, location, forecast_days=0):
        lat, lon = location
        args = {
            'latitude': lat,
            'longitude': lon,
            'timezone': 'auto',
            'timeformat': 'unixtime',

            # Open-Meteo is very flexible on which fields to output. (As of 20240907 this is equiv to 2.4 API calls)
            # These fields should more or less match the coverage of THIS library
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,cloud_cover,'
                'pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m,weather_code,is_day',
        }
        if forecast_days:
            args.update({
                'daily': 'temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,'
                    'sunrise,sunset,uv_index_max,precipitation_sum,precipitation_probability_max,'
                    'wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,weather_code,',
                'forecast_days': forecast_days,
            })
        if self.api_key:  # note: untested
            args['api_key'] = self.api_key

        if self.fill_current_with_hourly:
            args.update({
                # These additional fields are merged into the current conditions
                # With these enabled each call costs ~2.7 API calls
                'hourly': 'dew_point_2m,uv_index,visibility',
                'forecast_hours': 1,
            })

        return f'{self.base_url}?' + urllib.parse.urlencode(args)

    def _format_weather(self, _location, data):
        if data.get('error'):
            raise APIError(data.get('reason'))

        tz = zoneinfo.ZoneInfo(data['timezone'])
        current_data = data['current']

        # These values are not available in "current" conditions
        try:
            visibility = data['hourly']['visibility'][0] / 1000
        except (KeyError, IndexError):
            visibility = None
        try:
            uv_index = data['hourly']['uv_index'][0]
        except (KeyError, IndexError):
            uv_index = None

        weather_code = current_data.get('weather_code')
        current_out = WeatherConditions(
            weather_code=weather_code,
            summary=get_summary_for_wmo_code(weather_code, current_data['is_day']),
            # TODO: need to translate from WMO codes to icon
            icon=None,
            time=datetime.datetime.fromtimestamp(current_data['time'], tz),

            temperature=Temperature(c=current_data.get('temperature_2m')),
            feels_like=Temperature(c=current_data.get('apparent_temperature')),
            dew_point=Temperature(c=current_data.get('dew_point_2m')),
            humidity=current_data['relative_humidity_2m']/100 if 'relative_humidity_2m' in current_data else None,
            pressure=current_data.get('pressure_msl'),
            precipitation=Precipitation(
                mm=current_data.get('precipitation')
            ),
            cloud_cover=current_data['cloud_cover']/100 if 'cloud_cover' in current_data else None,
            wind=make_wind(
                direction=current_data.get('wind_direction_10m'),
                speed_kph=current_data.get('wind_speed_10m'),
                gust_kph=current_data.get('wind_gusts_10m')),
            uv_index=uv_index,
            visibility=Distance(km=visibility),

            # Only available for forecasts
            sunrise=None,
            sunset=None,
            low_temperature=None,
            high_temperature=None,
            low_feels_like=None,
            high_feels_like=None,
        )
        forecasts = []
        daily_data = data.get('daily')
        if daily_data:
            for day_index, daily_forecast_ts in enumerate(daily_data['time']):
                daily_forecast_time = datetime.datetime.fromtimestamp(daily_forecast_ts, tz)
                weather_code = daily_data['weather_code'][day_index]
                forecast_out = WeatherConditions(
                    weather_code=weather_code,
                    summary=get_summary_for_wmo_code(weather_code),
                    # TODO: need to translate from WMO codes to icon
                    icon=None,
                    time=daily_forecast_time,
                    low_temperature=Temperature(c=daily_data['temperature_2m_min'][day_index]),
                    high_temperature=Temperature(c=daily_data['temperature_2m_max'][day_index]),
                    low_feels_like=Temperature(c=daily_data['apparent_temperature_min'][day_index]),
                    high_feels_like=Temperature(c=daily_data['apparent_temperature_max'][day_index]),
                    precipitation=Precipitation(
                        mm=daily_data['precipitation_sum'][day_index],
                        percentage=daily_data['precipitation_probability_max'][day_index]/100,
                    ),
                    wind=make_wind(
                        direction=daily_data['wind_direction_10m_dominant'][day_index],
                        speed_kph=daily_data['wind_speed_10m_max'][day_index],
                        gust_kph=daily_data['wind_gusts_10m_max'][day_index],
                    ),
                    uv_index=daily_data['uv_index_max'][day_index],
                    sunrise=datetime.datetime.fromtimestamp(daily_data['sunrise'][day_index], tz),
                    sunset=datetime.datetime.fromtimestamp(daily_data['sunset'][day_index], tz),
                    # Only for current conditions
                    temperature=None,
                    feels_like=None,
                    humidity=None,
                    pressure=None,
                    cloud_cover=None,
                    dew_point=None,
                    visibility=None,
                )
                forecasts.append(forecast_out)

        resp = WeatherResponse(
            name='Open-Meteo.com',
            url='https://open-meteo.com/',
            current=current_out,
            daily_forecast=forecasts,
        )
        return resp

    def _get_json_geocode_url(self, location):
        args = {
            'name': location,
            'count': 1,
            'format': 'json',
            'language': 'en' # TODO lang support
        }
        return f'https://geocoding-api.open-meteo.com/v1/search?{urllib.parse.urlencode(args)}'

    def _parse_geocode(self, location, data):
        if data.get('error'):
            raise GeocodeAPIError(data.get('reason'))
        results = data.get('results')
        if not results:
            raise GeocodeAPIError(f'No results for {location!r}')
        return (results[0]['latitude'], results[0]['longitude'])
