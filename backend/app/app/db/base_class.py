from typing import Any
from typing import Mapping
from sqlalchemy.orm import as_declarative, declared_attr, Mapped


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> Mapped[str]:
        return cls.__name__.lower()


ExtraData = Mapped[Mapping[str, Any]]
Translations = Mapped[Mapping[str, str]]
