"""Support translation

Revision ID: 9a86e574d971
Revises: 7101c8fb024e
Create Date: 2022-05-17 11:34:31.597027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a86e574d971'
down_revision = '7101c8fb024e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('texts',
    sa.Column('id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('codes',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('text', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['text'], ['texts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notes',
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['codes.id'], ),
    sa.ForeignKeyConstraint(['text'], ['texts.id'], ),
    sa.PrimaryKeyConstraint('text', 'code')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notes')
    op.drop_table('codes')
    op.drop_table('texts')
    # ### end Alembic commands ###
