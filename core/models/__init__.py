
# cgai/models/__init__.py

# Create the SQLAlchemy instance before importing modules that use it
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import data models
from .user import User


__all__ = [
    "db",
    "User"
]