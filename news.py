"""Сервис новостей на базе RSS-агрегатора."""

import logging
import asyncio
from rss_service import RSSService

log = logging.getLogger(__name__)

# 📰 Список отборных RSS-каналов (News Engine 2.0)
RSS_CHANNELS = {
    # 🌍 Главные новости (Федеральные + СМИ)
    "general": [
        ("Lenta.ru", "https://lenta.ru/rss/news"),
        ("TASS", "https://tass.ru/rss/v2.xml"),
        ("RIA", "https://ria.ru/export/rss2/archive/index.xml"),
        ("Interfax", "https://www.interfax.ru/rss.asp"),
        ("Rossiyskaya Gazeta", "https://rg.ru/xml/index.xml"),
        ("Regnum", "https://regnum.ru/rss"),
        ("Moskovsky Komsomolets", "https://www.mk.ru/rss/index.xml"),
        ("AiF", "https://aif.ru/rss/news.php"),
        ("TV Zvezda", "https://tvzvezda.ru/export/rss.xml"),
    ],
    # 💻 IT и Технологии
    "technology": [
        ("Habr", "https://habr.com/ru/rss/all/all/"),
        ("3DNews", "https://www.3dnews.ru/news/rss/"),
        ("CNews", "https://www.cnews.ru/inc/rss/news.xml"),
        ("Rozetked", "https://rozetked.me/turbo"),
        ("Tproger", "https://tproger.ru/feed/"),
    ],
    # 💰 Бизнес и Финансы
    "business": [
        ("RBC", "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"),
        ("Kommersant", "https://www.kommersant.ru/RSS/news.xml"),
        ("Vedomosti", "https://www.vedomosti.ru/rss/news"),
    ],
    # ⚽ Спорт
    "sports": [
        ("Sports.ru", "https://www.sports.ru/rss/all_news.xml"),
        ("Sport-Express", "https://www.sport-express.ru/services/materials/news/se/"),
    ],
    # 🚗 Авто (New!)
    "auto": [
        ("Kolesa.ru", "https://www.kolesa.ru/rss"),
    ],
    # 🎬 Культура (Legacy)
    "entertainment": [
        ("Kino.mail", "https://kino.mail.ru/rss"),
    ],
    # 🧬 Наука (Legacy)
    "science": [
        ("Naked Science", "https://naked-science.ru/feed/"),
    ],
    # 💊 Здоровье (Legacy)
    "health": [
        ("Lifehacker (Здоровье)", "https://lifehacker.ru/tag/zdorove/feed/"),
    ]
}

class NewsService:
    def __init__(self):
        self.rss = RSSService()

    async def close(self):
        await self.rss.close()

    async def get_news_by_category(self, category: str) -> dict:
        """
        SMART MIXER: Получает новости из ВСЕХ источников категории параллельно,
        смешивает их и сортирует по свежести.
        """
        sources = RSS_CHANNELS.get(category, RSS_CHANNELS["general"])
        
        tasks = []
        for name, url in sources:
            tasks.append(self._fetch_source(name, url))
            
        results = await asyncio.gather(*tasks)
        
        # Смешиваем все результаты в одну кучу
        all_articles = []
        for res in results:
            if res:
                all_articles.extend(res)
                
        if not all_articles:
            return None
            
        # Сортируем по времени (свежие сверху)
        # x["timestamp"] - это float, чем больше, тем новее
        all_articles.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        # Убираем дубликаты (по заголовкам)
        seen_titles = set()
        unique_articles = []
        for art in all_articles:
            # Простая нормализация заголовка для сравнения
            t = art["title"].lower().strip()
            if t not in seen_titles:
                seen_titles.add(t)
                unique_articles.append(art)
                
        return {
            "source": "Smart Mix 🧠",  # Источник теперь смешанный
            "articles": unique_articles[:7] # Берем топ-7
        }

    async def _fetch_source(self, name: str, url: str) -> list | None:
        """Вспомогательный метод для получения и пометки новостей от конкретного источника."""
        log.info(f"📰 Запрос к {name}...")
        data = await self.rss.fetch_feed(url)
        if data:
            # Добавляем метку источника прямо в статью
            for item in data:
                item["source_name"] = name
            return data
        return None

    def format_news(self, data: dict, category_title: str) -> str:
        """Форматирует новости в красивый текст."""
        if not data or not data.get("articles"):
            return "❌ Не удалось получить новости по этой категории (все источники молчат). 😔"

        articles = data["articles"]
        
        lines = [f"<b>{category_title}</b>", ""]
        
        for i, item in enumerate(articles, 1):
            title = item.get("title", "Без заголовка")
            link = item.get("link", "#")
            src = item.get("source_name", "RSS")
            
            # Очистка заголовка
            title = title.replace("\xa0", " ").strip()
            
            lines.append(f"{i}. <a href='{link}'>{title}</a>")
            lines.append(f"   <i>Источник: {src}</i>") # Теперь пишем источник под каждой новостью
            lines.append("")
        
        return "\n".join(lines)
