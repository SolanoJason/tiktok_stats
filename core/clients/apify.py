from apify_client import ApifyClientAsync, ApifyClient
from core.settings import settings

client = ApifyClientAsync(token=settings.APIFY_API_KEY)

client_sync = ApifyClient(token=settings.APIFY_API_KEY)

tiktok_actor = client.actor(settings.APIFY_TIKTOK_SCRAPER_ACTOR_ID)

tiktok_actor_sync = client_sync.actor(settings.APIFY_TIKTOK_SCRAPER_ACTOR_ID)