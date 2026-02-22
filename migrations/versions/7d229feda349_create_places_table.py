from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '7d229feda349'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'places',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('category', sa.String, index=True, nullable=True),
        sa.Column('brand', sa.String, index=True, nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('geog', Geography(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('source', sa.String, nullable=True),
        sa.Column('metadata_json', JSONB, nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('places')
