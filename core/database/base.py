from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from contextlib import asynccontextmanager
from core.settings import settings
from sqlalchemy import MetaData
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

url = URL.create(
    drivername=settings.DB_DRIVER,
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

engine = create_async_engine(
    url,
    echo_pool=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=10,
    pool_recycle=1800,
    pool_timeout=10,
)

SessionFactory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

metadata = MetaData()

# Clase base para todos los modelos de la aplicación
class Base(AsyncAttrs, MappedAsDataclass, DeclarativeBase, kw_only=True):
    metadata = metadata
    # Mapeo de tipos Python a tipos SQLAlchemy
    type_annotation_map = {
        dict: JSON(none_as_null=True),  # Diccionarios como JSON
    }