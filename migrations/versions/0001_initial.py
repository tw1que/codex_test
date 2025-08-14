from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('telephone', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False, server_default='other'),
    )

def downgrade() -> None:
    op.drop_table('contacts')
