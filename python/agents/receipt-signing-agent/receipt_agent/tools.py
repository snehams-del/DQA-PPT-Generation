"""Example research tools for the receipt-signing agent."""


def web_search(query: str) -> dict:
    """Search the web for information on a topic.

    Args:
        query: The search query string.

    Returns:
        Search results with title, snippet, and URL.
    """
    # Placeholder - replace with real search API
    return {
        "results": [
            {
                "title": f"Result for: {query}",
                "snippet": f"Information about {query} from web search.",
                "url": f"https://example.com/search?q={query}",
            }
        ],
        "total_results": 1,
    }


def read_document(url: str) -> dict:
    """Read and extract content from a document URL.

    Args:
        url: The URL of the document to read.

    Returns:
        Document content with title and text.
    """
    return {
        "title": f"Document at {url}",
        "content": f"Extracted content from {url}",
        "word_count": 500,
    }


def analyze_data(data_description: str, analysis_type: str = "summary") -> dict:
    """Analyze data and produce insights.

    Args:
        data_description: Description of the data to analyze.
        analysis_type: Type of analysis (summary, trend, comparison).

    Returns:
        Analysis results with findings and confidence.
    """
    return {
        "analysis_type": analysis_type,
        "findings": [
            f"Key finding about {data_description}",
            f"Secondary insight from {analysis_type} analysis",
        ],
        "confidence": 0.85,
    }
