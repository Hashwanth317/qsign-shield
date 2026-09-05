"""Safe, isolated environment configuration for backend tests."""

import os


os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-only-secret-key-with-at-least-32-characters"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["ALLOW_OPERATOR_REGISTRATION"] = "false"
