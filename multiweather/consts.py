import importlib.resources
import json

WMOCODES = None
def _read_wmocodes():
    data = importlib.resources.files('multiweather').joinpath('vendor').joinpath('wmocodes.json').open('r')
    global WMOCODES
    WMOCODES = json.load(data)

_read_wmocodes()

def get_summary_for_wmo_code(wmo_code, is_day=True):
    time_of_day = 'day' if is_day else 'night'
    return WMOCODES[str(wmo_code)][time_of_day]['description']
