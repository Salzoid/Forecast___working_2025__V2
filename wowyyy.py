import requests
import csv
import matplotlib.pyplot as plt
import numpy as np
from tkinter import *
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

API_KEY = 'PUT YOUR KEY HERE'
BASE_URL = 'http://api.weatherstack.com/current'


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Forecast Pro")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f2f5")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()

        self.create_main_screen()

    def setup_styles(self):
        self.style.configure('TFrame', background="#f0f2f5")
        self.style.configure('TButton', font=('Segoe UI', 12), padding=10)
        self.style.configure('TLabel', background="#f0f2f5", font=('Segoe UI', 12))
        self.style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'))
        self.style.configure('Score.TLabel', font=('Segoe UI', 18, 'bold'))
        self.style.configure('Good.TLabel', foreground="#2ecc71")
        self.style.configure('Warning.TLabel', foreground="#e67e22")
        self.style.configure('Bad.TLabel', foreground="#e74c3c")
        self.style.configure('TEntry', font=('Segoe UI', 12), padding=8)

    def create_main_screen(self):
        self.clear_window()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=BOTH, padx=50, pady=50)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 30))

        ttk.Label(header_frame, text="Weather Forecast Pro", style='Header.TLabel').pack()

        # Search Frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=X, pady=20)

        self.location_entry = ttk.Entry(search_frame, font=('Segoe UI', 14))
        self.location_entry.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))

        search_btn = ttk.Button(search_frame, text="Search", command=self.search_weather)
        search_btn.pack(side=LEFT)

        # Weather Display Frame (initially empty)
        self.weather_frame = ttk.Frame(main_frame)
        self.weather_frame.pack(fill=BOTH, expand=True)

        # Sample recent searches
        recent_frame = ttk.Frame(main_frame)
        recent_frame.pack(fill=X, pady=20)

        ttk.Label(recent_frame, text="Recent searches:").pack(anchor='w')

        recent_searches = ["London", "New York", "Tokyo", "Paris"]
        for city in recent_searches:
            btn = ttk.Button(recent_frame, text=city, command=lambda c=city: self.set_location(c))
            btn.pack(side=LEFT, padx=5)

    def set_location(self, city):
        self.location_entry.delete(0, END)
        self.location_entry.insert(0, city)
        self.search_weather()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def search_weather(self):
        city = self.location_entry.get()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a location!")
            return

        try:
            data = self.get_weather_data(city)
            if 'error' in data:
                messagebox.showerror("Error", f"Error fetching data: {data['error']}")
                return

            weather = self.analyze_weather(data)
            self.display_weather(weather)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def get_weather_data(self, city):
        params = {'access_key': API_KEY, 'query': city}
        response = requests.get(BASE_URL, params=params)
        return response.json()

    def analyze_weather(self, data):
        if 'current' not in data:
            return {"error": data.get("error", "Unknown error")}

        current = data.get('current', {})
        location = data.get('location', {})

        return {
            'city': location.get('name', 'Unknown'),
            'temperature': current.get('temperature'),
            'feelslike': current.get('feelslike'),
            'description': current.get('weather_descriptions', ['Unknown'])[0],
            'humidity': current.get('humidity'),
            'wind_speed': current.get('wind_speed'),
            'visibility': current.get('visibility'),
            'pressure': current.get('pressure'),
            'uv_index': current.get('uv_index'),
            'localtime': location.get('localtime'),
            'is_day': 'yes' if current.get('is_day') == 'yes' else 'no'
        }

    def calculate_weather_score(self, weather):
        score = 100
        temp = weather['temperature']
        if temp is not None:
            if temp < 0 or temp > 35:
                score -= 40
            elif temp < 5 or temp > 30:
                score -= 30
            elif temp < 10 or temp > 25:
                score -= 15
            elif 15 <= temp <= 25:
                score += 10

        description = weather['description'].lower()
        bad_weather = ['rain', 'snow', 'thunder', 'shower', 'drizzle', 'sleet', 'blizzard']
        if any(bad in description for bad in bad_weather):
            score -= 30
        elif 'fog' in description or 'haze' in description:
            score -= 20
        elif 'cloud' in description:
            score -= 5

        wind = weather['wind_speed']
        if wind is not None:
            if wind > 40:
                score -= 30
            elif wind > 30:
                score -= 20
            elif wind > 20:
                score -= 10

        uv = weather['uv_index']
        if uv is not None:
            if uv >= 8:
                score -= 15
            elif uv >= 6:
                score -= 5

        humidity = weather['humidity']
        if humidity is not None:
            if humidity > 80 or humidity < 30:
                score -= 10

        pressure = weather['pressure']
        if pressure is not None:
            if pressure < 990 or pressure > 1030:
                score -= 15
            elif pressure < 1000 or pressure > 1020:
                score -= 5

        return max(0, min(100, score))

    def get_weather_icon(self, description):
        desc = description.lower()
        if 'sun' in desc or 'clear' in desc:
            return "☀️"
        elif 'rain' in desc:
            return "🌧️"
        elif 'cloud' in desc:
            return "☁️"
        elif 'snow' in desc:
            return "❄️"
        elif 'thunder' in desc:
            return "⚡"
        elif 'fog' in desc or 'haze' in desc:
            return "🌫️"
        else:
            return "🌈"

    def get_recommendations(self, weather):
        recommendations = []
        temp = weather['temperature']
        description = weather['description'].lower()
        wind = weather['wind_speed']
        uv = weather['uv_index']

        if 'rain' in description or 'shower' in description:
            recommendations.append(("☔", "Bring an umbrella"))
        if temp is not None and temp < 10:
            recommendations.append(("🧥", "Wear warm clothing"))
        if temp is not None and temp > 25:
            recommendations.append(("💧", "Stay hydrated"))
        if uv is not None and uv >= 6:
            recommendations.append(("🧴", "Use sun protection"))
        if wind is not None and wind > 20:
            recommendations.append(("🧣", "Windy — wear a scarf"))

        if all([temp is not None, 15 <= temp <= 25, wind is not None, wind < 20, 'rain' not in description]):
            recommendations.append(("🚶", "Perfect for a walk"))
        if temp is not None and temp > 20 and 'rain' not in description:
            recommendations.append(("🚴‍♀️", "Great for cycling"))
        if temp is not None and temp > 22 and uv is not None and uv < 8:
            recommendations.append(("🏖️", "Beach weather!"))
        if temp is not None and temp < 5:
            recommendations.append(("⛷️", "Try winter sports"))

        return recommendations

    def display_weather(self, weather):
        self.clear_window()

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

        # Header with back button
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20))

        back_btn = ttk.Button(header_frame, text="← Back", command=self.create_main_screen)
        back_btn.pack(side=LEFT)

        ttk.Label(header_frame, text=f"Weather in {weather['city']}", style='Header.TLabel').pack(side=LEFT, padx=10)

        # Weather data display
        data_frame = ttk.Frame(main_frame)
        data_frame.pack(fill=BOTH, expand=True)

        # Left column - Current conditions
        current_frame = ttk.Frame(data_frame)
        current_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10)

        # Current weather card
        card_frame = ttk.Frame(current_frame, relief='solid', borderwidth=1)
        card_frame.pack(fill=BOTH, expand=True, pady=10)

        # Weather icon and description
        icon = self.get_weather_icon(weather['description'])
        ttk.Label(card_frame, text=f"{icon} {weather['description']}", font=('Segoe UI', 24)).pack(pady=20)

        # Temperature display
        temp_frame = ttk.Frame(card_frame)
        temp_frame.pack(pady=10)

        ttk.Label(temp_frame, text=f"{weather['temperature']}°C", font=('Segoe UI', 48, 'bold')).pack(side=LEFT)
        feels_like = f"Feels like: {weather['feelslike']}°C"
        ttk.Label(temp_frame, text=feels_like, font=('Segoe UI', 14)).pack(side=LEFT, padx=10)

        # Weather score
        score = self.calculate_weather_score(weather)
        score_style = 'Good.TLabel' if score >= 70 else 'Warning.TLabel' if score >= 40 else 'Bad.TLabel'
        ttk.Label(card_frame, text=f"Weather Score: {score}/100", style=f'Score.{score_style}').pack(pady=10)

        # Right column - Detailed info
        details_frame = ttk.Frame(data_frame)
        details_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10)

        # Details grid
        detail_items = [
            ("💧 Humidity", f"{weather['humidity']}%"),
            ("🌬️ Wind", f"{weather['wind_speed']} km/h"),
            ("👁️ Visibility", f"{weather['visibility']} km"),
            ("📊 Pressure", f"{weather['pressure']} mb"),
            ("☀️ UV Index", weather['uv_index']),
            ("🕒 Local Time", weather['localtime'])
        ]

        for icon, value in detail_items:
            item_frame = ttk.Frame(details_frame)
            item_frame.pack(fill=X, pady=5)

            ttk.Label(item_frame, text=icon, font=('Segoe UI', 16)).pack(side=LEFT, padx=5)
            ttk.Label(item_frame, text=value, font=('Segoe UI', 14)).pack(side=LEFT)

        # Recommendations section
        rec_frame = ttk.Frame(main_frame)
        rec_frame.pack(fill=X, pady=20)

        ttk.Label(rec_frame, text="Recommendations", font=('Segoe UI', 16, 'bold')).pack(anchor='w')

        recommendations = self.get_recommendations(weather)
        for icon, text in recommendations:
            rec_item = ttk.Frame(rec_frame)
            rec_item.pack(fill=X, pady=5)

            ttk.Label(rec_item, text=icon, font=('Segoe UI', 16)).pack(side=LEFT, padx=10)
            ttk.Label(rec_item, text=text, font=('Segoe UI', 14)).pack(side=LEFT)

        # Save to CSV
        with open('weather_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['City', 'Temp (°C)', 'Feels Like (°C)', 'Condition',
                             'Humidity (%)', 'Wind (km/h)', 'Visibility (km)',
                             'Pressure (mb)', 'UV Index', 'Local Time', 'Score'])
            writer.writerow([weather['city'], weather['temperature'], weather['feelslike'],
                             weather['description'], weather['humidity'], weather['wind_speed'],
                             weather['visibility'], weather['pressure'], weather['uv_index'],
                             weather['localtime'], score])


if __name__ == "__main__":
    root = Tk()
    app = WeatherApp(root)
    root.mainloop()