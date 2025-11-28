"""
VoteWise Logging System Demo
Demonstrates all logging features and output formats.
"""

from apps.core.logging import logger


def demo_logging():
    """Demonstrate all logging features"""
    
    print("\n" + "="*80)
    print("VoteWise Enterprise Logging System Demo")
    print("="*80 + "\n")
    
    # System logs
    logger.info("Application started successfully", category="SYSTEM")
    logger.debug("Loading configuration", category="SYSTEM", extra_data={'config_file': 'settings.py'})
    
    # Authentication logs
    logger.auth("User login attempt", user="komradkat", ip="192.168.1.100")
    logger.success("User logged in successfully", category="AUTH", user="komradkat", ip="192.168.1.100")
    
    # Face verification logs
    logger.face_verify(
        "Attempting face verification",
        user="komradkat",
        ip="192.168.1.100",
        extra_data={'attempt': 1}
    )
    
    logger.face_verify(
        "Liveness check passed",
        user="komradkat",
        extra_data={'score': 0.966, 'is_real': True}
    )
    
    logger.success(
        "Face verification successful",
        category="FACE VERIFY",
        user="komradkat",
        extra_data={'distance': 0.079}
    )
    
    # Security events
    logger.security(
        "Liveness check failed - fake face detected",
        user="upup",
        extra_data={'score': 0.901, 'threshold': 0.95}
    )
    
    logger.warning(
        "Multiple failed login attempts detected",
        category="SECURITY",
        user="upup",
        ip="192.168.1.200",
        extra_data={'attempts': 5}
    )
    
    # Face enrollment
    logger.face_enroll(
        "Face enrollment initiated",
        user="newuser",
        ip="192.168.1.150"
    )
    
    logger.success(
        "Face enrolled successfully",
        category="FACE ENROLL",
        user="newuser",
        extra_data={'quality': 0.95}
    )
    
    # Voting logs
    logger.vote(
        "Vote submitted",
        user="komradkat",
        extra_data={'election': 'Student Council 2025', 'position': 'President'}
    )
    
    # Admin actions
    logger.admin_action(
        "Voter verified by admin",
        user="admin",
        extra_data={'voter': 'komradkat', 'action': 'verify'}
    )
    
    # Error logs
    logger.error(
        "Database connection failed",
        category="DATABASE",
        extra_data={'host': 'localhost', 'port': 5432}
    )
    
    logger.critical(
        "Critical system failure",
        category="SYSTEM",
        extra_data={'component': 'authentication'}
    )
    
    # Exception logging
    try:
        raise ValueError("This is a test exception")
    except Exception as e:
        logger.exception(
            "An error occurred during processing",
            category="SYSTEM",
            user="testuser"
        )
    
    print("\n" + "="*80)
    print("Demo complete! Check the logs/ directory for output files:")
    print("  - logs/votewise.log          (all logs)")
    print("  - logs/security.log          (security events)")
    print("  - logs/audit.log             (audit trail - JSON)")
    print("  - logs/errors.log            (errors only)")
    print("  - logs/face_verification.log (face ID logs)")
    print("="*80 + "\n")


if __name__ == '__main__':
    demo_logging()
