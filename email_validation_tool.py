import re

def validate_email(email):
    # Simple regex for email validation
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    if re.match(pattern, email):
        return True, "Valid email"
    else:
        return False, "Invalid email"
