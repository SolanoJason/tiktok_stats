from typing import Annotated
from .base import SessionFactory
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

async def get_session():
    # Crear una nueva sesión para cada request
    async with SessionFactory() as session:
        print(f"{session=} from get_session")
        yield session  # Entregar la sesión al endpoint
    # La sesión se cierra automáticamente al salir del contexto
    print("session closed")

SessionDep = Annotated[AsyncSession, Depends(get_session, scope="function")]