"""empty message

Revision ID: 09607fdb09c9
Revises: 3f9a538f0217
Create Date: 2016-08-05 16:51:15.475230

"""

# revision identifiers, used by Alembic.
revision = '09607fdb09c9'
down_revision = '3f9a538f0217'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('devices', sa.Column('device_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_devices_device_id'), 'devices', ['device_id'], unique=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_devices_device_id'), table_name='devices')
    op.drop_column('devices', 'device_id')
    ### end Alembic commands ###