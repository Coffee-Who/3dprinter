def scrape_104(keyword):
    # 模擬 104 內部 API 的請求頭
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': f'https://www.104.com.tw/jobs/search/?kw={keyword}',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 104 真正的資料介面 (API)
    api_url = f"https://www.104.com.tw/jobs/search/list?ro=0&kw={keyword}&order=1&asc=0&page=1&mode=s"
    
    try:
        resp = requests.get(api_url, headers=headers, timeout=15)
        data = resp.json() # API 返回的是 JSON 格式
        
        job_list = data.get('data', {}).get('list', [])
        results = []
        
        for job in job_list:
            results.append({
                "來源": "104 (API)",
                "公司名稱": job.get('custName'),
                "職位名稱": job.get('jobName').replace('<b>', '').replace('</b>', ''),
                "工作內容摘要": job.get('description').replace('\n', ' '),
                "連結": f"https://www.104.com.tw/job/{job.get('jobNo')}"
            })
        return results
    except Exception as e:
        st.error(f"API 抓取失敗: {e}")
        return []
