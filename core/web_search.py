"""
web_search.py
DuckDuckGo text search (kept from LIKKI_AI since it already worked well).
"""

from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 5) -> list[dict]:
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "link": r.get("href", ""),
                        "snippet": r.get("body", ""),
                    }
                )
    except Exception as e:
        print("Web search error:", e)
    return results
