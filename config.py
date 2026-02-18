"""Конфигурация погодного бота."""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = os.getenv("ADMIN_ID", "")  # Ваш Telegram ID для доступа

# OpenWeatherMap
OWM_API_KEY = os.getenv("OWM_API_KEY", "")
OWM_BASE = "https://api.openweathermap.org/data/2.5"
OWM_CURRENT_URL = f"{OWM_BASE}/weather"
OWM_FORECAST_URL = f"{OWM_BASE}/forecast"
OWM_AIR_URL = f"{OWM_BASE}/air_pollution"
OWM_GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
OWM_ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"


# Настройки по умолчанию
DEFAULT_UNITS = "metric"
DEFAULT_LANG = "ru"
MAX_FAVORITES = 5
THROTTLE_RATE = 1.0  # секунд между запросами
