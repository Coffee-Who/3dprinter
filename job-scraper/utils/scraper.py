import asyncio
from playwright.async_api import async_playwright

async def scrape_104(keyword: str, max_pages: int = 3) -> list:
    jobs = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for page_num in range(1, max_pages + 1):
            url = f'https://www.104.com.tw/jobs/search/?keyword={keyword}&jobsource=2018indexpoc&page={page_num}'
            await page.goto(url)
            await page.wait_for_timeout(4000)
            
            result = await page.evaluate('''() => {
                const cards = document.querySelectorAll("div.job-summary");
                return Array.from(cards).map(card => {
                    const titleEl   = card.querySelector("a[class*=title], a[title], h2 a");
                    const compEl    = card.querySelector("a[class*=company], a[class*=corp]");
                    const linkEl    = card.querySelector("a[href*='/job/']");
                    const allText   = card.innerText.split("\\n").map(s => s.trim()).filter(s => s.length > 0);
                    return {
                        title:   titleEl ? (titleEl.getAttribute("title") || titleEl.innerText.trim()) : "",
                        company: compEl  ? compEl.innerText.trim() : "",
                        url:     linkEl  ? "https://www.104.com.tw" + linkEl.getAttribute("href") : "",
                        raw:     allText
                    };
                });
            }''')
            
            if not result:
                break
            
            for job in result:
                raw = job.get('raw', [])
                jobs.append({
                    'title':      job.get('title', ''),
                    'company':    job.get('company', ''),
                    'url':        job.get('url', ''),
                    'location':   raw[2] if len(raw) > 2 else '',
                    'experience': raw[3] if len(raw) > 3 else '',
                    'education':  raw[4] if len(raw) > 4 else '',
                    'salary':     raw[5] if len(raw) > 5 else '',
                    'source':     '104'
                })
        
        await browser.close()
    
    return jobs


async def scrape_1111(keyword: str, max_pages: int = 3) -> list:
    # 1111 待實作
    return []


def scrape_jobs(keyword: str, sources: list, max_pages: int = 3) -> list:
    async def _run():
        tasks = []
        if '104' in sources:
            tasks.append(scrape_104(keyword, max_pages))
        if '1111' in sources:
            tasks.append(scrape_1111(keyword, max_pages))
        results = await asyncio.gather(*tasks)
        return [job for sublist in results for job in sublist]
    
    return asyncio.run(_run())