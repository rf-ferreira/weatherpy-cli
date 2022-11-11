import config
import os
import requests
import sys
from bs4 import BeautifulSoup as bs

class WeatherPy:
    def __init__(self):
        # Set language
        self._language = config.language

        # Get user info
        self._city = config.city
        self._latitude = config.latitude
        self._longitude = config.longitude

        # Set config
        if not config.is_set:
            self.reset()

        # Get weather info
        self._get_info()
    
    def _set_config(self, **kwargs) -> None:
        """
        Set new config values for `config.py` variables.

        **kwargs: gets the variable name and value (e.g., {language: languages.EN}).
        """
        config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.py'
        with open(config_file, 'r') as f:
            lines = f.readlines()

        for k, v in kwargs.items():
            for i, line in enumerate(lines):
                if k + ' = ' in line:
                    if '.' in str(v): # its a variable
                        lines[i] = f'{k} = {v}\n'
                    else: # its a string
                        lines[i] = f'{k} = "{v}"\n'
        
        with open(config_file, 'w') as f:
            f.writelines(lines)

    def _get_info(self) -> dict:
        """
        Gets the weather info based on data stored in `config.py` file.
        """
        url = f'https://weather.com/weather/hourbyhour/l/{self._latitude},{self._longitude}'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        page = requests.get(url, headers=headers)
        soup = bs(page.text, 'html.parser')

        self._state = soup.find('span', {'data-testid': 'PresentationName'}).text.split(',')[1]
        self._country = soup.find('span', {'data-testid': 'PresentationName'}).text.split(',')[2]
        self._temp = int(soup.find('span', {'data-testid': 'TemperatureValue'}).text.split('°')[0])
        self._temp_scale = soup.find('span', {'data-testid': 'languageSelectorStatus'}).next_element.next_element.text
        self._status = soup.find('p', {'data-testid': 'hourlyWxPhrase'}).text
        self._rain_probability = soup.find('span', {'data-testid': 'PercentageValue'}).text
        self._humidity = soup.find('span', {'data-testid': 'HumidityTitle'}).next_element.next_element.text

        # If the `self._temp_scale` value is different than the one in the
        # `config.py` file, it uses the config file value instead.
        if self._temp_scale != config.temp_scale:
            self.change_temp_scale(config.temp_scale.replace('°',''))
            self._temp_scale = config.temp_scale

        return {
            'state': self._state,
            'country': self._country,
            'temp': self._temp,
            'temp_scale': self._temp_scale,
            'status': self._status,
            'rain_probability': self._rain_probability,
            'humidity': self._humidity
        }

    def _temp_to_fahreinheit(self, temp: int) -> int:
        """
        Change the temperature from celsius to fahreinheit.

        temp: temperature in celsius.
        """
        return round((temp * (9/5)) + 32)

    def _temp_to_celsius(self, temp: int) -> int:
        """
        Change the temperature from fahreinheit to celsius.

        temp: temperature in fahreinheit.
        """
        return round((temp - 32) * (5/9))

    def change_city(self, city_name: str) -> dict:
        """
        Change the city name based on the user input and calls the 
        `self._get_info()` method with weather information about the new city.
        It also calls the `self._set_config()` method and change the city in
        the `config.py` file.

        city_name: city name.
        """
        url = 'https://www.climatempo.com.br/json/busca-cidades'
        response = requests.post(url, data={'name': {city_name}})
        city_exists = response.json()[0]['response']['data']

        if city_exists:
            city_info = city_exists[0]
            self._latitude = city_info['latitude']
            self._longitude = city_info['longitude']
            self._get_info()
            self._city = city_info['city']
            self._set_config(latitude=self._latitude, longitude=self._longitude, city=self._city)
            return city_info
        raise Exception(f"Couldn't find city with name: {city_name}")

    def change_language(self, lang: str) -> str:
        """
        Change the language based on the user input and calls
        the `self._set_config()` method to change the language in the
        `config.py` file.
        
        The list of possible names is stored on `languages.py` file.

        lang: language.
        """
        lang = lang.lower()
        valid_languages = ['pt: Portuguese', 'en: English']

        if lang == 'en' or lang == 'english':
            self._language = config.languages.EN
            self._set_config(language='languages.EN')
            return 'Language changed to English'
        elif lang == 'pt' or lang == 'portuguese':
            self._language = config.languages.PT
            self._set_config(language='languages.PT')
            return 'Language changed to Portuguese'
        raise Exception(f'You must provide a valid language such as: {valid_languages}')

    def change_temp_scale(self, scale: str) -> dict:
        """
        Change the temperature scale based on the user input and
        calls the `self._set_config()` method and change the temperature scale
        in the `config.py` file.
        
        scale: temperature scale (it can be celsius or fahrenheit).
        """
        scale = scale.lower()
        valid_scales = ['c: Celsius', 'f: Fahrenheit']

        if scale == 'c' or scale == 'celsius':
            if self._temp_scale == '°F':
                self._temp = self._temp_to_celsius(self._temp)
                self._temp_scale = '°C'
            self._set_config(temp_scale='°C')
            return {'temp': self._temp, 'temp_scale': self._temp_scale}
        elif scale == 'f' or scale == 'fahrenheit':
            if self._temp_scale == '°C':
                self._temp = self._temp_to_fahreinheit(self._temp)
                self._temp_scale = '°F'
            self._set_config(temp_scale='°F')
            return {'temp': self._temp, 'temp_scale': self._temp_scale}
        raise Exception(f'You must provide a valid scale such as: {valid_scales}')
    
    def reset(self) -> None:
        """
        Reset the `config.py` file setting the language to english, 
        temperature scale to fahrenheit and city to the user's city.

        The user's city is provided by the `user_data.py` file.
        """
        import user_data

        self._set_config(
            language='languages.EN',
            city=user_data.city,
            latitude=user_data.latitude,
            longitude=user_data.longitude,
            temp_scale='°F'
        )
        self._language = config.languages.EN
        self._city = user_data.city
        self._latitude = user_data.latitude
        self._longitude = user_data.longitude
        self._get_info()
        if config.temp_scale == '°C':
            self.change_temp_scale('f')
        self._temp_scale = '°F'

    def display_info(self) -> None:
        """
        Display the weather information.
        The weather information is set by the `self._get_info()` method.
        """
        print('{}: {},{},{}'.format(self._language['city'], self._city, self._state, self._country))
        print('{}: {}{}'.format(self._language['temp'], str(self._temp), self._temp_scale))
        print('{}'.format(self._language['status'][self._status]))
        print('{}: {}'.format(self._language['rain_probability'], self._rain_probability))
        print('{}: {}'.format(self._language['humidity'], self._humidity))

def main() -> None:
    weather = WeatherPy()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'lang':
            assert len(sys.argv) == 3, "No language was provided"
            weather.change_language(sys.argv[2])
        elif command == 'temp-scale':
            assert len(sys.argv) == 3, "No temperature scale was provided"
            weather.change_temp_scale(sys.argv[2])
        elif command == 'city':
            assert len(sys.argv) >= 3, "No city was provided"
            weather.change_city(' '.join(sys.argv[2:]))
        elif command == 'reset':
            assert len(sys.argv) == 2, "Command '<reset>' takes no argument"
            weather.reset()
        else:
            raise Exception(f'Unknown option: {sys.argv[1]}')

    weather.display_info()

if __name__ == '__main__':
    main()
