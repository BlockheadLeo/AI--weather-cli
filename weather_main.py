import requests
import argparse
from weather_codes import WEATHER_CODES 

def get_weather_data(lat, lon, days):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon, 
        "daily": "temperature_2m_mean,precipitation_probability_mean,weather_code",
        "forecast_days": days,
        "timezone": "auto",
    }


    try:
        response = requests.get(url, params=params)
        print(response.url)
        response.raise_for_status()
        return response.json()  
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
    

def convert_to_lat_lon(city, country=None):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 10,
        "language": "en",
        "format": "json",
    }

    try: 
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'results' not in data or len(data['results']) == 0:
            raise ValueError("No city found")
        
        if country:
            for result in data['results']:
                if result['country'].casefold() == country.casefold(): 
                    return (
                        result['latitude'], 
                        result['longitude'],
                        result['name'],
                        result['country'],
                        )

            raise ValueError(f"No {city} found in the {country}")    

        result = data['results'][0]    
        return (
            result['latitude'], 
            result['longitude'],
            result['name'],
            result['country'],
        )
       
            
    except requests.RequestException as e:
        print(f"Error fetching geocoding data: {e}")
        return None


def display_weather_data(location_name, country, weather_data):
    daily = weather_data['daily']
    print(f"Weather Forecast for {location_name}, {country}:")

    for i in range(len(daily['time'])):
        date  = daily['time'][i]
        temperature = daily['temperature_2m_mean'][i]
        precipitation = daily['precipitation_probability_mean'][i]
        code = daily['weather_code'][i]
        weather_description = WEATHER_CODES.get(code, "Unknown weather condition")

        print(f"{date}")
        print(f"{temperature}°C, Precipitation Probability: {precipitation}%")
        print(f"Condition: {weather_description}")
        

    

def main():
    parser = argparse.ArgumentParser(description="Get weather data for a specifiied city")
    parser.add_argument("city", type=str, help="City name")
    parser.add_argument("--country", type=str, default=None, help="Country name (optional)")
    parser.add_argument("--days", type=int, default=7, help="Number of days required for the forecast (default: 7)")
    args = parser.parse_args()

    if args.days < 1 or args.days > 16:
        parser.error("Number of days must be between 1 and 16")

    
    location = convert_to_lat_lon(args.city, args.country)
    if location is None:
        return

    lat, lon, location_name, country = location 
    
    weather_data = get_weather_data(lat, lon, args.days)
    if weather_data is None:
        return

    display_weather_data(location_name, country, weather_data)
    


if __name__ == "__main__":
    main()
