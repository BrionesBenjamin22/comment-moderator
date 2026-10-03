from datetime import datetime
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StringConstraints,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel


class Contract(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        from_attributes=True,
    )


class CommentCategory(str, Enum):
    ACADEMIC_EXPERIENCE = "ACADEMIC_EXPERIENCE"
    CONSTRUCTIVE_CRITICISM = "CONSTRUCTIVE_CRITICISM"
    PRAISE = "PRAISE"
    COMPLAINT = "COMPLAINT"
    PERSONAL_ATTACK = "PERSONAL_ATTACK"
    IRRELEVANT = "IRRELEVANT"


class HostilityLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class AcademicValue(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class DatasetStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


Dimension = Literal[
    "category",
    "insult",
    "disrespect",
    "personalAttack",
    "mockery",
    "sarcasm",
    "hostility",
    "academicValue",
]
Intensity = Annotated[float, Field(strict=True, ge=0, le=100, allow_inf_nan=False)]
CommentText = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=5000)]
ContextText = Annotated[str, StringConstraints(strict=True, max_length=200)]


class AnalyzeRequest(Contract):
    text: CommentText
    subject: ContextText | None = None
    teacher: ContextText | None = None

    @field_validator("text")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Comment must not be blank")
        return value


class ClassificationValues(Contract):
    category: CommentCategory
    insult: StrictBool
    disrespect: StrictBool
    personal_attack: StrictBool
    mockery: StrictBool
    sarcasm: StrictBool
    hostility: HostilityLevel
    academic_value: AcademicValue

    @model_validator(mode="after")
    def coherence(self):
        if self.insult and not self.disrespect:
            raise ValueError("R01: insult requires disrespect")
        return self


class ModelMetric(Contract):
    dimension: Dimension
    kind: Literal["probability", "confidence"]
    value: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]
    meaning: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=200)]


class ClassifierResult(Contract):
    classification: ClassificationValues
    classifier_version: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    model_version: Annotated[str, StringConstraints(min_length=1, max_length=100)] | None
    language: Annotated[str, StringConstraints(min_length=2, max_length=35)]
    processing_time_ms: Annotated[int, Field(strict=True, ge=0)]
    metrics: list[ModelMetric] = Field(default_factory=list)


class Corrections(Contract):
    category: CommentCategory | None = None
    insult: StrictBool | None = None
    disrespect: StrictBool | None = None
    personal_attack: StrictBool | None = None
    mockery: StrictBool | None = None
    sarcasm: StrictBool | None = None
    hostility: HostilityLevel | None = None
    academic_value: AcademicValue | None = None

    @model_validator(mode="after")
    def reject_explicit_null(self):
        if any(getattr(self, name) is None for name in self.model_fields_set):
            raise ValueError("Corrections must contain an explicit typed value")
        return self


class HumanIntensities(Contract):
    sarcasm_intensity: Intensity | None = None
    mockery_intensity: Intensity | None = None
    hostility_intensity: Intensity | None = None

    @model_validator(mode="after")
    def reject_explicit_null(self):
        if any(getattr(self, name) is None for name in self.model_fields_set):
            raise ValueError("Omit unavailable intensities instead of sending null")
        return self


class FeedbackRequest(Contract):
    accepted_fully: StrictBool
    disputed_dimensions: list[Dimension] = Field(default_factory=list, max_length=8)
    corrections: Corrections = Field(default_factory=Corrections)
    human_intensities: HumanIntensities = Field(default_factory=HumanIntensities)
    clarification: Annotated[str, StringConstraints(strict=True, max_length=2000)] | None = None

    @model_validator(mode="after")
    def matching_corrections(self):
        dimensions = self.disputed_dimensions
        correction_keys = set(self.corrections.model_dump(by_alias=True, exclude_unset=True))
        if len(dimensions) != len(set(dimensions)):
            raise ValueError("Disputed dimensions must not repeat")
        if self.accepted_fully and (dimensions or correction_keys):
            raise ValueError("Full acceptance cannot include corrections")
        if not self.accepted_fully and not dimensions:
            raise ValueError("Partial feedback requires a disputed dimension")
        if set(dimensions) != correction_keys:
            raise ValueError("Every disputed dimension requires exactly one correction")
        return self


class CommentRead(AnalyzeRequest):
    id: UUID
    language: str
    created_at: datetime
    dataset_status: DatasetStatus


class ClassificationRead(ClassificationValues):
    id: UUID
    comment_id: UUID
    classifier_version: str
    model_version: str | None
    processing_time_ms: int
    classified_at: datetime
    metrics: list[ModelMetric]


class FeedbackRead(FeedbackRequest):
    id: UUID
    comment_id: UUID
    feedback_at: datetime


class HealthResponse(Contract):
    status: Literal["ok", "unavailable"]
    database: Literal["ok", "unavailable"]
