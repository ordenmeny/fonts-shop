from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["*"]

MEDIA_ROOT = BASE_DIR / "media_dev"
STATIC_ROOT = BASE_DIR / "static_dev"


CORS_ALLOWED_ORIGINS = [
    "https://fonts.unimatch.ru",
]

CSRF_TRUSTED_ORIGINS = [
    "https://fonts.unimatch.ru",
]


