import re

VPA_PATTERN = re.compile(r'([a-zA-Z0-9.\-_]{2})[a-zA-Z0-9.\-_]+(@[a-zA-Z0-9.\-_]+)')
PHONE_PATTERN = re.compile(r'\b(?:\+?91[\-\s]?)?[6789]\d{9}\b')
PAN_PATTERN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')

SELF_TRANSFER_KEYWORDS = [
    "SELF", "OWN ACC", "CONTRA", "INTERNAL TRF", "SWEEP", "AUTO SWEEP", "TRANSFER TO SELF"
]

def mask_pii(narration: str) -> str:
    """Masks VPAs, account numbers, phone numbers, and PANs to ensure DPDP/GDPR compliance."""
    if not isinstance(narration, str):
        return ""
    
    masked = narration
    # Mask UPI IDs (e.g., suresh.design@icici -> su***@icici)
    masked = VPA_PATTERN.sub(r'\1***\2', masked)
    # Mask Phone Numbers (e.g., 9823012345 -> 98******45)
    masked = PHONE_PATTERN.sub(lambda m: m.group(0)[:2] + "*" * (len(m.group(0)) - 4) + m.group(0)[-2:], masked)
    # Mask Account numbers (length 8-18)
    masked = re.sub(r'\b\d{8,18}\b', lambda m: "XXXX" + m.group(0)[-4:], masked)
    # Mask PAN
    masked = PAN_PATTERN.sub(r'XXXXX\g<0>[5:9]X', masked)
    
    return masked

def is_self_transfer(narration: str) -> bool:
    """Detects circular/self-transfers between user's own accounts to prevent artificial turnover inflation."""
    if not isinstance(narration, str):
        return False
    upper = narration.upper()
    return any(keyword in upper for keyword in SELF_TRANSFER_KEYWORDS)