from pydantic import BaseModel, Field, EmailStr


class Login(BaseModel):
    email: EmailStr
    pwd: str = Field(min_length=12)

    model_config = {'extra': 'forbid'}

class PasswordUpdate(BaseModel):
    currentPwd: str = Field(min_length=12)
    newPwd: str = Field(min_length=12)

    model_config = {'extra': 'forbid'}