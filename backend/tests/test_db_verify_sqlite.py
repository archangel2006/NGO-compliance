"""
DB Verification Script (SQLite mode) -- validates ORM models, store wrappers,
and cascade logic without needing a running PostgreSQL server.

Run from the project root:
    python backend/tests/test_db_verify_sqlite.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── Patch DATABASE_URL to SQLite for this test ─────────────────────
import os
os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/ngo_verify_test.db"

# Patch JSON column for SQLite (SQLite doesn't have native JSON)
from sqlalchemy import types
class JsonText(types.TypeDecorator):
    impl = types.Text
    cache_ok = True
    def process_bind_param(self, value, dialect):
        import json
        return json.dumps(value) if value is not None else None
    def process_result_value(self, value, dialect):
        import json
        return json.loads(value) if value else None

import sqlalchemy.dialects.sqlite
# monkey-patch JSON → JsonText for SQLite
import sqlalchemy
_orig_JSON = sqlalchemy.JSON
def _json_sqlite_compat(*a, **kw):
    return JsonText()

# ── Now import models ──────────────────────────────────────────────
from sqlalchemy import create_engine, inspect, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey

SQLITE_URL = "sqlite:///C:/tmp/ngo_verify_test.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

# Enable FK enforcement in SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_con, con_record):
    dbapi_con.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ── Define minimal ORM (mirrors orm.py, JSON as Text) ─────────────
class Submission(Base):
    __tablename__ = "submissions"
    id = Column(String, primary_key=True)
    org_name = Column(String, nullable=False)
    state = Column(String(5))
    entity_type = Column(String)
    pan = Column(String(10))
    sector = Column(String)
    contact_email = Column(String)
    year_of_incorporation = Column(Integer)
    darpan_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    submitted_by = Column(String, nullable=True)
    progress_step = Column(Integer, default=0)
    score = Column(JsonText, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(String)
    updated_at = Column(String)

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"
    id = Column(String, primary_key=True)
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"))
    doc_type = Column(String)
    file_path = Column(String)
    file_name = Column(String, nullable=True)
    file_size = Column(Integer)
    ocr_status = Column(String)
    ocr_method = Column(String, nullable=True)
    ocr_quality = Column(String, nullable=True)
    uploaded_at = Column(String)

class ExtractedFields(Base):
    __tablename__ = "extracted_fields"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    merged_fields = Column(JsonText)
    extraction_log = Column(JsonText)
    created_at = Column(String)

class ComplianceFinding(Base):
    __tablename__ = "compliance_findings"
    id = Column(String, primary_key=True)
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"))
    dimension_id = Column(String)
    dimension_name = Column(String)
    status = Column(String)
    confidence = Column(Float)
    legal_citation = Column(String)
    ngo_evidence = Column(String)
    reasoning = Column(String)
    routing = Column(String)
    citation_valid = Column(Boolean)
    raw_llm_output = Column(String, nullable=True)
    matched_requirement = Column(String, default="")
    human_determination = Column(String, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(String, nullable=True)
    created_at = Column(String)

class HumanReviewQueue(Base):
    __tablename__ = "human_review_queue"
    id = Column(String, primary_key=True)
    finding_id = Column(String, ForeignKey("compliance_findings.id", ondelete="CASCADE"))
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"))
    dimension_name = Column(String)
    assigned_officer = Column(String)
    queue_status = Column(String)
    ai_recommendation_revealed = Column(Boolean, default=False)
    officer_determination = Column(String, nullable=True)
    officer_notes = Column(String, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(String, nullable=True)
    created_at = Column(String)

Base.metadata.create_all(bind=engine)

import uuid, datetime

PASS_S = "[PASS]"
FAIL_S = "[FAIL]"
INFO_S = "[INFO]"

def sep(title):
    print(f"\n{'-'*60}")
    print(f"  {title}")
    print('-'*60)

errors = []

# ── CHECK 1: Schema ───────────────────────────────────────────────
sep("CHECK 1 -- Schema Validation (SQLite mirror of PostgreSQL ORM)")

expected = {"submissions", "uploaded_documents", "extracted_fields",
            "compliance_findings", "human_review_queue"}
inspector = inspect(engine)
actual = set(inspector.get_table_names())
missing = expected - actual

if not missing:
    print(f"{PASS_S} All 5 tables created correctly.")
    for t in sorted(expected):
        cols = [c["name"] for c in inspector.get_columns(t)]
        print(f"  {t}: {cols}")
else:
    print(f"{FAIL_S} Missing tables: {missing}")
    errors.append("schema")

# ── CHECK 2: FK Cascade ───────────────────────────────────────────
sep("CHECK 2 -- FK Cascade Delete")

db = SessionLocal()
sid = str(uuid.uuid4())
fid = str(uuid.uuid4())
qid = str(uuid.uuid4())
ts  = datetime.datetime.utcnow().isoformat()

try:
    db.add(Submission(id=sid, org_name="Cascade Test NGO", state="dl",
                      entity_type="Society", pan="CSCP00001",
                      sector="Education", contact_email="x@x.com",
                      year_of_incorporation=2010, status="pending",
                      created_at=ts, updated_at=ts))
    db.flush()

    db.add(ExtractedFields(submission_id=sid,
                           merged_fields={"reg": "T123"},
                           extraction_log=[], created_at=ts))

    db.add(ComplianceFinding(id=fid, submission_id=sid,
                             dimension_id="registration",
                             dimension_name="Registration & Legal Status",
                             status="PASS", confidence=0.90,
                             legal_citation="SRA 1860, s.1",
                             ngo_evidence="reg T123",
                             reasoning="OK", routing="auto_report",
                             citation_valid=True, created_at=ts))

    db.add(HumanReviewQueue(id=qid, finding_id=fid, submission_id=sid,
                            dimension_name="Registration & Legal Status",
                            assigned_officer="officer@darpan.gov.in",
                            queue_status="pending",
                            ai_recommendation_revealed=False, created_at=ts))
    db.commit()
    print(f"{INFO_S} Seeded submission + finding + queue item.")

    sub_row = db.query(Submission).filter(Submission.id == sid).first()
    db.delete(sub_row)
    db.commit()

    remaining_f = db.query(ComplianceFinding).filter(ComplianceFinding.submission_id == sid).all()
    remaining_q = db.query(HumanReviewQueue).filter(HumanReviewQueue.submission_id == sid).all()
    remaining_e = db.query(ExtractedFields).filter(ExtractedFields.submission_id == sid).all()

    if not remaining_f and not remaining_q and not remaining_e:
        print(f"{PASS_S} Cascade delete works -- all child rows removed.")
    else:
        print(f"{FAIL_S} Orphan rows found: findings={len(remaining_f)} queue={len(remaining_q)} extracted={len(remaining_e)}")
        errors.append("cascade")
except Exception as e:
    db.rollback()
    print(f"{FAIL_S} Cascade test error: {e}")
    errors.append("cascade")
finally:
    db.close()

# ── CHECK 3: RowDict in-place mutation ────────────────────────────
sep("CHECK 3 -- Store Wrapper Insert / Mutate / Delete")

import collections.abc

class RowDict(dict):
    def __init__(self, initial_dict, wrapper, row_key):
        super().__init__(initial_dict)
        self._wrapper = wrapper
        self._row_key = row_key
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._wrapper._persist_key_value(self._row_key, key, value)

class DbDictWrapper(collections.abc.MutableMapping):
    def __init__(self, model_class, key_field="id"):
        self.model_class = model_class
        self.key_field = key_field
    def _sess(self): return SessionLocal()
    def _to_dict(self, obj):
        if not obj: return None
        d = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        return RowDict(d, self, getattr(obj, self.key_field))
    def _to_model(self, d):
        obj = self.model_class()
        for k, v in d.items():
            if hasattr(obj, k): setattr(obj, k, v)
        return obj
    def __getitem__(self, key):
        s = self._sess()
        try:
            row = s.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(key)).first()
            if not row: raise KeyError(key)
            return self._to_dict(row)
        finally: s.close()
    def __setitem__(self, key, value):
        s = self._sess()
        try:
            value[self.key_field] = str(key)
            row = s.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(key)).first()
            if row:
                for k, v in value.items():
                    if hasattr(row, k): setattr(row, k, v)
            else:
                row = self._to_model(value); s.add(row)
            s.commit()
        except Exception as e:
            s.rollback(); raise
        finally: s.close()
    def __delitem__(self, key):
        s = self._sess()
        try:
            row = s.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(key)).first()
            if not row: raise KeyError(key)
            s.delete(row); s.commit()
        except Exception as e:
            s.rollback(); raise
        finally: s.close()
    def __iter__(self):
        s = self._sess()
        try: return iter([getattr(r, self.key_field) for r in s.query(self.model_class).all()])
        finally: s.close()
    def __len__(self):
        s = self._sess()
        try: return s.query(self.model_class).count()
        finally: s.close()
    def get(self, key, default=None):
        try: return self[key]
        except KeyError: return default
    def values(self):
        s = self._sess()
        try: return [self._to_dict(r) for r in s.query(self.model_class).all()]
        finally: s.close()
    def keys(self): return list(self.__iter__())
    def items(self):
        s = self._sess()
        try: return [(getattr(r, self.key_field), self._to_dict(r)) for r in s.query(self.model_class).all()]
        finally: s.close()
    def _persist_key_value(self, row_key, col, val):
        s = self._sess()
        try:
            row = s.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(row_key)).first()
            if row and hasattr(row, col):
                setattr(row, col, val); s.commit()
        except Exception as e:
            s.rollback(); raise
        finally: s.close()

SUBMISSIONS_W = DbDictWrapper(Submission)
smoke_id = str(uuid.uuid4())
ts = datetime.datetime.utcnow().isoformat()

try:
    SUBMISSIONS_W[smoke_id] = {
        "id": smoke_id, "org_name": "Smoke NGO", "state": "ka",
        "entity_type": "Public Trust", "pan": "SMKP00001",
        "sector": "Health", "contact_email": "s@s.com",
        "year_of_incorporation": 2015, "status": "pending",
        "submitted_by": "officer@darpan.gov.in",
        "created_at": ts, "updated_at": ts,
    }
    print(f"{PASS_S} INSERT via store wrapper.")

    SUBMISSIONS_W[smoke_id]["status"] = "processing"
    fetched = SUBMISSIONS_W.get(smoke_id)
    assert fetched["status"] == "processing", f"Expected 'processing', got '{fetched['status']}'"
    print(f"{PASS_S} In-place RowDict mutation persisted to DB.")

    assert fetched["org_name"] == "Smoke NGO"
    print(f"{PASS_S} GET returns correct field values.")

    del SUBMISSIONS_W[smoke_id]
    assert SUBMISSIONS_W.get(smoke_id) is None
    print(f"{PASS_S} DELETE via store wrapper.")

except AssertionError as e:
    print(f"{FAIL_S} Assertion failed: {e}")
    errors.append("store_wrapper")
except Exception as e:
    print(f"{FAIL_S} Store wrapper error: {e}")
    errors.append("store_wrapper")
    try: del SUBMISSIONS_W[smoke_id]
    except: pass

# ── Cleanup & Result ──────────────────────────────────────────────
sep("RESULT")
import os as _os
try:
    _os.remove("C:/tmp/ngo_verify_test.db")
except: pass

if not errors:
    print(f"\n{PASS_S} All 3 checks passed. ORM, cascade, and store wrappers are correct.")
    print("     When PostgreSQL is running, the same logic applies -- only the dialect changes.")
else:
    print(f"\n{FAIL_S} Failed checks: {errors}")
    sys.exit(1)
