"""Add notes to Artwork

Revision ID: f0aed27282b7
Revises: 
Create Date: 2025-06-03 16:45:51.534588

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0aed27282b7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artworks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notes', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artworks', schema=None) as batch_op:
        batch_op.drop_column('notes')

    # ### end Alembic commands ###
