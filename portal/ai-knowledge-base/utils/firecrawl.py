from firecrawl import FirecrawlApp
import streamlit as st

@st.cache_resource
def get_firecrawl():
    return FirecrawlApp(api_key=st.secrets["FIRECRAWL_API_KEY"])

def crawl_website(url: str, max_pages: int = 10) -> list:
    """
    爬取網站，回傳頁面列表
    每個頁面：{ title, url, content }
    """
    app = get_firecrawl()

    result = app.crawl_url(
        url,
        params={
            'limit': max_pages,
            'scrapeOptions': {
                'formats': ['markdown'],
                'onlyMainContent': True,
            }
        }
    )

    pages = []
    if result and result.get('data'):
        for page in result['data']:
            content = page.get('markdown', '') or page.get('content', '')
            if content and len(content.strip()) > 100:
                pages.append({
                    'title': page.get('metadata', {}).get('title', url),
                    'url': page.get('metadata', {}).get('sourceURL', url),
                    'content': content
                })

    return pages

def scrape_single_page(url: str) -> dict:
    """爬取單一網頁"""
    app = get_firecrawl()
    result = app.scrape_url(url, params={
        'formats': ['markdown'],
        'onlyMainContent': True,
    })

    if result:
        return {
            'title': result.get('metadata', {}).get('title', url),
            'url': url,
            'content': result.get('markdown', '')
        }
    return None
