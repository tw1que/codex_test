from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'addresses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('street', sa.String(), nullable=True),
        sa.Column('number', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
    )
    op.create_table(
        'practices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('address_id', sa.Integer(), sa.ForeignKey('addresses.id')),
    )
    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('address_id', sa.Integer(), sa.ForeignKey('addresses.id')),
    )
    op.create_table(
        'contact_persons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('function', sa.String(), nullable=True),
    )
    op.create_table(
        'phone_numbers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('number', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('practice_id', sa.Integer(), sa.ForeignKey('practices.id')),
        sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id')),
        sa.Column('contact_person_id', sa.Integer(), sa.ForeignKey('contact_persons.id')),
    )
    op.create_table(
        'practice_contacts',
        sa.Column('practice_id', sa.Integer(), sa.ForeignKey('practices.id'), primary_key=True),
        sa.Column('contact_id', sa.Integer(), sa.ForeignKey('contact_persons.id'), primary_key=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        'supplier_contacts',
        sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id'), primary_key=True),
        sa.Column('contact_id', sa.Integer(), sa.ForeignKey('contact_persons.id'), primary_key=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_table('supplier_contacts')
    op.drop_table('practice_contacts')
    op.drop_table('phone_numbers')
    op.drop_table('contact_persons')
    op.drop_table('suppliers')
    op.drop_table('practices')
    op.drop_table('addresses')
