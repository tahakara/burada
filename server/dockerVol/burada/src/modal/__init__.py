from flask import Request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import text
from typing import Type, Any

db = SQLAlchemy()

from modal.RequestInfo import RequestInfo
from modal.User import User

def add_and_commit(db=db, obj: SQLAlchemy = None) -> None:
    """Add an object to the session and commit it."""
    if obj is None:
        return None
    db.session.add(obj)
    db.session.commit()

def save_request_info(db=db, request: Request = None, dust: str=None, dust_device: str=None) -> None:
    """Save request information to the database."""
    from modal.RequestInfo import RequestInfo  
    if request is None:
        return None
    request_info = RequestInfo.create_request_info(request, dust, dust_device)
    add_and_commit(db, request_info)

def select_uuid(db=db) -> str:
    """Select a UUID from the database."""
    result = db.session.execute(text("SELECT UUID()")).fetchone()
    return result[0]
