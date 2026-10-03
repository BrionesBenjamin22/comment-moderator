from app.classifier.interface import ClassifierError
from app.schemas.moderation import AnalyzeRequest, ClassifierResult


class FakeClassifier:
    """A fixed fixture, never a real semantic analysis."""

    def __init__(self, result: ClassifierResult | None = None, *, fail: bool = False):
        self.fail = fail
        self.result = result or ClassifierResult.model_validate(
            {
                "classification": {
                    "category": "ACADEMIC_EXPERIENCE",
                    "insult": False,
                    "disrespect": False,
                    "personalAttack": False,
                    "mockery": False,
                    "sarcasm": False,
                    "hostility": "NONE",
                    "academicValue": "MEDIUM",
                },
                "classifierVersion": "fake-v0.1",
                "modelVersion": "fake-fixture-v1",
                "language": "es",
                "processingTimeMs": 0,
                "metrics": [],
            }
        )

    async def classify(self, input: AnalyzeRequest) -> ClassifierResult:
        if self.fail:
            raise ClassifierError("Fake classifier failure")
        return self.result.model_copy(deep=True)
