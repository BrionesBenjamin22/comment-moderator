import asyncio
import math

import pytest
from pydantic import ValidationError

from app.classifier import ClassifierError, FakeClassifier
from app.config import Settings
from app.schemas.moderation import AnalyzeRequest, ClassificationValues, FeedbackRequest


def values(**overrides):
    return {
        "category": "CONSTRUCTIVE_CRITICISM",
        "insult": False,
        "disrespect": False,
        "personalAttack": False,
        "mockery": False,
        "sarcasm": False,
        "hostility": "NONE",
        "academicValue": "HIGH",
        **overrides,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"text": "   "},
        {"text": "x" * 5001},
        {"text": 123},
        {"text": "Hola", "datasetStatus": "VERIFIED"},
        {"text": "Hola", "subject": "x" * 201},
    ],
)
def test_invalid_inputs(payload):
    with pytest.raises(ValidationError):
        AnalyzeRequest.model_validate(payload)


def test_original_text_is_preserved():
    text = "  Qué máquina... <script>texto</script>\n"
    assert AnalyzeRequest(text=text).text == text


@pytest.mark.parametrize(
    "overrides",
    [
        {"insult": True, "disrespect": False},
        {"sarcasm": "true"},
        {"hostility": "EXTREME"},
        {"unknown": 1},
    ],
)
def test_invalid_classifications(overrides):
    with pytest.raises(ValidationError):
        ClassificationValues.model_validate(values(**overrides))


def test_no_forbidden_derived_rules():
    result = ClassificationValues.model_validate(
        values(
            personalAttack=True,
            mockery=True,
            sarcasm=True,
        )
    )
    assert not result.disrespect
    assert result.hostility == "NONE"


def test_full_acceptance_and_partial_feedback():
    assert FeedbackRequest(acceptedFully=True).corrections.model_fields_set == set()
    feedback = FeedbackRequest(
        acceptedFully=False,
        disputedDimensions=["sarcasm"],
        corrections={"sarcasm": False},
        humanIntensities={"sarcasmIntensity": 0},
    )
    assert feedback.corrections.model_dump(by_alias=True, exclude_unset=True) == {"sarcasm": False}
    assert feedback.human_intensities.sarcasm_intensity == 0
    assert feedback.human_intensities.mockery_intensity is None


def test_human_declaration_not_forced_to_r01():
    feedback = FeedbackRequest(
        acceptedFully=False,
        disputedDimensions=["insult", "disrespect"],
        corrections={"insult": True, "disrespect": False},
    )
    assert feedback.corrections.insult and not feedback.corrections.disrespect


@pytest.mark.parametrize(
    "payload",
    [
        {
            "acceptedFully": True,
            "disputedDimensions": ["sarcasm"],
            "corrections": {"sarcasm": True},
        },
        {"acceptedFully": False},
        {"acceptedFully": False, "disputedDimensions": ["sarcasm"], "corrections": {}},
        {
            "acceptedFully": False,
            "disputedDimensions": ["sarcasm", "sarcasm"],
            "corrections": {"sarcasm": True},
        },
        {
            "acceptedFully": False,
            "disputedDimensions": ["sarcasm"],
            "corrections": {"mockery": True},
        },
        {
            "acceptedFully": False,
            "disputedDimensions": ["sarcasm"],
            "corrections": {"sarcasm": "yes"},
        },
        {
            "acceptedFully": False,
            "disputedDimensions": ["sarcasm"],
            "corrections": {"sarcasm": None},
        },
        {"acceptedFully": True, "classification": {}},
    ],
)
def test_invalid_feedback(payload):
    with pytest.raises(ValidationError):
        FeedbackRequest.model_validate(payload)


@pytest.mark.parametrize("value", [-1, 101, math.nan, math.inf, "72", True, None])
def test_intensity_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        FeedbackRequest(acceptedFully=True, humanIntensities={"sarcasmIntensity": value})


def test_all_intensity_boundaries():
    feedback = FeedbackRequest(
        acceptedFully=True,
        humanIntensities={
            "sarcasmIntensity": 100,
            "mockeryIntensity": 0,
            "hostilityIntensity": 50.5,
        },
    )
    assert feedback.human_intensities.hostility_intensity == 50.5


def test_fake_deterministic_and_isolated():
    fake = FakeClassifier()
    first = asyncio.run(fake.classify(AnalyzeRequest(text="Un insulto")))
    second = asyncio.run(fake.classify(AnalyzeRequest(text="Un elogio")))
    assert first == second
    assert first.metrics == []
    first.classification.sarcasm = True
    assert not second.classification.sarcasm
    assert first.classifier_version.startswith("fake-")


def test_fake_failure():
    with pytest.raises(ClassifierError):
        asyncio.run(FakeClassifier(fail=True).classify(AnalyzeRequest(text="Comentario")))


@pytest.mark.parametrize(
    "overrides",
    [
        {"classifier_backend": "jev"},
        {"database_url": "sqlite:///fake.db"},
        {"cors_origins": ["*"]},
        {"comments_page_size_default": 51, "comments_page_size_max": 50},
        {"db_connect_timeout_seconds": 0},
    ],
)
def test_invalid_settings(overrides):
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            **{
                "database_url": "postgresql+psycopg://local:local@localhost/lab",
                **overrides,
            },
        )


def test_configurable_pagination_and_redacted_secret(settings):
    assert settings.comments_page_size_default == 12
    assert settings.comments_page_size_max == 50
    assert "unused:unused" not in repr(settings)
    configured = Settings(
        _env_file=None,
        database_url=settings.database_url,
        comments_page_size_default=60,
        comments_page_size_max=100,
    )
    assert configured.comments_page_size_default == 60
