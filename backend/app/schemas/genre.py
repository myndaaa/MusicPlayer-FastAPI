from typing import Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, model_validator 



class GenreBase(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    description: Optional[str] = None

    class Config:
        from_attributes = True  # enables ORM mode with SQLAlchemy models


class GenreCreate(GenreBase):
    pass  # no extra fields for creation after base


class GenreUpdate(BaseModel):
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]] = None
    description: Optional[str] = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "GenreUpdate":
        """
        Ensures that at least one of the optional fields is provided.
        """
        if self.name is None and self.description is None:
            raise ValueError("At least one field ('name' or 'description') must be provided.")
        return self

    class Config:
        from_attributes = True


class GenreOut(GenreBase):
    id: int
    is_active: bool
    created_at: datetime
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GenreStatus(BaseModel):
    is_active: bool
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True
