from redis import Redis
from typing import Any, Optional
import random

import os
from dotenv import load_dotenv

load_dotenv()

from ..JwtUtils import JwtUtils

class RedisClientUtils:
    def __init__(self, host: str='127.0.0.1', port: int=6379, db: int=0, password: str=None):
        """
        Initialize Redis client with optional database and password.
        
        Args:
            host (str): Redis server hostname or IP address. Defaults to '127.0.0.1'.
            port (int): Redis server port. Defaults to 6379.
            db (int): Redis database number. Defaults to 0.
            password (str, optional): Redis server password. Defaults to None.
        """
        self.redis_host = os.getenv('REDIS_HOST', host)
        self.redis_port = int(os.getenv('REDIS_PORT', port))
        self.db = int(os.getenv('REDIS_DB', db))
        self.password = os.getenv('REDIS_PASSWORD', password)
        self.client = self._connect()

    def _connect(self) -> Redis:
        """
        Connect to Redis server.

        Returns:
            Redis: Redis client instance.
        """
        return Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True  # Decode responses as strings
        )

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Set key with optional expire time (ex in seconds).
        
        Args:
            key (str): The key to set.
            value (Any): The value to store.
            ex (int, optional): Expiry time in seconds. Defaults to None.

        Returns:
            bool: True if successful, False otherwise.
        """
        return self.client.set(key, value, ex=ex)

    def get(self, key: str) -> Optional[Any]:
        """
        Get value of a key.

        Args:
            key (str): The key to retrieve.

        Returns:
            Any: The value stored at the key, or None if not found.
        """
        return self.client.get(key)

    def delete(self, key: str) -> int:
        """
        Delete a key.

        Args:
            key (str): The key to delete.

        Returns:
            int: The number of keys that were removed.
        """
        return self.client.delete(key)

    def exists(self, key: str) -> bool:
        """
        Check if a key exists.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return self.client.exists(key) == 1

class AuthRedisClientUtils(RedisClientUtils):
    def __init__(self):
        """
        Initialize the AuthRedisClient with environment-based Redis configuration.
        """
        self.host = os.getenv('REDIS_AUTH_HOST', os.getenv('REDIS_HOST', '127.0.0.1'))
        self.port = int(os.getenv('REDIS_AUTH_PORT', os.getenv('REDIS_PORT', 6379)))
        self.password = os.getenv('REDIS_AUTH_PASSWORD', os.getenv('REDIS_PASSWORD', None))
        self.db = int(os.getenv('REDIS_AUTH_SESSIONS_DB', os.getenv('REDIS_DB', 0)))
        super().__init__(host=self.host, port=self.port, db=self.db, password=self.password)

    @staticmethod
    def _generate_whitelist_key(user_uuid: str, jwt_token: str) -> str:
        """
        Generate Redis key for whitelist.

        Args:
            user_uuid (str): User ID.

        Returns:
            str: Whitelist key.
        """
        return f"whitelist:{user_uuid}:{jwt_token}"

    @staticmethod
    def _generate_blacklist_key(user_uuid: str, jwt_token: str) -> str:
        """
        Generate Redis key for blacklist.

        Args:
            user_uuid (str): User ID.

        Returns:
            str: Blacklist key.
        """
        return f"blacklist:{user_uuid}:{jwt_token}"

    def whitelist_token(self, user_uuid: str, jwt_token: str, full_token: dict | str, expire_seconds: int = 3600) -> bool:
        """
        Add a token to the whitelist.

        Args:
            user_uuid (str): User ID.
            jwt_token (str): JWT token to whitelist.
            expire_seconds (int, optional): Token expiration time in seconds. Defaults to 3600.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        key = self._generate_whitelist_key(user_uuid, jwt_token)
        return self.set(key, str(full_token), ex=expire_seconds)

    def is_token_whitelisted(self, user_uuid: str, jwt_token: str) -> Optional[str]:
        """
        Get the whitelisted token for a user.

        Args:
            user_uuid (str): User ID.

        Returns:
            str or None: Whitelisted token if exists, else None.
        """
        key = self._generate_whitelist_key(user_uuid, jwt_token)
        return self.get(key)

    def delete_whitelisted_token(self, user_uuid: str, jwt_token: str) -> bool:
        """
        Delete a whitelisted token for a user.

        Args:
            user_uuid (str): User ID.

        Returns:
            bool: True if the token was deleted, False otherwise.
        """
        key = self._generate_whitelist_key(user_uuid, jwt_token)
        return self.delete(key)

    def blacklist_token(self, user_uuid: str, jwt_token: str, full_token: dict | str, expire_seconds: int = 3600) -> bool:
        """
        Add a token to the blacklist.

        Args:
            user_uuid (str): User ID.
            jwt_token (str): JWT token to blacklist.
            expire_seconds (int, optional): Token expiration time in seconds. Defaults to 3600.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        key = self._generate_blacklist_key(user_uuid, jwt_token)
        return self.set(key, str(full_token), ex=expire_seconds)

    def is_token_blacklisted(self, user_uuid: str, jwt_token: str, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            user_uuid (str): User ID.
            jwt_token (str): JWT token to check.

        Returns:
            bool: True if the token is blacklisted, False otherwise.
        """
        key = self._generate_blacklist_key(user_uuid, jwt_token)
        blacklisted_token = self.get(key)
        return blacklisted_token

    def delete_all_whitelisted_tokens_by_user_uuid(self, user_uuid: str) -> bool:
        """
        Delete all whitelisted tokens for a user.

        Args:
            user_uuid (str): User ID.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        keys = self.client.keys(f"whitelist:{user_uuid}:*")
        if not keys:
            return False
        if len(keys) < 1:
            return True 

        results = []

        for key in keys:
            result = self.blacklist_token(user_uuid, key.split(":")[2], self.get(key), expire_seconds=self.get_ttl(key))
            results.append(tuple(key.split(":")[2], result))
            
        return all(results) if len(results) > 0 else False

    def get_ttl(self, key: str) -> int:
        """
        Get the time-to-live (TTL) of a key in seconds.

        Args:
            key (str): The key to check the TTL for.

        Returns:
            int: Remaining TTL in seconds. -2 if the key does not exist, -1 if the key exists but has no expiration.
        """
        return self.client.ttl(key)

    def convert_token_whitelist_to_blacklist(self, user_uuid:str, jwt_token: str) -> bool:
        """
        Move token from whitelist to blacklist with the remaining expire time (logout operation).

        Args:
            token (str): Token to verify before moving.

        Returns:
            bool: True if successful, False otherwise.
        """
        user_uuid = JwtUtils.decode_auth_token(jwt_token)["user_uuid"]

        whitelist_key = self._generate_whitelist_key(user_uuid, jwt_token)
        full_token = self.get(whitelist_key)
        if full_token is None:
            return False

        ttl_seconds = self.get_ttl(whitelist_key)
        if ttl_seconds <= 0:
            ttl_seconds = 3600  # default to 1 hour if no TTL found

        self.blacklist_token(user_uuid, jwt_token, full_token, expire_seconds=ttl_seconds)
        self.delete_whitelisted_token(user_uuid, jwt_token)
        return True

class VerificaitonRedisClientUtils(RedisClientUtils):
    def __init__(self):
        """
        Initialize the AuthRedisClient with environment-based Redis configuration.
        """
        self.host = os.getenv('REDIS_AUTH_HOST', os.getenv('REDIS_HOST', '127.0.0.1'))
        self.port = int(os.getenv('REDIS_AUTH_PORT', os.getenv('REDIS_PORT', 6379)))
        self.password = os.getenv('REDIS_AUTH_PASSWORD', os.getenv('REDIS_PASSWORD', None))
        self.db = int(os.getenv('REDIS_AUTH_DB', os.getenv('REDIS_DB', 0)))+1
        super().__init__(host=self.host, port=self.port, db=self.db, password=self.password)

    @staticmethod
    def _generate_email_verification_key(self, user_uuid: str) -> str:
        """
        Generate Redis key for email verification.

        Args:
            user_uuid (str): User ID.

        Returns:
            str: Verification key.
        """
        return f"verification_email:{user_uuid}"
    
    @staticmethod
    def _generate_verification_code_key(self, user_uuid: str) -> str:
        """
        Generate Redis key for email verification code.

        Args:
            user_uuid (str): User ID.

        Returns:
            str: Verification code key.
        """
        return f"verification_code:{user_uuid}"
    
    @staticmethod
    def _generate_verification_code(self, digits: int = 6) -> str:
        """
        Generate a random verification code without repeating any character 3 or more times.

        Args:
            digits (int): Number of digits in the verification code.

        Returns:
            str: Random verification code.
        """
        while True:
            code = ''.join(random.choices('0123456789', k=digits))
            if all(code.count(char) < 3 for char in set(code)):
                return code

    def set_email_verificaiton_token(self, user_uuid: str, jwt_token: str, expire_seconds: int = 3600) -> bool:
        """
        Set email verification token in Redis.

        Args:
            user_uuid (str): User ID.
            jwt_token (str): JWT token for email verification.
            verification_code (str): Verification code to set.
            expire_seconds (int, optional): Expiration time in seconds. Defaults to 3600.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        key = self._generate_email_verification_key(user_uuid)
        if self.exists(key):
            return False
        
        return self.set(key, jwt_token, ex=expire_seconds)
    
    def set_verification_code(self, user_uuid: str, verification_code: str, expire_seconds: int = 180) -> bool:
        """
        Set email verification code in Redis.

        Args:
            user_uuid (str): User ID.
            verification_code (str): Verification code to set.
            expire_seconds (int, optional): Expiration time in seconds. Defaults to 180.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        # check user already seted other code 
        key = self._generate_verification_code_key(user_uuid)

        if self.exists(key):
            return False
        
        return self.set(key, verification_code, ex=expire_seconds)

    def verify_email_verificaiton_token(self, user_uuid: str, jwt_token: str) -> bool:
        """
        Verify email verification token in Redis.

        Args:
            user_uuid (str): User ID.
            jwt_token (str): JWT token for email verification.
            verification_code (str): Verification code to verify.

        Returns:
            bool: True if the verification code matches, False otherwise.
        """
        key = self._generate_email_verification_key(user_uuid, jwt_token)
        stored_code = self.get(key)

        if stored_code:
            self.delete(key)
            return True
        return False

    def verify_verification_code(self, user_uuid: str, verification_code: str) -> bool:
        """
        Verify email verification code in Redis.

        Args:
            user_uuid (str): User ID.
            verification_code (str): Verification code to verify.

        Returns:
            bool: True if the verification code matches, False otherwise.
        """

        key = self._generate_verification_code_key(user_uuid)
        stored_code = self.get(key)

        if stored_code == verification_code:
            self.delete(key)
            return True
        return False

    def delete_all_email_verificaiton_tokens_by_user_uuid(self, user_uuid: str) -> bool:
        """
        Delete all email verification tokens for a user.

        Args:
            user_uuid (str): User ID.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        keys = self.client.keys(f"verification_email:{user_uuid}:*")
        if not keys:
            return False
        if len(keys) < 1:
            return True 

        results = []

        for key in keys:
            result = self.delete(key)
            results.append(result)
            
        return all(results) if len(results) > 0 else False
    
    def delete_all_verification_codes_by_user_uuid(self, user_uuid: str) -> bool:
        """
        Delete all verification codes for a user.

        Args:
            user_uuid (str): User ID.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        keys = self.client.keys(f"verification_code:{user_uuid}:*")
        if not keys:
            return False
        if len(keys) < 1:
            return True 

        results = []

        for key in keys:
            result = self.delete(key)
            results.append(result)
            
        return all(results) if len(results) > 0 else False
    
    def delete_all_email_verification_tokens(self) -> bool:
        """
        Delete all email verification tokens.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        keys = self.client.keys("verification_email:*")
        if not keys:
            return False
        if len(keys) < 1:
            return True 

        results = []

        for key in keys:
            result = self.delete(key)
            results.append(result)
            
        return all(results) if len(results) > 0 else False
    
    def delete_all_verification_codes(self) -> bool:
        """
        Delete all verification codes.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        keys = self.client.keys("verification_code:*")
        if not keys:
            return False
        if len(keys) < 1:
            return True 

        results = []

        for key in keys:
            result = self.delete(key)
            results.append(result)
            
        return all(results) if len(results) > 0 else False