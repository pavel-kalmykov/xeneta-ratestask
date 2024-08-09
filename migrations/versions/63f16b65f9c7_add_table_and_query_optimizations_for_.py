"""Add table and query optimizations for /rates endpoint

Revision ID: 63f16b65f9c7
Revises: Pavel Kalmykov Razgovorov <pavel.granalacant@gmail.com>
Create Date: 2024-08-09 16:47:36.376567

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "63f16b65f9c7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create materialized view to avoid recursive CTEs by pre-calculating them
    op.execute("""
        CREATE MATERIALIZED VIEW mv_region_hierarchy AS
        WITH RECURSIVE region_hierarchy AS (
            SELECT slug, parent_slug, 1 AS level
            FROM regions
            WHERE parent_slug IS NULL
            UNION ALL
            SELECT r.slug, r.parent_slug, rh.level + 1
            FROM regions r
            JOIN region_hierarchy rh ON r.parent_slug = rh.slug
        )
        SELECT * FROM region_hierarchy;

        CREATE INDEX idx_mv_region_hierarchy_slug ON mv_region_hierarchy (slug);
        CREATE INDEX idx_mv_region_hierarchy_parent_slug ON mv_region_hierarchy (parent_slug);
    """)

    # Create indexes for easier rates scan
    op.execute("""
        CREATE INDEX idx_regions_parent_slug ON regions (parent_slug);
        CREATE INDEX idx_ports_parent_slug ON ports (parent_slug);
        -- Covering indexes to search for codes and day, but including the price column
        -- so you don't have to look up the table.
        CREATE INDEX idx_prices_covering ON prices (day, orig_code, dest_code) INCLUDE (price);
    """)


def downgrade() -> None:
    # Drop materialized view and its indexes
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS mv_region_hierarchy CASCADE;
    """)

    # Drop indexes
    op.execute("""
        DROP INDEX IF EXISTS idx_regions_parent_slug;
        DROP INDEX IF EXISTS idx_ports_parent_slug;
        DROP INDEX IF EXISTS idx_prices_covering;
    """)
