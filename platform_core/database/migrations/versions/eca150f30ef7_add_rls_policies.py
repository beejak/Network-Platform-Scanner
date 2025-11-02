"""Add RLS policies

Revision ID: eca150f30ef7
Revises: b8e8931b11bb
Create Date: 2025-11-02 01:38:44.225546

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eca150f30ef7'
down_revision = 'b8e8931b11bb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE FUNCTION get_current_tenant_id() RETURNS UUID AS $$
    BEGIN
        RETURN current_setting('app.current_tenant')::uuid;
    EXCEPTION
        WHEN OTHERS THEN
            RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;")
    op.execute("CREATE POLICY tenant_isolation_policy ON tenants USING (tenant_id = get_current_tenant_id());")
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute("CREATE POLICY tenant_isolation_policy ON users USING (tenant_id = get_current_tenant_id());")


def downgrade() -> None:
    op.execute("DROP POLICY tenant_isolation_policy ON users;")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")
    op.execute("DROP POLICY tenant_isolation_policy ON tenants;")
    op.execute("ALTER TABLE tenants DISABLE ROW LEVEL SECURITY;")
    op.execute("DROP FUNCTION get_current_tenant_id();")
