from pydantic import BaseModel, Field, EmailStr

from store.models.base_model import CreateUpdateSchema, CreateSchema, BookBaseSchema

class RecentReviewsSchema(CreateSchema):
    book: BookBaseSchema = Field(..., examples=[BookBaseSchema(id=1, title="The Great Gatsby")])
    rating: float = Field(0, examples=[3.5])

class UserCreate(BaseModel):
    username : str = Field(..., examples=["booklover99"])
    email : EmailStr = Field(..., examples=["newuser@example.com"])
    password : str = Field(..., examples=["password123"])
    first_name : str = Field(..., examples=["John"])
    last_name : str = Field(..., examples=["Doe"])
    
class UserUpdate(BaseModel):
    username : str = Field(None, examples=["booklover99"])
    email : EmailStr = Field(None, examples=["newuserupdated@example.com"])
    first_name : str = Field(None, examples=["Jane"])
    last_name : str = Field(None, examples=["Smith"])

class UserCreateResponse(CreateUpdateSchema):
    username : str = Field(..., examples=["booklover99"])
    email : EmailStr = Field(..., examples=["newuser@example.com"])
    first_name : str = Field(..., examples=["John"])
    last_name : str = Field(..., examples=["Doe"])
    review_count : int = Field(0, examples=[7])

class UserUpdateResponse(CreateUpdateSchema):
    username : str = Field(None, examples=["booklover99"])
    email : EmailStr = Field(None, examples=["newuserupdated@example.com"])
    first_name : str = Field(None, examples=["Jane"])
    last_name : str = Field(None, examples=["Smith"])
    review_count : int = Field(None, examples=[7])

class UserResponse(CreateUpdateSchema):
    username : str = Field(..., examples=["booklover99"])
    email : EmailStr = Field(..., examples=["newuser@example.com"])
    first_name : str = Field(..., examples=["John"])
    last_name : str = Field(..., examples=["Doe"])
    review_count : int = Field(0, examples=[7])
    recent_reviews : list[RecentReviewsSchema] = Field([], examples=[
        RecentReviewsSchema(id=1, book= BookBaseSchema(id=1, title="The Great Gatsby"), rating=3.5, created_at= "2023-02-15T10:20:00Z"),
        RecentReviewsSchema(id=2, book= BookBaseSchema(id=2, title="The Book Thief"), rating=3.7, created_at= "2023-02-15T10:20:00Z")
    ])

class UsersResponse(CreateUpdateSchema):
    username : str = Field(..., examples=["booklover99"])
    email : EmailStr = Field(..., examples=["newuser@example.com"])
    first_name : str = Field(..., examples=["John"])
    last_name : str = Field(..., examples=["Doe"])
    review_count : int = Field(0, examples=[12])