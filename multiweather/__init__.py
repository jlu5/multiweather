from .backends.openmeteo import OpenMeteoBackend
from .backends.openweathermap_basic import OpenWeatherMapBackend
from .backends.pirateweather import PirateWeatherBackend
from .exceptions import APIError, UnknownBackendError
from .version import __version__

__all__ = [
    'APIError',
    'OpenMeteoBackend',
    'OpenWeatherMapBackend',
    'PirateWeatherBackend',
    'UnknownBackendError',
]

SERVICE_TO_BACKEND = {
    'openmeteo': OpenMeteoBackend,
    'openweathermap': OpenWeatherMapBackend,
    'pirateweather': PirateWeatherBackend,
}

def get_backend_by_name(name):
    """Return a backend class by its name. Raises UnknownBackendError if the
    backend name is unknown."""
    if backend := SERVICE_TO_BACKEND.get(name):
        return backend
    raise UnknownBackendError(f"Unknown backend {name!r}. Supported options are {tuple(SERVICE_TO_BACKEND.keys())}")
