"""Base class for weather backends"""

from abc import ABC, abstractmethod

import aiohttp
import requests

from multiweather.data import (
    WeatherResponse,
)

from multiweather.log import logger
from multiweather.version import __version__

type LatLon = tuple[float, float]
type Location = LatLon | str

DEFAULT_HEADERS = {
    'User-Agent': f'Mozilla/5.0 (compatible; python-multiweather/{__version__}) https://github.com/jlu5/multiweather'
}

class BaseWeatherBackend(ABC):
    """Base class for weather backends"""
    SUPPORTS_NATIVE_GEOCODE = False

    async def get_weather(self, location) -> WeatherResponse:
        """Fetch weather for <location> from the API (asynchronous)"""

    def get_weather_sync(self, location) -> WeatherResponse:
        """Fetch weather for <location> from the API (blocking)"""

class BaseJSONWeatherBackend(BaseWeatherBackend):
    """Base class for weather backends using a JSON API"""

    @abstractmethod
    def _get_json_request_url(self, location: Location, forecast_days=0) -> str:
        """Get the JSON API URL for a request"""

    @abstractmethod
    def _format_weather(self, location: Location, data) -> WeatherResponse:
        """Given a weather API's JSON response, generate a WeatherResponse instance"""

    def _get_json_geocode_url(self, location: str) -> str | None:
        """Get the JSON API URL for a geocode request (if applicable).

        If a backend does not need a separate API call to geocode inputs, this function should return None
        If built-in geocoding is not supported at all, raise NotImplementedError"""
        raise NotImplementedError("Only (lat, lon) inputs are supported by this backend")

    def _parse_geocode(self, location: str, data) -> LatLon:
        """Given a geocode API's JSON response, parse a lat, lon pair"""
        raise NotImplementedError("Only (lat, lon) inputs are supported by this backend")

    async def get_weather(self, location: Location, headers=None, forecast_days=0) -> WeatherResponse:
        async with aiohttp.ClientSession(headers=headers) as session:
            if isinstance(location, str):
                geocode_url = self._get_json_geocode_url(location)
                if geocode_url:
                    async with session.get(geocode_url) as resp:
                        json_data = await resp.json()
                        resolved_location = self._parse_geocode(location, json_data)
            else:
                resolved_location = location
            request_url = self._get_json_request_url(resolved_location, forecast_days=forecast_days)
            headers = headers or DEFAULT_HEADERS
            logger.debug("Using URL %s", request_url)
            async with session.get(request_url) as resp:
                json_data = await resp.json()
                return self._format_weather(resolved_location, json_data)

    def get_weather_sync(self, location: Location, timeout=10, headers=None, forecast_days=0) -> WeatherResponse:
        if isinstance(location, str):
            geocode_url = self._get_json_geocode_url(location)
            if geocode_url:
                resp = requests.get(geocode_url, timeout=timeout, headers=headers)
                resolved_location = self._parse_geocode(location, resp.json())
        else:
            resolved_location = location
        request_url = self._get_json_request_url(resolved_location, forecast_days=forecast_days)
        headers = headers or DEFAULT_HEADERS
        logger.debug("Using URL %s", request_url)
        resp = requests.get(request_url, timeout=timeout, headers=headers)
        json_data = resp.json()
        return self._format_weather(resolved_location, json_data)
