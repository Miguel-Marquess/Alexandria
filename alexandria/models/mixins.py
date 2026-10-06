from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class TimeStampMixin:
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        init=False,
        onupdate=func.now(),
        server_default=func.now(),
        nullable=True,
    )


class AuditorMixin(TimeStampMixin):
    __abstract__ = True

    created_by: Mapped[int] = mapped_column(
        ForeignKey('users.id'), init=False, nullable=True
    )

    updated_by: Mapped[int] = mapped_column(
        ForeignKey('users.id'), init=False, nullable=True
    )
