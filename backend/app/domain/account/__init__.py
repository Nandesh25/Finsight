# This file makes 'account' a Python package.
# It re-exports the Account class so users can write:
#     from app.domain.account import Account
# instead of:
#     from app.domain.account.account import Account

from app.domain.account.account import Account

__all__ = ["Account"]

