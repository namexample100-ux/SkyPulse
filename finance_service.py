"""Сервис для получения курсов валют через ExchangeRate-API."""
import aiohttp
import logging
import time

log = logging.getLogger(__name__)

class FinanceService:
    def __init__(self):
        self.base_url = "https://open.er-api.com/v6/latest/USD"
        self.session: aiohttp.ClientSession | None = None
        self._cache = {}
        self._cache_time = 0
        self._ttl = 3600  # 1 час кэша

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_rates(self) -> dict | None:
        """Получить актуальные курсы валют с кэшированием."""
        now = time.time()
        if self._cache and (now - self._cache_time < self._ttl):
            return self._cache

        try:
            session = await self._get_session()
            async with session.get(self.base_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("result") == "success":
                        self._cache = data.get("rates", {})
                        self._cache_time = now
                        return self._cache
                log.error(f"Ошибка FinanceAPI: {response.status}")
                return None
        except Exception as e:
            log.error(f"Ошибка при запросе FinanceAPI: {e}")
            return None

    def format_rates(self, rates: dict) -> str:
        """Форматирование курсов валют в текст для Telegram."""
        if not rates:
            return "📈 Не удалось получить свежие котировки."

        rub_rate = rates.get("RUB")
        if not rub_rate:
            return "📈 Ошибка: курс рубля не найден."

        # Рассчитываем курсы к рублю
        # ExchangeRate-API по умолчанию дает базу в USD
        usd_rub = rub_rate
        eur_usd = rates.get("EUR", 0)
        cny_usd = rates.get("CNY", 0)
        
        eur_rub = usd_rub / eur_usd if eur_usd else 0
        cny_rub = usd_rub / cny_usd if cny_usd else 0

        text = "📈 <b>Финансовый Пульс: Курсы валют</b>\n\n"
        text += f"💵 <b>USD:</b> <code>{usd_rub:.2f} ₽</code>\n"
        text += f"💶 <b>EUR:</b> <code>{eur_rub:.2f} ₽</code>\n"
        text += f"🇨🇳 <b>CNY:</b> <code>{cny_rub:.2f} ₽</code>\n\n"
        
        text += f"<i>Обновлено: {datetime.now().strftime('%H:%M')}</i>\n"
        text += "<i>Данные предоставлены ExchangeRate-API</i>"
        return text

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

from datetime import datetime
