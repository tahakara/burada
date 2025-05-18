from modal import db
from typing import Tuple, Optional, Self
from sqlalchemy.exc import SQLAlchemyError
import logging


from modal.messages.Messages import UserModelMessages as UMM
from utils.PasswordUtils import PasswordUtils


class User(db.Model):
    
    __tablename__ = 'users'
    __table_args__ = (

        db.Index('idx_username', 'username'),
        db.Index('idx_email', 'email'),
        db.Index('idx_phone', 'phone'),

        # charset and collation for MySQL
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_turkish_ci"
        }
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    phone = db.Column(db.String(20), unique=False, nullable=True)
    passwordHash = db.Column(db.String(128), nullable=False)
    passwordSalt = db.Column(db.String(128), nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    isDeleted = db.Column(db.Boolean, default=False)
    isEmailVerified = db.Column(db.Boolean, default=False)
    isPhoneVerified = db.Column(db.Boolean, default=False)
    lastLogin = db.Column(db.DateTime, nullable=True)
    uniqueID = db.Column(db.String(36), unique=True, nullable=False, default=db.func.uuid())
    updatedAt = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    createdAt = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f"<User {self.id}-{self.uniqueID}-{self.username}>"
    
    @classmethod
    def create(cls, username: str, email: str, phone: str, password: str) -> Tuple[bool, str, Optional["User"]]:
        """Create a new user in the database."""
        try:
            # Start a database transaction
            with db.session.begin():  # This will ensure that a rollback happens in case of an exception
            
                # Check if a user with the same username, email, or phone already exists
                existing_user = User.query.filter(
                    ((User.username == username) & (not User.isDeleted)) |
                    ((User.email == email) & (not User.isDeleted)) |
                    ((User.phone == phone) & (not User.isDeleted))
                ).first()

                if existing_user:
                    return (False, UMM.USERNAME_OR_EMAIL_OR_PHONE_ALREADY_EXISTS, None)

                passwordHash, passwordSalt = PasswordUtils.password_hash(password)
                # If no user exists, proceed with creating the user
                user = User(
                    username=username,
                    email=email,
                    phone=phone,
                    passwordHash=passwordHash,
                    passwordSalt=passwordSalt,
                    isActive=True,
                    isDeleted=False,
                    isEmailVerified=False,
                    isPhoneVerified=False,
                    lastLogin=None,
                    uniqueID=db.func.uuid(),
                    updatedAt=db.func.current_timestamp(),
                    createdAt=db.func.current_timestamp()
                )
                # Add user to the session
                db.session.add(user)
                db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback the transaction on error
            logging.error(UMM.ERROR_CREATING_USER + " " + str(e))
            return (False, UMM.ERROR_CREATING_USER, None)
        
        return (True, UMM.USER_CREATED_SUCCESSFULLY, user)
    
    def update(self, userId: int, username: str = None, email: str = None, phone: str = None, passwordHash: str = None, passwordSalt: str = None) -> Tuple[bool, str, Optional[Self: object]]:
        """Update an existing user in the database.
        
        Args:
            userId (int): User ID.
            username (str): New username.
            email (str): New email address.
            phone (str): New phone number.
            passwordHash (str): New password hash.
            passwordSalt (str): New password salt.

        Returns:
            Tuple: (success: bool, message: str, user: Optional[User]) 
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        if username:
            user.username = username
        if email:
            user.email = email
        if phone:
            user.phone = phone
        if passwordHash:
            user.passwordHash = passwordHash
        if passwordSalt:
            user.passwordSalt = passwordSalt
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_UPDATING_USER + " " + e)
            return (False, UMM.ERROR_UPDATING_USER)

        return (True, UMM.USER_UPDATED_SUCCESSFULLY, user)        
    
    def delete_permanent(self, userId: int) -> Tuple[bool, str]:
        """<strong>PERMANENT</strong> Delete a user permanent from the database.
        
        Args:
            userId (int): User ID.

        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_DELETING_USER + " " + e)
            return (False, UMM.ERROR_DELETING_USER)

        return (True, UMM.USER_DELETED_SUCCESSFULLY)        
    
    @classmethod
    def get_user_by_uniqueId(cls, uniqueId: str) -> Optional["User"]:
        """Select a user by unique ID.
        
        Args:
            uniqueId (str): Unique ID of the user.

        Returns:
            Optional[User]: User object if found, None otherwise.
        """
        return cls.query.filter_by(uniqueID=uniqueId).first()

    def activate(self, userId: int) -> Tuple[bool, str, Optional[Self: object]]:
        """Activate a user in the database.
        Args:
            userId (int): User ID.

        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        user.isActive = True
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_ACTIVATING_USER + " " + e)
            return (False, UMM.ERROR_ACTIVATING_USER)

        return (True, UMM.USER_ACTIVATED_SUCCESSFULLY, user)
    
    def deactivate(self, userId: int) -> Tuple[bool, str, Optional[Self: object]]:
        """Deactivate a user in the database.
        Args:
            userId (int): User ID.

        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        user.isActive = False
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_DEACTIVATING_USER + " " + e)
            return (False, UMM.ERROR_DEACTIVATING_USER)

        return (True, UMM.USER_DEACTIVATED_SUCCESSFULLY, user)
    
    def change_username(self, userId: int, newUsername: str) -> Tuple[bool, str, Optional[Self: object]]:
        """Change a user's username in the database.
        Args:
            userId (int): User ID.
            newUsername (str): New Username.
        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        # Check if the new username is already in use by another user
        existing_user = User.query.filter(
            (User.username == newUsername) & (User.isDeleted == False) & (User.id != userId)
        ).first()

        if existing_user:
            return (False, UMM.ERROR_USERNAME_NOT_AVAILABLE)
        
        user.username = newUsername
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_UPDATING_USERNAME + " " + e)
            return (False, UMM.ERROR_UPDATING_USERNAME)

        return (True, UMM.USERNAME_CHANGED_SUCCESSFULLY, user)
        
    def verify_email(self, userId: int) -> Tuple[bool, str, Optional[Self: object]]:
        # TODO: Feature: Add email verification logic refactorinr redis and other things
        """Verify a user's email in the database.
        Args:
            userId (int): User ID.
        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        user.isEmailVerified = True
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_VERIFYING_EMAIL + " " + e)
            return (False, UMM.ERROR_VERIFYING_EMAIL)

        return (True, UMM.EMAIL_VERIFIED_SUCCESSFULLY, user)
    
    def change_email(self, userId: int, newEmail: str) -> Tuple[bool, str, Optional[Self: object]]:
        # TODO: Feature: Add email verification logic refactorinr redis and other things
        """Change a user's email in the database.
        Args:
            userId (int): User ID.
            newEmail (str): New email address.
        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        # Check if the new email is already in use by another user
        existing_user = User.query.filter(
            (User.email == newEmail) & (User.isDeleted == False) & (User.id != userId)
        ).first()

        if existing_user:
            return (False, UMM.ERROR_EMAIL_NOT_AVAILABLE)
        
        user.email = newEmail
        user.isEmailVerified = False  # Reset email verification status
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_CHANGING_EMAIL + " " + e)
            return (False, UMM.ERROR_CHANGING_EMAIL)

        return (True, UMM.EMAIL_CHANGED_SUCCESSFULLY, user)
    
    def verify_phone(self, userId: int) -> Tuple[bool, str, Optional[Self: object]]:
        # TODO: Feature: Add phone verification logic refactorinr redis and other things
        """Verify a user's phone number in the database.
        Args:
            userId (int): User ID.
        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        user.isPhoneVerified = True
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_VERIFYING_PHONE + " " + e)
            return (False, UMM.ERROR_VERIFYING_PHONE)

        return (True, UMM.PHONE_VERIFIED_SUCCESSFULLY, user)
    
    def change_phone(self, userId: int, newPhone: str) -> Tuple[bool, str, Optional[Self: object]]:
        # TODO: Feature: Add phone verification logic refactorinr redis and other things
        """Validate a password against a stored hash and salt.      
        Args:
            userId (int): User ID.
            newPhone (str): New phone number.
            
        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        # Check if the new email is already in use by another user
        existing_user = User.query.filter(
            (User.phone == newPhone) & (User.isDeleted == False) & (User.id != userId)
        ).first()

        if existing_user:
            return (False, UMM.ERROR_PHONE_NOT_AVAILABLE)

        user.phone = newPhone
        user.isPhoneVerified = False # Reset phone verification status

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_CHANGING_PHONE + " " + e)
            return (False, UMM.ERROR_CHANGING_PHONE)
        
        return (True, UMM.PHONE_CHANGED_SUCCESSFULLY, user)
    
    def change_password(self, userId: int, newPassword: str) -> Tuple[bool, str, Optional[Self: object]]:
        # TODO: Feature: Notify user about password change via email or SMS
        """Change a user's password in the database.
        Args:
            userId (int): User ID.
            newPassword (str): New password.

        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        magic = PasswordUtils.password_hash(newPassword)

        user.passwordHash = magic[0]
        user.passwordSalt = magic[1]

        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_CHANGING_PASSWORD + " " + e)
            return (False, UMM.ERROR_CHANGING_PASSWORD)

        return (True, UMM.PASSWORD_CHANGED_SUCCESSFULLY, user)

    def delete(self, userId: int) -> Tuple[bool, str, Optional[Self: object]]:
        """<strong>Soft Delete</strong> Mark a user as deleted in the database. Phone and Email verification status will be reset.
        Args:
            userId (int): User ID
        
        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        user = User.query.get(userId)
        if not user:
            return (False, UMM.USER_NOT_FOUND)
        
        user.isDeleted = True
        user.isPhoneVerified = False  # Reset phone verification status
        user.isEmailVerified = False  # Reset email verification status
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_DELETING_USER + " " + e)
            return (False, UMM.ERROR_DELETING_USER)

        return (True, UMM.USER_DELETED_SUCCESSFULLY, user)
    
    @classmethod
    def login(cls, password: str, username: str = None, email: str = None, phone: str = None) -> Tuple[bool, str, Optional[Self: object]]:
        """Login a user by username, email, or phone and password. <br>
        Args:
            password(str): Password
            username(str): Username
            email(str): Email
            phone(str): Phone number
        Returns:
            Tuple: (success: bool, message: str, user: Optional[User])
        """
        # Find user by username, email, or phone
        conditions = []

        if username:
            conditions.append((User.username == username) & (User.isDeleted == False))
        if email:
            conditions.append((User.email == email) & (User.isDeleted == False))
        if phone:
            conditions.append((User.phone == phone) & (User.isDeleted == False))

        # Şimdi conditions listesinde 1 ya da daha fazla filtre var
        if not conditions:
            return (False, UMM.INVALID_USERNAME_OR_PASSWORD, None)

        user = User.query.filter(db.or_(*conditions)).first()
        if not user:
            return (False, UMM.USER_NOT_FOUND)

        if not PasswordUtils.validate_password(password, user.passwordHash, user.passwordSalt):
            return (False, UMM.INVALID_USERNAME_OR_PASSWORD)

        # Update last login time
        user.lastLogin = db.func.current_timestamp()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(UMM.ERROR_UPDATING_USER + " " + str(e))
            return (False, UMM.ERROR_UPDATING_USER, user)

        return (True, UMM.USER_LOGGED_IN_SUCCESSFULLY, user)
