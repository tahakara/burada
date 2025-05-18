from pydantic import BaseModel, Field, EmailStr, constr, field_validator

from .LoginSchema import LoginSchema
from ..messages.Messages import RegisterUserSchemaMessages as RUSM 
from ..custom_types.CustomTypes import CustomTypes as CT

class RegisterSchema(LoginSchema):
    # TODO: Phone number validation is not fully (global) implemented yet.
    """This class defines the schema for user registration.
    It uses Pydantic for data validation and serialization.
    """             
    username: CT.UsernameType = Field(description=RUSM.USER_SCHEMA_USERNAME_DESCRIPTION)                   # type: ignore
    email: EmailStr = Field(description=RUSM.USER_SCHEMA_EMAIL_DESCRIPTION)                            # type: ignore
    phone: CT.PhoneType = Field(description=RUSM.USER_SCHEMA_PHONE_DESCRIPTION)                            # type: ignore
    password: CT.PasswordType = Field(description=RUSM.USER_SCHEMA_PASSWORD_DESCRIPTION)                   # type: ignore
    passwordConfirm: CT.PasswordType = Field(description=RUSM.USER_SCHEMA_PASSWORD_CONFIRM_DESCRIPTION)    # type: ignore

    @field_validator('passwordConfirm')
    @classmethod
    def validate_password(cls, value):
        import re
        if not re.search(r'[a-z]', value):
            raise ValueError('Password Confirm must contain at least one lowercase letter')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password Confirm must contain at least one uppercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password Confirm must contain at least one digit')
        if not re.search(r'[@$!%*?&]', value):
            raise ValueError('Password Confirm must contain at least one special character (@$!%*?&)')
        return value
    
class UsernameCheckSchema(BaseModel):
    """This class defines the schema for checking username availability.
    It uses Pydantic for data validation and serialization.
    """             
    username: CT.UsernameType = Field(description=RUSM.USER_SCHEMA_USERNAME_DESCRIPTION)                   # type: ignore

class EmailCheckSchema(BaseModel):
    """This class defines the schema for checking email availability.
    It uses Pydantic for data validation and serialization.
    """             
    email: EmailStr = Field(description=RUSM.USER_SCHEMA_EMAIL_DESCRIPTION)                            # type: ignore

class PhoneCheckSchema(BaseModel):
    """This class defines the schema for checking phone availability.
    It uses Pydantic for data validation and serialization.
    """             
    phone: CT.PhoneType = Field(description=RUSM.USER_SCHEMA_PHONE_DESCRIPTION)                            # type: ignore
    @field_validator('phone')
    def phone_max_length(cls, v):
        if v and len(v) > 20:
            raise ValueError('Phone must be at most 20 characters long')
        return v
    
    @field_validator('phone')
    def remove_plus(cls, v):
        if v and v.startswith('+'):
            return v[1:]
        return v