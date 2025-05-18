class ModelMessages():
    """Class to handle messages for the Models module."""

class UserModelMessages(ModelMessages):
    """Class to handle messages for the User model."""
    
    #region User Model Messages
    USERNAME_OR_EMAIL_OR_PHONE_ALREADY_EXISTS = "A user with the same username, email, or phone already exists."
    ERROR_CREATING_USER = "An error occurred while creating the user."
    USER_CREATED_SUCCESSFULLY = "User created successfully."

    USER_NOT_FOUND = "User not found."
    ERROR_UPDATING_USER = "An error occurred while updating the user."
    USER_UPDATED_SUCCESSFULLY = "User updated successfully."

    ERROR_DELETING_USER = "An error occurred while deleting the user."
    USER_DELETED_SUCCESSFULLY = "User deleted successfully."

    ERROR_ACTIVATING_USER = "An error occurred while activating the user."
    USER_ACTIVATED_SUCCESSFULLY = "User activated successfully."

    ERROR_DEACTIVATING_USER = "An error occurred while deactivating the user."
    USER_DEACTIVATED_SUCCESSFULLY = "User deactivated successfully."

    ERROR_USERNAME_NOT_AVAILABLE = "Username is not available."
    ERROR_UPDATING_USERNAME = "An error occurred while updating the username."
    USERNAME_CHANGED_SUCCESSFULLY = "Username changed successfully."

    ERROR_VERIFYING_EMAIL = "An error occurred while verifying the email."
    EMAIL_VERIFIED_SUCCESSFULLY = "Email verified successfully."

    ERROR_CHANGING_EMAIL = "An error occurred while changing the email."
    ERROR_EMAIL_NOT_AVAILABLE = "Email is not available."
    EMAIL_CHANGED_SUCCESSFULLY = "Email changed successfully."

    ERROR_VERIFYING_PHONE = "An error occurred while verifying the phone number."
    PHONE_VERIFIED_SUCCESSFULLY = "Phone number verified successfully."

    ERROR_CHANGING_PHONE = "An error occurred while changing the phone number."
    ERROR_PHONE_NOT_AVAILABLE = "Phone number is not available."
    PHONE_CHANGED_SUCCESSFULLY = "Phone number changed successfully."

    ERROR_CHANGING_PASSWORD = "An error occurred while changing the password."
    PASSWORD_CHANGED_SUCCESSFULLY = "Password changed successfully."

    INVALID_USERNAME_OR_PASSWORD = "Invalid username or password."

    USER_LOGGED_IN_SUCCESSFULLY = "User logged in successfully."