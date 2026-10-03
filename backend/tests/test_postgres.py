import asyncio
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.classifier import FakeClassifier
from app.config import Settings
from app.main import create_app
from app.models import Classification, Comment, Feedback
from app.schemas.moderation import AnalyzeRequest, ClassificationRead, CommentRead, DatasetStatus

pytestmark = pytest.mark.postgres


def seed(engine):
    result = asyncio.run(FakeClassifier().classify(AnalyzeRequest(text="Comentario de prueba")))
    comment = Comment(text="Comentario de prueba", language=result.language)
    with Session(engine) as session:
        session.add(comment)
        session.flush()
        classification = Classification(
            comment_id=comment.id,
            **result.classification.model_dump(),
            classifier_version=result.classifier_version,
            model_version=result.model_version,
            processing_time_ms=result.processing_time_ms,
        )
        session.add(classification)
        session.commit()
        return comment.id


def test_migration_matches_metadata(postgres):
    engine, _, config = postgres
    assert set(inspect(engine).get_table_names()) == {
        "comments",
        "classifications",
        "feedbacks",
        "alembic_version",
    }
    command.check(config)


def test_defaults_timestamps_relationships_and_read_schemas(postgres):
    engine, _, _ = postgres
    comment_id = seed(engine)
    with Session(engine) as session:
        comment = session.get(Comment, comment_id)
        assert comment.dataset_status == DatasetStatus.PENDING
        assert comment.created_at.tzinfo is not None
        assert comment.classification.classified_at.tzinfo is not None
        assert comment.feedback is None
        assert (
            CommentRead.model_validate(comment).model_dump(by_alias=True)["datasetStatus"]
            == "PENDING"
        )
        assert ClassificationRead.model_validate(comment.classification).metrics == []


def test_fk_and_r01(postgres):
    engine, _, _ = postgres
    with Session(engine) as session:
        session.add(Feedback(comment_id=uuid4(), accepted_fully=True))
        with pytest.raises(IntegrityError):
            session.commit()
    with engine.begin() as connection:
        comment_id = uuid4()
        connection.execute(
            text("INSERT INTO comments (id,text,language) VALUES (:id,'test','es')"),
            {"id": comment_id},
        )
        with pytest.raises(IntegrityError), connection.begin_nested():
            connection.execute(
                text("""
                INSERT INTO classifications
                (id,comment_id,category,insult,disrespect,personal_attack,mockery,sarcasm,
                 hostility,academic_value,classifier_version,processing_time_ms)
                VALUES (:id,:comment_id,'COMPLAINT',true,false,false,false,false,
                        'NONE','LOW','test',0)
            """),
                {"id": uuid4(), "comment_id": comment_id},
            )


def test_unique_classification(postgres):
    engine, _, _ = postgres
    comment_id = seed(engine)
    with Session(engine) as session:
        original = session.scalar(
            select(Classification).where(Classification.comment_id == comment_id)
        )
        session.add(
            Classification(
                comment_id=comment_id,
                category=original.category,
                insult=False,
                disrespect=False,
                personal_attack=False,
                mockery=False,
                sarcasm=False,
                hostility="NONE",
                academic_value="LOW",
                classifier_version="test",
                processing_time_ms=0,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


def test_concurrent_feedback_one_shot(postgres):
    engine, api_url, _ = postgres
    comment_id = seed(engine)
    runtime = create_engine(api_url)

    def submit():
        try:
            with Session(runtime) as session:
                session.add(Feedback(comment_id=comment_id, accepted_fully=True))
                session.commit()
            return "created"
        except IntegrityError:
            return "conflict"

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: submit(), range(2)))
        assert sorted(outcomes) == ["conflict", "created"]
        assert submit() == "conflict"
        with Session(engine) as session:
            comment = session.get(Comment, comment_id)
            assert comment.feedback.accepted_fully
            assert comment.dataset_status == DatasetStatus.PENDING
            assert comment.classification.classifier_version == "fake-v0.1"
    finally:
        runtime.dispose()


@pytest.mark.parametrize("table", ["comments", "classifications", "feedbacks"])
def test_runtime_cannot_update_delete_or_truncate(postgres, table):
    _, api_url, _ = postgres
    runtime = create_engine(api_url)
    try:
        for statement in (
            f"UPDATE {table} SET id = id WHERE false",
            f"DELETE FROM {table} WHERE false",
            f"TRUNCATE {table} CASCADE",
        ):
            with pytest.raises(DBAPIError), runtime.begin() as connection:
                connection.execute(text(statement))
    finally:
        runtime.dispose()


def test_database_trigger_preserves_original(postgres):
    engine, _, _ = postgres
    comment_id = seed(engine)
    with pytest.raises(DBAPIError), engine.begin() as connection:
        connection.execute(
            text("UPDATE comments SET text='edited' WHERE id=:id"), {"id": comment_id}
        )


def test_health_real_database(postgres):
    _, api_url, _ = postgres
    with TestClient(create_app(Settings(_env_file=None, database_url=api_url))) as client:
        assert client.get("/health").json() == {"status": "ok", "database": "ok"}
