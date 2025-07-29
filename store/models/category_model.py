from pydantic import BaseModel, Field

from store.models.base_model import CreateUpdateSchema, BaseSchema, BookBaseSchema

class TopBooksSchema(BookBaseSchema):
    author: BaseSchema = Field(..., examples=[BaseSchema(id=1, name="F. Scott Fitzgerald")])
    average_rating: float = Field(0, examples=[3.1])

class CategoryCreate(BaseModel):
    name: str = Field(..., examples=['Historical Fiction'])
    description: str = Field(None, examples=['Fictional stories set in the past that often incorporate real historical events'])

class CategoryUpdate(BaseModel):
    name: str = Field(None, examples=['Fiction'])
    description: str = Field(None, examples=['Updated description: Literary works created from the imagination, including novels, short stories, and plays.'])

class CategoryCreateResponse(CreateUpdateSchema):
    name: str = Field(..., examples=['Historical Fiction'])
    description: str = Field(None, examples=['Fictional stories set in the past that often incorporate real historical events'])
    book_count: int = Field(0, examples=[8])

class CategoryUpdateResponse(CreateUpdateSchema):
    name: str = Field(None, examples=['Fiction'])
    description: str = Field(None, examples=['Fiction description'])
    book_count: int = Field(0, examples=[8])

class CategoryResponse(CreateUpdateSchema):
    name: str = Field(None, examples=['Fiction'])
    description: str = Field(None, examples=['Fiction description'])
    book_count: int = Field(0, examples=[8])
    top_books: list[TopBooksSchema] = Field(None, examples=[[
        TopBooksSchema(id=1, title="The Great Gatsby", author=BaseSchema(id=1, name="F. Scott Fitzgerald"), average_rating=4.2),
        TopBooksSchema(id=2, title="The Book Thief", author=BaseSchema(id=2, name="Stephen King"), average_rating=2.9)
        ]])

class CategorysResponse(CreateUpdateSchema):
    name: str = Field(None, examples=['Fiction'])
    description: str = Field(None, examples=['Fiction description'])
    book_count: int = Field(0, examples=[8])
    