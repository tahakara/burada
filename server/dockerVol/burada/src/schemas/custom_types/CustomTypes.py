from pydantic import constr, EmailStr

class CustomTypes():
    UsernameType = constr(pattern="^[a-zA-Z0-9_]+$", min_length=3, max_length=80)
    PhoneType = constr(min_length=10, max_length=20)
    PasswordType = constr(min_length=8, max_length=128)    