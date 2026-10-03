from typing import Protocol

from app.schemas.moderation import AnalyzeRequest, ClassifierResult


class ClassifierError(Exception):
    """Provider-independent classification failure."""


class Classifier(Protocol):
    async def classify(self, input: AnalyzeRequest) -> ClassifierResult: ...
