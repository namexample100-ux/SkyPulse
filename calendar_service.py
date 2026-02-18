"""Сервис для работы с календарем: праздники и время."""
import aiohttp
import logging
from datetime import datetime, timezone, timedelta

log = logging.getLogger(__name__)

class CalendarService:
    def __init__(self):
        self.holiday_url = "https://date.nager.at/api/v3/PublicHolidays"
        self.session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_holidays(self, country_code: str = "RU") -> list[dict] | None:
        """Получить список праздников на текущий год."""
        try:
            year = datetime.now().year
            session = await self._get_session()
            async with session.get(f"{self.holiday_url}/{year}/{country_code}") as response:
                if response.status == 200:
                    return await response.json()
                log.error(f"Ошибка HolidayAPI: {response.status}")
                return None
        except Exception as e:
            log.error(f"Ошибка при запросе HolidayAPI: {e}")
            return None

    def get_time_in_timezone(self, offset_seconds: int) -> str:
        """Получить текущее время на основе смещения в секундах."""
        tz = timezone(timedelta(seconds=offset_seconds))
        now = datetime.now(tz=tz)
        return now.strftime("%H:%M:%S")

    def format_holidays(self, holidays: list[dict]) -> str:
        """Форматирование ближайших праздников."""
        if not holidays:
            return "🗓 Праздники не найдены."

        now = datetime.now().date()
        upcoming = [h for h in holidays if datetime.strptime(h['date'], '%Y-%m-%d').date() >= now][:5]

        if not upcoming:
            return "🗓 На ближайшее время праздников не запланировано."

        text = "🗓 <b>Календарный Пульс: Праздники</b>\n\n"
        for h in upcoming:
            date_str = datetime.strptime(h['date'], '%Y-%m-%d').strftime('%d.%m')
            name = h.get('localName', h.get('name'))
            text += f"▪️ <b>{date_str}</b> — {name}\n"
        
        return text

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
