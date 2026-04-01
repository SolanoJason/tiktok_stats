import schedule
import time as time_module
from sqlalchemy import select
from core.database import SyncSessionFactory, load_models
from apps.tiktok.models import Video, RawData, VideoStats
from core.clients import apify_tiktok_actor_sync, apify_client_sync

load_models()

def scrape_tiktok():
    with SyncSessionFactory() as session:
        stmt = select(Video)
        videos = session.scalars(stmt).all()
        run_input = {
            "postURLs": [video.url for video in videos]
        }
        run = apify_tiktok_actor_sync.call(run_input=run_input)
        for item in apify_client_sync.dataset(run["defaultDatasetId"]).iterate_items():
            url = item["webVideoUrl"]
            video = next(video for video in videos if video.url == item["webVideoUrl"])
            raw_data = RawData(data=item)
            session.add(raw_data)

            video_stats = VideoStats(
                video=video,
                raw_data=raw_data,
                diggs=item["diggCount"],
                shares=item["shareCount"],
                plays=item["playCount"],
                collects=item["collectCount"],
                comments=item["commentCount"],
                reposts=item["repostCount"],
            )

            video.last_stat = video_stats

            session.add(video_stats)
            session.commit()
        
    print("Scraping TikTok...")

schedule.every().day.at("18:00", "America/Lima").do(scrape_tiktok)

while True:
    print("Waiting for next job...")
    schedule.run_pending()
    time_module.sleep(20)