"""
FinSight — Phase 5: User, Account & Domain Relationships
========================================================

This phase introduces the User domain model and establishes proper object
relationships using composition and association.
"""

from .user import User
from .account import Account

__all__ = ["User", "Account"]
