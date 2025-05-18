from pydantic import BaseModel, Field, EmailStr, constr, field_validator, model_validator
from typing import Optional

from ..messages.Messages import LoginUserSchemaMessages as LUSM 
from ..custom_types.CustomTypes import CustomTypes as CT


class LoginSchema(BaseModel):
    """This class defines the schema for user login and registration.
    It uses Pydantic for data validation and serialization.
    """    
    # ..., its mean required field
    username: Optional[CT.UsernameType] = Field(default=None, description=LUSM.USER_SCHEMA_USERNAME_DESCRIPTION)    # type: ignore
    email: Optional[EmailStr] = Field(default=None, description=LUSM.USER_SCHEMA_EMAIL_DESCRIPTION)             
    phone: Optional[CT.PhoneType] = Field(default=None, description=LUSM.USER_SCHEMA_PHONE_DESCRIPTION)             # type: ignore
    password: Optional[CT.PasswordType] = Field(default=None, description=LUSM.USER_SCHEMA_PASSWORD_DESCRIPTION)    # type: ignore

    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        import re
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter (a-z).')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter (A-Z).')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit (0-9).')
        if not re.search(r'[@$!%*?&_]', value):
            raise ValueError('Password must contain at least one special character (@$!%*?&).')
        return value
    
    @field_validator('email')
    def email_max_length(cls, v):
        if v and len(v) > 120:
            raise ValueError('Email must be at most 120 characters long.')
        if v and "@" not in v:
            raise ValueError('Email must be a valid email address.')
        return v
    
    @field_validator('phone')
    def remove_plus(cls, v):
        if v and v.startswith('+'):
            return v[1:]  # Removing the '+' sign

    @model_validator(mode="after")
    def check_username_email_phone(self):
        if not (self.username or self.email or self.phone):
            raise ValueError('You must provide either username, email, or phone')
        return self