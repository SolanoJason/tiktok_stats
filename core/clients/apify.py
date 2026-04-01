from apify_client import ApifyClientAsync
from core.settings import settings

client = ApifyClientAsync(token=settings.APIFY_API_KEY)

tiktok_actor = client.actor(settings.APIFY_TIKTOK_SCRAPER_ACTOR_ID)