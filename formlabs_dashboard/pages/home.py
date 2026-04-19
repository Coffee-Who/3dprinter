import streamlit as st

def render():
    st.markdown("""
    <div class="page-wrap">

      <!-- HERO -->
      <div class="hero">
        <div class="hero-eyebrow">實威國際 × Formlabs Dashboard</div>
        <div class="hero-title">掌握每一次<br><span>列印的脈動</span></div>
        <div class="hero-desc">
          整合 Formlabs Dashboard API，即時監控所有連網印表機的狀態、
          材料用量與列印歷史，讓數據驅動每一個決策。
        </div>
      </div>

      <!-- FEATURE CARDS -->
      <div class="section-title">平台功能</div>
      <div class="section-sub">一站式掌握 Formlabs 機隊運作狀況</div>

      <div class="feat-grid">
        <div class="feat-card">
          <div class="feat-icon">🖨️</div>
          <div class="feat-name">印表機狀態監控</div>
          <div class="feat-desc">即時顯示每台機器的運作狀態、目前任務進度與剩餘時間。</div>
        </div>
        <div class="feat-card">
          <div class="feat-icon">📈</div>
          <div class="feat-name">列印統計分析</div>
          <div class="feat-desc">依人員、機器、材料多維度交叉分析，找出產能瓶頸。</div>
        </div>
        <div class="feat-card">
          <div class="feat-icon">🧴</div>
          <div class="feat-name">材料用量追蹤</div>
          <div class="feat-desc">精確記錄每種樹脂 / 尼龍粉末的消耗量，協助成本控管。</div>
        </div>
        <div class="feat-card">
          <div class="feat-icon">⚙️</div>
          <div class="feat-name">API 金鑰管理</div>
          <div class="feat-desc">安全存儲 Client ID / Secret，支援多帳號切換。</div>
        </div>
        <div class="feat-card">
          <div class="feat-icon">📅</div>
          <div class="feat-name">日期區間篩選</div>
          <div class="feat-desc">自由選擇統計週期，快速產出日報、週報、月報。</div>
        </div>
        <div class="feat-card">
          <div class="feat-icon">🔄</div>
          <div class="feat-name">每日自動更新</div>
          <div class="feat-desc">透過排程自動抓取最新資料，每次開啟皆為最新狀態。</div>
        </div>
      </div>

      <!-- QUICK START -->
      <div style="margin-top:2.5rem">
        <div class="section-title">快速開始</div>
        <div class="section-sub">三步驟完成串接</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem">
          <div class="card">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:var(--accent);opacity:.4;margin-bottom:.5rem">01</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:.4rem">取得 API 憑證</div>
            <div style="font-size:.82rem;color:var(--muted);line-height:1.6">
              登入 <code style="background:var(--surface2);padding:.1rem .35rem;border-radius:4px">dashboard.formlabs.com/#developer</code>
              建立 Application，取得 Client ID 與 Client Secret。
            </div>
          </div>
          <div class="card">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:var(--accent);opacity:.4;margin-bottom:.5rem">02</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:.4rem">輸入憑證</div>
            <div style="font-size:.82rem;color:var(--muted);line-height:1.6">
              前往「列印儀表板」頁面，在側邊欄輸入你的 Client ID 和 Client Secret，系統自動換取 Access Token。
            </div>
          </div>
          <div class="card">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:var(--accent);opacity:.4;margin-bottom:.5rem">03</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:.4rem">開始分析</div>
            <div style="font-size:.82rem;color:var(--muted);line-height:1.6">
              所有機台資料自動載入，選擇篩選條件即可查看各種統計圖表與列印紀錄。
            </div>
          </div>
        </div>
      </div>

      <!-- FOOTER -->
      <div style="margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem">
        <div style="font-size:.78rem;color:var(--muted)">
          🏢 實威國際股份有限公司 — 台中分公司 ｜ 應用工程師工具平台
        </div>
        <div style="font-size:.75rem;color:var(--muted);opacity:.6">
          Powered by Formlabs Web API v0.8.1
        </div>
      </div>

    </div>
    """, unsafe_allow_html=True)

    # CTA button (Streamlit native so it works)
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("📊 前往儀表板", use_container_width=True, type="primary"):
            st.query_params["page"] = "dashboard"
            st.session_state.page = "dashboard"
            st.rerun()
