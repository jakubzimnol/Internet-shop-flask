"""empty message

Revision ID: dba3aa4d0d34
Revises:
Create Date: 2018-10-23 14:39:01.493640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dba3aa4d0d34'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'category', ['id'])
    op.drop_constraint('category_item_id_fkey', 'category', type_='foreignkey')
    op.drop_column('category', 'item_id')
    op.add_column('item', sa.Column('category_id', sa.Integer(), nullable=True))
    op.add_column('item', sa.Column('subcategory_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'item', 'category', ['category_id'], ['id'])
    op.create_foreign_key(None, 'item', 'subcategory', ['subcategory_id'], ['id'])
    op.drop_constraint('subcategory_item_id_fkey', 'subcategory', type_='foreignkey')
    op.drop_column('subcategory', 'item_id')
    op.add_column('user', sa.Column('_password_hash', sa.String(length=128), nullable=True))
    op.drop_column('user', 'password_hash')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password_hash', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.drop_column('user', '_password_hash')
    op.add_column('subcategory', sa.Column('item_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('subcategory_item_id_fkey', 'subcategory', 'item', ['item_id'], ['id'])
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_column('item', 'subcategory_id')
    op.drop_column('item', 'category_id')
    op.add_column('category', sa.Column('item_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('category_item_id_fkey', 'category', 'item', ['item_id'], ['id'])
    op.drop_constraint(None, 'category', type_='unique')
    # ### end Alembic commands ###
