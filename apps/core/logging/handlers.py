"""
Custom log handlers for VoteWise logging system.
Provides file rotation, filtering, and specialized handlers.
"""

import logging
import logging.handlers
import os
from pathlib import Path


class CategoryFileHandler(logging.handlers.RotatingFileHandler):
    """
    File handler that only logs messages from specific categories.
    """
    
    def __init__(self, filename, category=None, maxBytes=10485760, backupCount=30, **kwargs):
        """
        Initialize the handler.
        
        Args:
            filename: Path to log file
            category: Category to filter (None = all categories)
            maxBytes: Maximum file size before rotation (default 10MB)
            backupCount: Number of backup files to keep (default 30)
        """
        # Ensure directory exists
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, **kwargs)
        self.category = category
    
    def emit(self, record):
        """Emit a record if it matches the category filter"""
        if self.category is None or getattr(record, 'category', None) == self.category:
            super().emit(record)


class SecurityFileHandler(logging.handlers.RotatingFileHandler):
    """
    Specialized handler for security-related logs.
    Only logs WARNING level and above for security events.
    """
    
    def __init__(self, filename, maxBytes=10485760, backupCount=90, **kwargs):
        """
        Initialize the security handler.
        
        Args:
            filename: Path to security log file
            maxBytes: Maximum file size before rotation (default 10MB)
            backupCount: Number of backup files to keep (default 90 for 3 months)
        """
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, **kwargs)
        self.setLevel(logging.WARNING)
    
    def emit(self, record):
        """Emit security-related records"""
        category = getattr(record, 'category', '')
        if 'SECURITY' in category or 'FACE' in category or record.levelno >= logging.WARNING:
            super().emit(record)


class AuditFileHandler(logging.handlers.RotatingFileHandler):
    """
    Specialized handler for audit trail logs.
    Logs voting, admin actions, and authentication events.
    """
    
    AUDIT_CATEGORIES = {'VOTE', 'ADMIN', 'AUTH', 'FACE ENROLL'}
    
    def __init__(self, filename, maxBytes=10485760, backupCount=365, **kwargs):
        """
        Initialize the audit handler.
        
        Args:
            filename: Path to audit log file
            maxBytes: Maximum file size before rotation (default 10MB)
            backupCount: Number of backup files to keep (default 365 for 1 year)
        """
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, **kwargs)
    
    def emit(self, record):
        """Emit audit-related records"""
        category = getattr(record, 'category', '')
        if category in self.AUDIT_CATEGORIES:
            super().emit(record)


class ErrorFileHandler(logging.handlers.RotatingFileHandler):
    """
    Handler that only logs ERROR and CRITICAL level messages.
    """
    
    def __init__(self, filename, maxBytes=10485760, backupCount=60, **kwargs):
        """
        Initialize the error handler.
        
        Args:
            filename: Path to error log file
            maxBytes: Maximum file size before rotation (default 10MB)
            backupCount: Number of backup files to keep (default 60)
        """
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount, **kwargs)
        self.setLevel(logging.ERROR)
