"""empty message

Revision ID: 1c55086f1e5b
Revises: 65548242bb8d
Create Date: 2016-08-14 07:47:37.789006

"""

# revision identifiers, used by Alembic.
revision = '1c55086f1e5b'
down_revision = '65548242bb8d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('SoftwareDistribution', 'type')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('SoftwareDistribution', sa.Column('type', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    ### end Alembic commands ###
