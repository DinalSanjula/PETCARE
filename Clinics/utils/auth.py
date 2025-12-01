from types import SimpleNamespace

async def get_current_user():
    """
    TEMPORARY placeholder.
    Real implementation should extract user from JWT/session.
    """
    # Returning a fake user object with id=1
    return SimpleNamespace(id=1)