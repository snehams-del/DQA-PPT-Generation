"""Test receipt signing and verification."""

from protect_mcp_adk import ReceiptSigner


def test_sign_and_verify():
    """Test that signed receipts verify correctly."""
    signer = ReceiptSigner.generate()
    receipt = signer.sign_tool_call(
        tool_name="web_search",
        tool_args={"query": "test"},
        decision="allow",
        result={"results": [{"title": "Test"}]},
    )

    assert receipt.verify(signer.public_key_hex)
    assert receipt.payload["tool_name"] == "web_search"
    assert receipt.payload["decision"] == "allow"
    assert "test" not in receipt.to_json()  # Privacy: raw args not in receipt


def test_chain_integrity():
    """Test that receipt chain links correctly."""
    signer = ReceiptSigner.generate()

    r1 = signer.sign_tool_call("web_search", {"query": "adk"})
    r2 = signer.sign_tool_call("read_document", {"url": "https://example.com"})
    r3 = signer.sign_tool_call("analyze_data", {"data_description": "results"})

    assert r1.payload["previousReceiptHash"] is None
    assert r2.payload["previousReceiptHash"] is not None
    assert r3.payload["previousReceiptHash"] is not None
    assert r1.payload["sequence"] == 1
    assert r2.payload["sequence"] == 2
    assert r3.payload["sequence"] == 3

    # All verify
    for r in [r1, r2, r3]:
        assert r.verify(signer.public_key_hex)


def test_tamper_detection():
    """Test that tampered receipts fail verification."""
    signer = ReceiptSigner.generate()
    receipt = signer.sign_tool_call("web_search", {"query": "test"})

    # Tamper with the payload
    receipt.payload["decision"] = "deny"
    assert not receipt.verify(signer.public_key_hex)
