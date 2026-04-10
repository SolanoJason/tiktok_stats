from __future__ import annotations
from core.database import TimeStampMixin, intpk, Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from .enums import GenderEnum, PeruDepartmentEnum


class RawData(TimeStampMixin, Base):
    __tablename__ = "raw_data"

    id: Mapped[intpk] = mapped_column(init=False)
    data: Mapped[dict | None] = mapped_column(default=None)


class Video(TimeStampMixin, Base):
    __tablename__ = "videos"

    id: Mapped[intpk] = mapped_column(init=False)
    url: Mapped[str] = mapped_column(unique=True)
    gender: Mapped[GenderEnum | None]
    department: Mapped[PeruDepartmentEnum | None]

    stats: Mapped[list[VideoStats]] = relationship(
        back_populates="video",
        cascade="save-update, delete, delete-orphan",
        single_parent=True,
        default_factory=list,
        repr=False,
        order_by="VideoStats.created_at.desc()",
        foreign_keys="VideoStats.video_id",
    )
    last_stat_id: Mapped[int | None] = mapped_column(
        ForeignKey("video_stats.id", use_alter=True), default=None
    )
    last_stat: Mapped[VideoStats | None] = relationship(
        default=None,
        repr=False,
        cascade="save-update",
        foreign_keys=last_stat_id,
        post_update=True,
    )


class VideoStats(TimeStampMixin, Base):
    __tablename__ = "video_stats"

    id: Mapped[intpk] = mapped_column(init=False)

    diggs: Mapped[int]
    shares: Mapped[int]
    plays: Mapped[int]
    collects: Mapped[int]
    comments: Mapped[int]
    reposts: Mapped[int]

    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id"), repr=False, default=None
    )
    video: Mapped[Video] = relationship(
        back_populates="stats",
        cascade="save-update",
        repr=False,
        default=None,
        foreign_keys=video_id,
    )

    raw_data_id: Mapped[int | None] = mapped_column(
        ForeignKey("raw_data.id"), default=None, repr=False
    )
    raw_data: Mapped[RawData | None] = relationship(default=None, repr=False, cascade="save-update", foreign_keys=raw_data_id)
