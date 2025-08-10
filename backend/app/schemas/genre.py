from typing import Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, model_validator


class GenreBase(BaseModel):
    """Base schema for genre data with common fields"""
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    description: Optional[str] = None

    class Config:
        from_attributes = True


class GenreCreate(GenreBase):
    """Schema for creating a new genre"""
    pass


class GenreUpdate(BaseModel):
    """Schema for updating a genre"""
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]] = None
    description: Optional[str] = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "GenreUpdate":
        """Ensures that at least one of the optional fields is provided"""
        if self.name is None and self.description is None:
            raise ValueError("At least one field ('name' or 'description') must be provided.")
        return self

    class Config:
        from_attributes = True


class GenreOut(GenreBase):
    """Schema for genre output with all fields"""
    id: int
    is_active: bool
    created_at: datetime
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GenreStats(BaseModel):
    """Schema for genre statistics"""
    total_genres: int
    active_genres: int
    inactive_genres: int
    genres_with_songs: int
    most_used_genre: Optional[str] = None
    least_used_genre: Optional[str] = None

    class Config:
        from_attributes = True
