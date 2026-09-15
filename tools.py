from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the Web for recent and realible information on a topic. Return Titles, URl and Snippets."""

    search_results= tavily.search(query=query, max_results =5)

    out = []

    for r in search_results['results']:
        out.append(
       f"Title: {r['title']}\n URL: {r['url']}\n SNIPPET: {r['content'][:300]}\n"
    )
    return "\n----\n".join(out)

#print(web_search.invoke({'query':'Recent News about Artificial Intelligenece Advancements Including Research Papers and Development in 2026, Market Valuations and Influential People.'}))

@tool   
def scrap_url(url:str) -> str:
    "Scrape and return clean text content from a given URL for deeper reading"   
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]

    except Exception as e:
        return f"Error scraping URL: {e}"

