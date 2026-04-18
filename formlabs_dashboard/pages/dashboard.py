"""
pages/dashboard.py  —  Formlabs 列印儀表板
API 設定內嵌於頁面頂部，不依賴側邊欄
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import formlabs_api as api

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
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

STATUS_COLORS = {"PRINTING":"#4ade80","FINISHED":"#60a5fa","IDLE":"#6b7280",
                 "ABORTED":"#ff4d00","ERROR":"#ff4d00","PAUSED":"#fbbf24","QUEUED":"#a78bfa"}
PILL_CLASS    = {"PRINTING":"pill-printing","FINISHED":"pill-finished","IDLE":"pill-idle",
                 "ABORTED":"pill-error","ERROR":"pill-error","PAUSED":"pill-paused"}
def status_pill(s):
    return f'<span class="status-pill {PILL_CLASS.get(s,"pill-idle")}">{s}</span>'

def _init():
    defs = {
        "use_demo": True, "api_token": "",
        "date_from": datetime.now().date() - timedelta(days=30),
        "date_to":   datetime.now().date(),
        "settings_open": False,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
def settings_panel():
    mode_txt = "🟡 Demo 模式" if st.session_state.use_demo else "🟢 Live API"

    col_h, col_btn = st.columns([6, 1])
    with col_h:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:.75rem">
          <div class="section-title" style="margin:0">📊 列印儀表板</div>
          <span style="font-size:.72rem;background:rgba(255,255,255,.07);
                padding:.2rem .7rem;border-radius:20px;color:#9ca3af">{mode_txt}</span>
        </div>
        <div class="section-sub" style="margin:.25rem 0 0">Formlabs Dashboard API 即時資料</div>
        """, unsafe_allow_html=True)
    with col_btn:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        btn_label = "✕ 關閉" if st.session_state.settings_open else "⚙️ 設定"
        if st.button(btn_label, use_container_width=True, key="toggle_settings"):
            st.session_state.settings_open = not st.session_state.settings_open
            st.rerun()

    # ── 展開面板 ─────────────────────────────────────────────────────────────
    if st.session_state.settings_open:
        st.markdown("""
        <div style="background:rgba(255,77,0,.06);border:1px solid rgba(255,77,0,.25);
             border-radius:12px;padding:1.25rem 1.5rem;margin-top:.75rem">
        """, unsafe_allow_html=True)

        # 資料來源
        st.markdown("**資料來源**")
        src = st.radio("資料來源", ["🟡 Demo 模擬資料（不需 API Key）", "🟢 Live API（輸入憑證）"],
                       index=0 if st.session_state.use_demo else 1,
                       horizontal=True, label_visibility="collapsed", key="src_radio")
        st.session_state.use_demo = ("Demo" in src)

        if not st.session_state.use_demo:
            st.markdown("<div style='margin-top:.75rem'></div>", unsafe_allow_html=True)
            st.markdown("**Formlabs API 憑證** — 取得方式：登入 `dashboard.formlabs.com/#developer` → Create Application")
            a1, a2, a3 = st.columns([2, 2, 1])
            cid  = a1.text_input("Client ID",     placeholder="貼上 Client ID",     key="cid_inp")
            csec = a2.text_input("Client Secret", placeholder="貼上 Client Secret", type="password", key="csec_inp")
            with a3:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("🔐 連線", use_container_width=True, type="primary"):
                    with st.spinner("取得 Access Token…"):
                        try:
                            tok = api.get_access_token(cid, csec)
                            st.session_state.api_token    = tok["access_token"]
                            st.session_state.settings_open = False
                            st.success("✅ 連線成功！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 連線失敗：{e}")
        else:
            st.info("Demo 模式：使用模擬資料，無需 API Key。切換至 Live API 後輸入憑證即可連接真實機台。")

        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        st.markdown("**統計日期範圍**")
        d1, d2, d3 = st.columns([2, 2, 1])
        st.session_state.date_from = d1.date_input("開始", value=st.session_state.date_from, key="df2")
        st.session_state.date_to   = d2.date_input("結束", value=st.session_state.date_to,   key="dt2")
        with d3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("✅ 套用", use_container_width=True):
                st.session_state.settings_open = False
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── 快捷日期列（設定關閉時顯示） ─────────────────────────────────────────
    else:
        today = datetime.now().date()
        q1,q2,q3,q4,q5 = st.columns(5)
        def qbtn(col, label, days):
            with col:
                if st.button(label, use_container_width=True, key=f"qd{days}"):
                    st.session_state.date_from = today - timedelta(days=days)
                    st.session_state.date_to   = today
                    st.rerun()
        qbtn(q1, "今天",     0)
        qbtn(q2, "近 7 天",  6)
        qbtn(q3, "近 30 天", 29)
        qbtn(q4, "近 90 天", 89)
        q5.markdown(
            f'<div style="font-size:.73rem;color:#6b7280;text-align:right;padding:.35rem 0">'
            f'{st.session_state.date_from} → {st.session_state.date_to}</div>',
            unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,.06);margin:.75rem 0 1rem'>",
                unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_data(use_demo, token, df_str, dt_str):
    if use_demo:
        return api.mock_printers(), api.mock_prints(days=90)
    printers = api.list_printers(token)
    prints   = api.list_all_prints(token,
                   date_gt=df_str+"T00:00:00Z", date_lt=dt_str+"T23:59:59Z")
    return printers, prints

def build_df(prints):
    if not prints:
        return pd.DataFrame()
    df = pd.DataFrame(prints)
    for c in ["print_started_at","print_finished_at"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)
    if "elapsed_duration_ms" in df.columns:
        df["duration_h"] = df["elapsed_duration_ms"] / 3_600_000
    elif "print_started_at" in df.columns and "print_finished_at" in df.columns:
        df["duration_h"] = (df["print_finished_at"]-df["print_started_at"]).dt.total_seconds()/3600
    df["user_name"] = (df["user"].apply(
        lambda u: (u.get("first_name","")+" "+u.get("last_name","")).strip()
        if isinstance(u,dict) else str(u)) if "user" in df.columns else "未知")
    if "print_started_at" in df.columns:
        df["date"] = df["print_started_at"].dt.date
    if "material_name" not in df.columns and "material" in df.columns:
        df["material_name"] = df["material"]
    def suc(row):
        prs = row.get("print_run_success")
        return prs.get("print_run_success","UNKNOWN") if isinstance(prs,dict) else "UNKNOWN"
    df["success"] = df.apply(lambda r: suc(r.to_dict()), axis=1) \
        if "print_run_success" in df.columns else "UNKNOWN"
    return df

# ─────────────────────────────────────────────────────────────────────────────
def kpi_row(printers, df):
    total    = len(printers)
    printing = sum(1 for p in printers if p.get("printer_status",{}).get("status","")=="PRINTING")
    jobs     = len(df) if not df.empty else 0
    succ     = int((df["success"]=="SUCCESS").sum()) if not df.empty and "success" in df.columns else 0
    vol      = df["volume_ml"].sum()  if not df.empty and "volume_ml"  in df.columns else 0
    hrs      = df["duration_h"].sum() if not df.empty and "duration_h" in df.columns else 0
    rate     = f"{succ/jobs*100:.0f}%" if jobs else "—"
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("🖨️ 印表機",  total)
    c2.metric("🟢 列印中",  printing)
    c3.metric("📋 任務數",  jobs)
    c4.metric("✅ 成功率",  rate)
    c5.metric("🧴 用量",    f"{vol:,.0f} ml")
    c6.metric("⏱️ 時數",    f"{hrs:,.1f} h")

def printer_cards(printers):
    st.markdown("""
    <div class="section-title" style="margin-top:1.5rem">印表機即時狀態</div>
    <div class="section-sub">所有連線機台的即時監控</div>
    """, unsafe_allow_html=True)
    cols = st.columns(min(len(printers), 3))
    for i, p in enumerate(printers):
        ps     = p.get("printer_status",{})
        cpr    = ps.get("current_print_run") or {}
        status = ps.get("status","UNKNOWN")
        color  = STATUS_COLORS.get(status,"#6b7280")
        pill   = status_pill(status)
        credit = ps.get("material_credit") or 0
        bw     = int(credit*100)
        bc     = "#4ade80" if credit>.3 else "#fbbf24" if credit>.1 else "#ff4d00"
        mat    = cpr.get("material_name", cpr.get("material","—")) if cpr else "—"
        mat    = mat or "—"
        cur    = cpr.get("currently_printing_layer") or 0 if cpr else 0
        tot    = cpr.get("layer_count") or 1 if cpr else 1
        pct    = min(int(cur/max(tot,1)*100),100)
        eta    = cpr.get("estimated_time_remaining_ms") or 0 if cpr else 0
        eta_s  = f"{eta/3_600_000:.1f} h" if eta>0 else "—"
        ud     = cpr.get("user",{}) if cpr else {}
        op     = (ud.get("first_name","")+" "+ud.get("last_name","")).strip() or "—"
        prog   = (f"<div style='margin:.5rem 0 .75rem'><div style='font-size:.7rem;"
                  f"color:#6b7280;margin-bottom:.25rem'>進度 {pct}%</div>"
                  f"<div style='background:rgba(255,255,255,.08);border-radius:4px;height:5px'>"
                  f"<div style='width:{pct}%;background:#ff4d00;border-radius:4px;height:5px'>"
                  f"</div></div></div>") if cpr else ""
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card" style="border-left:3px solid {color};margin-bottom:1rem">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.5rem">
                <div>
                  <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:.9rem;color:#e8eaf0">
                    {p.get('alias',p.get('serial','—'))}
                  </div>
                  <div style="font-size:.68rem;color:#6b7280">{p.get('serial','')}</div>
                </div>{pill}
              </div>
              {prog}
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:.35rem;font-size:.76rem">
                <div><span style="color:#6b7280">操作員</span><br><b style="color:#e8eaf0">{op}</b></div>
                <div><span style="color:#6b7280">剩餘</span><br><b style="color:#e8eaf0">{eta_s}</b></div>
                <div style="grid-column:span 2"><span style="color:#6b7280">材料</span><br>
                  <b style="color:#e8eaf0">{str(mat)[:35]}</b></div>
              </div>
              <div style="margin-top:.6rem">
                <div style="font-size:.68rem;color:#6b7280;margin-bottom:.2rem">材料餘量 {bw}%</div>
                <div style="background:rgba(255,255,255,.08);border-radius:4px;height:4px">
                  <div style="width:{bw}%;background:{bc};border-radius:4px;height:4px"></div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

def charts_section(df):
    if df.empty:
        st.info("此日期範圍內無列印記錄"); return
    st.markdown("""
    <div class="section-title" style="margin-top:2rem">統計分析</div>
    <div class="section-sub">切換維度深入洞察</div>""", unsafe_allow_html=True)

    dim = st.radio("維度", ["👤 人員","🖨️ 機器","🧴 材料","📊 狀態","📅 日期趨勢"],
                   horizontal=True, label_visibility="collapsed", key="dim_radio")
    cL, cR = st.columns(2)

    if "日期" in dim:
        daily = df.groupby("date").agg(任務數=("guid","count"),材料用量_ml=("volume_ml","sum")).reset_index()
        daily["date"] = pd.to_datetime(daily["date"])
        f1 = px.bar(daily,x="date",y="任務數",color_discrete_sequence=["#ff4d00"],title="每日任務數")
        apply_layout(f1); f1.update_traces(marker_cornerradius=3)
        f2 = px.area(daily,x="date",y="材料用量_ml",color_discrete_sequence=["#ff8c42"],title="每日材料用量(ml)")
        apply_layout(f2); f2.update_traces(fill="tozeroy",line_width=2)
        cL.plotly_chart(f1,use_container_width=True); cR.plotly_chart(f2,use_container_width=True)
        return

    dm = {"👤 人員":"user_name","🖨️ 機器":"printer","🧴 材料":"material_name","📊 狀態":"status"}
    dc = dm.get(dim,"user_name"); lbl = dim.split(" ",1)[-1]
    if dc not in df.columns: st.warning(f"欄位 {dc} 不存在"); return

    grp = (df.groupby(dc).agg(任務數=("guid","count"),材料用量_ml=("volume_ml","sum"),平均時長_h=("duration_h","mean"))
           .reset_index().sort_values("任務數",ascending=False).head(15))

    fb = px.bar(grp,x=dc,y="任務數",color=dc,title=f"任務數—{lbl}",labels={dc:lbl})
    apply_layout(fb); fb.update_traces(marker_cornerradius=4); fb.update_layout(showlegend=False)
    fp = px.pie(grp,names=dc,values="材料用量_ml",title=f"材料佔比—{lbl}",hole=.45)
    apply_layout(fp); fp.update_traces(textfont_color="#e8eaf0",pull=[.03]*len(grp))
    cL.plotly_chart(fb,use_container_width=True); cR.plotly_chart(fp,use_container_width=True)

    c3,c4 = st.columns(2)
    fd = px.bar(grp.sort_values("平均時長_h"),x=dc,y="平均時長_h",color=dc,
                title=f"平均時長(h)—{lbl}",labels={dc:lbl,"平均時長_h":"h"})
    apply_layout(fd); fd.update_traces(marker_cornerradius=4); fd.update_layout(showlegend=False)
    c3.plotly_chart(fd,use_container_width=True)

    if "success" in df.columns:
        s2 = df.copy(); s2["ok"] = s2["success"].apply(lambda x: 1 if x=="SUCCESS" else 0)
        sr = s2.groupby(dc)["ok"].mean().reset_index(); sr.columns=[dc,"成功率"]
        sr["成功率"] = (sr["成功率"]*100).round(1)
        fs = px.bar(sr.sort_values("成功率"),x=dc,y="成功率",color=dc,
                    title=f"成功率(%)—{lbl}",labels={dc:lbl})
        apply_layout(fs); fs.update_traces(marker_cornerradius=4)
        fs.update_layout(showlegend=False,yaxis_range=[0,105])
        c4.plotly_chart(fs,use_container_width=True)

def print_log_table(df):
    st.markdown("""
    <div class="section-title" style="margin-top:2rem">列印紀錄</div>
    <div class="section-sub">詳細任務清單，支援多維度篩選</div>""", unsafe_allow_html=True)
    if df.empty: st.info("無資料"); return

    f1,f2,f3,f4 = st.columns(4)
    mo = ["全部"]+sorted(df["printer"].dropna().unique().tolist())
    uo = ["全部"]+sorted(df["user_name"].dropna().unique().tolist())
    ao = ["全部"]+(sorted(df["material_name"].dropna().unique().tolist()) if "material_name" in df.columns else [])
    so = ["全部"]+sorted(df["status"].dropna().unique().tolist())
    sm = f1.selectbox("🖨️ 機器",mo,key="tm"); su = f2.selectbox("👤 人員",uo,key="tu")
    sa = f3.selectbox("🧴 材料",ao,key="ta"); ss = f4.selectbox("📊 狀態",so,key="ts")

    flt = df.copy()
    if sm!="全部": flt=flt[flt["printer"]==sm]
    if su!="全部": flt=flt[flt["user_name"]==su]
    if sa!="全部" and "material_name" in flt.columns: flt=flt[flt["material_name"]==sa]
    if ss!="全部": flt=flt[flt["status"]==ss]

    show = flt.sort_values("print_started_at",ascending=False).head(200)
    rows = ""
    for _,r in show.iterrows():
        pill  = status_pill(str(r.get("status","")))
        ts    = str(r.get("print_started_at",""))[:16].replace("T"," ") if pd.notna(r.get("print_started_at")) else "—"
        dh    = r.get("duration_h",0) or 0
        vol   = r.get("volume_ml",0) or 0
        mat   = str(r.get("material_name",r.get("material","—")) or "—")[:28]
        name  = str(r.get("name","—"))[:32]
        rows += (f"<tr><td title='{r.get('name','')}' style='max-width:180px;overflow:hidden;"
                 f"text-overflow:ellipsis;white-space:nowrap'>{name}</td>"
                 f"<td>{r.get('printer','—')}</td><td>{r.get('user_name','—')}</td>"
                 f"<td>{mat}</td><td>{pill}</td><td>{ts}</td>"
                 f"<td>{dh:.1f} h</td><td>{vol:.0f} ml</td></tr>")

    st.markdown(f"""
    <div class="card" style="overflow-x:auto;padding:0">
      <table class="data-table"><thead><tr>
        <th>任務名稱</th><th>機器</th><th>操作員</th>
        <th>材料</th><th>狀態</th><th>開始時間</th><th>時長</th><th>用量</th>
      </tr></thead><tbody>{rows}</tbody></table>
    </div>
    <div style="font-size:.72rem;color:#6b7280;margin-top:.5rem;text-align:right">
      顯示 {len(show):,} 筆（共 {len(flt):,} 筆符合）
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
def render():
    _init()
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    settings_panel()

    with st.spinner("載入資料中…"):
        try:
            printers, prints = load_data(
                st.session_state.use_demo, st.session_state.api_token,
                str(st.session_state.date_from), str(st.session_state.date_to))
        except Exception as e:
            st.error(f"❌ 資料載入失敗：{e}")
            st.markdown("</div>", unsafe_allow_html=True); return

    df = build_df(prints)
    if not df.empty and "date" in df.columns:
        df = df[(df["date"] >= st.session_state.date_from) &
                (df["date"] <= st.session_state.date_to)]

    st.markdown(
        f'<div style="font-size:.74rem;color:#6b7280;margin-bottom:.75rem">'
        f'最後更新：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True)

    kpi_row(printers, df)
    printer_cards(printers)
    charts_section(df)
    print_log_table(df)
    st.markdown("</div>", unsafe_allow_html=True)
