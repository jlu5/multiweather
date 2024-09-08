# multiweather

A Python weather library supporting multiple backends. Because weather APIs [go](https://www.reddit.com/r/webdev/comments/8tjavu) [away](https://www.reddit.com/r/androidapps/comments/1aoz984/), and you shouldn't have to rewrite your code each time.

## Currently supported

- [Open-Meteo.com](https://open-meteo.com/)
- [PirateWeather](https://pirateweather.net/en/latest/)

## Usage
```python
from multiweather import OpenMeteoBackend # or your preferred backend

om = OpenMeteoBackend() # pass api_key=... for those backends require one

# Blocking fetcher
weather = om.get_weather_sync((lat, lon))

# Or in an async context
async def get_weather():
    weather = await om.get_weather((lat, lon))
```

Both `get_weather` and `get_weather_sync` return a [`WeatherResponse`](multiweather/data.py) dataclass instance.
