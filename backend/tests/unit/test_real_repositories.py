"""Unit tests verifying real repository implementations handle pymongo documents with ObjectId _id and datetimes."""

import copy
from datetime import UTC, datetime, timedelta

from bson import ObjectId
import pytest

from app.repositories.admin_repo import AdminRepository
from app.repositories.audit_repo import AuditRepository
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.feedback_repo import FeedbackRepository
from app.repositories.scheme_repo import SchemeRepository
from app.schemas.admin import AdminRole, AdminUserCreate
from app.schemas.chunk import ChunkSection, SchemeChunkCreate
from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import (
    CriterionField,
    CriterionOperator,
    FeedbackVote,
    SchemeLevel,
    SchemeStatus,
)
from app.schemas.feedback import FeedbackCreate
from app.schemas.scheme import SchemeCreate, SchemeUpdate


def make_mongo_doc(data: dict) -> dict:
    """Helper producing documents exactly as pymongo returns them:

    Contains an ObjectId for '_id', strips 'id' if present, and preserves datetime values.
    """
    doc = copy.deepcopy(data)
    if "id" in doc:
        raw_id = doc.pop("id")
        if ObjectId.is_valid(str(raw_id)):
            doc["_id"] = ObjectId(str(raw_id))
        else:
            doc["_id"] = ObjectId()
    elif "_id" not in doc:
        doc["_id"] = ObjectId()
    elif not isinstance(doc["_id"], ObjectId):
        doc["_id"] = ObjectId(str(doc["_id"]))

    return doc


class FakePyMongoCursor:
    """Async cursor simulating pymongo cursor behaviors."""

    def __init__(self, docs: list[dict]):
        self._docs = docs

    def sort(self, key: str, direction: int = 1):
        reverse = direction < 0
        self._docs.sort(key=lambda x: str(x.get(key, "")), reverse=reverse)
        return self

    def skip(self, n: int):
        self._docs = self._docs[n:]
        return self

    def limit(self, n: int):
        self._docs = self._docs[:n]
        return self

    async def to_list(self, length: int | None = None):
        if length is not None:
            return [copy.deepcopy(d) for d in self._docs[:length]]
        return [copy.deepcopy(d) for d in self._docs]


class FakeInsertOneResult:
    def __init__(self, inserted_id: ObjectId):
        self.inserted_id = inserted_id


class FakeInsertManyResult:
    def __init__(self, inserted_ids: list[ObjectId]):
        self.inserted_ids = inserted_ids


class FakeUpdateResult:
    def __init__(self, modified_count: int):
        self.modified_count = modified_count


class FakeDeleteResult:
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class FakePyMongoCollection:
    """Simulates pymongo collection: mutates input docs with _id ObjectId and returns BSON types."""

    def __init__(self):
        self.docs: list[dict] = []

    async def insert_one(self, doc: dict) -> FakeInsertOneResult:
        oid = ObjectId()
        # In real pymongo, insert_one mutates the input doc in place by setting _id
        doc["_id"] = oid
        self.docs.append(copy.deepcopy(doc))
        return FakeInsertOneResult(oid)

    async def insert_many(self, docs: list[dict]) -> FakeInsertManyResult:
        oids = []
        for d in docs:
            oid = ObjectId()
            d["_id"] = oid
            self.docs.append(copy.deepcopy(d))
            oids.append(oid)
        return FakeInsertManyResult(oids)

    def _matches(self, doc: dict, query: dict) -> bool:
        if not query:
            return True
        for k, v in query.items():
            if k == "$or":
                import re

                matched_any = False
                for branch in v:
                    for bk, bv in branch.items():
                        if isinstance(bv, dict) and "$regex" in bv:
                            pattern = bv["$regex"]
                            target_val = str(doc.get(bk, ""))
                            if re.search(pattern, target_val, re.IGNORECASE):
                                matched_any = True
                                break
                        elif doc.get(bk) == bv:
                            matched_any = True
                            break
                    if matched_any:
                        break
                if not matched_any:
                    return False
            elif isinstance(v, dict) and "$in" in v:
                if doc.get(k) not in v["$in"]:
                    return False
            elif isinstance(v, ObjectId):
                if doc.get(k) != v:
                    return False
            elif doc.get(k) != v:
                return False
        return True

    async def find_one(self, query: dict) -> dict | None:
        for d in self.docs:
            if self._matches(d, query):
                return copy.deepcopy(d)
        return None

    def find(self, query: dict | None = None) -> FakePyMongoCursor:
        matched = [d for d in self.docs if self._matches(d, query or {})]
        return FakePyMongoCursor(matched)

    async def count_documents(self, query: dict) -> int:
        return sum(1 for d in self.docs if self._matches(d, query))

    async def find_one_and_update(
        self, query: dict, update: dict, return_document: bool = True
    ) -> dict | None:
        for d in self.docs:
            if self._matches(d, query):
                if "$set" in update:
                    d.update(copy.deepcopy(update["$set"]))
                return copy.deepcopy(d)
        return None

    async def update_one(self, query: dict, update: dict) -> FakeUpdateResult:
        for d in self.docs:
            if self._matches(d, query):
                if "$set" in update:
                    d.update(copy.deepcopy(update["$set"]))
                return FakeUpdateResult(1)
        return FakeUpdateResult(0)

    async def delete_many(self, query: dict) -> FakeDeleteResult:
        initial_len = len(self.docs)
        self.docs = [d for d in self.docs if not self._matches(d, query)]
        return FakeDeleteResult(initial_len - len(self.docs))

    def aggregate(self, pipeline: list) -> FakePyMongoCursor:
        results = []
        for d in self.docs:
            res = copy.deepcopy(d)
            res["score"] = 0.95
            results.append(res)
        return FakePyMongoCursor(results)


class FakePyMongoDatabase:
    """Simulates pymongo AsyncDatabase handle."""

    def __init__(self):
        self._collections: dict[str, FakePyMongoCollection] = {}

    def __getitem__(self, name: str) -> FakePyMongoCollection:
        if name not in self._collections:
            self._collections[name] = FakePyMongoCollection()
        return self._collections[name]


# ==================== SchemeRepository Tests ====================


@pytest.fixture
def sample_scheme_create() -> SchemeCreate:
    now = datetime.now(UTC)
    return SchemeCreate(
        slug="pm-kisan-real-test",
        name="PM Kisan Real Test Scheme",
        name_hi="पीएम किसान रियल टेस्ट",
        level=SchemeLevel.CENTRAL,
        state=None,
        category_tags=["agriculture"],
        benefit_summary="Direct financial support of Rs 6,000 per year.",
        benefit_summary_hi="प्रति वर्ष ₹6,000 की वित्तीय सहायता।",
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.OCCUPATION,
                    op=CriterionOperator.EQ,
                    value="farmer",
                )
            ]
        ),
        required_documents=["Land Record"],
        application_steps=["Apply online"],
        apply_url="https://pmkisan.gov.in/apply",
        source_url="https://pmkisan.gov.in/guidelines.pdf",
        source_hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        status=SchemeStatus.VERIFIED,
        verified_by="admin@internal.gov",
        verified_at=now,
        last_verified=now,
        is_sample=False,
    )


@pytest.mark.asyncio
async def test_scheme_repo_real_methods_with_mongo_documents(
    sample_scheme_create: SchemeCreate,
) -> None:
    """Test all SchemeRepository methods with fake pymongo collection returning ObjectId _id."""
    db = FakePyMongoDatabase()
    repo = SchemeRepository(db)

    # 1. create_scheme (writes with real pymongo _id mutation)
    created = await repo.create_scheme(sample_scheme_create)
    assert created.slug == "pm-kisan-real-test"
    assert created.id is not None
    assert len(created.id) == 24  # Valid 24-character hex string of ObjectId

    # 2. get_by_slug
    fetched = await repo.get_by_slug("pm-kisan-real-test")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "PM Kisan Real Test Scheme"

    # 3. get_by_id_or_slug (by ObjectId string)
    by_id = await repo.get_by_id_or_slug(created.id)
    assert by_id is not None
    assert by_id.slug == "pm-kisan-real-test"

    # 4. get_by_id_or_slug (by slug)
    by_slug = await repo.get_by_id_or_slug("pm-kisan-real-test")
    assert by_slug is not None
    assert by_slug.id == created.id

    # 5. count_verified
    count_v = await repo.count_verified()
    assert count_v == 1

    # 6. get_verified_schemes
    verified_schemes = await repo.get_verified_schemes()
    assert len(verified_schemes) == 1
    assert verified_schemes[0].id == created.id

    # 7. get_admin_schemes
    admin_schemes = await repo.get_admin_schemes(status=SchemeStatus.VERIFIED)
    assert len(admin_schemes) == 1
    assert admin_schemes[0].id == created.id

    # 8. count_admin_schemes
    count_admin = await repo.count_admin_schemes(status=SchemeStatus.VERIFIED)
    assert count_admin == 1

    # 9. update_scheme
    update_data = SchemeUpdate(benefit_summary="Updated benefit summary of Rs 8,000.")
    updated = await repo.update_scheme("pm-kisan-real-test", update_data)
    assert updated is not None
    assert updated.benefit_summary == "Updated benefit summary of Rs 8,000."
    assert updated.id == created.id

    # 10. delete_sample_schemes
    # Insert a sample scheme first
    sample_doc = make_mongo_doc(
        sample_scheme_create.model_dump()
        | {"slug": "sample-to-delete", "is_sample": True}
    )
    await db["schemes"].insert_one(sample_doc)
    deleted = await repo.delete_sample_schemes()
    assert deleted == 1


# ==================== ChunkRepository Tests ====================


@pytest.mark.asyncio
async def test_chunk_repo_real_methods_with_mongo_documents() -> None:
    """Test all ChunkRepository methods with fake pymongo collection."""
    db = FakePyMongoDatabase()
    repo = ChunkRepository(db)

    chunks = [
        SchemeChunkCreate(
            scheme_id="scheme-real-1",
            section=ChunkSection.ELIGIBILITY,
            text="Real eligibility text for chunking test.",
            embedding=[0.1, 0.2, 0.3],
            source_url="https://pmkisan.gov.in/doc.pdf",
            page=1,
        ),
        SchemeChunkCreate(
            scheme_id="scheme-real-1",
            section=ChunkSection.BENEFITS,
            text="Real benefits text for chunking test.",
            embedding=[0.4, 0.5, 0.6],
            source_url="https://pmkisan.gov.in/doc.pdf",
            page=2,
        ),
    ]

    # 1. create_chunks
    ids = await repo.create_chunks(chunks)
    assert len(ids) == 2
    for cid in ids:
        assert len(cid) == 24

    # 2. get_chunks_by_scheme_id
    retrieved = await repo.get_chunks_by_scheme_id("scheme-real-1")
    assert len(retrieved) == 2
    assert retrieved[0].id == ids[0]
    assert retrieved[1].id == ids[1]

    # 3. vector_search
    searched = await repo.vector_search(query_vector=[0.1, 0.2, 0.3], limit=5)
    assert len(searched) == 2
    assert searched[0].score == 0.95
    assert searched[0].id is not None

    # 4. delete_chunks_by_scheme_id
    deleted_count = await repo.delete_chunks_by_scheme_id("scheme-real-1")
    assert deleted_count == 2
    assert len(await repo.get_chunks_by_scheme_id("scheme-real-1")) == 0


# ==================== AdminRepository Tests ====================


@pytest.mark.asyncio
async def test_admin_repo_real_methods_with_mongo_documents() -> None:
    """Test all AdminRepository methods with fake pymongo collection."""
    db = FakePyMongoDatabase()
    repo = AdminRepository(db)

    user_create = AdminUserCreate(
        email="real.admin@yojanasetu.gov.in",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$dummyhashhere1234567890",
        role=AdminRole.ADMIN,
    )

    # 1. create_admin (validates no _id extra inputs error)
    admin = await repo.create_admin(user_create)
    assert admin.email == "real.admin@yojanasetu.gov.in"
    assert admin.id is not None
    assert len(admin.id) == 24

    # 2. get_by_email
    fetched = await repo.get_by_email("REAL.ADMIN@yojanasetu.gov.in")
    assert fetched is not None
    assert fetched.id == admin.id
    assert fetched.role == AdminRole.ADMIN

    # 3. update_login_attempts
    lock_time = datetime.now(UTC) + timedelta(minutes=15)
    ok_update = await repo.update_login_attempts(
        email="real.admin@yojanasetu.gov.in",
        failed_logins=3,
        locked_until=lock_time,
    )
    assert ok_update is True
    updated_admin = await repo.get_by_email("real.admin@yojanasetu.gov.in")
    assert updated_admin.failed_logins == 3

    # 4. reset_failed_logins
    ok_reset = await repo.reset_failed_logins("real.admin@yojanasetu.gov.in")
    assert ok_reset is True
    reset_admin = await repo.get_by_email("real.admin@yojanasetu.gov.in")
    assert reset_admin.failed_logins == 0
    assert reset_admin.locked_until is None

    # 5. count_admins
    assert await repo.count_admins() == 1


# ==================== AuditRepository Tests ====================


@pytest.mark.asyncio
async def test_audit_repo_real_methods_with_mongo_documents() -> None:
    """Test all AuditRepository methods with fake pymongo collection."""
    db = FakePyMongoDatabase()
    repo = AuditRepository(db)

    # 1. log_event (validates no _id extra inputs error)
    log_entry = await repo.log_event(
        actor="system_admin",
        action="verify_scheme",
        target="pm-kisan-slug",
        diff={"status": {"old": "needs_review", "new": "verified"}},
    )
    assert log_entry.actor == "system_admin"
    assert log_entry.id is not None
    assert len(log_entry.id) == 24

    # 2. get_by_target
    target_logs = await repo.get_by_target("pm-kisan-slug")
    assert len(target_logs) == 1
    assert target_logs[0].id == log_entry.id

    # 3. get_logs
    all_logs = await repo.get_logs()
    assert len(all_logs) == 1
    assert all_logs[0].id == log_entry.id

    # 4. count_logs
    assert await repo.count_logs() == 1
    assert await repo.count_logs(target="pm-kisan-slug") == 1
    assert await repo.count_logs(target="unknown-target") == 0


# ==================== FeedbackRepository Tests ====================


@pytest.mark.asyncio
async def test_feedback_repo_real_methods_with_mongo_documents() -> None:
    """Test all FeedbackRepository methods with fake pymongo collection."""
    db = FakePyMongoDatabase()
    repo = FeedbackRepository(db)

    fb_create = FeedbackCreate(
        scheme_id="pm-kisan-test",
        vote=FeedbackVote.HELPFUL,
        comment="Very helpful scheme details.",
    )

    # 1. create_feedback (validates no _id extra inputs error)
    created = await repo.create_feedback(fb_create)
    assert created.scheme_id == "pm-kisan-test"
    assert created.id is not None
    assert len(created.id) == 24

    # 2. get_feedback_by_scheme
    fb_list = await repo.get_feedback_by_scheme("pm-kisan-test")
    assert len(fb_list) == 1
    assert fb_list[0].id == created.id
    assert fb_list[0].vote == FeedbackVote.HELPFUL

