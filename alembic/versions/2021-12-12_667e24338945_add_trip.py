"""add trip

Revision ID: 667e24338945
Revises: 
Create Date: 2021-12-12 15:33:14.628952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '667e24338945'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('trip',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_trip')),
    sa.UniqueConstraint('chat_id', 'name', name=op.f('uq_trip_chat_id'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trip')
    # ### end Alembic commands ###