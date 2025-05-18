# databsede password hash alanım ve password salt alanım var ve 128 karakter limiti var ikisinin de ayrı ayrı mysql kullanıyorum be string olarak tutuyorum
import hashlib
import secrets
from typing import Optional, Tuple

class PasswordUtils:
    """Utility class for password hashing and validation."""

    @staticmethod
    def validate_password(password: str, password_hash: str, salt: str) -> bool:
        """Validate a password against a stored hash and salt.
        
        Args:
            password (str): The password to validate.
            password_hash (str): The stored hashed password.
            salt (str): The stored salt used for hashing.
            
        Returns:
            bool: True if the password is valid, False otherwise.
        """
        # Hash the provided password with the same salt
        hashed_password, _ = PasswordUtils.password_hash(password, salt)
        
        # Compare the hashed password with the stored hash
        return hashed_password == password_hash

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """Generate a random salt for password hashing.
        
        Args:
            length (int): The length of the salt.
            
        Returns:
            str: The generated salt.
        """
        # Using `secrets` to generate a secure random salt
        salt = secrets.token_hex(length)
        return salt

    @staticmethod
    def password_hash(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a password with an optional salt.
        
        Args:
            password (str): The password to hash.
            salt (str, optional): The salt to use for hashing. If None, a new salt will be generated.
        
        Returns:
            tuple[str, str]: TThe hashed password and the used salt.
        
        """
        if salt is None:
            salt = PasswordUtils.generate_salt()
        
        # Hash the password with the salt using sha256
        hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        
        return hashed_password, salt
