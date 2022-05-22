"""empty message

Revision ID: 38e7afa4efe3
Revises: 0c5cd5cea4d7
Create Date: 2022-05-23 01:37:55.076106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38e7afa4efe3'
down_revision = '0c5cd5cea4d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('words', sa.JSON()))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('games', 'words')
    # ### end Alembic commands ###
