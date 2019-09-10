import urllib.request
import json


def check_weather(city):
    """Function that finds the current weather info for Coventry"""
    # fetches the JSON data from API
    with urllib.request.urlopen(
            'http://api.apixu.com/v1/current.json?key=da55ba7713f54de3a28113313172211&q=' + city) as webPage:
        raw_data = webPage.read()

    # uses JSON library to decode data from API
    raw_data_json = json.loads(raw_data.decode("utf-8"))

    try:  # Gets current temperature from JSON element
        current_temp = str(raw_data_json["current"]["temp_c"])
    except KeyError:  # catches error where no element available
        current_temp = 'No temperature available'

    try:  # Gets current weather condition from JSON element
        current_condition = str(raw_data_json["current"]["condition"]["text"])
    except KeyError:  # catches error where no element available
        current_condition = 'No temperature available'

    return current_temp, current_condition
