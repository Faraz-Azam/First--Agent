import google.generativeai as genai
import re
import requests
import os
from dotenv import load_dotenv

# Load API key from .env file (SAFE - not visible in code)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: API key not found in .env file!")
    exit()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3.6-flash")

# ==================== MATH FUNCTIONS ====================
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b): return "Cannot divide by zero" if b == 0 else a / b

# ==================== WEATHER FUNCTION ====================
def get_weather(city_name):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        geo_data = requests.get(geo_url).json()

        if not geo_data.get('results'):
            return f"❌ City '{city_name}' not found! Try a simpler name."

        city_info = geo_data['results'][0]
        lat, lon = city_info['latitude'], city_info['longitude']
        country = city_info.get('country', 'Unknown')

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m&timezone=auto"
        current = requests.get(weather_url).json()['current']

        codes = {0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Foggy",48:"Foggy",
                 51:"Light drizzle",61:"Slight rain",63:"Moderate rain",65:"Heavy rain",
                 80:"Rain showers",95:"Thunderstorm"}
        desc = codes.get(current['weather_code'], "Unknown")

        return f"""
🌍 Weather in {city_info['name']}, {country}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌡️  Temperature: {current['temperature_2m']}°C
☁️  Condition: {desc}
💧 Humidity: {current['relative_humidity_2m']}%
💨 Wind: {current['wind_speed_10m']} km/h
"""
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==================== HELPERS ====================
def extract_numbers(text):
    return [float(n) for n in re.findall(r'\d+\.?\d*', text)]

def extract_location(text):
    remove_words = ['weather','what','whats',"what's",'is','the','in','of','tell','me','please',
                     'show','get','temperature','condition','like','how','current','right','now',
                     'till','until','today','currently','can','you']
    words = [w.strip('?.,!') for w in text.lower().split()]
    location_words = [w for w in words if w not in remove_words and len(w) > 1]
    return ' '.join(location_words) if location_words else None

def identify_operation(text):
    t = text.lower()
    if any(w in t for w in ['plus','add','sum']): return "add"
    if any(w in t for w in ['minus','subtract']): return "subtract"
    if any(w in t for w in ['multiply','times','product']): return "multiply"
    if any(w in t for w in ['divide','divided','division']): return "divide"
    if any(w in t for w in ['weather','temperature','forecast','rain','sunny','hot','cold','cloudy']): return "weather"
    return None

# ==================== MAIN PROCESSOR ====================
def process_command(user_input):
    operation = identify_operation(user_input)

    if operation in ["add", "subtract", "multiply", "divide"]:
        numbers = extract_numbers(user_input)
        if len(numbers) >= 2:
            a, b = numbers[0], numbers[1]
            result = {"add": add, "subtract": subtract, "multiply": multiply, "divide": divide}[operation](a, b)
            print(f"✅ Result: {result}")
        else:
            print("❌ Need two numbers!")

    elif operation == "weather":
        location = extract_location(user_input)
        if location:
            print(get_weather(location))
        else:
            print("❌ Which city? Say: 'Weather in Paris'")

    else:
        print("🤖 AI:", model.generate_content(user_input).text)

# ==================== RUN ====================
if __name__ == "__main__":
    print("Type 'exit' to quit\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        if user_input:
            process_command(user_input)
            print()