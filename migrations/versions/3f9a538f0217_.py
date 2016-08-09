"""empty message

Revision ID: 3f9a538f0217
Revises: None
Create Date: 2016-08-05 16:09:33.846438

"""

# revision identifiers, used by Alembic.
revision = '3f9a538f0217'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('deviceGroups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('groupname', sa.String(length=64), nullable=True),
    sa.Column('business', sa.Integer(), nullable=True),
    sa.Column('isdelete', sa.Boolean(), nullable=True),
    sa.Column('instaff', sa.String(length=64), nullable=True),
    sa.Column('inputtime', sa.DateTime(), nullable=True),
    sa.Column('remarks', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('DeviceRelationshipDeviceGroup',
    sa.Column('deviceGroup_id', sa.Integer(), nullable=True),
    sa.Column('device_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['deviceGroup_id'], ['deviceGroups.id'], ),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], )
    )
    op.create_table('TaskRelationshipTaskGroup',
    sa.Column('deviceTaskGroup_id', sa.Integer(), nullable=True),
    sa.Column('deviceTask_id', sa.Integer(), nullable=True),
    sa.Column('PQ', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['deviceTaskGroup_id'], ['deviceTaskGroup.id'], ),
    sa.ForeignKeyConstraint(['deviceTask_id'], ['deviceTasks.id'], )
    )
    op.drop_table('registrations')
    op.add_column(u'devices', sa.Column('an', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_devices_an'), 'devices', ['an'], unique=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_devices_an'), table_name='devices')
    op.drop_column(u'devices', 'an')
    op.create_table('registrations',
    sa.Column('deviceTaskGroup_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('deviceTask_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['deviceTaskGroup_id'], [u'deviceTaskGroup.id'], name=u'registrations_ibfk_1'),
    sa.ForeignKeyConstraint(['deviceTask_id'], [u'deviceTasks.id'], name=u'registrations_ibfk_2'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.drop_table('TaskRelationshipTaskGroup')
    op.drop_table('DeviceRelationshipDeviceGroup')
    op.drop_table('deviceGroups')
    ### end Alembic commands ###