from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import Date, func, select
from sqlalchemy.orm import aliased, selectinload

from apps.tiktok.models import Video, VideoStats, RawData
from apps.tiktok.utils import extract_tiktok_username, validate_tiktok_url, normalize_tiktok_url
from core.database.dependencies import SessionDep
from core.clients import apify_tiktok_actor, apify_client

router = APIRouter(prefix="/tiktok", tags=["tiktok"])


class CreateVideoRequest(BaseModel):
    url: str


class VideoStatResponse(BaseModel):
    id: int
    diggs: int
    shares: int
    plays: int
    collects: int
    comments: int
    reposts: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class VideoResponse(BaseModel):
    id: int
    url: str
    last_stat: VideoStatResponse | None = None
    
    class Config:
        from_attributes = True


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


@router.post("/videos", response_model=VideoResponse)
async def create_video(request: CreateVideoRequest, session: SessionDep):
    """
    Creates a new video from a TikTok URL.
    Validates that the URL is a valid TikTok video URL, normalizes it, scrapes the video stats,
    and stores both the Video and its initial VideoStats.
    """
    url = request.url.strip()
    
    # Validate that it's a valid TikTok URL
    if not validate_tiktok_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid TikTok URL. URL must contain a username (@user) and video ID."
        )
    
    # Normalize the URL
    normalized_url = normalize_tiktok_url(url)
    
    # Check if video already exists
    stmt = select(Video).where(Video.url == normalized_url)
    existing_video = (await session.execute(stmt)).scalars().first()
    
    if existing_video:
        raise HTTPException(
            status_code=409,
            detail="Video already exists in the database"
        )
    
    # Scrape the video stats immediately
    run_input = {"postURLs": [normalized_url]}
    run = await apify_tiktok_actor.call(run_input=run_input)

    if run is None:
        raise HTTPException(status_code=500, detail="Failed to scrape video stats")

    dataset = apify_client.dataset(run["defaultDatasetId"])
    item = None
    async for scraped in dataset.iterate_items():
        if item is None:
            item = scraped
        if scraped.get("webVideoUrl") == normalized_url:
            item = scraped
            break

    if item is None:
        raise HTTPException(status_code=500, detail="Scraping completed but no video data was found")

    # Create and save the video with its initial stats
    video = Video(url=normalized_url)
    session.add(video)
    await session.flush()

    raw_data = RawData(data=item)
    session.add(raw_data)

    video_stats = VideoStats(
        video=video,
        raw_data=raw_data,
        diggs=item.get("diggCount", 0),
        shares=item.get("shareCount", 0),
        plays=item.get("playCount", 0),
        collects=item.get("collectCount", 0),
        comments=item.get("commentCount", 0),
        reposts=item.get("repostCount", 0),
    )

    video.last_stat = video_stats
    session.add(video_stats)
    await session.commit()
    await session.refresh(video)
    
    return VideoResponse(
        id=video.id,
        url=video.url,
        last_stat=VideoStatResponse(
            id=video_stats.id,
            diggs=video_stats.diggs,
            shares=video_stats.shares,
            plays=video_stats.plays,
            collects=video_stats.collects,
            comments=video_stats.comments,
            reposts=video_stats.reposts,
            created_at=video_stats.created_at,
        ),
    )


@router.get("/videos", response_model=list[VideoResponse])
async def list_videos(session: SessionDep):
    """
    Returns a list of all videos in the database with their latest stats.
    """
    stmt = (
        select(Video)
        .options(selectinload(Video.last_stat))
        .order_by(Video.created_at.desc())
    )
    videos = (await session.execute(stmt)).scalars().unique().all()
    
    return [
        VideoResponse(
            id=video.id,
            url=video.url,
            last_stat=VideoStatResponse(
                id=video.last_stat.id,
                diggs=video.last_stat.diggs,
                shares=video.last_stat.shares,
                plays=video.last_stat.plays,
                collects=video.last_stat.collects,
                comments=video.last_stat.comments,
                reposts=video.last_stat.reposts,
                created_at=video.last_stat.created_at,
            ) if video.last_stat else None
        )
        for video in videos
    ]


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
