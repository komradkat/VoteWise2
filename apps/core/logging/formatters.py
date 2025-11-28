"""
Custom formatters for VoteWise logging system.
Provides colored console output and structured JSON logging.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors and icons to log messages.
    """
    
    # Level colors and icons
    LEVEL_COLORS = {
        'DEBUG': (Colors.BRIGHT_BLACK, '🔍'),
        'INFO': (Colors.BRIGHT_BLUE, 'ℹ️'),
        'WARNING': (Colors.BRIGHT_YELLOW, '⚠️'),
        'ERROR': (Colors.BRIGHT_RED, '❌'),
        'CRITICAL': (Colors.BG_RED + Colors.BRIGHT_WHITE, '🚨'),
        'SUCCESS': (Colors.BRIGHT_GREEN, '✅'),
        'SECURITY': (Colors.BRIGHT_MAGENTA, '🛡️'),
    }
    
    # Category colors
    CATEGORY_COLORS = {
        'SYSTEM': Colors.BRIGHT_CYAN,
        'FACE VERIFY': Colors.BRIGHT_BLUE,
        'FACE ENROLL': Colors.BRIGHT_GREEN,
        'SECURITY': Colors.BRIGHT_MAGENTA,
        'AUTH': Colors.YELLOW,
        'VOTE': Colors.GREEN,
        'ADMIN': Colors.MAGENTA,
        'DATABASE': Colors.CYAN,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors and structure"""
        
        # Get level color and icon
        level_color, level_icon = self.LEVEL_COLORS.get(
            record.levelname, 
            (Colors.WHITE, '•')
        )
        
        # Get category from record (if exists)
        category = getattr(record, 'category', 'SYSTEM')
        category_color = self.CATEGORY_COLORS.get(category, Colors.WHITE)
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Build the formatted message
        parts = [
            f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET}",
            f"{level_color}{level_icon} {record.levelname}{Colors.RESET}",
            f"{category_color}[{category}]{Colors.RESET}",
        ]
        
        # Add user context if available
        if hasattr(record, 'user') and record.user:
            parts.append(f"{Colors.BRIGHT_CYAN}[User: {record.user}]{Colors.RESET}")
        
        # Add IP if available
        if hasattr(record, 'ip') and record.ip:
            parts.append(f"{Colors.BRIGHT_BLACK}[IP: {record.ip}]{Colors.RESET}")
        
        # Add the main message
        message = record.getMessage()
        parts.append(f"{Colors.WHITE}{message}{Colors.RESET}")
        
        # Add extra data if available
        if hasattr(record, 'extra_data') and record.extra_data:
            extra_str = ' '.join([f"{k}={v}" for k, v in record.extra_data.items()])
            parts.append(f"{Colors.BRIGHT_BLACK}({extra_str}){Colors.RESET}")
        
        formatted = ' '.join(parts)
        
        # Add exception info if present
        if record.exc_info:
            formatted += '\n' + self.formatException(record.exc_info)
        
        return formatted


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs structured JSON logs for production/parsing.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON"""
        
        log_data: Dict[str, Any] = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'category': getattr(record, 'category', 'SYSTEM'),
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add user context
        if hasattr(record, 'user') and record.user:
            log_data['user'] = record.user
        
        # Add IP
        if hasattr(record, 'ip') and record.ip:
            log_data['ip'] = record.ip
        
        # Add extra data
        if hasattr(record, 'extra_data') and record.extra_data:
            log_data['extra'] = record.extra_data
        
        # Add exception info
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class PlainFormatter(logging.Formatter):
    """
    Simple plain text formatter for file logs (no colors).
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as plain text"""
        
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        category = getattr(record, 'category', 'SYSTEM')
        
        parts = [
            f"[{timestamp}]",
            f"[{record.levelname}]",
            f"[{category}]",
        ]
        
        if hasattr(record, 'user') and record.user:
            parts.append(f"[User: {record.user}]")
        
        if hasattr(record, 'ip') and record.ip:
            parts.append(f"[IP: {record.ip}]")
        
        parts.append(record.getMessage())
        
        if hasattr(record, 'extra_data') and record.extra_data:
            extra_str = ' '.join([f"{k}={v}" for k, v in record.extra_data.items()])
            parts.append(f"({extra_str})")
        
        formatted = ' '.join(parts)
        
        if record.exc_info:
            formatted += '\n' + self.formatException(record.exc_info)
        
        return formatted
