"""Exercise the route and the repository's actual conditional UPDATE on a disposable DB."""
import sqlite3
from datetime import datetime
from uuid import UUID, uuid4
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from reconcileai.api.identity import DevelopmentActor
from reconcileai.api.routers import reconciliation as routes
from reconcileai.modules.reconciliation.schemas import ReconciliationCreate, ReviewDecision


@pytest.fixture
def review_db():
    sqlite3.register_adapter(UUID, str)
    sqlite3.register_converter("UUID", lambda value: UUID(value.decode()))
    sqlite3.register_converter("INSTANT", lambda value: datetime.fromisoformat(value.decode()))
    engine = create_engine("sqlite://", connect_args={"detect_types": sqlite3.PARSE_DECLTYPES})
    with Session(engine) as db:
        db.connection().connection.driver_connection.create_function("now", 0, lambda: "2026-01-01")
        db.execute(text("CREATE TABLE memberships (organization_id UUID, user_id UUID, role TEXT)"))
        db.execute(text("""CREATE TABLE reconciliation_cases (
            id UUID, organization_id UUID, purchase_order_id UUID, invoice_number TEXT,
            invoice_amount NUMERIC, currency TEXT, vendor_name TEXT, match_status TEXT, confidence NUMERIC,
            explanation TEXT, decision TEXT, reviewed_by UUID, reviewed_at TEXT, submitted_by UUID,
            duplicate_of UUID, created_at INSTANT DEFAULT '2026-01-01')"""))
        org, case, maker, checker = (uuid4() for _ in range(4))
        for uid in (maker, checker):
            db.execute(text("INSERT INTO memberships VALUES (:org,:uid,'FINANCE_APPROVER')"), {"org":org,"uid":uid})
        db.execute(text("INSERT INTO reconciliation_cases(id,organization_id,submitted_by,confidence) VALUES (:id,:org,:maker,0.82)"), {"id":case,"org":org,"maker":maker})
        yield db, org, case, maker, checker
    engine.dispose()


@pytest.mark.parametrize("decision", ["APPROVED","REJECTED"])
def test_independent_finance_reviewer_only(review_db, decision):
    db, org, case, maker, checker = review_db
    payload = ReviewDecision(decision=decision)
    for uid, role, tenant, code in [
        (maker,"FINANCE_APPROVER",org,403), (checker,"ORG_ADMIN",org,403),
        (checker,"AP_ANALYST",org,403), (checker,"FINANCE_APPROVER",uuid4(),404),
        (uuid4(),"FINANCE_APPROVER",org,403),
    ]:
        with pytest.raises(HTTPException) as exc:
            routes.review_case(case,payload,DevelopmentActor(uid,tenant,role),db)
        assert exc.value.status_code == code
    assert db.scalar(text("SELECT decision FROM reconciliation_cases")) is None
    actor = DevelopmentActor(checker,org,"FINANCE_APPROVER")
    assert routes.review_case(case,payload,actor,db)["decision"] == decision
    assert db.scalar(text("SELECT reviewed_by FROM reconciliation_cases")) == checker
    with pytest.raises(HTTPException) as exc:
        routes.review_case(case,payload,actor,db)
    assert exc.value.status_code == 409


def test_unknown_maker_is_locked(review_db):
    db, org, case, _, checker = review_db
    db.execute(text("UPDATE reconciliation_cases SET submitted_by=NULL"))
    with pytest.raises(HTTPException) as exc:
        routes.review_case(case, ReviewDecision(decision="REJECTED"), DevelopmentActor(checker,org,"FINANCE_APPROVER"), db)
    assert exc.value.status_code == 403


def test_new_submission_uses_session_identity(review_db):
    db, org, _, maker, checker = review_db
    payload = ReconciliationCreate.model_validate(dict(purchase_order_id=uuid4(), invoice_number="INV-1",
        invoice_amount="100", currency="INR", vendor_name="Demo", submitted_by=str(checker)))
    with patch.object(routes.repository,"create",return_value={}) as save:
        routes.create_case(payload,DevelopmentActor(maker,org,"AP_ANALYST"),db)
        save.assert_called_once_with(db,org,maker,payload)
        assert "submitted_by" not in payload.model_dump()
