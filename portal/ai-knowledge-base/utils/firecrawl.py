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
        limit=max_pages,
        scrape_formats=['markdown']
    )

    pages = []
    if result and hasattr(result, 'data') and result.data:
        for page in result.data:
            content = ''
            if hasattr(page, 'markdown'):
                content = page.markdown or ''
            elif hasattr(page, 'content'):
                content = page.content or ''

            if content and len(content.strip()) > 100:
                title = url
                page_url = url
                if hasattr(page, 'metadata') and page.metadata:
                    title = getattr(page.metadata, 'title', url) or url
                    page_url = getattr(page.metadata, 'source_url', url) or url

                pages.append({
                    'title': title,
                    'url': page_url,
                    'content': content
                })

    return pages

def scrape_single_page(url: str) -> dict:
    """爬取單一網頁"""
    app = get_firecrawl()
    result = app.scrape_url(url, formats=['markdown'])

    if result:
        content = ''
        title = url
        if hasattr(result, 'markdown'):
            content = result.markdown or ''
        if hasattr(result, 'metadata') and result.metadata:
            title = getattr(result.metadata, 'title', url) or url

        return {
            'title': title,
            'url': url,
            'content': content
        }
    return None
