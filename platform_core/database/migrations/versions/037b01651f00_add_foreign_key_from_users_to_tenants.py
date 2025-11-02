"""Add foreign key from users to tenants

Revision ID: 037b01651f00
Revises: eca150f30ef7
Create Date: 2025-11-02 01:40:16.444519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '037b01651f00'
down_revision = 'eca150f30ef7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_tenants_tenant_id", "tenants", ["tenant_id"])
    op.create_foreign_key(
        "fk_users_tenant_id",
        "users",
        "tenants",
        ["tenant_id"],
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_tenant_id", "users", type_="foreignkey")
    op.drop_constraint("uq_tenants_tenant_id", "tenants", type_="unique")
