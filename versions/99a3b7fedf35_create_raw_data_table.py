"""Create raw_data_table

Revision ID: 99a3b7fedf35
Revises: 07d0cbda088a
Create Date: 2023-04-15 00:38:10.945200

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BIT


# revision identifiers, used by Alembic.
revision = '99a3b7fedf35'
down_revision = '07d0cbda088a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'raw_data',
        sa.Column('id',sa.Uuid),
        sa.Column('casos', sa.Integer),
        sa.Column('casospermil', sa.Float),
        sa.Column( 'hombres80', sa.Float),
        sa.Column('mujeres80', sa.Float),
	  sa.Column('pobla80', sa.Float),
	  sa.Column('pobla65', sa.Float),
	  sa.Column('poblamid', sa.Float),
        sa.Column('pobladata', sa.Float),
        sa.Column('pobladens', sa.Float),
	sa.Column('mujeres', sa.Float),
	sa.Column('urbano', sa.Float),
	sa.Column('expectvida', sa.Float),
	sa.Column('neontlmort', sa.Float),
	sa.Column('dismort', sa.Float),
	sa.Column('lesion', sa.Float),
	sa.Column('enfnotrans', sa.Float),
	sa.Column('enftrans', sa.Float),
	sa.Column('pbi', sa.Float),
	sa.Column('tuberculosis', sa.Integer),
	sa.Column('diabetes', sa.Float),
	sa.Column('medicos', sa.Float),
	sa.Column('camas', sa.Float),
	sa.Column('immunsaramp', sa.Integer),
	sa.Column('tempmarzo', sa.Float),
	sa.Column('hiptenh', sa.Float),
	sa.Column('hiptenm', sa.Float),
	sa.Column('hipten', sa.Float),
	sa.Column('bcg', BIT),
	sa.Column('tiempo', sa.Float),
	sa.Column('l10casospermil', sa.Float),

    )


def downgrade() -> None:
    op.drop_table('raw_data')