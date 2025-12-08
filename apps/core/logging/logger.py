"""
VoteWise Enterprise Logger
Main logging interface for the entire application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from .formatters import ColoredFormatter, JSONFormatter, PlainFormatter
from .handlers import (
    CategoryFileHandler,
    SecurityFileHandler,
    AuditFileHandler,
    ErrorFileHandler
)


# Custom log level for SUCCESS
SUCCESS_LEVEL = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL, 'SUCCESS')

# Custom log level for SECURITY
SECURITY_LEVEL = 35  # Between WARNING (30) and ERROR (40)
logging.addLevelName(SECURITY_LEVEL, 'SECURITY')


class VoteWiseLogger:
    """
    Enterprise logging system for VoteWise.
    Provides colored console output and structured file logging.
    """
    
    def __init__(self, name: str = 'votewise'):
        """Initialize the logger with all handlers"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Get project root
        project_root = Path(__file__).parent.parent.parent.parent
        logs_dir = project_root / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        # Console Handler (colored, for development)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        # Main log file (all logs, plain text)
        main_handler = CategoryFileHandler(
            logs_dir / 'votewise.log',
            category=None,  # All categories
            maxBytes=10485760,  # 10MB
            backupCount=30
        )
        main_handler.setFormatter(PlainFormatter())
        self.logger.addHandler(main_handler)
        
        # Security log file
        security_handler = SecurityFileHandler(
            logs_dir / 'security.log',
            maxBytes=10485760,
            backupCount=90  # 3 months
        )
        security_handler.setFormatter(PlainFormatter())
        self.logger.addHandler(security_handler)
        
        # Audit log file (JSON for easy parsing)
        audit_handler = AuditFileHandler(
            logs_dir / 'audit.log',
            maxBytes=10485760,
            backupCount=365  # 1 year
        )
        audit_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(audit_handler)
        
        # Error log file
        error_handler = ErrorFileHandler(
            logs_dir / 'errors.log',
            maxBytes=10485760,
            backupCount=60
        )
        error_handler.setFormatter(PlainFormatter())
        self.logger.addHandler(error_handler)
        
        # Face verification specific log
        face_verify_handler = CategoryFileHandler(
            logs_dir / 'face_verification.log',
            category='FACE VERIFY',
            maxBytes=5242880,  # 5MB
            backupCount=30
        )
        face_verify_handler.setFormatter(PlainFormatter())
        self.logger.addHandler(face_verify_handler)
    
    def _log(self, level: int, message: str, category: str = 'SYSTEM', 
             user: Optional[str] = None, ip: Optional[str] = None, 
             extra_data: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Internal logging method.
        
        Args:
            level: Log level
            message: Log message
            category: Log category
            user: Username (if applicable)
            ip: IP address (if applicable)
            extra_data: Additional data to log
            **kwargs: Additional keyword arguments
        """
        extra = {
            'category': category,
            'user': user,
            'ip': ip,
            'extra_data': extra_data or {}
        }
        self.logger.log(level, message, extra=extra, **kwargs)
    
    # Convenience methods for different log levels
    
    def debug(self, message: str, category: str = 'SYSTEM', **kwargs):
        """Log a debug message"""
        self._log(logging.DEBUG, message, category, **kwargs)
    
    def info(self, message: str, category: str = 'SYSTEM', **kwargs):
        """Log an info message"""
        self._log(logging.INFO, message, category, **kwargs)
    
    def warning(self, message: str, category: str = 'SYSTEM', **kwargs):
        """Log a warning message"""
        self._log(logging.WARNING, message, category, **kwargs)
    
    def error(self, message: str, category: str = 'SYSTEM', **kwargs):
        """Log an error message"""
        self._log(logging.ERROR, message, category, **kwargs)
    
    def critical(self, message: str, category: str = 'SYSTEM', **kwargs):
        """Log a critical message"""
        self._log(logging.CRITICAL, message, category, **kwargs)
    
    def success(self, message: str, category: str = 'SYSTEM', **kwargs):
        """Log a success message"""
        self._log(SUCCESS_LEVEL, message, category, **kwargs)
    
    def security(self, message: str, category: str = 'SECURITY', **kwargs):
        """Log a security event"""
        self._log(SECURITY_LEVEL, message, category, **kwargs)
    
    # Category-specific convenience methods
    
    def face_verify(self, message: str, user: Optional[str] = None, **kwargs):
        """Log a face verification event"""
        self._log(logging.INFO, message, 'FACE VERIFY', user=user, **kwargs)
    
    def face_enroll(self, message: str, user: Optional[str] = None, **kwargs):
        """Log a face enrollment event"""
        self._log(logging.INFO, message, 'FACE ENROLL', user=user, **kwargs)
    
    def auth(self, message: str, user: Optional[str] = None, **kwargs):
        """Log an authentication event"""
        self._log(logging.INFO, message, 'AUTH', user=user, **kwargs)
    
    def vote(self, message: str, user: Optional[str] = None, **kwargs):
        """Log a voting event"""
        self._log(logging.INFO, message, 'VOTE', user=user, **kwargs)
    
    def admin_action(self, message: str, user: Optional[str] = None, **kwargs):
        """Log an admin action"""
        self._log(logging.INFO, message, 'ADMIN', user=user, **kwargs)
    
    def election(self, message: str, user: Optional[str] = None, **kwargs):
        """Log an election management event"""
        self._log(logging.INFO, message, 'ELECTION', user=user, **kwargs)
    
    def candidate(self, message: str, user: Optional[str] = None, **kwargs):
        """Log a candidate management event"""
        self._log(logging.INFO, message, 'CANDIDATE', user=user, **kwargs)
    
    def voter_mgmt(self, message: str, user: Optional[str] = None, **kwargs):
        """Log a voter management event"""
        self._log(logging.INFO, message, 'VOTER_MGMT', user=user, **kwargs)
    
    def timeline(self, message: str, user: Optional[str] = None, **kwargs):
        """Log a timeline event"""
        self._log(logging.INFO, message, 'TIMELINE', user=user, **kwargs)
    
    def email(self, message: str, **kwargs):
        """Log an email operation"""
        self._log(logging.INFO, message, 'EMAIL', **kwargs)
    
    def database(self, message: str, **kwargs):
        """Log a database operation"""
        self._log(logging.DEBUG, message, 'DATABASE', **kwargs)
    
    # Exception logging
    
    def exception(self, message: str, category: str = 'SYSTEM', **kwargs):
        """Log an exception with stack trace"""
        self.logger.exception(message, extra={
            'category': category,
            'user': kwargs.get('user'),
            'ip': kwargs.get('ip'),
            'extra_data': kwargs.get('extra_data', {})
        })


# Create singleton instance
logger = VoteWiseLogger()
