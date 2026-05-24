import re
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator


class Login(BaseModel):
    email: EmailStr
    pwd: str = Field(min_length=12)

    model_config = {'extra': 'forbid'}


class PasswordUpdate(BaseModel):
    currentPwd: str
    newPwd: str = Field(min_length=12)

    model_config = {'extra': 'forbid'}

    @field_validator('newPwd')
    @classmethod
    def validate_new_password(cls, v):
        """ Validate a new password format (at least one uppercase letter, one lowercase letter, one digit, one special character) """
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[^a-zA-Z0-9\s]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @model_validator(mode='after')
    def validate_passwords_differ(self):
        if self.currentPwd == self.newPwd:
            raise ValueError('Current and new passwords cannot be the same')
        return self
