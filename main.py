from dotenv import load_dotenv
import os
import requests
from twilio.rest import Client


load_dotenv()

MY_LAT = float(os.getenv('LATITUDE'))
MY_LONG = float(os.getenv('LONGITUDE'))
OPEN_WEATHER_API = os.getenv('OPEN_WEATHER_MAP_API_V2')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TWILIO_RECEIPENT = os.getenv('TWILIO_RECEIPENT')


def open_weather():
    """
    Use the OpenWeatherMap API to determine the weather in a location
    Send text via Twilio giving forecast for next 24 hours
    :return: None
    """
    url = "https://api.openweathermap.org/data/2.5/onecall"
    parameters = {
        "lat": MY_LAT,
        "lon": MY_LONG,
        "appid": OPEN_WEATHER_API,
        "exclude": "current,minutely,daily",
        "units": "imperial"
    }
    response = requests.get(url=url, params=parameters)

    response.raise_for_status()

    weather_data = response.json()

    sky_condition_set = set()
    temp_high = -1000
    temp_low = 1000
    humidity_high = 0
    humidity_low = 100
    wind_speed_high = 0
    wind_speed_low = 100

    for hour in weather_data['hourly'][:24]:
        weather_id = hour['weather'][0]['id']
        if weather_id < 800:
            sky_condition = str(hour['weather'][0]['description']).title()
        else:
            sky_condition = str(hour['weather'][0]['main']).title()
        sky_condition_set.add(sky_condition)

        temp = int(round(hour['temp'], 0))
        if temp > temp_high:
            temp_high = temp
        if temp < temp_low:
            temp_low = temp

        humidity = hour['humidity']
        if humidity > humidity_high:
            humidity_high = humidity
        if humidity < humidity_low:
            humidity_low = humidity

        wind_speed = int(round(hour['wind_speed'], 0))
        if wind_speed > wind_speed_high:
            wind_speed_high = wind_speed
        if wind_speed < wind_speed_low:
            wind_speed_low = wind_speed

    upcoming_sky_conditions = ""
    for sky in sky_condition_set:
        upcoming_sky_conditions += f'{sky}, '

    if upcoming_sky_conditions[-2] == ",":
        upcoming_sky_conditions = upcoming_sky_conditions[:-2]

    message = f"Forecast for next 24 hours:\n\n" \
              f"High: {temp_high}\n" \
              f"Low: {temp_low}\n" \
              f"Humidity Range: {humidity_low}% - {humidity_high}%\n" \
              f"Wind Speed Range: {wind_speed_low} - {wind_speed_high} mph\n" \
              f"Skies: {upcoming_sky_conditions}"
    send_text(message)

    return


def send_text(message):
    """
    Use Twilio message service to send SMS
    :param message: str
    :return: message.sid
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=TWILIO_RECEIPENT
    )

    return message.sid


if __name__ == "__main__":
    open_weather()

