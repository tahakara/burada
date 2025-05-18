class SchemaMessages():
    """This class contains various message constants that can be used Schema Validations."""

class LoginUserSchemaMessages(SchemaMessages):
    USER_SCHEMA_USERNAME_DESCRIPTION = "Username must be alphanumeric, can include underscores, and be between 3 and 80 characters."
    USER_SCHEMA_EMAIL_DESCRIPTION = "Email must be a valid email address and no longer than 120 characters."
    USER_SCHEMA_PHONE_DESCRIPTION = "Phone number must be between 10 and 20 characters."
    USER_SCHEMA_PASSWORD_DESCRIPTION ="Password must be between 8 and 128 characters, contain at least one uppercase letter, one lowercase letter, one number, and one special character."
    

class RegisterUserSchemaMessages(LoginUserSchemaMessages):
    """This class contains various message constants that can be used in RegisterUserSchema."""

    #region Register User Schema Messages
    USER_SCHEMA_PASSWORD_CONFIRM_DESCRIPTION = "Password confirmation must match the password."
    #endregion Register User Schema Messages    