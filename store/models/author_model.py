from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

from store.models.base_model import CreateUpdateSchema, BookBaseSchema
   
class AuthorBooksSchema(BookBaseSchema):
    isbn: str = Field(..., examples=["9780547928227"])
    publication_date: date = Field(..., examples=["1937-09-21"])

class AuthorCreate(BaseModel):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: date = Field(..., examples=["1947-09-21"])
    country: Optional[str] = Field(None, examples=["United States"])

    class Config:
        orm_mode = True

class AuthorUpdate(BaseModel):
    name: str = Field(None, examples=["Stephen King"])
    biography: str = Field(None, examples=["Stephen Edwin King is an American author of horror,  suspense, crime and fantasy novels."])
    birth_date: date = Field(None, examples=["1947-09-21"])
    death_date: Optional[date] = Field(None, examples=["1973-09-02"])
    country: Optional[str] = Field(None, examples=["India"])

class AuthorCreateResponse(CreateUpdateSchema):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: date = Field(..., examples=["1947-09-21"])
    death_date: Optional[date] = Field(None, examples=["1947-09-21"])
    country: Optional[str] = Field(None, examples=["United States"])
    book_count : int = Field(0, examples=[6])

class AuthorUpdateResponse(CreateUpdateSchema):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror,  suspense, crime and fantasy novels."])
    birth_date: date = Field(..., examples=["1947-09-21"])
    death_date: Optional[date] = Field(None, examples=["1973-09-02"])
    country: Optional[str] = Field(None, examples=["India"])
    book_count : int = Field(0, examples=[6])

class AuthorResponse(CreateUpdateSchema):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: date = Field(..., examples=["1947-09-21"])
    death_date: Optional[date] = Field(None, examples=["1973-09-02"])
    country: Optional[str] = Field(None, examples=["United States"])
    book_count : int = Field(0, examples=[6])
    books : list[AuthorBooksSchema] = Field([], examples=[[
        AuthorBooksSchema(id=1, title="The Hobbit", isbn="9780547928227", publication_date="1937-09-21"),
        AuthorBooksSchema(id=2, title="The Book Thief", isbn="9782547928527", publication_date="1961-11-13")]])
    
class AuthorsResponse(CreateUpdateSchema):
    name: str = Field(..., examples=["Stephen King"])
    biography: str = Field(..., examples=["Stephen Edwin King is an American author of horror, supernatural fiction, suspense, crime, science-fiction, and fantasy novels."])
    birth_date: date = Field(..., examples=["1947-09-21"])
    death_date: Optional[date] = Field(None, examples=["1973-09-02"])
    country: Optional[str] = Field(None, examples=["United States"])
    book_count : int = Field(0, examples=[6])
