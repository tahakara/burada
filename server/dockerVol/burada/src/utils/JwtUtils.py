import jwt
import datetime
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

class JwtUtils:    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")  # JWT secret key from environment variable or default
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")  # Default to HS256 if not set
        # Default expiration times if not set in .env
        self.access_token_expiration = datetime.timedelta(seconds=int(os.getenv("JWT_EXPIRATION_TIME", 3600)))  # 1 hour
        self.refresh_token_expiration = datetime.timedelta(seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRATION_TIME", 3600 * 24 * 2)))  # 30 days

    def create_token(self, user_uuid: str, username: str, email: str) -> Dict[str, str]:
        """Creates a JWT token for the user.
        Args:
            user_uuid (str): User ID
            username (str): Username
            email (str): Email address
        Returns:
            Dict: (acces_token (str), refresh_token (str), username (str), email (str), uuid (str))
        """
        access_token = self.encode_auth_token(user_uuid, is_refresh_token=False)
        refresh_token = self.encode_auth_token(user_uuid, is_refresh_token=True)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'username': username,
            'email': email,
            'uuid': user_uuid,
        }

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validates the JWT token and returns user information.
        Args:
            token (str): JWT token
        Returns:
            Optinal[Dict]: Token content (user_uuid (str), username (str), email (str)) or None
        """
        payload = self.decode_auth_token(token)
        if payload:
            return {
                'user_uuid': payload['user_uuid'],
                'username': payload.get('username'),
                'email': payload.get('email'),
            }
        return None

    def encode_auth_token(self, user_uuid: str, is_refresh_token: bool = False) -> str:
        """Generates a JWT token for the user.
        Args:
            user_uuid (str): User ID
            is_refresh_token (str): Whether to generate a refresh token
        
        Returns: 
            str: JWT Token
        """
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + (
            self.refresh_token_expiration if is_refresh_token else self.access_token_expiration
        )

        payload = {
            'exp': expiration_time,
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'user_uuid': user_uuid  # Payload içinde taşıdığımız veri (kullanıcı ID'si)
        }

        # Token oluşturma
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_auth_token(self, auth_token: str) -> Optional[Dict[str, Any]]:
        """Validates the JWT token and returns user information.
        Args:
            auth_token (str): JWT token.
        
        Retuns:
            Optional[Dict]: Token content (user ID) or None
        """
        try:
            payload = jwt.decode(auth_token, self.secret_key, algorithms=[self.algorithm])
            return payload 
        except jwt.ExpiredSignatureError:
            return None  
        except jwt.InvalidTokenError:
            return None  

    def refresh_auth_token(self, refresh_token: str) -> Optional[str]:
        """Obtains a new access token using a valid refresh token.
        Args:
            refresh_token (str): Refresh token.
        
        Returns:
            Optional[str]: New access token or None if refresh token is invalid.
        """
        payload = self.decode_auth_token(refresh_token)

        if payload:
            user_uuid = payload['user_uuid']
            return self.encode_auth_token(user_uuid, is_refresh_token=False) 
        return None
