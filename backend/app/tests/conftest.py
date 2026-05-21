from __future__ import annotations

from pathlib import Path
from typing import Callable
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.repositories.report_repository import ReportRecord

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEST_DB_DIR = Path(__file__).resolve().parents[2] / ".test_dbs"


@pytest.fixture()
def fixture_html() -> Callable[[str], str]:
    def _load(name: str) -> str:
        return (FIXTURES_DIR / name).read_text(encoding="utf-8")

    return _load


@pytest.fixture()
def client() -> TestClient:
    TEST_DB_DIR.mkdir(exist_ok=True)
    db_path = TEST_DB_DIR / f"test-{uuid4().hex}.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine, tables=[ReportRecord.__table__])

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
    db_path.unlink(missing_ok=True)
