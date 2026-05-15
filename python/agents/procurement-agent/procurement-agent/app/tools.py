import datetime
from google.cloud import firestore

def _get_firestore_client() -> firestore.Client:
    return firestore.Client(database="contract-metadata")

def find_expiring_contracts(days: int) -> dict:
    """Find contracts that expire within a given number of days.

    Args:
        days: The number of days from today to look forward for expiring contracts.

    Returns:
        dict: A dictionary containing the list of expiring contracts.
    """
    try:
        db = _get_firestore_client()
        now = datetime.datetime.now(datetime.timezone.utc)
        target_date = now + datetime.timedelta(days=days)

        collection_ref = db.collection('contracts')
        query = collection_ref.where(filter=firestore.FieldFilter("termination_date", ">=", now)) \
                              .where(filter=firestore.FieldFilter("termination_date", "<=", target_date))

        results = []
        for doc in query.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            # Convert datetime objects to string for JSON serialization
            if 'termination_date' in data and data['termination_date']:
                data['termination_date'] = data['termination_date'].isoformat()
            if 'processed_at' in data and data['processed_at']:
                data['processed_at'] = data['processed_at'].isoformat()
            if 'last_spend_update' in data and data['last_spend_update']:
                data['last_spend_update'] = data['last_spend_update'].isoformat()
            results.append(data)

        return {"status": "success", "expiring_contracts": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_all_contracts() -> dict:
    """Get all existing contracts and their identifiers.

    Returns:
        dict: A dictionary containing the list of all contracts.
    """
    try:
        db = _get_firestore_client()
        collection_ref = db.collection('contracts')

        results = []
        for doc in collection_ref.stream():
            data = doc.to_dict()
            results.append({
                "id": doc.id,
                "provider_name": data.get("provider_name"),
                "termination_date_str": data.get("termination_date_str")
            })

        return {"status": "success", "contracts": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_consumption(contract_id: str) -> dict:
    """Check the current consumption of a given contract against the signed commitment.

    Args:
        contract_id: The ID of the contract/document to check.

    Returns:
        dict: A dictionary containing the consumption and commitment data.
    """
    try:
        db = _get_firestore_client()
        doc_ref = db.collection('contracts').document(contract_id)
        doc = doc_ref.get()

        if not doc.exists:
            return {"status": "not_found", "message": f"No contract found with ID {contract_id}"}

        data = doc.to_dict()
        contract_info = {
            "id": doc.id,
            "provider_name": data.get("provider_name"),
            "commitment_amount": data.get("commitment_amount"),
            "current_spend": data.get("current_spend", 0.0),
            "currency": data.get("currency"),
            "termination_date_str": data.get("termination_date_str")
        }

        return {"status": "success", "contract": contract_info}
    except Exception as e:
        return {"status": "error", "message": str(e)}
