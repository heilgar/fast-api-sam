from uuid import UUID

from pydantic import BaseModel


class Item(BaseModel):
    id: UUID
    name: str
    description: str
