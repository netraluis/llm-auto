import json
import httpx
from typing import Dict, Any
from config import Config


async def get_current_weather(arguments: Dict[str, Any]) -> str:
    """
    Obtiene el clima actual de una ubicación usando WeatherAPI.com
    
    Args:
        arguments: Dict con 'location' (str) - ciudad o ubicación a consultar
        
    Returns:
        JSON string con los datos del clima
    """
    location = arguments.get("location", "")
    
    if not Config.WEATHER_API_KEY:
        # Fallback a simulación si no hay API key
        return json.dumps({
            "location": location,
            "temperature": "22°C",
            "condition": "Sunny",
            "humidity": "65%",
            "note": "Using simulated data - no API key configured"
        })
    
    try:
        # Llamada real a WeatherAPI.com
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api.weatherapi.com/v1/current.json",
                params={
                    "key": Config.WEATHER_API_KEY,
                    "q": location,
                    "aqi": "no"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return json.dumps({
                    "location": f"{data['location']['name']}, {data['location']['country']}",
                    "temperature": f"{data['current']['temp_c']}°C",
                    "condition": data['current']['condition']['text'],
                    "humidity": f"{data['current']['humidity']}%",
                    "wind_kph": data['current']['wind_kph'],
                    "feels_like": f"{data['current']['feelslike_c']}°C"
                })
            else:
                return json.dumps({
                    "error": f"Weather API error: {response.status_code}",
                    "location": location
                })
                
    except Exception as e:
        return json.dumps({
            "error": f"Failed to fetch weather: {str(e)}",
            "location": location
        })

