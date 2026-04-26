import streamlit as st
import json, os, time
from datetime import datetime
from utils.scraper import scrape_104, scrape_1111
from utils.storage import load_jobs, save_jobs, load_config, save_config
from utils.exporter import export_excel

st.set_page_config(
    page_title="職缺雷達系統",
    page_icon="🎯",
    layout="wide"
)

# ── 深色主題 CSS ──
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}
[data-testid="stMain"], [data-testid="stAppViewBlockContainer"] {
    background-color: #0d1117 !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
}

/* Header */
.page-header {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border-bottom: 1px solid #30363d;
    padding: 20px 28px 16px;
    margin: -6rem -4rem 2rem;
    display: flex; align-items: center; gap: 14px;
}
.header-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
}
.header-title { font-size: 22px; font-weight: 700; color: #e6edf3; margin: 0; }
.header-sub   { font-size: 12px; color: #8b949e; margin: 0; }

/* Cards */
.stat-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-bottom: 24px;
}
.stat-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 16px 20px;
}
.stat-num  { font-size: 28px; font-weight: 700; color: #58a6ff; line-height: 1; }
.stat-lbl  { font-size: 11px; color: #8b949e; margin-top: 4px;
             text-transform: uppercase; letter-spacing: .5px; }

/* Job Cards */
.job-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 16px 20px;
    margin-bottom: 10px; transition: border-color .2s;
}
.job-card:hover { border-color: #58a6ff; }
.job-title { font-size: 15px; font-weight: 600; color: #58a6ff; }
.job-company { font-size: 13px; color: #8b949e; margin-top: 2px; }
.job-meta { display: flex; gap: 16px; margin-top: 10px; flex-wrap: wrap; }
.job-tag {
    background: #21262d; border: 1px solid #30363d;
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: #c9d1d9;
}
.job-tag.green  { border-color: #238636; color: #3fb950; background: #0f2a1a; }
.job-tag.blue   { border-color: #1f6feb; color: #58a6ff; background: #0d1f3c; }
.job-tag.purple { border-color: #6e40c9; color: #a371f7; background: #1a0d3c; }
.job-tag.source-104  { border-color: #e36209; color: #f0883e; background: #2d1b00; }
.job-tag.source-1111 { border-color: #1f6feb; color: #58a6ff; background: #0d1f3c; }
.new-badge {
    display: inline-block; background: #1a3a1a; border: 1px solid #238636;
    color: #3fb950; border-radius: 20px; font-size: 10px;
    padding: 1px 8px; margin-left: 8px; vertical-align: middle;
}

/* Section */
.section-hd {
    font-size: 13px; font-weight: 600; color: #8b949e;
    text-transform: uppercase; letter-spacing: .8px;
    margin: 24px 0 12px; padding-bottom: 8px;
    border-bottom: 1px solid #21262d;
}

/* Buttons */
[data-testid="stButton"] button {
    background: #21262d !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important; border-radius: 8px !important;
    font-size: 13px !important; transition: all .15s !important;
}
[data-testid="stButton"] button:hover {
    background: #30363d !important; border-color: #58a6ff !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #1f6feb, #1158b7) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
}
button[kind="primary"]:hover { opacity: .9 !important; }

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #21262d !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important; border-radius: 8px !important;
}
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: #21262d !important; color: #e6edf3 !important;
    border-color: #30363d !important;
}
label, .stMarkdown p { color: #c9d1d9 !important; }
[data-testid="stCheckbox"] label { color: #c9d1d9 !important; }

/* Toast */
.stAlert { border-radius: 10px !important; }

/* Tabs */
[data-testid="stTabs"] [role="tab"] {
    color: #8b949e !important; border-radius: 8px 8px 0 0 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #58a6ff !important; border-bottom: 2px solid #58a6ff !important;
}

/* Progress */
.scrape-log {
    background: #0d1117; border: 1px solid #21262d;
    border-radius: 8px; padding: 12px 16px;
    font-family: monospace; font-size: 12px; color: #3fb950;
    max-height: 200px; overflow-y: auto;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════
# HEADER
# ══════════════════════════════
st.markdown("""
<div class="page-header">
  <div class="header-icon">🎯</div>
  <div>
    <div class="header-title">職缺雷達系統</div>
    <div class="header-sub">104 ✦ 1111 · 自動爬取 · 定時匯出 Excel</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 載入資料 ──
jobs   = load_jobs()
config = load_config()

# ══════════════════════════════
# 統計卡片
# ══════════════════════════════
total   = len(jobs)
new_today = len([j for j in jobs if j.get("date","") == datetime.now().strftime("%Y-%m-%d")])
src_104  = len([j for j in jobs if j.get("source") == "104"])
src_1111 = len([j for j in jobs if j.get("source") == "1111"])

st.markdown(f"""
<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-num">{total}</div>
    <div class="stat-lbl">📋 總職缺數</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="color:#3fb950">{new_today}</div>
    <div class="stat-lbl">✨ 今日新增</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="color:#f0883e">{src_104}</div>
    <div class="stat-lbl">🔶 104 人力銀行</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="color:#58a6ff">{src_1111}</div>
    <div class="stat-lbl">🔷 1111 人力銀行</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════
# TABS
# ══════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["🔍 職缺列表", "⚙️ 搜尋設定", "⏰ 排程設定", "📥 匯出 Excel"])

# ──────────────────────────────
# TAB 1: 職缺列表
# ──────────────────────────────
with tab1:
    col_f1, col_f2, col_f3, col_f4 = st.columns([3, 2, 2, 1])
    with col_f1:
        kw_filter = st.text_input("🔎 篩選職缺", placeholder="輸入職稱、公司、技能…")
    with col_f2:
        src_filter = st.selectbox("來源", ["全部", "104", "1111"])
    with col_f3:
        sort_by = st.selectbox("排序", ["最新優先", "薪資高低", "公司名稱"])
    with col_f4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 立即爬取", type="primary", use_container_width=True):
            st.session_state["do_scrape"] = True

    # 篩選
    filtered = jobs
    if kw_filter:
        kw = kw_filter.lower()
        filtered = [j for j in filtered if
                    kw in j.get("title","").lower() or
                    kw in j.get("company","").lower() or
                    kw in " ".join(j.get("skills",[])).lower() or
                    kw in j.get("content","").lower()]
    if src_filter != "全部":
        filtered = [j for j in filtered if j.get("source") == src_filter]

    # 排序
    if sort_by == "最新優先":
        filtered = sorted(filtered, key=lambda x: x.get("date",""), reverse=True)
    elif sort_by == "薪資高低":
        filtered = sorted(filtered, key=lambda x: x.get("salary_min", 0), reverse=True)
    elif sort_by == "公司名稱":
        filtered = sorted(filtered, key=lambda x: x.get("company",""))

    st.markdown(f'<div class="section-hd">共 {len(filtered)} 筆職缺</div>', unsafe_allow_html=True)

    if not filtered:
        st.info("📭 尚無資料，請至【搜尋設定】設定關鍵字後點擊「立即爬取」")
    else:
        for job in filtered[:100]:  # 最多顯示100筆
            is_new = job.get("date","") == datetime.now().strftime("%Y-%m-%d")
            new_tag = '<span class="new-badge">NEW</span>' if is_new else ""
            src_cls = "source-104" if job.get("source") == "104" else "source-1111"
            skills_html = " ".join([f'<span class="job-tag purple">{s}</span>'
                                    for s in job.get("skills", [])[:5]])
            salary = job.get("salary", "面議")
            exp    = job.get("experience", "")
            edu    = job.get("education", "")

            st.markdown(f"""
<div class="job-card">
  <div class="job-title">
    <a href="{job.get('url','#')}" target="_blank" style="color:#58a6ff;text-decoration:none;">
      {job.get('title','（未命名）')}
    </a>{new_tag}
  </div>
  <div class="job-company">🏢 {job.get('company','—')} &nbsp;·&nbsp; 📍 {job.get('location','—')}</div>
  <div class="job-meta">
    <span class="job-tag {src_cls}">{'🔶 104' if job.get('source')=='104' else '🔷 1111'}</span>
    <span class="job-tag green">💰 {salary}</span>
    {'<span class="job-tag blue">📅 ' + exp + '</span>' if exp else ''}
    {'<span class="job-tag">🎓 ' + edu + '</span>' if edu else ''}
    {skills_html}
  </div>
  <div style="font-size:12px;color:#8b949e;margin-top:8px;line-height:1.5;">
    {job.get('content','')[:150]}{'…' if len(job.get('content',''))>150 else ''}
  </div>
  <div style="font-size:11px;color:#484f58;margin-top:8px;">🗓 {job.get('date','')}</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────
# TAB 2: 搜尋設定
# ──────────────────────────────
with tab2:
    st.markdown('<div class="section-hd">關鍵字設定</div>', unsafe_allow_html=True)

    col_k1, col_k2 = st.columns(2)
    with col_k1:
        keywords_raw = st.text_area(
            "搜尋關鍵字（每行一個）",
            value="\n".join(config.get("keywords", ["Python工程師", "資料分析師"])),
            height=160,
            help="每行輸入一個關鍵字，系統會逐一搜尋"
        )
    with col_k2:
        st.markdown("**搜尋來源**")
        use_104  = st.checkbox("🔶 104 人力銀行",  value=config.get("use_104", True))
        use_1111 = st.checkbox("🔷 1111 人力銀行", value=config.get("use_1111", True))

        st.markdown("**進階設定**")
        max_pages = st.number_input("每個關鍵字爬取頁數", 1, 10, config.get("max_pages", 3))
        dedup = st.checkbox("自動去除重複職缺", value=config.get("dedup", True))

    st.markdown('<div class="section-hd">篩選條件</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        exclude_kw = st.text_area(
            "排除關鍵字（每行一個）",
            value="\n".join(config.get("exclude_keywords", [])),
            height=100,
            help="包含這些字的職缺會被過濾掉"
        )
    with col_f2:
        salary_min = st.number_input("最低薪資（元）", 0, 200000, config.get("salary_min", 0), step=1000)
    with col_f3:
        locations = st.text_area(
            "限定縣市（每行一個，空白=全台）",
            value="\n".join(config.get("locations", [])),
            height=100
        )

    if st.button("💾 儲存設定", type="primary"):
        config.update({
            "keywords":         [k.strip() for k in keywords_raw.split("\n") if k.strip()],
            "use_104":          use_104,
            "use_1111":         use_1111,
            "max_pages":        max_pages,
            "dedup":            dedup,
            "exclude_keywords": [k.strip() for k in exclude_kw.split("\n") if k.strip()],
            "salary_min":       salary_min,
            "locations":        [l.strip() for l in locations.split("\n") if l.strip()],
        })
        save_config(config)
        st.success("✅ 設定已儲存！")

    st.divider()
    st.markdown('<div class="section-hd">立即執行爬蟲</div>', unsafe_allow_html=True)
    if st.button("🚀 立即開始爬取", type="primary") or st.session_state.get("do_scrape"):
        st.session_state["do_scrape"] = False
        keywords = config.get("keywords", [])
        if not keywords:
            st.error("請先設定關鍵字！")
        else:
            log_area = st.empty()
            progress = st.progress(0)
            log_lines = []

            def log(msg):
                log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
                log_area.markdown(
                    f'<div class="scrape-log">{"<br>".join(log_lines[-20:])}</div>',
                    unsafe_allow_html=True
                )

            all_new = []
            total_steps = (
                (len(keywords) if use_104  else 0) +
                (len(keywords) if use_1111 else 0)
            )
            step = 0

            for kw in keywords:
                if use_104:
                    log(f"🔶 104 搜尋：{kw}")
                    try:
                        results = scrape_104(kw, max_pages=max_pages)
                        log(f"   → 取得 {len(results)} 筆")
                        all_new.extend(results)
                    except Exception as e:
                        log(f"   ❌ 失敗：{e}")
                    step += 1
                    progress.progress(step / max(total_steps, 1))
                    time.sleep(1.5)

                if use_1111:
                    log(f"🔷 1111 搜尋：{kw}")
                    try:
                        results = scrape_1111(kw, max_pages=max_pages)
                        log(f"   → 取得 {len(results)} 筆")
                        all_new.extend(results)
                    except Exception as e:
                        log(f"   ❌ 失敗：{e}")
                    step += 1
                    progress.progress(step / max(total_steps, 1))
                    time.sleep(1.5)

            # 去重 + 篩選
            existing_urls = {j["url"] for j in jobs}
            added = [j for j in all_new if j["url"] not in existing_urls]

            # 排除關鍵字篩選
            excl = config.get("exclude_keywords", [])
            if excl:
                added = [j for j in added if not any(
                    e.lower() in j.get("title","").lower() or
                    e.lower() in j.get("content","").lower()
                    for e in excl
                )]

            jobs.extend(added)
            save_jobs(jobs)
            progress.progress(1.0)
            log(f"✅ 完成！新增 {len(added)} 筆職缺")
            st.success(f"🎉 爬取完成！共新增 {len(added)} 筆職缺")
            st.rerun()

# ──────────────────────────────
# TAB 3: 排程設定
# ──────────────────────────────
with tab3:
    st.markdown('<div class="section-hd">自動排程說明</div>', unsafe_allow_html=True)
    st.info("""
    **⏰ 定時爬取** 透過 GitHub Actions 實現（完全免費）

    設定步驟：
    1. 將此專案 Push 到 GitHub
    2. GitHub Actions 會依照 `.github/workflows/daily_scrape.yml` 的設定自動執行
    3. 預設每天 **早上 9:00（台灣時間）** 自動爬取並更新資料
    """)

    st.markdown('<div class="section-hd">排程時間設定</div>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sched_hour = st.number_input("執行時間（小時，台灣時間）", 0, 23,
                                      config.get("schedule_hour", 9))
    with col_s2:
        sched_min  = st.number_input("執行時間（分鐘）", 0, 59,
                                      config.get("schedule_min", 0))

    auto_export = st.checkbox("每次爬取後自動匯出 Excel",
                               value=config.get("auto_export", True))

    if st.button("💾 儲存排程設定", type="primary"):
        config.update({
            "schedule_hour": sched_hour,
            "schedule_min":  sched_min,
            "auto_export":   auto_export,
        })
        save_config(config)
        # 更新 GitHub Actions yml
        utc_hour = (sched_hour - 8) % 24
        yml_path = ".github/workflows/daily_scrape.yml"
        if os.path.exists(yml_path):
            with open(yml_path) as f:
                yml = f.read()
            yml = yml.replace(
                yml.split("cron:")[1].split("\n")[0],
                f" '{sched_min} {utc_hour} * * *'"
            )
            with open(yml_path, "w") as f:
                f.write(yml)
        st.success(f"✅ 排程已設為每天 {sched_hour:02d}:{sched_min:02d}（台灣時間）")

    st.markdown('<div class="section-hd">資料管理</div>', unsafe_allow_html=True)
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        keep_days = st.number_input("保留幾天的資料", 1, 365,
                                     config.get("keep_days", 30))
        if st.button("🧹 清除舊資料"):
            from datetime import timedelta
            cutoff = (datetime.now() - timedelta(days=keep_days)).strftime("%Y-%m-%d")
            before = len(jobs)
            jobs_kept = [j for j in jobs if j.get("date","") >= cutoff]
            save_jobs(jobs_kept)
            st.success(f"✅ 清除 {before - len(jobs_kept)} 筆舊資料")
            st.rerun()
    with col_m2:
        st.metric("目前資料量", f"{len(jobs)} 筆")
        st.metric("最後更新", config.get("last_run", "尚未執行"))

# ──────────────────────────────
# TAB 4: 匯出 Excel
# ──────────────────────────────
with tab4:
    st.markdown('<div class="section-hd">匯出設定</div>', unsafe_allow_html=True)

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        export_src = st.multiselect("匯出來源", ["104", "1111"],
                                     default=["104", "1111"])
        export_date = st.selectbox("匯出範圍",
                                    ["全部資料", "今天", "最近7天", "最近30天"])
    with col_e2:
        export_cols = st.multiselect(
            "選擇欄位",
            ["職缺名稱", "公司名稱", "工作地點", "薪資", "工作內容",
             "技能需求", "學歷要求", "工作年資", "來源", "連結", "抓取日期"],
            default=["職缺名稱", "公司名稱", "工作地點", "薪資",
                     "技能需求", "來源", "連結", "抓取日期"]
        )

    if st.button("📥 產生並下載 Excel", type="primary"):
        from datetime import timedelta
        filtered_export = [j for j in jobs if j.get("source") in export_src]
        if export_date == "今天":
            today = datetime.now().strftime("%Y-%m-%d")
            filtered_export = [j for j in filtered_export if j.get("date","") == today]
        elif export_date == "最近7天":
            cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            filtered_export = [j for j in filtered_export if j.get("date","") >= cutoff]
        elif export_date == "最近30天":
            cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            filtered_export = [j for j in filtered_export if j.get("date","") >= cutoff]

        if not filtered_export:
            st.warning("⚠️ 沒有符合條件的資料")
        else:
            excel_bytes = export_excel(filtered_export, export_cols)
            fname = f"職缺資料_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            st.download_button(
                label=f"⬇️ 下載 {fname}（{len(filtered_export)} 筆）",
                data=excel_bytes,
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success(f"✅ 已準備 {len(filtered_export)} 筆資料")
