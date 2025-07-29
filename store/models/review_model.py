from pydantic import BaseModel, Field

from store.models.base_model import CreateUpdateSchema, UserBaseSchema

class UserDetailsSchema(UserBaseSchema):
    first_name: str = Field(..., examples=["Jane"])
    last_name: str = Field(..., examples=["Smith"])

class ReviewCreate(BaseModel):
    rating: float = Field(..., examples=[2.7])
    title: str = Field(..., examples=["Thought-provoking classic"])
    content: str = Field(None, examples=["Orwell's predictions about surveillance society are eerily prescient."])

class ReviewUpdate(BaseModel):
    rating: float = Field(None, examples=[2.4])
    title: str = Field(None, examples=["A timeless masterpiece!"])
    content: str = Field(None, examples=["Updated review: This book brilliantly captures the essence of the American Dream during the Roaring Twenties."])

class ReviewCreateResponse(CreateUpdateSchema):
    book_id: int = Field(..., examples=[1])
    user: UserBaseSchema = Field(..., examples=[UserBaseSchema(id=1, username="booklover99")])
    rating: float = Field(..., examples=[2.9])
    title: str = Field(..., examples=["Thought-provoking classic"])
    content: str = Field(None, examples=["Orwell's predictions about surveillance society are eerily prescient."])

class ReviewUpdateResponse(CreateUpdateSchema):
    book_id: int = Field(..., examples=[1])
    user: UserBaseSchema = Field(..., examples=[UserBaseSchema(id=1, username="booklover99")])
    rating: float = Field(..., examples=[2.5])
    title: str = Field(..., examples=["A timeless masterpiece!"])
    content: str = Field(None, examples=["Updated review: This book brilliantly captures the essence of the American Dream during the Roaring Twenties."])

class ReviewResponse(CreateUpdateSchema):
    book_id: int = Field(..., examples=[1])
    user: UserDetailsSchema = Field(..., examples=[UserDetailsSchema(id=1, username="booklover99", first_name="Jane", last_name="Smith")])
    rating: float = Field(..., examples=[2.2])
    title: str = Field(..., examples=["A timeless masterpiece!"])
    content: str = Field(None, examples=["This book perfectly captures the essence of the Roaring Twenties."])

class ReviewsResponse(CreateUpdateSchema):
    book_id: int = Field(..., examples=[1])
    user: UserBaseSchema = Field(..., examples=[UserBaseSchema(id=1, username="booklover99")])
    rating: float = Field(..., examples=[2.1])
    title: str = Field(..., examples=["A masterpiece!"])
    content: str = Field(None, examples=["This book perfectly captures the essence of the Roaring Twenties."])