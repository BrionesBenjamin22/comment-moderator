from fastapi import Request

from app.classifier.interface import Classifier


def get_classifier(request: Request) -> Classifier:
    return request.app.state.classifier
