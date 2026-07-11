from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Genre(str, Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE = "science"
    HISTORY = "history"
    BIOGRAPHY = "biography"
    FANTASY = "fantasy"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    THRILLER = "thriller"
    CHILDREN = "children"
    OTHER = "other"


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300, description="Title of the book")
    author: str = Field(..., min_length=1, max_length=200, description="Author of the book")
    isbn: str = Field(..., min_length=10, max_length=17, description="ISBN of the book")
    published_date: str = Field(..., description="Publication date in YYYY-MM-DD format")
    genre: Genre = Field(default=Genre.OTHER, description="Genre of the book")
    price: float = Field(..., gt=0, description="Price of the book")
    stock_quantity: int = Field(default=0, ge=0, description="Number of copies in stock")
    description: Optional[str] = Field(default=None, max_length=2000, description="Description of the book")

    @field_validator("published_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("published_date must be in YYYY-MM-DD format")
        return v


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    isbn: Optional[str] = Field(None, min_length=10, max_length=17)
    published_date: Optional[str] = None
    genre: Optional[Genre] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=2000)

    @field_validator("published_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("published_date must be in YYYY-MM-DD format")
        return v


class Book(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime


class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookStats(BaseModel):
    total_books: int
    total_stock: int
    total_value: float
    by_genre: dict[str, int]
