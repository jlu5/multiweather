"""Base class for weather backends"""

from abc import ABC, abstractmethod

import aiohttp
import requests

from multiweather.data import (
    WeatherResponse,
)

from multiweather.log import logger

type LatLon = tuple[float, float]
# type Location = LatLon | str

class APIError(Exception):
    """Generic class for API errors"""

class BaseWeatherBackend(ABC):
    """Base class for weather backends"""
    async def get_weather(self, location) -> WeatherResponse:
        """Fetch weather for <location> from the API (asynchronous)"""

    def get_weather_sync(self, location) -> WeatherResponse:
        """Fetch weather for <location> from the API (blocking)"""

class BaseJSONWeatherBackend(BaseWeatherBackend):
    """Base class for weather backends using a JSON API"""

    @abstractmethod
    def _get_json_request_url(self, location) -> str:
        """Get the JSON API URL for a request"""

    @abstractmethod
    def _format_weather(self, location, data) -> WeatherResponse:
        """Given a weather API's JSON response, generate a WeatherResponse instance"""

    async def get_weather(self, location) -> WeatherResponse:
        request_url = self._get_json_request_url(location)
        logger.debug("Using URL %s", request_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as resp:
                json_data = await resp.json()
                return self._format_weather(location, json_data)

    def get_weather_sync(self, location, timeout=10) -> WeatherResponse:
        request_url = self._get_json_request_url(location)
        logger.debug("Using URL %s", request_url)
        resp = requests.get(request_url, timeout=timeout)
        json_data = resp.json()
        return self._format_weather(location, json_data)
