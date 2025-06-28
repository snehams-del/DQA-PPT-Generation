"""Tool to search Google Scholar for papers on a given topic"""

import os
import requests

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def find_papers_tool(query: str) -> dict:
    """Performs a search on Google Scholar using SerpApi, limiting results to 5 articles
    and returning specific details like title, link, snippet, and author information.

    Args:
        query: The search query string.

    Returns:
        A dictionary containing a list of up to 5 simplified article results.
        Each article dictionary will have 'title', 'link', 'snippet', 'author_names', and 'author_ids'.
        Returns a dictionary with an 'error' key if the request fails.
    """
    if not os.getenv("SERPAPI_API_KEY"):
        return {"error": "SERPAPI_API_KEY environment variable not set."}

    base_url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
        "as_ylo": "2000",
        "num": 5, 
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        search_results = response.json()

        processed_articles = []

        if "organic_results" in search_results:
            for result in search_results["organic_results"]:
                author_names = []
                author_ids = []
                if "publication_info" in result:
                    if "authors" in result["publication_info"]:
                        for author in result["publication_info"]["authors"]:
                            author_names.append(author.get("name", "N/A"))
                            author_ids.append(author.get("author_id", "N/A"))
                    elif "summary" in result["publication_info"]:
                        author_names.append(result["publication_info"].get("summary", "N/A"))

                article_info = {
                    "title": result.get("title", "N/A"),
                    "link": result.get("link", "N/A"),
                    "snippet": result.get("snippet", "N/A"),
                    "author_names": author_names,
                    "author_ids": author_ids,
                }
                processed_articles.append(article_info)

        return {"articles": processed_articles}

    except requests.exceptions.RequestException as e:
        print(f"A request error occurred: {e}")
        return {"error": f"Request error: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": f"Unexpected error: {e}"}
