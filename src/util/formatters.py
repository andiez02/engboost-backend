
from typing import Dict


def pick_user(user: Dict) -> Dict:
    """
    Pick specific fields from a user dictionary.
    """
    if not user:
        return {}
    
    keys = ["_id", "email", "username", "displayName", "avatar", "role", "isActive", "createdAt", "updatedAt"]
    return {key: user[key] for key in keys if key in user}
