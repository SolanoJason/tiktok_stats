from typing import Annotated
from sqlalchemy.orm import mapped_column
from core.settings import settings

# Tipo anotado para claves primarias de tipo entero
intpk = Annotated[int, mapped_column(primary_key=True)]
