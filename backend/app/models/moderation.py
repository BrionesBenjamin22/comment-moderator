from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.schemas.moderation import AcademicValue, CommentCategory, DatasetStatus, HostilityLevel


def enum_column(enum_class, name):
    return Enum(enum_class, name=name, values_callable=lambda enum: [item.value for item in enum])


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        CheckConstraint("length(btrim(text)) BETWEEN 1 AND 5000", name="text_length"),
        Index("ix_comments_created_at_id", "created_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(String(200))
    teacher: Mapped[str | None] = mapped_column(String(200))
    language: Mapped[str] = mapped_column(String(35))
    dataset_status: Mapped[DatasetStatus] = mapped_column(
        enum_column(DatasetStatus, "dataset_status"),
        default=DatasetStatus.PENDING,
        server_default="PENDING",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    classification: Mapped["Classification"] = relationship(back_populates="comment")
    feedback: Mapped["Feedback | None"] = relationship(
        primaryjoin="Comment.id == foreign(Feedback.comment_id)",
        back_populates="comment",
    )


class Classification(Base):
    __tablename__ = "classifications"
    __table_args__ = (
        CheckConstraint("NOT insult OR disrespect", name="r01"),
        CheckConstraint("processing_time_ms >= 0", name="processing_time"),
        CheckConstraint("jsonb_typeof(metrics) = 'array'", name="metrics_array"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    comment_id: Mapped[UUID] = mapped_column(ForeignKey("comments.id"), unique=True)
    category: Mapped[CommentCategory] = mapped_column(
        enum_column(CommentCategory, "comment_category")
    )
    insult: Mapped[bool] = mapped_column(Boolean)
    disrespect: Mapped[bool] = mapped_column(Boolean)
    personal_attack: Mapped[bool] = mapped_column(Boolean)
    mockery: Mapped[bool] = mapped_column(Boolean)
    sarcasm: Mapped[bool] = mapped_column(Boolean)
    hostility: Mapped[HostilityLevel] = mapped_column(
        enum_column(HostilityLevel, "hostility_level")
    )
    academic_value: Mapped[AcademicValue] = mapped_column(
        enum_column(AcademicValue, "academic_value")
    )
    classifier_version: Mapped[str] = mapped_column(String(100))
    model_version: Mapped[str | None] = mapped_column(String(100))
    processing_time_ms: Mapped[int] = mapped_column(Integer)
    metrics: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    classified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    comment: Mapped[Comment] = relationship(back_populates="classification")


class Feedback(Base):
    __tablename__ = "feedbacks"
    __table_args__ = (
        CheckConstraint("jsonb_typeof(disputed_dimensions) = 'array'", name="dimensions_array"),
        CheckConstraint("jsonb_typeof(corrections) = 'object'", name="corrections_object"),
        CheckConstraint("jsonb_typeof(human_intensities) = 'object'", name="intensities_object"),
        CheckConstraint(
            "(accepted_fully AND disputed_dimensions = '[]'::jsonb AND corrections = '{}'::jsonb)"
            " OR (NOT accepted_fully AND jsonb_array_length(disputed_dimensions) > 0"
            " AND corrections <> '{}'::jsonb)",
            name="acceptance",
        ),
        CheckConstraint(
            "clarification IS NULL OR length(clarification) <= 2000", name="clarification"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    comment_id: Mapped[UUID] = mapped_column(ForeignKey("classifications.comment_id"), unique=True)
    accepted_fully: Mapped[bool] = mapped_column(Boolean)
    disputed_dimensions: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    corrections: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    human_intensities: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    clarification: Mapped[str | None] = mapped_column(Text)
    feedback_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    comment: Mapped[Comment] = relationship(
        primaryjoin="foreign(Feedback.comment_id) == Comment.id",
        back_populates="feedback",
    )
