
import asyncio
import aiohttp
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# Список кандидатов на проверку
CANDIDATES = {
    "🦁 Федеральные / Агентства": [
        ("TASS", "https://tass.ru/rss/v2.xml"),
        ("RIA Novosti", "https://ria.ru/export/rss2/archive/index.xml"),
        ("Interfax", "https://www.interfax.ru/rss.asp"),
        ("Rossiyskaya Gazeta", "https://rg.ru/xml/index.xml"),
        ("Regnum", "https://regnum.ru/rss"),
    ],
    "📺 ТВ и Видео-СМИ": [
        ("Vesti", "https://www.vesti.ru/vesti.rss"),
        ("1tv (Perviy)", "https://www.1tv.ru/rss/news"),
        ("NTV", "https://www.ntv.ru/exp/news.rss"),
        ("Ren TV", "https://ren.tv/rss"),
        ("TV Zvezda", "https://tvzvezda.ru/export/rss.xml"),
    ],
    "💼 Деловые и Аналитика": [
        ("RBC", "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"),
        ("Kommersant", "https://www.kommersant.ru/RSS/news.xml"),
        ("Vedomosti", "https://www.vedomosti.ru/rss/news"),
        ("Forbes Russia", "https://www.forbes.ru/feed"),
        ("Expert", "https://expert.ru/rss/"),
    ],
    "🌍 Интернет-издания / Порталы": [
        ("Lenta.ru", "https://lenta.ru/rss/news"),
        ("Gazeta.ru", "https://www.gazeta.ru/export/rss/lenta.xml"),
        ("MK (Moskovsky Komsomolets)", "https://www.mk.ru/rss/index.xml"),
        ("KP (Komsomolskaya Pravda)", "https://www.kp.ru/rss/nmain.xml"),
        ("AiF (Arg & Fakty)", "https://aif.ru/rss/news.php"),
        ("Fontanka (SPb)", "https://www.fontanka.ru/fontanka.rss"),
    ],
    "🗽 Независимые / Эмигрантские": [
        ("Meduza", "https://meduza.io/rss/all"),
        ("Mediazona", "https://zona.media/rss"),
        ("The Bell", "https://thebell.io/rss"),
        ("TV Rain (Dozhd)", "https://tvrain.tv/export/rss/all.xml"),
        ("Novaya Gazeta Europe", "https://novayagazeta.eu/feed/rss"),
        ("DW Russian", "https://rss.dw.com/xml/rss-ru-all"),
        ("BBC Russian", "https://feeds.bbci.co.uk/russian/rss.xml"),
    ],
    "💻 Технологии и IT": [
        ("Habr", "https://habr.com/ru/rss/all/all/"),
        ("3DNews", "https://www.3dnews.ru/news/rss/"),
        ("Hi-Tech Mail.ru", "https://hi-tech.mail.ru/news/feed/"),
        ("CNews", "https://www.cnews.ru/inc/rss/news.xml"),
        ("IXBT", "https://www.ixbt.com/export/news.rss"),
        ("Tproger", "https://tproger.ru/feed/"),
        ("Rozetked", "https://rozetked.me/turbo"),
    ],
    "⚽ Спорт": [
        ("Sports.ru", "https://www.sports.ru/rss/all_news.xml"),
        ("Championat", "https://www.championat.com/rss/news.xml"),
        ("Sport-Express", "https://www.sport-express.ru/services/materials/news/se/"),
        ("Sovetsky Sport", "https://www.sovsport.ru/rss/news"),
        ("Match TV", "https://matchtv.ru/export/rss.xml"),
    ],
    "🚗 Авто": [
        ("Autonews", "https://www.autonews.ru/rss"),
        ("Drive.ru", "https://www.drive.ru/rss/news"),
        ("Kolesa.ru", "https://www.kolesa.ru/rss"),
    ]
}

async def verify_feed(session, category, name, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                content = await response.text()
                # Простая проверка на наличие тегов RSS/XML
                if "<rss" in content or "<feed" in content or "<?xml" in content:
                    return (category, name, url, "✅ VERIFIED")
                else:
                    return (category, name, url, "⚠️ NOT_RSS (200 OK but bad content)")
            else:
                return (category, name, url, f"❌ FAILED ({response.status})")
    except Exception as e:
        return (category, name, url, f"❌ ERROR ({str(e)[:50]})")

async def main():
    print("🚀 Starting RSS Verification...\n")
    
    tasks = []
    async with aiohttp.ClientSession() as session:
        for cat, feeds in CANDIDATES.items():
            for name, url in feeds:
                tasks.append(verify_feed(session, cat, name, url))
        
        results = await asyncio.gather(*tasks)
        
        # Группировка результатов
        grouped = {}
        for res in results:
            cat, name, url, status = res
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append((name, url, status))
            
        # Вывод
        for cat, items in grouped.items():
            print(f"\n{cat}")
            print("=" * 60)
            for name, url, status in items:
                print(f"[{status}] {name:<25} {url}")

if __name__ == "__main__":
    asyncio.run(main())
