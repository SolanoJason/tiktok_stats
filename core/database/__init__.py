# Módulo de base de datos: exporta componentes principales y configura el almacenamiento
from .base import Base, SessionFactory, engine, url, sync_engine, SyncSessionFactory
from .dependencies import SessionDep
from .mixins import TimeStampMixin
from .types import intpk

def load_models():
    import apps.tiktok.models
