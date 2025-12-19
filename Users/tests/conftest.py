# PETCARE/Users/tests/conftest.py

"""
This file intentionally keeps Users tests lightweight.

All shared fixtures (DB, async_client, RBAC tokens)
are defined in the root-level conftest.py.

Pytest will automatically discover and use them.
"""

# Optional re-exports for clarity (NOT required)
# These imports ensure IDE autocomplete and explicit dependency
from conftest import (  # noqa: F401
    async_client,
    db_session,
    owner_token,
    clinic_token,
    admin_token,
    welfare_token,
)