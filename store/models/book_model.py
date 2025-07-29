from pydantic import BaseModel, Field
from datetime import date
from store.models.base_model import CreateUpdateSchema, BaseSchema

class BookCreate(BaseModel):
    title : str = Field(..., examples=["The Great Gatsby"])
    isbn : str = Field(..., examples=["9780451524935"])
    publication_date : date = Field(..., examples=["1949-06-08"])
    description : str = Field(..., examples=["A dystopian novel about totalitarianism."])
    page_count : int = Field(..., examples=[328])
    language : str = Field(..., examples=["en"])
    author_id : int = Field(..., examples=[1])
    category_ids : list[int] = Field([], examples=[[1,2]])

class BookUpdate(BaseModel):
    title : str = Field(None, examples=["The Great Gatsby"])
    isbn : str = Field(None, examples=["9780451524935"])
    publication_date : date = Field(None, examples=["1949-06-08"])
    description : str = Field(None, examples=["A dystopian novel about totalitarianism. Updated!!!"])
    page_count : int = Field(None, examples=[328])
    language : str = Field(None, examples=["en"])
    author_id : int = Field(None,examples=[1])
    category_ids : list[int] = Field([], examples=[[1,2]])

class BookCreateResponse(CreateUpdateSchema):
    title : str = Field(..., examples=["The Great Gatsby"])
    isbn : str = Field(..., examples=["9780451524935"])
    publication_date : date = Field(..., examples=["1949-06-08"])
    description : str = Field(..., examples=["A dystopian novel about totalitarianism."])
    page_count : int = Field(..., examples=[328])
    language : str = Field(..., examples=["en"])
    author: BaseSchema = Field(..., examples=[BaseSchema(id=1, name="F. Scott Fitzgerald")])
    categories: list[BaseSchema] = Field([], examples=[[
        BaseSchema(id=1, name="Fiction"), 
        BaseSchema(id=2, name="Horror")]])
    average_rating : float = Field(0, examples=[4.6])

class BookUpdateResponse(CreateUpdateSchema):
    title : str = Field(..., examples=["The Great Gatsby"])
    isbn : str = Field(..., examples=["9780451524935"])
    publication_date : date = Field(..., examples=["1949-06-08"])
    description : str = Field(..., examples=["A dystopian novel about totalitarianism. Updated!!!"])
    page_count : int = Field(..., examples=[328])
    language : str = Field(..., examples=["en"])
    author: BaseSchema = Field(..., examples=[BaseSchema(id=1, name="F. Scott Fitzgerald")])
    categories: list[BaseSchema] = Field([], examples=[[
        BaseSchema(id=1, name="Fiction"), 
        BaseSchema(id=2, name="Horror")]])
    average_rating : float = Field(0, examples=[4.6])

class BookResponse(CreateUpdateSchema):
    title : str = Field(..., examples=["The Great Gatsby"])
    isbn : str = Field(..., examples=["9780451524935"])
    publication_date : date = Field(..., examples=["1949-06-08"])
    description : str = Field(..., examples=["A dystopian novel about totalitarianism."])
    page_count : int = Field(..., examples=[328])
    language : str = Field(..., examples=["en"])
    author: BaseSchema = Field(..., examples=[BaseSchema(id=1, name="F. Scott Fitzgerald")])
    categories: list[BaseSchema] = Field([], examples=[[
        BaseSchema(id=1, name="Fiction"), 
        BaseSchema(id=2, name="Horror")]])
    average_rating : float = Field(0, examples=[4.6])

class BooksResponse(CreateUpdateSchema):
    title : str = Field(..., examples=["The Great Gatsby"])
    isbn : str = Field(..., examples=["9780451524935"])
    publication_date : date = Field(..., examples=["1949-06-08"])
    description : str = Field(..., examples=["A dystopian novel about totalitarianism."])
    page_count : int = Field(..., examples=[328])
    language : str = Field(..., examples=["en"])
    author: BaseSchema = Field(..., examples=[BaseSchema(id=1, name="F. Scott Fitzgerald")])
    categories: list[BaseSchema] = Field([], examples=[[
        BaseSchema(id=1, name="Fiction"), 
        BaseSchema(id=2, name="Horror")]])
    average_rating : float = Field(0, examples=[4.6])


