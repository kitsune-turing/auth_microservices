"""Password hashing service using BCrypt.

This adapter implements the PasswordServicePort interface.
"""
import logging
import bcrypt

from src.core.ports.repository_ports import PasswordServicePort

logger = logging.getLogger(__name__)


class BcryptPasswordService(PasswordServicePort):
    """BCrypt implementation of password hashing."""
    
    def __init__(self, rounds: int = 12):
        """
        Initialize BCrypt service.
        
        Args:
            rounds: Cost factor for BCrypt (default: 12)
                   Higher values are more secure but slower
        """
        self.rounds = rounds
        logger.info(f"BCrypt password service initialized with rounds={rounds}")
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using BCrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password as string
        """
        try:
            # Convert password to bytes
            password_bytes = password.encode('utf-8')
            
            # Generate salt and hash
            salt = bcrypt.gensalt(rounds=self.rounds)
            hashed = bcrypt.hashpw(password_bytes, salt)
            
            # Return as string
            return hashed.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Password hashing failed: {str(e)}")
            raise
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            password_hash: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            # Convert to bytes
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            
            # Verify
            return bcrypt.checkpw(password_bytes, hash_bytes)
            
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return False


__all__ = ["BcryptPasswordService"]
