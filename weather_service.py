import requests
import os

API_KEY = os.getenv("API_KEY")  # IMPORTANT: Replace with your OpenWeatherMap API key
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city_name):
    """
    Fetches weather data for a given city.
    """
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"  # Use metric units for temperature in Celsius
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None