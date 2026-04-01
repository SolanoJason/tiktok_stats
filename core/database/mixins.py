from sqlalchemy.orm import MappedAsDataclass, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime, UTC
from sqlalchemy import func


class TimeStampMixin(MappedAsDataclass, kw_only=True):
    # Fecha de creación: se establece automáticamente al crear el registro
    created_at: Mapped[datetime] = mapped_column(
        DateTime(True),
        insert_default=lambda: datetime.now(UTC),  # Valor por defecto en Python
        server_default=func.now(),  # Valor por defecto en la base de datos
        init=False,  # No se pasa en el constructor
        repr=False  # No se muestra en la representación
    )
    # Fecha de actualización: se actualiza automáticamente al modificar el registro
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(True),
        insert_default=lambda: datetime.now(UTC),  # Valor por defecto en Python
        server_default=func.now(),  # Valor por defecto en la base de datos
        init=False,  # No se pasa en el constructor
        onupdate=lambda: datetime.now(UTC),  # Se actualiza automáticamente
        repr=False  # No se muestra en la representación
    )