import pytest
from unittest.mock import MagicMock, patch
from qdrant_client.models import PointStruct, CollectionsResponse, CollectionDescription


class TestVectorStore:
    @patch("app.vector_store.client.QdrantClient")
    def test_collections_initialized(self, mock_client):
        mock_client.return_value.get_collections.return_value = CollectionsResponse(
            collections=[]
        )
        from app.vector_store.client import VectorStore
        store = VectorStore()
        assert store.client.create_collection.call_count == 6

    @patch("app.vector_store.client.QdrantClient")
    def test_upsert_and_search(self, mock_client):
        mock_client.return_value.get_collections.return_value = CollectionsResponse(
            collections=[]
        )
        mock_client.return_value.search.return_value = [
            MagicMock(id=1, score=0.95, payload={"test": "data"})
        ]
        from app.vector_store.client import VectorStore
        store = VectorStore()
        store.upsert("case_labels", [
            PointStruct(id=1, vector=[0.1] * 1024, payload={"name": "test_case"})
        ])
        mock_client.return_value.upsert.assert_called_once()
        results = store.search("case_labels", [0.1] * 1024, limit=1)
        assert len(results) == 1


def test_vector_store_import():
    from app.vector_store.client import VectorStore
    assert VectorStore is not None