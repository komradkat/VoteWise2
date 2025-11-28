# VoteWise Enterprise Logging System

## Overview

Professional, color-coded logging system for the VoteWise application with structured output, file rotation, and category-based filtering.

## Features

- ✅ **Colored Console Output** - Beautiful, readable logs with icons and colors
- ✅ **Multiple Log Files** - Automatic categorization and rotation
- ✅ **Structured Logging** - JSON format for easy parsing
- ✅ **Security Audit Trail** - Dedicated security and audit logs
- ✅ **User Context** - Automatic user and IP tracking
- ✅ **File Rotation** - Automatic log rotation with configurable retention
- ✅ **Category Filtering** - Separate logs for different components

## Log Categories

| Category | Description | Example Use Case |
|----------|-------------|------------------|
| `SYSTEM` | Application lifecycle | Startup, shutdown, configuration |
| `FACE VERIFY` | Face verification | Login attempts, liveness checks |
| `FACE ENROLL` | Face enrollment | New face registrations |
| `SECURITY` | Security events | Spoofing attempts, breaches |
| `AUTH` | Authentication | Login, logout, session management |
| `VOTE` | Voting actions | Vote submission, results |
| `ADMIN` | Admin actions | User management, configuration |
| `DATABASE` | Database operations | Queries, connections |

## Log Levels

| Level | Icon | Color | Use Case |
|-------|------|-------|----------|
| `DEBUG` | 🔍 | Gray | Detailed diagnostic information |
| `INFO` | ℹ️ | Blue | General informational messages |
| `SUCCESS` | ✅ | Green | Successful operations |
| `WARNING` | ⚠️ | Yellow | Warning messages |
| `SECURITY` | 🛡️ | Magenta | Security-related events |
| `ERROR` | ❌ | Red | Error messages |
| `CRITICAL` | 🚨 | Red BG | Critical system failures |

## Log Files

All logs are stored in the `logs/` directory:

```
logs/
├── votewise.log              # All logs (plain text, 30 days retention)
├── security.log              # Security events only (90 days retention)
├── audit.log                 # Audit trail in JSON format (365 days retention)
├── errors.log                # Errors and critical events (60 days retention)
└── face_verification.log     # Face ID specific logs (30 days retention)
```

## Usage Examples

### Basic Logging

```python
from apps.core.logging import logger

# Simple info log
logger.info("Application started", category="SYSTEM")

# Debug with extra data
logger.debug("Loading config", category="SYSTEM", extra_data={'file': 'settings.py'})

# Success message
logger.success("User registered", category="AUTH", user="komradkat")
```

### Face Verification Logging

```python
# Face verification attempt
logger.face_verify(
    "Attempting verification",
    user="komradkat",
    ip="192.168.1.100",
    extra_data={'attempt': 1}
)

# Liveness check result
logger.face_verify(
    "Liveness check passed",
    user="komradkat",
    extra_data={'score': 0.966, 'is_real': True}
)

# Verification success
logger.success(
    "Face verified successfully",
    category="FACE VERIFY",
    user="komradkat",
    extra_data={'distance': 0.079}
)
```

### Security Events

```python
# Security warning
logger.security(
    "Fake face detected",
    user="attacker",
    extra_data={'score': 0.85, 'threshold': 0.95}
)

# Critical security event
logger.critical(
    "Multiple spoofing attempts",
    category="SECURITY",
    user="attacker",
    ip="192.168.1.200",
    extra_data={'attempts': 10}
)
```

### Exception Logging

```python
try:
    # Some operation
    process_data()
except Exception as e:
    logger.exception(
        "Failed to process data",
        category="SYSTEM",
        user="komradkat"
    )
```

### Category-Specific Methods

```python
# Authentication
logger.auth("User logged in", user="komradkat", ip="192.168.1.100")

# Voting
logger.vote("Vote submitted", user="komradkat", extra_data={'election': 'SC 2025'})

# Admin actions
logger.admin_action("Voter verified", user="admin", extra_data={'voter': 'komradkat'})

# Database
logger.database("Query executed", extra_data={'table': 'users', 'time': '0.05s'})
```

## Console Output Example

```
[2025-11-28 10:12:45.123] ℹ️ INFO [SYSTEM] Application started
[2025-11-28 10:12:46.456] ✅ SUCCESS [AUTH] [User: komradkat] [IP: 192.168.1.100] User logged in successfully
[2025-11-28 10:12:47.789] 🔍 DEBUG [FACE VERIFY] [User: komradkat] Liveness check initiated (score=0.966)
[2025-11-28 10:12:48.012] ✅ SUCCESS [FACE VERIFY] [User: komradkat] Face verified successfully (distance=0.079)
[2025-11-28 10:12:49.345] 🛡️ SECURITY [SECURITY] [User: upup] Fake face detected (score=0.901 threshold=0.95)
[2025-11-28 10:12:50.678] ❌ ERROR [DATABASE] Database connection failed (host=localhost port=5432)
```

## File Output Example (Plain Text)

```
[2025-11-28 10:12:45.123] [INFO] [SYSTEM] Application started
[2025-11-28 10:12:46.456] [SUCCESS] [AUTH] [User: komradkat] [IP: 192.168.1.100] User logged in successfully
[2025-11-28 10:12:47.789] [DEBUG] [FACE VERIFY] [User: komradkat] Liveness check initiated (score=0.966)
```

## File Output Example (JSON - Audit Log)

```json
{"timestamp": "2025-11-28T10:12:46.456", "level": "SUCCESS", "category": "AUTH", "message": "User logged in successfully", "module": "views", "function": "login_view", "line": 42, "user": "komradkat", "ip": "192.168.1.100"}
{"timestamp": "2025-11-28T10:12:50.123", "level": "INFO", "category": "VOTE", "message": "Vote submitted", "module": "views", "function": "submit_vote", "line": 156, "user": "komradkat", "extra": {"election": "Student Council 2025", "position": "President"}}
```

## Configuration

The logging system is automatically configured with sensible defaults. To customize:

1. Edit `apps/core/logging/logger.py` to adjust file paths or retention
2. Modify `apps/core/logging/formatters.py` to change colors or format
3. Update `apps/core/logging/handlers.py` to add custom handlers

## Running the Demo

To see all logging features in action:

```bash
python demo_logging.py
```

This will generate sample logs in all categories and create the log files in the `logs/` directory.

## Best Practices

1. **Use appropriate log levels**: DEBUG for development, INFO for normal operations, WARNING/ERROR for issues
2. **Include context**: Always include user, IP, and relevant data
3. **Use categories**: Helps with filtering and analysis
4. **Don't log sensitive data**: Passwords, tokens, etc. should never be logged
5. **Use extra_data**: For structured information that can be parsed later

## Integration

The logger is already integrated into:
- ✅ Face verification (`apps/biometrics/views.py`)
- ⏳ Authentication (to be added)
- ⏳ Voting system (to be added)
- ⏳ Admin panel (to be added)

## Monitoring

Check logs regularly:

```bash
# View all logs
tail -f logs/votewise.log

# View security events only
tail -f logs/security.log

# View errors
tail -f logs/errors.log

# Search for specific user
grep "komradkat" logs/votewise.log

# Search for security events
grep "SECURITY" logs/security.log
```

## Troubleshooting

**Logs not appearing?**
- Check that the `logs/` directory exists and is writable
- Verify the logger is imported: `from apps.core.logging import logger`

**Colors not showing?**
- Colors only appear in terminal output, not in files
- Some terminals don't support ANSI colors

**Too many log files?**
- Adjust `backupCount` in `handlers.py` to keep fewer rotated files
- Adjust `maxBytes` to change when files rotate
