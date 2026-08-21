# Database-backed store — swaps out transient in-memory dicts for PostgreSQL/SQLite.
# Maintains backward-compatible dictionary interfaces for all FastAPI routers.

from datetime import datetime
import uuid
import collections.abc
from backend.models.database import SessionLocal
from backend.models.orm import (
    Submission, UploadedDocument, ExtractedFields, ComplianceFinding, HumanReviewQueue
)

def new_id():
    return str(uuid.uuid4())

def now():
    return datetime.utcnow().isoformat()


class RowDict(dict):
    """
    Custom dict subclass that intercepts mutations (like RowDict['status'] = 'processing')
    and writes them back to the database via its parent wrapper.
    """
    def __init__(self, initial_dict, wrapper, row_key):
        super().__init__(initial_dict)
        self._wrapper = wrapper
        self._row_key = row_key

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._wrapper._persist_key_value(self._row_key, key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
        self._wrapper._persist_key_delete(self._row_key, key)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._wrapper._persist_dict(self._row_key, self)

    def pop(self, key, default=None):
        val = super().pop(key, default)
        self._wrapper._persist_key_delete(self._row_key, key)
        return val


class DbDictWrapper(collections.abc.MutableMapping):
    """
    A dictionary interface backed by a relational database table.
    Ensures seamless compatibility with all dict operations in FastAPI routers.
    """
    def __init__(self, model_class, key_field="id"):
        self.model_class = model_class
        self.key_field = key_field

    def _get_session(self):
        return SessionLocal()

    def _to_dict(self, obj):
        if not obj:
            return None
        d = {}
        for c in obj.__table__.columns:
            val = getattr(obj, c.name)
            d[c.name] = val
        
        # Virtual dictionary mapping for Submission 'score'
        if self.model_class == Submission:
            if obj.overall_score is not None or obj.score_label is not None:
                d["score"] = {
                    "overall_score": obj.overall_score,
                    "label": obj.score_label,
                    "grant_ready": obj.grant_ready,
                    "pass_count": obj.pass_count or 0,
                    "fail_count": obj.fail_count or 0,
                    "uncertain_count": obj.uncertain_count or 0,
                    "corpus_gap_count": obj.corpus_gap_count or 0,
                }
            else:
                d["score"] = None

        return RowDict(d, self, getattr(obj, self.key_field))

    def _to_model(self, d, session):
        obj = self.model_class()
        for k, v in d.items():
            if k == "score" and isinstance(v, dict) and self.model_class == Submission:
                obj.overall_score = v.get("overall_score")
                obj.score_label = v.get("label")
                obj.grant_ready = v.get("grant_ready")
                obj.pass_count = v.get("pass_count", 0)
                obj.fail_count = v.get("fail_count", 0)
                obj.uncertain_count = v.get("uncertain_count", 0)
                obj.corpus_gap_count = v.get("corpus_gap_count", 0)
            elif hasattr(obj, k):
                setattr(obj, k, v)
        return obj

    def __getitem__(self, key):
        session = self._get_session()
        try:
            row = session.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(key)
            ).first()
            if not row:
                raise KeyError(key)
            return self._to_dict(row)
        finally:
            session.close()

    def __setitem__(self, key, value):
        session = self._get_session()
        try:
            value[self.key_field] = str(key)
            row = session.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(key)
            ).first()
            if row:
                for k, v in value.items():
                    if k == "score" and isinstance(v, dict) and self.model_class == Submission:
                        row.overall_score = v.get("overall_score")
                        row.score_label = v.get("label")
                        row.grant_ready = v.get("grant_ready")
                        row.pass_count = v.get("pass_count", 0)
                        row.fail_count = v.get("fail_count", 0)
                        row.uncertain_count = v.get("uncertain_count", 0)
                        row.corpus_gap_count = v.get("corpus_gap_count", 0)
                    elif hasattr(row, k):
                        setattr(row, k, v)
            else:
                row = self._to_model(value, session)
                session.add(row)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def __delitem__(self, key):
        session = self._get_session()
        try:
            row = session.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(key)
            ).first()
            if not row:
                raise KeyError(key)
            session.delete(row)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def __iter__(self):
        session = self._get_session()
        try:
            keys = [getattr(row, self.key_field) for row in session.query(self.model_class).all()]
            return iter(keys)
        finally:
            session.close()

    def __len__(self):
        session = self._get_session()
        try:
            return session.query(self.model_class).count()
        finally:
            session.close()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def values(self):
        session = self._get_session()
        try:
            return [self._to_dict(row) for row in session.query(self.model_class).all()]
        finally:
            session.close()

    def keys(self):
        return list(self.__iter__())

    def items(self):
        session = self._get_session()
        try:
            return [(getattr(row, self.key_field), self._to_dict(row)) for row in session.query(self.model_class).all()]
        finally:
            session.close()

    def _persist_key_value(self, row_key, col_name, val):
        session = self._get_session()
        try:
            row = session.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(row_key)
            ).first()
            if row:
                if col_name == "score" and isinstance(val, dict) and self.model_class == Submission:
                    row.overall_score = val.get("overall_score")
                    row.score_label = val.get("label")
                    row.grant_ready = val.get("grant_ready")
                    row.pass_count = val.get("pass_count", 0)
                    row.fail_count = val.get("fail_count", 0)
                    row.uncertain_count = val.get("uncertain_count", 0)
                    row.corpus_gap_count = val.get("corpus_gap_count", 0)
                elif hasattr(row, col_name):
                    setattr(row, col_name, val)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _persist_key_delete(self, row_key, col_name):
        session = self._get_session()
        try:
            row = session.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(row_key)
            ).first()
            if row and hasattr(row, col_name):
                setattr(row, col_name, None)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _persist_dict(self, row_key, d):
        session = self._get_session()
        try:
            row = session.query(self.model_class).filter(
                getattr(self.model_class, self.key_field) == str(row_key)
            ).first()
            if row:
                for k, v in d.items():
                    if k == "score" and isinstance(v, dict) and self.model_class == Submission:
                        row.overall_score = v.get("overall_score")
                        row.score_label = v.get("label")
                        row.grant_ready = v.get("grant_ready")
                        row.pass_count = v.get("pass_count", 0)
                        row.fail_count = v.get("fail_count", 0)
                        row.uncertain_count = v.get("uncertain_count", 0)
                        row.corpus_gap_count = v.get("corpus_gap_count", 0)
                    elif hasattr(row, k):
                        setattr(row, k, v)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# ── Database Dict Instances ───────────────────────────────────────────
SUBMISSIONS = DbDictWrapper(Submission)
DOCUMENTS   = DbDictWrapper(UploadedDocument)
EXTRACTED   = DbDictWrapper(ExtractedFields, key_field="submission_id")
FINDINGS    = DbDictWrapper(ComplianceFinding)
QUEUE       = DbDictWrapper(HumanReviewQueue)
REPORTS     = {}


# ── Helpers ───────────────────────────────────────────────────────────

def get_submission(submission_id: str) -> dict:
    return SUBMISSIONS.get(submission_id)

def get_documents_for_submission(submission_id: str) -> list:
    session = SessionLocal()
    try:
        rows = session.query(UploadedDocument).filter(UploadedDocument.submission_id == str(submission_id)).all()
        return [DOCUMENTS._to_dict(row) for row in rows]
    finally:
        session.close()

def get_findings_for_submission(submission_id: str) -> list:
    session = SessionLocal()
    try:
        rows = session.query(ComplianceFinding).filter(ComplianceFinding.submission_id == str(submission_id)).all()
        return [FINDINGS._to_dict(row) for row in rows]
    finally:
        session.close()

def get_queue_for_submission(submission_id: str) -> list:
    session = SessionLocal()
    try:
        rows = session.query(HumanReviewQueue).filter(HumanReviewQueue.submission_id == str(submission_id)).all()
        return [QUEUE._to_dict(row) for row in rows]
    finally:
        session.close()