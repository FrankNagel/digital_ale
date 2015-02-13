"""Create some indices

Revision ID: 1d30bb17d08d
Revises: 4934034dd9fd
Create Date: 2015-02-13 10:18:30.740994

"""

# revision identifiers, used by Alembic.
revision = '1d30bb17d08d'
down_revision = '4934034dd9fd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_tbl_observation_place_of_inquiry_fkey'), 'tbl_observation', ['place_of_inquiry_fkey'], unique=False)
    op.create_index(op.f('ix_tbl_observation_pronounciation_fkey'), 'tbl_observation', ['pronounciation_fkey'], unique=False)
    op.create_index(op.f('ix_tbl_pronounciation_sheet_entry_fkey'), 'tbl_pronounciation', ['sheet_entry_fkey'], unique=False)
    op.create_index(op.f('ix_tbl_scan_concept_fkey'), 'tbl_scan', ['concept_fkey'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tbl_scan_concept_fkey'), table_name='tbl_scan')
    op.drop_index(op.f('ix_tbl_pronounciation_sheet_entry_fkey'), table_name='tbl_pronounciation')
    op.drop_index(op.f('ix_tbl_observation_pronounciation_fkey'), table_name='tbl_observation')
    op.drop_index(op.f('ix_tbl_observation_place_of_inquiry_fkey'), table_name='tbl_observation')
    ### end Alembic commands ###