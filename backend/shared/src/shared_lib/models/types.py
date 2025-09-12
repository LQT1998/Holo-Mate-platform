import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import JSON as SA_JSON
from sqlalchemy.types import TypeDecorator


class GUID(TypeDecorator):
    """Cross-dialect UUID.

    - PostgreSQL: native UUID
    - Others (SQLite): VARCHAR(36)
    """

    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        # sqlite and others expect string
        return (
            str(value) if isinstance(value, uuid.UUID) else str(uuid.UUID(str(value)))
        )

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


class JSONFlexible(TypeDecorator):
    """Use JSONB in Postgres, JSON elsewhere (e.g., SQLite for tests)."""

    impl = SA_JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB)
        return dialect.type_descriptor(SA_JSON)
