import datetime
import pytest
from unittest.mock import MagicMock, patch
from app.tools import find_expiring_contracts, check_consumption, get_all_contracts

@pytest.fixture
def mock_firestore_client():
    with patch('app.tools.firestore.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client
        mock_client_class.assert_called_once_with(database="contract-metadata")

def test_find_expiring_contracts_success(mock_firestore_client):
    # Mock data
    now = datetime.datetime.now(datetime.timezone.utc)
    mock_doc = MagicMock()
    mock_doc.id = "test-id"
    mock_doc.to_dict.return_value = {
        "provider_name": "Test Provider",
        "termination_date": now + datetime.timedelta(days=10),
        "commitment_amount": 1000.0,
        "currency": "USD"
    }
    
    mock_query = MagicMock()
    mock_query.stream.return_value = [mock_doc]
    mock_firestore_client.collection.return_value.where.return_value.where.return_value = mock_query
    
    result = find_expiring_contracts(30)
    
    assert result["status"] == "success"
    assert len(result["expiring_contracts"]) == 1
    assert result["expiring_contracts"][0]["provider_name"] == "Test Provider"
    assert result["expiring_contracts"][0]["id"] == "test-id"

def test_get_all_contracts_success(mock_firestore_client):
    mock_doc = MagicMock()
    mock_doc.id = "contract-123"
    mock_doc.to_dict.return_value = {
        "provider_name": "Google",
        "termination_date_str": "2027-01-01"
    }
    
    mock_firestore_client.collection.return_value.stream.return_value = [mock_doc]
    
    result = get_all_contracts()
    
    assert result["status"] == "success"
    assert len(result["contracts"]) == 1
    assert result["contracts"][0]["id"] == "contract-123"
    assert result["contracts"][0]["provider_name"] == "Google"

def test_check_consumption_success(mock_firestore_client):
    # Mock data
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.id = "contract-123"
    mock_doc.to_dict.return_value = {
        "provider_name": "Test Provider",
        "commitment_amount": 5000.0,
        "current_spend": 2500.0,
        "currency": "USD",
        "termination_date_str": "2026-12-31"
    }
    
    mock_firestore_client.collection.return_value.document.return_value.get.return_value = mock_doc
    
    result = check_consumption("contract-123")
    
    assert result["status"] == "success"
    assert result["contract"]["id"] == "contract-123"
    assert result["contract"]["current_spend"] == 2500.0
    assert result["contract"]["commitment_amount"] == 5000.0

def test_check_consumption_not_found(mock_firestore_client):
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore_client.collection.return_value.document.return_value.get.return_value = mock_doc
    
    result = check_consumption("non-existent-id")
    
    assert result["status"] == "not_found"
    assert "No contract found with ID" in result["message"]
