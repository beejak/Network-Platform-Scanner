"""
Role-Based Access Control using Casbin.
Supports multi-tenancy with per-tenant policies.
"""
import uuid
from typing import List, Optional

import casbin
import casbin_async_sqlalchemy_adapter


class RBACManager:
    """Manages RBAC policies with Casbin."""

    def __init__(self, db_url: str) -> None:
        # Casbin model definition
        self.model_conf = """
[request_definition]
r = sub, obj, act, tenant

[policy_definition]
p = sub, obj, act, tenant

[role_definition]
g = _, _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub, r.tenant) && r.obj == p.obj && r.act == p.act && r.tenant == p.tenant
"""
        # Initialize adapter (async SQLAlchemy)
        self.adapter = casbin_async_sqlalchemy_adapter.Adapter(db_url)
        self.enforcer = casbin.AsyncEnforcer(self.model_conf, self.adapter)

    async def check_permission(
        self, user_id: str, resource: str, action: str, tenant_id: str
    ) -> bool:
        """Check if user has permission for action on resource in tenant."""
        result: bool = await self.enforcer.enforce(user_id, resource, action, tenant_id)
        return result

    async def add_role_for_user(self, user_id: str, role: str, tenant_id: str) -> bool:
        """Assign role to user within a tenant."""
        result: bool = await self.enforcer.add_role_for_user(user_id, role, tenant_id)
        return result

    async def add_policy(
        self, role: str, resource: str, action: str, tenant_id: str
    ) -> bool:
        """Add permission policy for a role in a tenant."""
        result: bool = await self.enforcer.add_policy(role, resource, action, tenant_id)
        return result


# Default roles and permissions
DEFAULT_ROLES = {
    "admin": ["*", "*", "all"],  # Full access
    "operator": ["devices", "networks", "flows"],
    "viewer": ["read"],
}
