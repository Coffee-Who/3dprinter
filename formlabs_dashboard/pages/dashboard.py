"""
pages/dashboard.py  —  Formlabs 列印儀表板
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import formlabs_api as api

# ── Plotly shared theme ───────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#9ca3af", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    colorway=["#ff4d00","#ff8c42","#60a5fa","#4ade80","#f472b6","#a78bfa","#fbbf24"],
    legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#e8eaf0"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)"),
)

def apply_layout(fig, title=""):
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font_color="#e8eaf0", font_size=13))
    return fig

# ── Status helpers ────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "PRINTING":  "#4ade80",
    "FINISHED":  "#60a5fa",
    "IDLE":      "#6b7280",
    "ABORTED":   "#ff4d00",
    "ERROR":     "#ff4d00",
    "PAUSED":    "#fbbf24",
    "QUEUED":    "#a78bfa",
}
PILL_CLASS = {
    "PRINTING": "pill-printing",
    "FINISHED": "pill-finished",
    "IDLE":     "pill-idle",
    "ABORTED":  "pill-error",
    "ERROR":    "pill-error",
    "PAUSED":   "pill-paused",
}

def status_pill(s):
    cls = PILL_CLASS.get(s, "pill-idle")
    return f'<span class="status-pill {cls}">{s}</span>'

# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.05rem;
                    color:#e8eaf0;margin-bottom:1.2rem;padding-bottom:.8rem;
                    border-bottom:1px solid rgba(255,255,255,0.07)">
          ⚙️ API 設定
        </div>
        """, unsafe_allow_html=True)

        use_demo = st.toggle("使用 Demo 資料（不需 API Key）", value=True)

        client_id     = ""
        client_secret = ""
        if not use_demo:
            client_id     = st.text_input("Client ID",     type="default",  placeholder="從 Dashboard Developer 頁取得")
            client_secret = st.text_input("Client Secret", type="password", placeholder="••••••••••••••••")
            if st.button("🔐 連線", use_container_width=True):
                with st.spinner("取得 Access Token…"):
                    try:
                        tok = api.get_access_token(client_id, client_secret)
                        st.session_state["api_token"] = tok["access_token"]
                        st.session_state["use_demo"]  = False
                        st.success("✅ 連線成功！")
                    except Exception as e:
                        st.error(f"連線失敗：{e}")
        else:
            st.session_state["use_demo"] = True
            st.info("🟡 Demo 模式：資料為模擬數據")

        st.divider()
        st.markdown('<div style="font-size:.78rem;color:#6b7280;font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem">篩選條件</div>', unsafe_allow_html=True)

        # Date range
        today = datetime.now().date()
        date_from = st.date_input("開始日期", value=today - timedelta(days=30))
        date_to   = st.date_input("結束日期", value=today)

        return {
            "use_demo":    st.session_state.get("use_demo", True),
            "token":       st.session_state.get("api_token", ""),
            "date_from":   date_from,
            "date_to":     date_to,
        }

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_data(use_demo, token, date_from_str, date_to_str):
    if use_demo:
        printers = api.mock_printers()
        prints   = api.mock_prints(days=30)
    else:
        printers = api.list_printers(token)
        prints   = api.list_all_prints(
            token,
            date_gt=date_from_str + "T00:00:00Z",
            date_lt=date_to_str   + "T23:59:59Z",
        )
    return printers, prints


def build_df(prints):
    if not prints:
        return pd.DataFrame()
    df = pd.DataFrame(prints)

    # parse datetimes
    for col in ["print_started_at", "print_finished_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    # duration hours
    if "elapsed_duration_ms" in df.columns:
        df["duration_h"] = df["elapsed_duration_ms"] / 3_600_000
    elif "print_started_at" in df.columns and "print_finished_at" in df.columns:
        df["duration_h"] = (df["print_finished_at"] - df["print_started_at"]).dt.total_seconds() / 3600

    # user display
    if "user" in df.columns:
        df["user_name"] = df["user"].apply(
            lambda u: (u.get("first_name","") + " " + u.get("last_name","")).strip()
            if isinstance(u, dict) else str(u)
        )
    else:
        df["user_name"] = "未知"

    # date column
    if "print_started_at" in df.columns:
        df["date"] = df["print_started_at"].dt.date

    # material fallback
    if "material_name" not in df.columns and "material" in df.columns:
        df["material_name"] = df["material"]

    # success flag
    def success(row):
        prs = row.get("print_run_success") if isinstance(row, dict) else None
        if isinstance(prs, dict):
            return prs.get("print_run_success","UNKNOWN")
        return "UNKNOWN"
    df["success"] = df.apply(lambda r: success(r.to_dict()), axis=1) if "print_run_success" in df.columns else "UNKNOWN"

    return df

# ── KPI row ───────────────────────────────────────────────────────────────────
def kpi_row(printers, df):
    total_printers = len(printers)
    printing_now   = sum(1 for p in printers
                         if p.get("printer_status",{}).get("status","") == "PRINTING")
    total_jobs     = len(df) if not df.empty else 0
    success_jobs   = len(df[df["success"] == "SUCCESS"]) if not df.empty and "success" in df.columns else 0
    total_vol      = df["volume_ml"].sum() if not df.empty and "volume_ml" in df.columns else 0
    total_h        = df["duration_h"].sum() if not df.empty and "duration_h" in df.columns else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("🖨️ 印表機總數",  total_printers)
    c2.metric("🟢 列印中",      printing_now)
    c3.metric("📋 列印任務數",  total_jobs)
    c4.metric("✅ 成功完成",    success_jobs,
              delta=f"{success_jobs/total_jobs*100:.0f}%" if total_jobs else None)
    c5.metric("🧴 材料使用 (ml)", f"{total_vol:,.0f}")
    c6.metric("⏱️ 累計列印時數", f"{total_h:,.1f} h")

# ── Printer status cards ──────────────────────────────────────────────────────
def printer_cards(printers):
    st.markdown("""
    <div class="section-title" style="margin-top:1.5rem">印表機狀態</div>
    <div class="section-sub">即時連線狀態總覽</div>
    """, unsafe_allow_html=True)

    cols = st.columns(min(len(printers), 3))
    for i, p in enumerate(printers):
        ps  = p.get("printer_status", {})
        cpr = ps.get("current_print_run") or {}
        status = ps.get("status", "UNKNOWN")
        color  = STATUS_COLORS.get(status, "#6b7280")
        pill   = status_pill(status)

        # material credit bar
        credit = ps.get("material_credit", 0)
        bar_w  = int(credit * 100)
        bar_color = "#4ade80" if credit > 0.3 else "#fbbf24" if credit > 0.1 else "#ff4d00"

        # current job info
        job_name = cpr.get("name", "—") if cpr else "—"
        mat_name = cpr.get("material_name", cpr.get("material","—")) if cpr else "—"
        cur_layer = cpr.get("currently_printing_layer", 0) if cpr else 0
        tot_layer = cpr.get("layer_count", 1) if cpr else 1
        pct = min(int(cur_layer / max(tot_layer,1) * 100), 100) if cpr else 0
        eta_ms = cpr.get("estimated_time_remaining_ms", 0) if cpr else 0
        eta_h  = eta_ms / 3_600_000
        eta_str = f"{eta_h:.1f} h 剩餘" if eta_h > 0 else "—"
        user_d  = cpr.get("user", {}) if cpr else {}
        operator = (user_d.get("first_name","") + " " + user_d.get("last_name","")).strip() or "—"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="card" style="border-left:3px solid {color};margin-bottom:1rem">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.75rem">
                <div>
                  <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:.95rem;color:#e8eaf0">{p.get('alias', p.get('serial','—'))}</div>
                  <div style="font-size:.72rem;color:#6b7280;margin-top:.15rem">{p.get('serial','')}</div>
                </div>
                {pill}
              </div>
              {"<div style='margin-bottom:.75rem'><div style='font-size:.72rem;color:#6b7280;margin-bottom:.3rem'>任務進度 "+str(pct)+"%</div><div style='background:rgba(255,255,255,0.08);border-radius:4px;height:5px'><div style='width:"+str(pct)+"%%;background:#ff4d00;border-radius:4px;height:5px'></div></div></div>" if cpr else ""}
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:.4rem;font-size:.77rem">
                <div><span style="color:#6b7280">操作員</span><br><span style="color:#e8eaf0">{operator}</span></div>
                <div><span style="color:#6b7280">剩餘時間</span><br><span style="color:#e8eaf0">{eta_str}</span></div>
                <div style="grid-column:span 2"><span style="color:#6b7280">材料</span><br><span style="color:#e8eaf0">{mat_name}</span></div>
              </div>
              <div style="margin-top:.75rem">
                <div style="font-size:.7rem;color:#6b7280;margin-bottom:.25rem">材料餘量 {int(credit*100)}%</div>
                <div style="background:rgba(255,255,255,0.08);border-radius:4px;height:4px">
                  <div style="width:{bar_w}%;background:{bar_color};border-radius:4px;height:4px"></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
def charts_section(df, cfg):
    if df.empty:
        st.info("目前無列印記錄可顯示")
        return

    st.markdown("""
    <div class="section-title" style="margin-top:2rem">統計分析</div>
    <div class="section-sub">切換維度，深入洞察列印行為</div>
    """, unsafe_allow_html=True)

    # ── filter bar
    tab_dim = st.radio(
        "統計維度",
        ["人員", "機器", "材料", "狀態", "日期趨勢"],
        horizontal=True,
        label_visibility="collapsed",
    )

    col_left, col_right = st.columns(2)

    # ── daily trend (always show on right when in trend mode)
    if tab_dim == "日期趨勢":
        daily = df.groupby("date").agg(
            任務數=("guid","count"),
            材料用量_ml=("volume_ml","sum"),
        ).reset_index()
        daily["date"] = pd.to_datetime(daily["date"])

        fig1 = px.bar(daily, x="date", y="任務數",
                      color_discrete_sequence=["#ff4d00"],
                      title="每日列印任務數")
        apply_layout(fig1)
        fig1.update_traces(marker_cornerradius=3)

        fig2 = px.area(daily, x="date", y="材料用量_ml",
                       color_discrete_sequence=["#ff8c42"],
                       title="每日材料用量 (ml)")
        apply_layout(fig2)
        fig2.update_traces(fill="tozeroy", line_width=2)

        col_left.plotly_chart(fig1, use_container_width=True)
        col_right.plotly_chart(fig2, use_container_width=True)
        return

    # ── dimension column picker
    dim_col = {
        "人員": "user_name",
        "機器": "printer",
        "材料": "material_name",
        "狀態": "status",
    }.get(tab_dim, "user_name")

    label = tab_dim

    # bar: job count by dim
    grp = df.groupby(dim_col).agg(
        任務數=("guid","count"),
        材料用量_ml=("volume_ml","sum"),
        平均時長_h=("duration_h","mean"),
    ).reset_index().sort_values("任務數", ascending=False).head(15)

    fig_bar = px.bar(grp, x=dim_col, y="任務數",
                     color=dim_col,
                     title=f"列印任務數 — 依{label}",
                     labels={dim_col: label})
    apply_layout(fig_bar)
    fig_bar.update_traces(marker_cornerradius=4)
    fig_bar.update_layout(showlegend=False)

    # pie: material volume share
    fig_pie = px.pie(grp, names=dim_col, values="材料用量_ml",
                     title=f"材料用量佔比 — 依{label}",
                     hole=0.45)
    apply_layout(fig_pie)
    fig_pie.update_traces(textfont_color="#e8eaf0", pull=[0.03]*len(grp))

    col_left.plotly_chart(fig_bar, use_container_width=True)
    col_right.plotly_chart(fig_pie, use_container_width=True)

    # ── second row: avg duration + success rate
    col3, col4 = st.columns(2)

    fig_dur = px.bar(grp.sort_values("平均時長_h"), x=dim_col, y="平均時長_h",
                     color=dim_col,
                     title=f"平均列印時長 (h) — 依{label}",
                     labels={dim_col: label, "平均時長_h": "時長 (h)"})
    apply_layout(fig_dur)
    fig_dur.update_traces(marker_cornerradius=4)
    fig_dur.update_layout(showlegend=False)

    # success rate by dim
    if "success" in df.columns:
        succ = df.copy()
        succ["成功"] = succ["success"].apply(lambda x: 1 if x=="SUCCESS" else 0)
        sr = succ.groupby(dim_col)["成功"].mean().reset_index()
        sr.columns = [dim_col, "成功率"]
        sr["成功率"] = (sr["成功率"] * 100).round(1)
        fig_sr = px.bar(sr.sort_values("成功率"), x=dim_col, y="成功率",
                        color=dim_col,
                        title=f"列印成功率 (%) — 依{label}",
                        labels={dim_col: label})
        apply_layout(fig_sr)
        fig_sr.update_traces(marker_cornerradius=4)
        fig_sr.update_layout(showlegend=False, yaxis_range=[0,105])
        col4.plotly_chart(fig_sr, use_container_width=True)

    col3.plotly_chart(fig_dur, use_container_width=True)

# ── Print log table ───────────────────────────────────────────────────────────
def print_log_table(df, printers):
    st.markdown("""
    <div class="section-title" style="margin-top:2rem">列印紀錄</div>
    <div class="section-sub">詳細任務清單（最新 200 筆）</div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.info("無資料")
        return

    # filter controls
    f1, f2, f3, f4 = st.columns(4)
    # unique options
    machine_opts = ["全部"] + sorted(df["printer"].dropna().unique().tolist())
    user_opts    = ["全部"] + sorted(df["user_name"].dropna().unique().tolist())
    mat_opts     = ["全部"] + sorted(df["material_name"].dropna().unique().tolist()) if "material_name" in df.columns else ["全部"]
    stat_opts    = ["全部"] + sorted(df["status"].dropna().unique().tolist())

    sel_machine = f1.selectbox("機器", machine_opts, key="tbl_machine")
    sel_user    = f2.selectbox("人員", user_opts,    key="tbl_user")
    sel_mat     = f3.selectbox("材料", mat_opts,     key="tbl_mat")
    sel_stat    = f4.selectbox("狀態", stat_opts,    key="tbl_stat")

    filtered = df.copy()
    if sel_machine != "全部": filtered = filtered[filtered["printer"]       == sel_machine]
    if sel_user    != "全部": filtered = filtered[filtered["user_name"]     == sel_user]
    if sel_mat     != "全部" and "material_name" in filtered.columns:
        filtered = filtered[filtered["material_name"] == sel_mat]
    if sel_stat    != "全部": filtered = filtered[filtered["status"]        == sel_stat]

    show = filtered.sort_values("print_started_at", ascending=False).head(200)

    # build HTML table
    rows_html = ""
    for _, r in show.iterrows():
        pill = status_pill(str(r.get("status","")))
        started = str(r.get("print_started_at",""))[:16].replace("T"," ") if pd.notna(r.get("print_started_at")) else "—"
        dur_h   = r.get("duration_h", 0) or 0
        vol     = r.get("volume_ml",  0) or 0
        mat     = r.get("material_name", r.get("material","—")) or "—"
        rows_html += f"""
        <tr>
          <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="{r.get('name','')}">
            {str(r.get('name','—'))[:30]}
          </td>
          <td>{r.get('printer','—')}</td>
          <td>{r.get('user_name','—')}</td>
          <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{mat[:25]}</td>
          <td>{pill}</td>
          <td>{started}</td>
          <td>{dur_h:.1f} h</td>
          <td>{vol:.0f} ml</td>
        </tr>
        """

    st.markdown(f"""
    <div class="card" style="overflow-x:auto;padding:0">
      <table class="data-table">
        <thead>
          <tr>
            <th>任務名稱</th><th>機器</th><th>操作員</th>
            <th>材料</th><th>狀態</th><th>開始時間</th>
            <th>時長</th><th>用量</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    <div style="font-size:.72rem;color:#6b7280;margin-top:.5rem;text-align:right">
      顯示 {len(show):,} 筆（共 {len(filtered):,} 筆符合篩選）
    </div>
    """, unsafe_allow_html=True)

# ── Main render ───────────────────────────────────────────────────────────────
def render():
    cfg = sidebar()

    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    # heading
    st.markdown("""
    <div class="section-title">📊 列印儀表板</div>
    <div class="section-sub">Formlabs Dashboard API 即時資料</div>
    """, unsafe_allow_html=True)

    # load data
    with st.spinner("載入資料中…"):
        try:
            printers, prints = load_data(
                cfg["use_demo"],
                cfg["token"],
                str(cfg["date_from"]),
                str(cfg["date_to"]),
            )
        except Exception as e:
            st.error(f"❌ 資料載入失敗：{e}")
            st.markdown("</div>", unsafe_allow_html=True)
            return

    df = build_df(prints)

    # filter df by date (for demo mode)
    if not df.empty and "date" in df.columns:
        df = df[
            (df["date"] >= cfg["date_from"]) &
            (df["date"] <= cfg["date_to"])
        ]

    # last updated badge
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:1.25rem">
      <span style="width:7px;height:7px;background:#4ade80;border-radius:50%;display:inline-block"></span>
      <span style="font-size:.75rem;color:#6b7280">
        最後更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        {'　｜　🟡 Demo 模式' if cfg['use_demo'] else '　｜　🟢 Live API'}
      </span>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    kpi_row(printers, df)

    # Printer cards
    printer_cards(printers)

    # Charts
    charts_section(df, cfg)

    # Table
    print_log_table(df, printers)

    st.markdown("</div>", unsafe_allow_html=True)
