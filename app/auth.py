from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import hashlib
import secrets
import hmac

SECRET_KEY = "secret_key_for_homework_change_in_prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SALT_LENGTH = 32  # Длина соли в байтах

def get_password_hash(password: str) -> str:
    """
    Хеширует пароль с использованием соли и SHA-256.
    Возвращает строку формата: salt:hash
    """
    # Генерируем случайную соль
    salt = secrets.token_hex(SALT_LENGTH)
    # Создаем хеш из соли + пароля
    hash_object = hashlib.sha256((salt + password).encode('utf-8'))
    password_hash = hash_object.hexdigest()
    # Возвращаем соль и хеш вместе, разделенные двоеточием
    return f"{salt}:{password_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет пароль.
    Ожидает строку формата: salt:hash
    """
    try:
        # Разделяем сохраненную строку на соль и хеш
        salt, stored_hash = hashed_password.split(':')
        # Создаем хеш из введенного пароля с той же солью
        hash_object = hashlib.sha256((salt + plain_password).encode('utf-8'))
        calculated_hash = hash_object.hexdigest()
        # Сравниваем хеши
        return hmac.compare_digest(calculated_hash, stored_hash)
    except (ValueError, AttributeError):
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt