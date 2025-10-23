import os
import pygame
import math
import sys
import datetime
import requests
import threading
import time
import io
from SHT31 import SHT31

sht31 = SHT31()

API_KEY = ""
WEATHER_LOCATION = "Taipei"

# Initialize pygame
pygame.init()
size = (1280, 720)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Dashboard Display")
pygame.mouse.set_visible(False)

# Fonts
font_path = "ShareTechMono-Regular.ttf"
font_date = pygame.font.Font(font_path, 60)
font_time = pygame.font.Font(font_path, 220)   # Bigger time font
font_weather = pygame.font.Font(font_path, 40)

# Colors
BLACK = (10, 10, 30)
WHITE = (230, 230, 230)
SHADOW_COLOR = (30, 30, 60)

clock = pygame.time.Clock()

weekday_map = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thur",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}

# Weather data
weather_description = ""
weather_temp = ""
weather_icon_code = None
weather_icon_surface = None


def download_icon(icon_code):
    url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    try:
        response = requests.get(url, timeout=10)
        image_bytes = response.content
        image_file = io.BytesIO(image_bytes)
        image = pygame.image.load(image_file).convert_alpha()
        return image
    except Exception as e:
        print("Failed to download weather icon:", e)
        return None


def get_weather(city_name):
    global weather_description, weather_temp, WEATHER_LOCATION, weather_icon_code, weather_icon_surface
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("cod") == 200:
            WEATHER_LOCATION = data["name"]
            weather_description = data["weather"][0]["description"].capitalize()
            weather_temp = f"{data['main']['temp']}°C"
            icon_code = data["weather"][0]["icon"]
            if icon_code != weather_icon_code:
                weather_icon_code = icon_code
                weather_icon_surface = download_icon(icon_code)
        else:
            weather_description = "N/A"
            weather_temp = ""
            weather_icon_surface = None
    except Exception:
        weather_description = "Error"
        weather_temp = ""
        weather_icon_surface = None


def weather_update_loop():
    while True:
        get_weather(WEATHER_LOCATION)
        time.sleep(300)


threading.Thread(target=weather_update_loop, daemon=True).start()


def render_text_with_shadow(font, text, main_color, shadow_color):
    text_surface = font.render(text, True, main_color)
    shadow_surface = font.render(text, True, shadow_color)
    return text_surface, shadow_surface


start_time = time.time()
mytemp = 0
myhumi = 0
c = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if c % 500 == 0:
        sht31.write_command()
        result = sht31.read_data()
        mytemp = round(result['c'], 2)
        myhumi = round(result['h'], 2)
    c += 1

    now = datetime.datetime.now()
    weekday_str = weekday_map[now.weekday()]
    date_str = now.strftime("%Y/%m/%d ") + weekday_str
    time_str = now.strftime("%H:%M")
    temp_humi_str = f"Temp {mytemp}°C | Humi {myhumi}%"

    screen.fill(BLACK)

    # Render text
    date_text, date_shadow = render_text_with_shadow(font_date, date_str, WHITE, SHADOW_COLOR)
    time_text, time_shadow = render_text_with_shadow(font_time, time_str, WHITE, SHADOW_COLOR)
    location_text, location_shadow = render_text_with_shadow(font_weather, WEATHER_LOCATION, WHITE, SHADOW_COLOR)
    weather_text, weather_shadow = render_text_with_shadow(font_weather, f"{weather_description} {weather_temp}", WHITE, SHADOW_COLOR)
    temp_humi_text, temp_humi_shadow = render_text_with_shadow(font_weather, temp_humi_str, WHITE, SHADOW_COLOR)

    shadow_offset = (3, 3)

    # Positions (Dashboard layout)
    time_pos = (size[0] // 4, size[1] // 2)
    date_pos = (size[0] // 4, size[1] // 2 - 180)

    weather_pos = (size[0] * 3 // 4, size[1] // 4)
    location_pos = (size[0] * 3 // 4, size[1] // 4 - 60)
    temp_humi_pos = (size[0] * 3 // 4, size[1] * 3 // 4)

    # Draw shadows
    for surf, pos in [
        (date_shadow, date_pos),
        (time_shadow, time_pos),
        (location_shadow, location_pos),
        (weather_shadow, weather_pos),
        (temp_humi_shadow, temp_humi_pos),
    ]:
        rect = surf.get_rect(center=(pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]))
        screen.blit(surf, rect)

    # Draw main text
    for surf, pos in [
        (date_text, date_pos),
        (time_text, time_pos),
        (location_text, location_pos),
        (weather_text, weather_pos),
        (temp_humi_text, temp_humi_pos),
    ]:
        rect = surf.get_rect(center=pos)
        screen.blit(surf, rect)

    # Weather icon with animation
    if weather_icon_surface:
        elapsed = time.time() - start_time
        icon_float_offset = 5 * math.sin(elapsed * 2)
        icon_rect = weather_icon_surface.get_rect()
        icon_rect.center = (size[0] * 3 // 4, size[1] // 2 + int(icon_float_offset))
        screen.blit(weather_icon_surface, icon_rect)

    pygame.display.flip()
    clock.tick(30)

