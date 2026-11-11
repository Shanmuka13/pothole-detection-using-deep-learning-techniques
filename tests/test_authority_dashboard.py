from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app import main
from app.mongo_store import _MemoryCollection


def test_memory_store_supports_authority_region_queries():
    collection = _MemoryCollection([
        {"complaint_id": "CMP-1", "district": "NTR", "state": "Andhra Pradesh"},
        {"complaint_id": "CMP-2", "district": "Guntur", "state": "Andhra Pradesh"},
        {"complaint_id": "CMP-3", "district": "Palnadu", "state": "Andhra Pradesh"},
    ])

    results = collection.find({
        "$or": [
            {"district": {"$in": ["Guntur", "Krishna"]}},
            {"state": {"$in": ["Telangana"]}},
        ]
    })

    assert [item["complaint_id"] for item in results] == ["CMP-2"]


def test_memory_store_sorts_mixed_demo_timestamps():
    collection = _MemoryCollection([
        {"complaint_id": "CMP-old", "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc)},
        {"complaint_id": "CMP-new", "created_at": "2026-10-29T10:00:00+00:00"},
    ])

    results = collection.find(sort=[("created_at", -1)])

    assert [item["complaint_id"] for item in results] == ["CMP-new", "CMP-old"]


def test_authority_update_does_not_replace_mongo_document():
    record = {
        "_id": "mongo-id",
        "complaint_id": "CMP-1",
        "authority_id": "AUTH001",
        "status": "PENDING_VERIFICATION",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    collection = _MemoryCollection([record])
    original_collection = main.store.collection
    original_tokens = main.ACTIVE_TOKENS.copy()
    main.store.collection = lambda _name: collection
    main.ACTIVE_TOKENS.clear()
    main.ACTIVE_TOKENS["token"] = {"role": "authority", "account_id": "AUTH001"}
    try:
        result = main.update_complaint(
            "CMP-1",
            main.ComplaintStatusRequest(status="in_progress"),
            "Bearer token",
        )
    finally:
        main.store.collection = original_collection
        main.ACTIVE_TOKENS.clear()
        main.ACTIVE_TOKENS.update(original_tokens)

    assert result["status"] == "IN_PROGRESS"
    assert collection.records[0]["_id"] == "mongo-id"
    assert collection.records[0]["updated_at"]


def test_authority_update_rejects_unknown_status():
    collection = _MemoryCollection([{
        "complaint_id": "CMP-1",
        "authority_id": "AUTH001",
        "status": "PENDING_VERIFICATION",
    }])
    original_collection = main.store.collection
    original_tokens = main.ACTIVE_TOKENS.copy()
    main.store.collection = lambda _name: collection
    main.ACTIVE_TOKENS.clear()
    main.ACTIVE_TOKENS["token"] = {"role": "authority", "account_id": "AUTH001"}
    try:
        with pytest.raises(HTTPException) as error:
            main.update_complaint(
                "CMP-1",
                main.ComplaintStatusRequest(status="not-a-status"),
                "Bearer token",
            )
    finally:
        main.store.collection = original_collection
        main.ACTIVE_TOKENS.clear()
        main.ACTIVE_TOKENS.update(original_tokens)

    assert error.value.status_code == 400
