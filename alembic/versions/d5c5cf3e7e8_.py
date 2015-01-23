"""empty message

Revision ID: d5c5cf3e7e8
Revises: 2258610c4832
Create Date: 2015-01-19 12:49:06.259732

"""

# revision identifiers, used by Alembic.
revision = 'd5c5cf3e7e8'
down_revision = '2258610c4832'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import DDL


def upgrade():
    #Note: alter type can't be run in a transaction, this needs transaction_per_migration=True in the context, too.
    if not op.get_context().as_sql:
        connection = op.get_bind()
        connection.execution_options(isolation_level='AUTOCOMMIT')
    op.execute(DDL("ALTER TYPE candidate_source ADD VALUE 'manual'"))
    op.execute(DDL("ALTER TYPE candidate_source ADD VALUE 'ale'"))

def downgrade():
    pass
