"""
Transaction domain module.

This module exports the Transaction domain model for tracking financial transactions.
"""

from .transaction import Transaction, TransactionType

__all__ = ["Transaction", "TransactionType"]
