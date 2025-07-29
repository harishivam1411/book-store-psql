from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, EmailStr

TokenStr = Annotated[str, Field(..., examples=["eyJQGdtYWlsLmNvbSIsImlkIjoiNzBjMzhkYTEtNmEzYS00NDQ2LTg5MGMtNDYzOTM4YzA0Nm"
                                             "FhIiwidG9rZW5fdHlwZSI6ImFjY2Vzc190b2tlbiJ9.IJI-K-BsqODkgjI8MN-NBxBKmIxQ6z_ZOLhmKWMouTc"])]
EmailExample = Annotated[EmailStr, Field(..., json_schema_extra={'examples': ['bookstore@example.com']})]
PasswordExample = Annotated[str, Field(..., json_schema_extra={'examples': ['password123']})]

class TokenRequest(BaseModel):
    id: int
    username: str

class TokenResponse(BaseModel):
    access_token: TokenStr
    refresh_token: TokenStr

class TokenPayload(BaseModel):
    user_id: int
    exp: datetime
    token_type: str
    valid: bool = True

class UserLogin(BaseModel):
    username: str = Field(..., example="booklover99")
    password: PasswordExample

class PasswordReset(BaseModel):
    old_password: Optional[PasswordExample] = None
    new_password: PasswordExample