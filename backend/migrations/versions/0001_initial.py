"""Initial immutable comments, classifications and one-shot feedback."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("subject", sa.String(200)),
        sa.Column("teacher", sa.String(200)),
        sa.Column("language", sa.String(35), nullable=False),
        sa.Column(
            "dataset_status",
            sa.Enum("PENDING", "VERIFIED", "REJECTED", name="dataset_status"),
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "length(btrim(text)) BETWEEN 1 AND 5000", name="ck_comments_text_length"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_comments"),
    )
    op.create_index("ix_comments_created_at_id", "comments", ["created_at", "id"])
    op.create_table(
        "classifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("comment_id", sa.Uuid(), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "ACADEMIC_EXPERIENCE",
                "CONSTRUCTIVE_CRITICISM",
                "PRAISE",
                "COMPLAINT",
                "PERSONAL_ATTACK",
                "IRRELEVANT",
                name="comment_category",
            ),
            nullable=False,
        ),
        sa.Column("insult", sa.Boolean(), nullable=False),
        sa.Column("disrespect", sa.Boolean(), nullable=False),
        sa.Column("personal_attack", sa.Boolean(), nullable=False),
        sa.Column("mockery", sa.Boolean(), nullable=False),
        sa.Column("sarcasm", sa.Boolean(), nullable=False),
        sa.Column(
            "hostility",
            sa.Enum("NONE", "LOW", "MODERATE", "HIGH", "SEVERE", name="hostility_level"),
            nullable=False,
        ),
        sa.Column(
            "academic_value",
            sa.Enum("VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH", name="academic_value"),
            nullable=False,
        ),
        sa.Column("classifier_version", sa.String(100), nullable=False),
        sa.Column("model_version", sa.String(100)),
        sa.Column("processing_time_ms", sa.Integer(), nullable=False),
        sa.Column("metrics", postgresql.JSONB(), server_default="[]", nullable=False),
        sa.Column(
            "classified_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("NOT insult OR disrespect", name="ck_classifications_r01"),
        sa.CheckConstraint("processing_time_ms >= 0", name="ck_classifications_processing_time"),
        sa.CheckConstraint(
            "jsonb_typeof(metrics) = 'array'", name="ck_classifications_metrics_array"
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"], ["comments.id"], name="fk_classifications_comment_id_comments"
        ),
        sa.UniqueConstraint("comment_id", name="uq_classifications_comment_id"),
        sa.PrimaryKeyConstraint("id", name="pk_classifications"),
    )
    op.create_table(
        "feedbacks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("comment_id", sa.Uuid(), nullable=False),
        sa.Column("accepted_fully", sa.Boolean(), nullable=False),
        sa.Column("disputed_dimensions", postgresql.JSONB(), server_default="[]", nullable=False),
        sa.Column("corrections", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column("human_intensities", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column("clarification", sa.Text()),
        sa.Column(
            "feedback_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "jsonb_typeof(disputed_dimensions) = 'array'", name="ck_feedbacks_dimensions_array"
        ),
        sa.CheckConstraint(
            "jsonb_typeof(corrections) = 'object'", name="ck_feedbacks_corrections_object"
        ),
        sa.CheckConstraint(
            "jsonb_typeof(human_intensities) = 'object'", name="ck_feedbacks_intensities_object"
        ),
        sa.CheckConstraint(
            "(accepted_fully AND disputed_dimensions = '[]'::jsonb AND corrections = '{}'::jsonb)"
            " OR (NOT accepted_fully AND jsonb_array_length(disputed_dimensions) > 0"
            " AND corrections <> '{}'::jsonb)",
            name="ck_feedbacks_acceptance",
        ),
        sa.CheckConstraint(
            "clarification IS NULL OR length(clarification) <= 2000",
            name="ck_feedbacks_clarification",
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"],
            ["classifications.comment_id"],
            name="fk_feedbacks_comment_id_classifications",
        ),
        sa.UniqueConstraint("comment_id", name="uq_feedbacks_comment_id"),
        sa.PrimaryKeyConstraint("id", name="pk_feedbacks"),
    )
    # Database protection also applies to privileged writes outside the API.
    op.execute("""
        CREATE FUNCTION reject_original_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'Original records are immutable';
        END;
        $$;
    """)
    for table in ("comments", "classifications", "feedbacks"):
        op.execute(f"""
            CREATE TRIGGER immutable_original BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION reject_original_mutation();
        """)


def downgrade():
    for table in ("feedbacks", "classifications", "comments"):
        op.drop_table(table)
    op.execute("DROP FUNCTION reject_original_mutation()")
    for name in ("academic_value", "hostility_level", "comment_category", "dataset_status"):
        postgresql.ENUM(name=name).drop(op.get_bind(), checkfirst=True)
