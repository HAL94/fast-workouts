from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_hashed_pw(password: str):
    return pwd_context.hash(password)
