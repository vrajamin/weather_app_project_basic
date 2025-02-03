import requests
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# ========================================
# Global Variables and Theme Colors Setup
# ========================================
PRIMARY = "#B886FC"
PRIMARY_VARIANT = "#3700B3"
SECONDARY = "#030AC5"
BACKGROUND = "#121212"
SURFACE = "#ff4b33"  # New color for vertical sections and button
ERROR = "#CF6679"
TEXT_ON_PRIMARY = "#000000"
TEXT_ON_SURFACE = "#FFFFFF"


# ========================================
# Utility Function for Color Blending
# ========================================
def blend_colors(color1, color2, alpha):
    def hex_to_rgb(hex_color):
        return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))

    def rgb_to_hex(rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    blended = tuple(int(rgb1[i] * alpha + rgb2[i] * (1 - alpha)) for i in range(3))
    return rgb_to_hex(blended)


BLENDED_SURFACE = blend_colors(SURFACE, BACKGROUND, 0.7)  # 70% opacity


# ========================================
# Functions for Retrieving Weather Data
# ========================================
def get_weather(api_key, city, state=None, country=None):
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    if state:
        location_query = f"{city},{state},{country}"
    else:
        location_query = f"{city},{country}"

    geo_params = {
        "q": location_query,
        "limit": 1,
        "appid": api_key
    }
    geo_response = requests.get(geo_url, params=geo_params)
    if geo_response.status_code != 200 or not geo_response.json():
        print(f"Geo API Response: {geo_response.status_code}, {geo_response.text}")
        return None, None

    geo_data = geo_response.json()[0]
    lat, lon = geo_data["lat"], geo_data["lon"]

    weather_params = {"lat": lat, "lon": lon, "appid": api_key, "units": "imperial"}
    forecast_params = {"lat": lat, "lon": lon, "appid": api_key, "units": "imperial"}

    weather_response = requests.get(weather_url, params=weather_params)
    forecast_response = requests.get(forecast_url, params=forecast_params)

    print(f"Weather API Response: {weather_response.status_code}, {weather_response.text}")

    if weather_response.status_code == 200 and forecast_response.status_code == 200:
        return weather_response.json(), forecast_response.json()
    else:
        return None, None


def get_location():
    api_key = "57963b8f9b3b55"  # Replace with your actual ipinfo.io API key
    try:
        response = requests.get(f"https://ipinfo.io/json?token={api_key}")
        response.raise_for_status()
        ip_info = response.json()
        print(f"IPInfo Response: {ip_info}")
        city = ip_info.get("city", "")
        country = ip_info.get("country", "")
        if not city or not country:
            print("Error: Unable to find city or country in the response.")
            return None, None
        return city, country
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location: {e}")
        return None, None


def format_location_input(location):
    if location.lower() == "auto":
        return "auto"

    parts = [part.strip() for part in location.split() if part.strip()]

    if len(parts) < 2:
        return None  # Invalid input

    if len(parts) == 2:
        return f"{parts[0]}, {parts[1]}"

    if len(parts) > 2:
        city = " ".join(parts[:-2])
        state = parts[-2]
        country = parts[-1]
        return f"{city}, {state}, {country}"

    return None  # Invalid input


# ========================================
# Functions for Displaying Weather in the GUI
# ========================================
def display_weather_in_gui(data, forecast_data):
    if not data or not forecast_data:
        output_label.config(text="Error: Unable to fetch weather data. Check your location and try again.",
                            font=("Helvetica", 12), fg=ERROR)
        return

    # Clear previous output
    for widget in output_frame.winfo_children():
        widget.destroy()

    # Today's Weather Section
    today_frame = tk.Frame(output_frame, bg=BLENDED_SURFACE, padx=10, pady=10, relief="solid", borderwidth=1)
    today_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    tk.Label(today_frame, text="Today's Weather", font=("Helvetica", 14, "bold"), bg=BLENDED_SURFACE,
             fg=TEXT_ON_SURFACE).pack(pady=5)
    tk.Label(today_frame, text=f"Location: {data['name']}", font=("Helvetica", 12), bg=BLENDED_SURFACE,
             fg=TEXT_ON_SURFACE).pack()
    tk.Label(today_frame, text=f"Temperature: {data['main']['temp']}°F", font=("Helvetica", 12), bg=BLENDED_SURFACE,
             fg=TEXT_ON_SURFACE).pack()
    tk.Label(today_frame, text=f"Weather: {data['weather'][0]['description'].title()}", font=("Helvetica", 12),
             bg=BLENDED_SURFACE, fg=TEXT_ON_SURFACE).pack()
    tk.Label(today_frame, text=f"Humidity: {data['main']['humidity']}%", font=("Helvetica", 12), bg=BLENDED_SURFACE,
             fg=TEXT_ON_SURFACE).pack()
    tk.Label(today_frame, text=f"Wind: {data['wind']['speed']} mph", font=("Helvetica", 12), bg=BLENDED_SURFACE,
             fg=TEXT_ON_SURFACE).pack()

    # 5-Day Forecast Sections
    for i, forecast in enumerate(forecast_data["list"][:5], start=1):
        forecast_frame = tk.Frame(output_frame, bg=BLENDED_SURFACE, padx=10, pady=10, relief="solid", borderwidth=1)
        forecast_frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)

        date = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%a, %b %d")
        tk.Label(forecast_frame, text=date, font=("Helvetica", 14, "bold"), bg=BLENDED_SURFACE,
                 fg=TEXT_ON_SURFACE).pack(pady=5)
        tk.Label(forecast_frame, text=f"Temp: {forecast['main']['temp']}°F", font=("Helvetica", 12), bg=BLENDED_SURFACE,
                 fg=TEXT_ON_SURFACE).pack()
        tk.Label(forecast_frame, text=f"Weather: {forecast['weather'][0]['description'].title()}",
                 font=("Helvetica", 12), bg=BLENDED_SURFACE, fg=TEXT_ON_SURFACE).pack()
        tk.Label(forecast_frame, text=f"Humidity: {forecast['main']['humidity']}%", font=("Helvetica", 12),
                 bg=BLENDED_SURFACE, fg=TEXT_ON_SURFACE).pack()
        tk.Label(forecast_frame, text=f"Wind: {forecast['wind']['speed']} mph", font=("Helvetica", 12),
                 bg=BLENDED_SURFACE, fg=TEXT_ON_SURFACE).pack()


# ========================================
# Function to Show Information about the Program
# ========================================
def show_info():
    info_text = (
        "The Product Manager Accelerator Program is designed to support PM professionals through every stage of their careers. "
        "From students looking for entry-level jobs to Directors looking to take on a leadership role, our program has helped over hundreds "
        "of students fulfill their career aspirations.\n\n"
        "Our Product Manager Accelerator community are ambitious and committed. Through our program they have learnt, honed and developed new PM "
        "and leadership skills, giving them a strong foundation for their future endeavors."
    )
    messagebox.showinfo("Information", info_text)


# ========================================
# Function to Fetch Weather Data and Update the GUI
# ========================================
def fetch_weather():
    location = entry.get().strip()

    if location.lower() == "auto":
        city, country = get_location()
        print(f"Detected Location: {city}, {country}")
        if not city or not country:
            output_label.config(text="Error: Unable to determine your location.", font=("Helvetica", 12), fg=ERROR)
            return
        state = None
    else:
        formatted_location = format_location_input(location)

        if not formatted_location:
            output_label.config(text="Error: Enter city name, 2-letter state code, 2-letter country code",
                                font=("Helvetica", 16), fg=ERROR)
            return

        parts = formatted_location.split(",")
        city = parts[0].strip()
        state = parts[1].strip() if len(parts) == 3 else None
        country = parts[-1].strip()

    weather_data, forecast_data = get_weather(api_key, city, state, country)
    display_weather_in_gui(weather_data, forecast_data)


# ========================================
# Main GUI Setup and Application Loop
# ========================================
root = tk.Tk()
root.title("Weather App - by Vraj Amin")
root.geometry("1200x400")
root.configure(bg=BACKGROUND)

api_key = "ae53373282fddf6392a2ad05266c48a2"  # Replace with your actual OpenWeatherMap API key

header_frame = tk.Frame(root, bg=PRIMARY, padx=10, pady=10)
header_frame.pack(fill="x")
tk.Label(header_frame, text="Weather App - by Vraj Amin", font=("Helvetica", 20, "bold"), bg=PRIMARY,
         fg=TEXT_ON_PRIMARY).pack(side="left")
tk.Button(header_frame, text="Info", command=show_info, font=("Helvetica", 12), bg=PRIMARY_VARIANT,
          fg=TEXT_ON_PRIMARY).pack(side="right")

input_frame = tk.Frame(root, bg=BACKGROUND, padx=20, pady=10)
input_frame.pack(fill="x")

tk.Label(input_frame, text="Enter Location (City, State, Country) or 'auto':", font=("Helvetica", 12), bg=BACKGROUND,
         fg=TEXT_ON_SURFACE).grid(row=0, column=0, sticky="w")
entry = tk.Entry(input_frame, font=("Helvetica", 12), width=30)
entry.grid(row=1, column=0, pady=5, sticky="w")

tk.Button(input_frame, text="Get Weather", font=("Helvetica", 12), command=fetch_weather, bg=SURFACE,
          fg=TEXT_ON_PRIMARY, padx=10, pady=5).grid(row=1, column=1, padx=10)

output_frame = tk.Frame(root, bg=BACKGROUND, padx=10, pady=10)
output_frame.pack(fill="both", expand=True)
for i in range(6):
    output_frame.columnconfigure(i, weight=1)

output_label = tk.Label(output_frame, text="", font=("Helvetica", 12), bg=BACKGROUND, fg=TEXT_ON_SURFACE)
output_label.grid(row=0, column=0, columnspan=6)

root.mainloop()
