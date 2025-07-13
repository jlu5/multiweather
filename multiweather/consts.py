"""Weather code definitions"""

# Reference: https://open-meteo.com/en/docs#weather_variable_documentation
_WMO_CODES = {
    0: "Sunny",
    1: "A few clouds",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Light snow showers",
    86: "Snow showers",
    95: "Thunderstorm",
    96: "Hailstorm",
    99: "Hailstorm"
}
_WMO_CODES_NIGHT = _WMO_CODES | {
    0: "Clear"
}

def get_summary_for_wmo_code(wmo_code, is_day=True):
    """Get a short summary for a WMO 4680 code"""
    data = _WMO_CODES if is_day else _WMO_CODES_NIGHT
    return data[wmo_code]
