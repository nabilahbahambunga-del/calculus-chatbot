from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def normalize_password(password: str) -> str:
    # จำกัดความยาวไม่เกิน 72 bytes (bcrypt limit)
    return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

def hash_password(password: str):
    password = normalize_password(password)
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    plain_password = normalize_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)
