"""empty message

Revision ID: 4934034dd9fd
Revises: d5c5cf3e7e8
Create Date: 2015-02-09 15:04:24.406112

"""

# revision identifiers, used by Alembic.
revision = '4934034dd9fd'
down_revision = 'd5c5cf3e7e8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tbl_pronounciation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sheet_entry_fkey', sa.Unicode(length=32), nullable=False),
    sa.Column('grouping_code', sa.Text(), nullable=True),
    sa.Column('pronounciation', sa.Text(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['sheet_entry_fkey'], ['tbl_sheet_entry.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tbl_observation',
    sa.Column('pronounciation_fkey', sa.Integer(), nullable=False),
    sa.Column('place_of_inquiry_fkey', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['place_of_inquiry_fkey'], ['tbl_place_of_inquiry.id'], ),
    sa.ForeignKeyConstraint(['pronounciation_fkey'], ['tbl_pronounciation.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('pronounciation_fkey', 'place_of_inquiry_fkey')
    )
    op.add_column(u'tbl_sheet_entry', sa.Column('parser_messages', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'tbl_sheet_entry', 'parser_messages')
    op.drop_table('tbl_observation')
    op.drop_table('tbl_pronounciation')
    ### end Alembic commands ###
