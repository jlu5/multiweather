#!/usr/bin/env python3
"""Integration tests for weather backends"""
import dataclasses
import datetime
import os
import typing
import unittest

from multiweather import (
    OpenMeteoBackend,
    OpenWeatherMapBackend,
    PirateWeatherBackend,
)
import multiweather.data

API_KEY_OPENWEATHERMAP = os.environ.get('API_KEY_OPENWEATHERMAP')
API_KEY_PIRATEWEATHER = os.environ.get('API_KEY_PIRATEWEATHER')

class BaseTestCase:
    # This is defined at a different level to prevent unittest from running the base class
    # https://stackoverflow.com/a/25695512
    class IntegrationTestBase(unittest.IsolatedAsyncioTestCase):
        MAX_TIME_DRIFT = datetime.timedelta(hours=12)
        TEST_FORECAST_DAYS = 3
        backend = None
        supports_geocoding = False
        supports_daily_forecast = False

        def _type_check(self, data, expected_type=None):
            if expected_type:
                self.assertIsInstance(data, expected_type)
            # assert data.__annotations__, "No annotations to check"
            for attr, expected_attr_type in data.__annotations__.items():
                value = getattr(data, attr)
                if isinstance(value, int) and issubclass(float, expected_attr_type):
                    # Special case: any type hint including float should accept ints too
                    continue
                if isinstance(expected_attr_type, typing.GenericAlias):
                    type_args = typing.get_args(expected_attr_type)
                    assert len(type_args) == 1, f"Type check not implemented for {type(value)}"
                    for subvalue in value:
                        self._type_check(subvalue, type_args[0])
                    continue

                self.assertIsInstance(value, expected_attr_type,
                    f"Attribute {attr!r} has unexpected type {type(value)}")

                if dataclasses.is_dataclass(value):
                    self._type_check(value)

        def _smoke_test_weather(self, weatherdata, forecast_days=0):
            """Run basic checks on the weather data (independent of the actual reported values)"""
            self.assertLessEqual(
                abs(datetime.datetime.now(datetime.UTC) - weatherdata.current.time),
                self.MAX_TIME_DRIFT,
                "Time drift for current weather conditions too high")

            # Current conditions are kind of useless if these are missing
            self.assertIsNotNone(weatherdata.current.summary)
            self.assertIsNotNone(weatherdata.current.temperature)

            # Daily forecasts
            if self.supports_daily_forecast:
                self.assertGreaterEqual(len(weatherdata.daily_forecast), forecast_days)
            last_datetime = None
            # Forecast times should be monotonically increasing
            for daily_forecast in weatherdata.daily_forecast:
                self.assertIsNotNone(daily_forecast.summary)
                self.assertIsNotNone(daily_forecast.high_temperature)
                self.assertIsNotNone(daily_forecast.low_temperature)

                if last_datetime:
                    self.assertGreater(
                        daily_forecast.time,
                        last_datetime,
                        "Expected daily forecast timestamps to be increasing"
                    )
                    last_datetime = daily_forecast.date
            self._type_check(weatherdata, expected_type=multiweather.data.WeatherResponse)

        def test_integration_sync(self):
            """Test the synchronous get_weather path"""
            forecast_days = self.TEST_FORECAST_DAYS if self.supports_daily_forecast else 0
            w = self.backend.get_weather_sync((49.000000, -123.000000), forecast_days=forecast_days)
            self._smoke_test_weather(w, forecast_days=forecast_days)

        async def test_integration_async(self):
            """Test the asynchronous get_weather path"""
            w = await self.backend.get_weather((48.000000, 2.000000))
            self._smoke_test_weather(w)

        async def test_geocoding_async(self):
            """Test the synchronous get_weather path with geocoding, if supported by the backend"""
            if not self.supports_geocoding:
                return
            w = await self.backend.get_weather('London')
            self._smoke_test_weather(w)

        def test_geocoding_sync(self):
            """Test the synchronous get_weather path with geocoding, if supported by the backend"""
            if not self.supports_geocoding:
                return
            w = self.backend.get_weather_sync('Vancouver')
            self._smoke_test_weather(w)

class TestOpenMeteo(BaseTestCase.IntegrationTestBase):
    def setUp(self):
        # Disable fill_current_with_hourly to save a few API calls
        self.backend = OpenMeteoBackend(fill_current_with_hourly=False)
        self.supports_geocoding = True
        self.supports_daily_forecast = True

@unittest.skipUnless(API_KEY_OPENWEATHERMAP, "API_KEY_OPENWEATHERMAP env var not set")
class TestOpenWeatherMap(BaseTestCase.IntegrationTestBase):
    def setUp(self):
        self.backend = OpenWeatherMapBackend(API_KEY_OPENWEATHERMAP)
        self.supports_geocoding = True

@unittest.skipUnless(API_KEY_PIRATEWEATHER, "API_KEY_PIRATEWEATHER env var not set")
class TestPirateWeather(BaseTestCase.IntegrationTestBase):
    def setUp(self):
        self.backend = PirateWeatherBackend(API_KEY_PIRATEWEATHER)
        self.supports_daily_forecast = True

if __name__ == '__main__':
    unittest.main()
