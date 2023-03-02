"""empty message

Revision ID: 5418102b62ab
Revises: ffb6dacbfb77
Create Date: 2023-02-08 09:40:06.899137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5418102b62ab'
down_revision = 'ffb6dacbfb77'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('file_content')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_content',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.TEXT(), nullable=True),
    sa.Column('data', sa.BLOB(), nullable=False),
    sa.Column('rendered_data', sa.TEXT(), nullable=False),
    sa.Column('pic_date', sa.DATETIME(), nullable=False),
    sa.Column('filename', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###