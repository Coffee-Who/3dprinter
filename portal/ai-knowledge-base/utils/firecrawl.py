from firecrawl import Firecrawl
import streamlit as st

@st.cache_resource
def get_firecrawl():
    return Firecrawl(api_key=st.secrets["FIRECRAWL_API_KEY"])

def crawl_website(url: str, max_pages: int = 10) -> list:
    app = get_firecrawl()

    result = app.crawl(
        url,
        limit=max_pages,
        scrape_options={'formats': ['markdown']}
    )

    pages = []
    if result and hasattr(result, 'data') and result.data:
        for page in result.data:
            content = getattr(page, 'markdown', '') or ''
            if content and len(content.strip()) > 100:
                metadata = getattr(page, 'metadata', None)
                title = url
                page_url = url
                if metadata:
                    title   = getattr(metadata, 'title', url) or url
                    page_url = getattr(metadata, 'source_url', url) or url
                pages.append({
                    'title': title,
                    'url': page_url,
                    'content': content
                })
    return pages

def scrape_single_page(url: str) -> dict:
    app = get_firecrawl()
    result = app.scrape(url, formats=['markdown'])
    if result:
        content = getattr(result, 'markdown', '') or ''
        metadata = getattr(result, 'metadata', None)
        title = url
        if metadata:
            title = getattr(metadata, 'title', url) or url
        return {'title': title, 'url': url, 'content': content}
    return None
