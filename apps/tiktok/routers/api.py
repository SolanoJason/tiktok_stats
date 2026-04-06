from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from sqlalchemy import Date, func, select
from sqlalchemy.orm import aliased

from apps.tiktok.models import Video, VideoStats, RawData
from apps.tiktok.utils import extract_tiktok_username
from core.database.dependencies import SessionDep
from core.clients import apify_tiktok_actor, apify_client

router = APIRouter(prefix="/tiktok", tags=["tiktok"])


async def get_campaign_history_data(session: SessionDep) -> list[dict]:
    date_expr = func.timezone("America/Lima", VideoStats.created_at).cast(Date)
    rn_expr = func.row_number().over(
        partition_by=(Video.id, date_expr),
        order_by=VideoStats.created_at.desc(),
    )

    subquery = (
        select(Video, VideoStats, rn_expr.label("rn"))
        .join(VideoStats, Video.id == VideoStats.video_id)
        .subquery()
    )

    v_alias = aliased(Video, subquery)
    vs_alias = aliased(VideoStats, subquery)

    stmt = (
        select(v_alias, vs_alias)
        .select_from(subquery)
        .where(subquery.c.rn == 1)
        .order_by(vs_alias.created_at.asc())
    )

    results = (await session.execute(stmt)).all()

    return [
        {
            "username": extract_tiktok_username(video.url),
            "url": video.url,
            "date_of_stats": stats.created_at.astimezone(ZoneInfo("America/Lima")).date().isoformat(),
            "diggs": stats.diggs,
            "shares": stats.shares,
            "plays": stats.plays,
            "collects": stats.collects,
            "comments": stats.comments,
            "reposts": stats.reposts,
        }
        for video, stats in results
    ]


@router.get("/campaign/history")
async def campaign_history(session: SessionDep):
    return await get_campaign_history_data(session)


@router.post("/update-videos")
async def update_videos(session: SessionDep):
    stmt = select(Video)
    result = await session.execute(stmt)
    videos = result.scalars().all()
    
    if not videos:
        raise HTTPException(status_code=404, detail="No videos to update")
    
    run_input = {
        "postURLs": [video.url for video in videos]
    }
    
    run = await apify_tiktok_actor.call(run_input=run_input)

    if run is None:
        raise HTTPException(status_code=500, detail="Failed to scrape videos")
    
    dataset = apify_client.dataset(run["defaultDatasetId"])
    async for item in dataset.iterate_items():
        url = item["webVideoUrl"]
        video = next(video for video in videos if video.url == url)
        
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
    
    await session.commit()
    
    return {"message": "Videos updated successfully"}
