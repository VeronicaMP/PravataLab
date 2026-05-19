#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error

# Configurable IDs (default to Veronica Pravata)
GOOGLE_SCHOLAR_ID = os.environ.get("GOOGLE_SCHOLAR_ID", "_-1UOnoAAAAJ")
SEMANTIC_SCHOLAR_ID = os.environ.get("SEMANTIC_SCHOLAR_ID", "79375083")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

OUTPUT_FILE = "publications.json"

def fetch_semantic_scholar(author_id):
    print(f"Fetching publications from Semantic Scholar for ID: {author_id}...")
    url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers?fields=title,year,authors,venue,externalIds,url,citationCount"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("data", [])
    except Exception as e:
        print(f"Error fetching from Semantic Scholar: {e}", file=sys.stderr)
        return None

def fetch_serpapi(author_id, api_key):
    print(f"Fetching publications from Google Scholar via SerpAPI for ID: {author_id}...")
    url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id={author_id}&api_key={api_key}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("articles", [])
    except Exception as e:
        print(f"Error fetching from SerpAPI: {e}", file=sys.stderr)
        return None

def convert_semantic_scholar_papers(papers):
    converted = []
    for paper in papers:
        title = paper.get("title", "")
        authors = [author.get("name", "") for author in paper.get("authors", [])]
        
        year = paper.get("year")
        date = [int(year), 1] if year is not None else [2000, 1]
        
        journal = paper.get("venue", "")
        
        doi = paper.get("externalIds", {}).get("DOI")
        link = f"https://doi.org/{doi}" if doi else paper.get("url", "")
        
        citations = paper.get("citationCount", 0)
        
        converted.append({
            "title": title,
            "authors": authors,
            "date": date,
            "journal": journal,
            "link": link,
            "citations": citations
        })
    return converted

def convert_serpapi_articles(articles):
    converted = []
    for article in articles:
        title = article.get("title", "")
        authors_str = article.get("authors", "")
        authors = [a.strip() for a in authors_str.split(",") if a.strip()]
        
        year_str = article.get("year", "")
        try:
            year = int(year_str) if year_str else 2000
        except ValueError:
            year = 2000
        date = [year, 1]
        
        journal = article.get("publication", "")
        link = article.get("link", "")
        
        citations = article.get("cited_by", {}).get("value", 0) if isinstance(article.get("cited_by"), dict) else article.get("cited_by", 0)
        
        converted.append({
            "title": title,
            "authors": authors,
            "date": date,
            "journal": journal,
            "link": link,
            "citations": citations
        })
    return converted

def main():
    publications = None
    
    if SERPAPI_API_KEY:
        articles = fetch_serpapi(GOOGLE_SCHOLAR_ID, SERPAPI_API_KEY)
        if articles:
            publications = convert_serpapi_articles(articles)
    else:
        print("SERPAPI_API_KEY environment variable not set. Falling back to Semantic Scholar...")
        papers = fetch_semantic_scholar(SEMANTIC_SCHOLAR_ID)
        if papers:
            publications = convert_semantic_scholar_papers(papers)

    if not publications:
        print("Failed to retrieve any publications. Preserving existing publications.json.", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully retrieved {len(publications)} publications. Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(publications, f, indent=2, ensure_ascii=False)
    print("Done!")

if __name__ == "__main__":
    main()
