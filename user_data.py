"""
Set the `config.py` with user's city.
"""

import os
import requests

def user_data():
    url = 'https://ipinfo.io/json'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return {
        'city': data['city'],
        'latitude': data['loc'].split(',')[0],
        'longitude': data['loc'].split(',')[1]
    }

user_data = user_data()

config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.py'
with open(config_file, 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'is_set' in line:
        # If `is_set` is False it's the first time opening the `config.py` file.
        # If it's the first time, the `config.py` values must be `None` so it can
        # be set by the `WeatherPy` class on it's initialization.
        # After it's initialized, the `config.py` file will always have a value.
        lines[i] = 'is_set = True\n'
    if 'city' in line:
        lines[i] = 'city = "' + user_data['city'] + '"\n'
    if 'latitude' in line:
        lines[i] = 'latitude = ' + user_data['latitude'] + '\n'
    if 'longitude' in line:
        lines[i] = 'longitude = ' + user_data['longitude'] + '\n'

with open(config_file, 'w') as f:
    f.writelines(lines)

city = user_data['city']
latitude = user_data['latitude']
longitude = user_data['longitude']