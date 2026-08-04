import pyotp

def generate_otp_secret() -> str:
    return pyotp.random_base32()

def verify_otp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
