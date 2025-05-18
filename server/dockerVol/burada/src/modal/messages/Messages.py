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

class LessonModelMessages:
    LESSON_ALREADY_EXISTS = "A lesson with this name already exists."
    LESSON_CREATED_SUCCESSFULLY = "Lesson created successfully."
    ERROR_CREATING_LESSON = "An error occurred while creating the lesson."
    LESSON_UPDATED_SUCCESSFULLY = "Lesson updated successfully."
    ERROR_UPDATING_LESSON = "An error occurred while updating the lesson."
    LESSON_DELETED_SUCCESSFULLY = "Lesson deleted successfully."
    ERROR_DELETING_LESSON = "An error occurred while deleting the lesson."
    LESSON_NAME_ALREADY_EXISTS = "Another lesson with this name already exists."

class LessonTeacherModelMessages:
    ASSIGNMENT_ALREADY_EXISTS = "This teacher is already assigned to this lesson."
    ASSIGNMENT_CREATED_SUCCESSFULLY = "Teacher assigned to lesson successfully."
    ERROR_CREATING_ASSIGNMENT = "An error occurred while assigning the teacher to the lesson."
    ASSIGNMENT_DELETED_SUCCESSFULLY = "Assignment removed successfully."
    ERROR_DELETING_ASSIGNMENT = "An error occurred while removing the assignment."

class StudentModelMessages:
    STUDENT_CREATED_SUCCESSFULLY = "Student created successfully."
    ERROR_CREATING_STUDENT = "An error occurred while creating the student."
    STUDENT_UPDATED_SUCCESSFULLY = "Student updated successfully."
    ERROR_UPDATING_STUDENT = "An error occurred while updating the student."
    STUDENT_DELETED_SUCCESSFULLY = "Student deleted successfully."
    ERROR_DELETING_STUDENT = "An error occurred while deleting the student."

class AttenationModelMessages:
    ACTIVE_SESSION_EXISTS = "An active attendance session already exists for this lesson."
    SESSION_CREATED_SUCCESSFULLY = "Attendance session created successfully."
    ERROR_CREATING_SESSION = "An error occurred while creating the attendance session."
    SESSION_CLOSED_SUCCESSFULLY = "Attendance session closed successfully."
    SESSION_ALREADY_CLOSED = "This attendance session has already been closed."
    ERROR_CLOSING_SESSION = "An error occurred while closing the attendance session."
    NO_ACTIVE_SESSION = "No active attendance session found for this lesson."
    NOT_AUTHORIZED_FOR_LESSON = "You are not authorized to start attendance for this lesson."

class AttenationDetailModelMessages:
    ALREADY_MARKED_PRESENT = "This student has already been marked present in this session."
    ATTENDANCE_RECORDED_SUCCESSFULLY = "Attendance recorded successfully."
    ERROR_RECORDING_ATTENDANCE = "An error occurred while recording attendance."