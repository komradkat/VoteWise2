# VoteWise2 Logger - Quick Reference Guide

## Import

```python
from apps.core.logging import logger
```

## Basic Usage

### Log Levels

```python
# Debug (development only)
logger.debug("Detailed diagnostic info", category="SYSTEM")

# Info (general information)
logger.info("User action completed", category="SYSTEM")

# Success (successful operations)
logger.success("Operation completed successfully", category="SYSTEM")

# Warning (potential issues)
logger.warning("Unusual activity detected", category="SYSTEM")

# Error (errors that don't crash the app)
logger.error("Failed to process request", category="SYSTEM")

# Critical (severe errors)
logger.critical("System failure", category="SYSTEM")

# Security (security-related events)
logger.security("Unauthorized access attempt", category="SECURITY")
```

## Category-Specific Methods

### Authentication
```python
logger.auth("User logged in", user="komradkat", ip="192.168.1.1")
logger.auth("Password reset completed", user="komradkat")
```

### Voting
```python
logger.vote("Vote submitted", user="komradkat", extra_data={'election_id': 1})
logger.vote("Vote processing error", user="komradkat")
```

### Election Management
```python
logger.election("Created election: SC 2025", user="admin", extra_data={'election_id': 1})
logger.election("Updated position: President", user="admin", extra_data={'position_id': 5})
```

### Candidate Management
```python
logger.candidate("Registered candidate: John Doe", user="admin", extra_data={'candidate_id': 10})
logger.candidate("Updated candidate profile", user="admin", extra_data={'candidate_id': 10})
```

### Voter Management
```python
logger.voter_mgmt("Verified voter: komradkat", user="admin")
logger.voter_mgmt("Bulk verified 50 voters", user="admin", extra_data={'count': 50})
```

### Admin Actions
```python
logger.admin_action("Created administrator", user="superadmin", extra_data={'admin_id': 3})
logger.admin_action("Updated admin profile", user="admin")
```

### Timeline Management
```python
logger.timeline("Created timeline event", user="admin", extra_data={'event_id': 7})
logger.timeline("Deleted timeline event", user="admin")
```

### Face Biometrics
```python
logger.face_verify("Face verification successful", user="komradkat", extra_data={'distance': 0.079})
logger.face_enroll("Face enrolled for user", user="admin", extra_data={'enrolled_user': 'komradkat'})
```

### Email Operations
```python
logger.email("Welcome email sent", extra_data={'recipient': 'user@example.com'})
logger.email("Bulk email sent", extra_data={'sent_count': 100, 'total': 150})
```

### Security Events
```python
logger.security("Failed login attempt", user="attacker", ip="192.168.1.200", extra_data={'attempts': 5})
logger.security("Fake face detected", user="attacker", extra_data={'score': 0.85})
logger.security("Profile edit blocked during election", user="komradkat")
```

## Advanced Usage

### With Exception Handling
```python
try:
    # Some operation
    process_data()
except Exception as e:
    logger.exception(
        "Failed to process data",
        category="SYSTEM",
        user="komradkat",
        extra_data={'error': str(e)}
    )
```

### With IP Address
```python
ip = request.META.get('REMOTE_ADDR')
logger.auth("User logged in", user="komradkat", ip=ip)
```

### With Extra Data
```python
logger.vote(
    "Vote submitted",
    user="komradkat",
    extra_data={
        'election_id': 1,
        'election_name': 'SC 2025',
        'positions_voted': 5,
        'timestamp': datetime.now().isoformat()
    }
)
```

## Best Practices

### ✅ DO

```python
# Include user context
logger.admin_action("Created election", user=request.user.username)

# Include relevant data
logger.vote("Vote submitted", user=user.username, extra_data={'election_id': election.id})

# Use appropriate categories
logger.security("Failed login", user=username, category="SECURITY")

# Log important business events
logger.voter_mgmt("Verified voter", user=admin.username)
```

### ❌ DON'T

```python
# Don't log sensitive data
logger.info(f"Password: {password}")  # NEVER!
logger.info(f"Token: {token}")  # NEVER!

# Don't use generic messages
logger.info("Something happened")  # Too vague

# Don't log in tight loops
for i in range(10000):
    logger.debug(f"Processing {i}")  # Too much noise

# Don't use wrong categories
logger.vote("User logged in")  # Wrong category
```

## Common Patterns

### User Registration
```python
logger.auth(f"New user registered: {user.username}", user=user.username, extra_data={'email': user.email})
logger.face_enroll(f"Face enrolled for new user: {user.username}", user=user.username)
```

### Voter Verification
```python
logger.voter_mgmt(f"Verified voter: {voter.user.username}", user=request.user.username)
```

### Election Creation
```python
logger.election(f"Created election: {election.name}", user=request.user.username, extra_data={'election_id': election.id})
```

### Failed Security Event
```python
logger.security(
    f"Spoofing attempt detected",
    user=username,
    extra_data={'liveness_score': score, 'threshold': threshold}
)
```

### Email Notification
```python
logger.email(
    f"Sent {sent_count} election notifications",
    extra_data={
        'election_id': election.id,
        'notification_type': 'started',
        'sent_count': sent_count
    }
)
```

## Viewing Logs

### Console (Development)
Logs appear in the terminal with colors and icons:
```
[2025-12-01 10:20:45] ✅ SUCCESS [AUTH] [User: komradkat] User logged in successfully
[2025-12-01 10:20:46] ℹ️ INFO [VOTE] [User: komradkat] Vote submitted (election_id=1)
[2025-12-01 10:20:47] 🛡️ SECURITY [SECURITY] [User: attacker] Failed login attempt
```

### Log Files (Production)
```bash
# View all logs
tail -f logs/votewise.log

# View security events
tail -f logs/security.log

# View errors
tail -f logs/errors.log

# View audit trail (JSON)
tail -f logs/audit.log

# Search for specific user
grep "komradkat" logs/votewise.log

# Search for specific category
grep "ELECTION" logs/votewise.log

# Search for errors
grep "ERROR" logs/errors.log
```

## Log Rotation

Logs automatically rotate when they reach 10MB:
- `votewise.log` → `votewise.log.1`, `votewise.log.2`, etc.
- Old logs are automatically deleted based on retention policy
- No manual intervention needed

## Troubleshooting

### Logs not appearing?
1. Check that `logs/` directory exists
2. Verify logger is imported: `from apps.core.logging import logger`
3. Check file permissions on `logs/` directory

### Colors not showing?
- Colors only appear in terminal, not in files
- Some terminals don't support ANSI colors
- This is normal and doesn't affect functionality

### Too many log files?
- Adjust `backupCount` in `apps/core/logging/handlers.py`
- Reduce retention period if needed

## Quick Reference Table

| Method | Category | Use For |
|--------|----------|---------|
| `logger.auth()` | AUTH | Login, logout, registration |
| `logger.vote()` | VOTE | Vote submission, errors |
| `logger.election()` | ELECTION | Elections, positions, partylists |
| `logger.candidate()` | CANDIDATE | Candidate registration/updates |
| `logger.voter_mgmt()` | VOTER_MGMT | Voter verification, rejection |
| `logger.admin_action()` | ADMIN | General admin operations |
| `logger.timeline()` | TIMELINE | Timeline events |
| `logger.face_verify()` | FACE VERIFY | Face verification |
| `logger.face_enroll()` | FACE ENROLL | Face enrollment |
| `logger.email()` | EMAIL | Email operations |
| `logger.security()` | SECURITY | Security events |
| `logger.info()` | SYSTEM | General information |
| `logger.error()` | SYSTEM | Errors |
| `logger.warning()` | SYSTEM | Warnings |

## Need Help?

- See `apps/core/logging/README.md` for detailed documentation
- See `docs/LOGGING_COVERAGE.md` for complete business process coverage
- See `docs/LOGGING_IMPLEMENTATION.md` for implementation details
