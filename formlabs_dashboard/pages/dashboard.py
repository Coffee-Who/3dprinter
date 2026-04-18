"""
pages/dashboard.py  —  Formlabs 列印儀表板（單頁）
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import formlabs_api as api

# ── Plotly theme ───────────────────────────────────────────────────────────────
PLOTLY_CFG = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#9ca3af", size=11),
    margin=dict(l=10, r=10, t=36, b=10),
    colorway=["#ff4d00","#ff8c42","#60a5fa","#4ade80",
               "#f472b6","#a78bfa","#fbbf24","#34d399","#38bdf8"],
    legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#e8eaf0"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)"),
)
def _lay(fig, title=""):
    fig.update_layout(**PLOTLY_CFG,
                      title=dict(text=title, font_color="#e8eaf0", font_size=13))
    return fig

STATUS_COLOR = {
    "PRINTING":"#4ade80","FINISHED":"#60a5fa","IDLE":"#6b7280",
    "ABORTED":"#ff4d00","ERROR":"#ff4d00","PAUSED":"#fbbf24","QUEUED":"#a78bfa",
}
PILL_CLS = {
    "PRINTING":"pill-printing","FINISHED":"pill-finished","IDLE":"pill-idle",
    "ABORTED":"pill-error","ERROR":"pill-error","PAUSED":"pill-paused","QUEUED":"pill-queued",
}
def spill(s):
    return f'<span class="status-pill {PILL_CLS.get(s,"pill-idle")}">{s}</span>'

def _sf(v, d=0.0):
    try:    return float(v or d)
    except: return d

def _si(v, d=0):
    try:    return int(v or d)
    except: return d

# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    for k, v in {
        "use_demo":      True,
        "api_token":     "",
        "client_id":     "",
        "client_secret": "",
        "api_connected": False,
        "date_from":     datetime.now().date() - timedelta(days=30),
        "date_to":       datetime.now().date(),
        "settings_open": False,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def _load(use_demo, token, df_s, dt_s):
    if use_demo:
        # formlabs_api.py 中的 mock 資料已使用真實機器名稱且完全對應
        return api.mock_printers(), api.mock_prints(days=90)
    printers = api.list_printers(token)
    prints   = api.list_all_prints(token,
                   date_gt=df_s+"T00:00:00Z", date_lt=dt_s+"T23:59:59Z")
    return printers, prints


def _build_df(prints):
    if not prints:
        return pd.DataFrame()
    df = pd.DataFrame(prints)

    # 時間欄位
    for c in ["print_started_at","print_finished_at"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)

    # 列印時長
    if "elapsed_duration_ms" in df.columns:
        df["duration_h"] = df["elapsed_duration_ms"].fillna(0) / 3_600_000
    elif "print_started_at" in df.columns and "print_finished_at" in df.columns:
        df["duration_h"] = (
            (df["print_finished_at"] - df["print_started_at"])
            .dt.total_seconds() / 3600
        )
    else:
        df["duration_h"] = 0.0

    # 操作員
    if "user" in df.columns:
        df["user_name"] = df["user"].apply(
            lambda u: (u.get("first_name","")+" "+u.get("last_name","")).strip() or "未知"
            if isinstance(u, dict) else "未知"
        )
    else:
        df["user_name"] = "未知"

    # 日期
    if "print_started_at" in df.columns:
        df["date"] = df["print_started_at"].dt.date

    # ── 材料：優先 material_name，fallback material，最後填「未知」
    if "material_name" in df.columns:
        # 若 material_name 為空，嘗試用 material 欄位補
        if "material" in df.columns:
            df["material_name"] = df["material_name"].where(
                df["material_name"].notna() & (df["material_name"] != ""),
                df["material"]
            )
    elif "material" in df.columns:
        df["material_name"] = df["material"]
    else:
        df["material_name"] = "未知"
    df["material_name"] = df["material_name"].fillna("未知").replace("", "未知")

    # ── 機器：確保 printer 欄位存在
    if "printer" not in df.columns:
        df["printer"] = "未知"
    df["printer"] = df["printer"].fillna("未知").replace("", "未知")

    # 成功狀態
    def _suc(row):
        prs = row.get("print_run_success")
        return prs.get("print_run_success","UNKNOWN") if isinstance(prs,dict) else "UNKNOWN"
    df["success"] = (
        df.apply(lambda r: _suc(r.to_dict()), axis=1)
        if "print_run_success" in df.columns else "UNKNOWN"
    )

    # 欄位保險
    if "guid"      not in df.columns: df["guid"]      = df.index.astype(str)
    if "volume_ml" not in df.columns: df["volume_ml"] = 0.0
    if "status"    not in df.columns: df["status"]    = "UNKNOWN"
    df["volume_ml"]  = pd.to_numeric(df["volume_ml"],  errors="coerce").fillna(0)
    df["duration_h"] = pd.to_numeric(df["duration_h"], errors="coerce").fillna(0)
    return df

# ── NAV ────────────────────────────────────────────────────────────────────────
def _nav():
    mode = "🟡 Demo" if st.session_state.use_demo else "🟢 Live API"
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"""
    <div class="nav-bar">
      <div class="nav-logo">🖨️ FORMLABS<span>HUB</span>
        <span class="nav-badge" style="margin-left:.5rem">{mode}</span>
      </div>
      <div style="font-size:.75rem;color:#ffffff;font-weight:500">
        最後更新　{ts}
      </div>
    </div>""", unsafe_allow_html=True)

# ── SETTINGS ───────────────────────────────────────────────────────────────────
def _settings():
    _, c2 = st.columns([8,1])
    with c2:
        lbl = "✕ 關閉" if st.session_state.settings_open else "⚙️ API 設定"
        if st.button(lbl, use_container_width=True, key="tog_set"):
            st.session_state.settings_open = not st.session_state.settings_open
            st.rerun()
    if not st.session_state.settings_open:
        return

    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ API 連線設定")
    src = st.radio("來源", ["🟡 Demo 模擬資料","🟢 Live API"],
                   index=0 if st.session_state.use_demo else 1,
                   horizontal=True, label_visibility="collapsed")
    st.session_state.use_demo = "Demo" in src

    if not st.session_state.use_demo:
        st.markdown(
            '<div style="font-size:.78rem;color:#9ca3af;margin:.4rem 0 .7rem">'
            '取得憑證：<a href="https://dashboard.formlabs.com/#developer" '
            'target="_blank" style="color:#ff8c42">dashboard.formlabs.com/#developer</a>'
            ' → Create Application</div>', unsafe_allow_html=True)
        a1,a2,a3 = st.columns([3,3,1])
        cid  = a1.text_input("Client ID",     value=st.session_state.client_id,
                              placeholder="貼上 Client ID", key="inp_cid")
        csec = a2.text_input("Client Secret", value=st.session_state.client_secret,
                              placeholder="貼上 Client Secret",
                              type="password", key="inp_csec")
        st.session_state.client_id     = cid
        st.session_state.client_secret = csec
        with a3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("🔐 連線", use_container_width=True, type="primary"):
                with st.spinner("取得 Token…"):
                    try:
                        tok = api.get_access_token(cid, csec)
                        st.session_state.api_token    = tok["access_token"]
                        st.session_state.api_connected = True
                        st.session_state.settings_open = False
                        _load.clear()
                        st.success("✅ 連線成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
        if st.session_state.api_connected:
            st.success("✅ 已連線 — 本次工作階段有效，無需重複輸入")
    else:
        st.info("Demo 模式：模擬資料，不需 API 金鑰。")
    st.markdown("</div>", unsafe_allow_html=True)

# ── DATE BAR ───────────────────────────────────────────────────────────────────
def _date_bar():
    today = datetime.now().date()
    st.markdown(
        '<div style="font-size:.76rem;color:#9ca3af;margin-bottom:.35rem;font-weight:500">'
        '📅　統計日期區間</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,_,c6,c7 = st.columns([1,1,1,1,.1,2,2])
    def qb(col, label, days):
        with col:
            if st.button(label, use_container_width=True, key=f"qb{days}"):
                st.session_state.date_from = today - timedelta(days=days)
                st.session_state.date_to   = today
                _load.clear(); st.rerun()
    qb(c1,"今天",0); qb(c2,"7 天",6); qb(c3,"30 天",29); qb(c4,"90 天",89)
    nf = c6.date_input("開始", value=st.session_state.date_from,
                        label_visibility="collapsed", key="df_in")
    nt = c7.date_input("結束", value=st.session_state.date_to,
                        label_visibility="collapsed", key="dt_in")
    if nf != st.session_state.date_from or nt != st.session_state.date_to:
        st.session_state.date_from = nf
        st.session_state.date_to   = nt
        _load.clear(); st.rerun()

# ── KPI ────────────────────────────────────────────────────────────────────────
def _kpi(printers, df):
    total    = len(printers)
    printing = sum(1 for p in printers
                   if (p.get("printer_status") or {}).get("status","")=="PRINTING")
    jobs  = len(df)
    succ  = int((df["success"]=="SUCCESS").sum()) if not df.empty else 0
    vol   = df["volume_ml"].sum()  if not df.empty else 0.0
    hrs   = df["duration_h"].sum() if not df.empty else 0.0
    rate  = f"{succ/jobs*100:.0f}%" if jobs else "—"
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("🖨️ 印表機",   total)
    c2.metric("🟢 列印中",   printing)
    c3.metric("📋 任務數",   f"{jobs:,}")
    c4.metric("✅ 成功率",   rate)
    c5.metric("🧴 用量",     f"{vol:,.0f} ml")
    c6.metric("⏱️ 列印時數", f"{hrs:,.1f} h")

# ── PRINTER CARDS ──────────────────────────────────────────────────────────────
def _printer_cards(printers):
    st.markdown("""
    <div class="sec-title" style="margin-top:1.5rem">🖨️ 印表機即時狀態</div>
    <div class="sec-sub">所有連線機台監控</div>""", unsafe_allow_html=True)
    if not printers:
        st.info("目前無連線機台"); return

    for row_start in range(0, len(printers), 3):
        batch = printers[row_start:row_start+3]
        cols  = st.columns(len(batch))
        for col, p in zip(cols, batch):
            ps     = p.get("printer_status") or {}
            cpr    = ps.get("current_print_run") or {}
            status = ps.get("status","UNKNOWN")
            color  = STATUS_COLOR.get(status,"#6b7280")
            pill   = spill(status)
            credit = _sf(ps.get("material_credit"), 0.0)
            bw     = min(int(credit*100), 100)
            bc     = "#4ade80" if bw>30 else "#fbbf24" if bw>10 else "#ff4d00"

            # 顯示名稱：alias > serial
            name  = str(p.get("alias") or p.get("serial") or "未知機器")
            sn    = str(p.get("serial") or "")
            mtype = str(p.get("machine_type_id") or "")

            mat  = str(cpr.get("material_name") or cpr.get("material") or "—")[:45] if cpr else "—"
            cur  = _si(cpr.get("currently_printing_layer") if cpr else 0)
            tot  = _si(cpr.get("layer_count") if cpr else 0) or 1
            pct  = min(int(cur/tot*100), 100)
            eta  = _si(cpr.get("estimated_time_remaining_ms") if cpr else 0)
            etas = f"{eta/3_600_000:.1f} h" if eta>0 else "—"
            ud   = (cpr.get("user") or {}) if cpr else {}
            op   = ((ud.get("first_name","")+" "+ud.get("last_name","")).strip()) or "—"
            job  = str(cpr.get("name") or "—")[:45] if cpr else "—"

            prog = (
                f"<div style='margin:.45rem 0 .65rem'>"
                f"<div style='font-size:.67rem;color:#9ca3af;margin-bottom:.2rem'>"
                f"{job} · 進度 {pct}%</div>"
                f"<div style='background:rgba(255,255,255,.1);border-radius:3px;height:4px'>"
                f"<div style='width:{pct}%;background:#ff4d00;border-radius:3px;height:4px'></div>"
                f"</div></div>"
            ) if cpr else (
                "<div style='font-size:.67rem;color:#6b7280;margin:.35rem 0'>無進行中任務</div>"
            )

            with col:
                st.markdown(f"""
                <div class="card" style="border-left:3px solid {color};margin-bottom:.75rem">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                      <div style="font-family:'Syne',sans-serif;font-weight:800;
                                  font-size:.92rem;color:#ffffff">{name}</div>
                      <div style="font-size:.64rem;color:#9ca3af;margin-top:.1rem">
                        {mtype}　{sn}</div>
                    </div>{pill}
                  </div>
                  {prog}
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:.3rem;font-size:.74rem;margin-top:.2rem">
                    <div><span style="color:#9ca3af">操作員</span><br>
                         <b style="color:#ffffff">{op}</b></div>
                    <div><span style="color:#9ca3af">預計完成</span><br>
                         <b style="color:#ffffff">{etas}</b></div>
                    <div style="grid-column:span 2"><span style="color:#9ca3af">材料</span><br>
                         <b style="color:#ffffff">{mat}</b></div>
                  </div>
                  <div style="margin-top:.6rem">
                    <div style="font-size:.64rem;color:#9ca3af;margin-bottom:.15rem">材料餘量 {bw}%</div>
                    <div style="background:rgba(255,255,255,.1);border-radius:3px;height:3px">
                      <div style="width:{bw}%;background:{bc};border-radius:3px;height:3px"></div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

# ── FILTER BAR ─────────────────────────────────────────────────────────────────
def _filter_bar(df):
    if df.empty:
        return df
    st.markdown("""
    <div class="sec-title" style="margin-top:1.5rem">🔍 資料篩選</div>
    <div class="sec-sub">可複選，留空代表全選；同時套用至圖表與列印紀錄</div>
    """, unsafe_allow_html=True)

    f1,f2,f3,f4 = st.columns(4)
    machines  = sorted(df["printer"].dropna().unique().tolist())
    users     = sorted(df["user_name"].dropna().unique().tolist())
    materials = sorted(df["material_name"].dropna().unique().tolist())
    statuses  = sorted(df["status"].dropna().unique().tolist())

    sel_m = f1.multiselect("🖨️ 機器",  machines,  placeholder=f"全部（{len(machines)} 台）", key="flt_m")
    sel_u = f2.multiselect("👤 人員",  users,     placeholder=f"全部（{len(users)} 人）",   key="flt_u")
    sel_a = f3.multiselect("🧴 材料",  materials, placeholder=f"全部（{len(materials)} 種）",key="flt_a")
    sel_s = f4.multiselect("📊 狀態",  statuses,  placeholder=f"全部（{len(statuses)} 種）",key="flt_s")

    flt = df.copy()
    if sel_m: flt = flt[flt["printer"].isin(sel_m)]
    if sel_u: flt = flt[flt["user_name"].isin(sel_u)]
    if sel_a: flt = flt[flt["material_name"].isin(sel_a)]
    if sel_s: flt = flt[flt["status"].isin(sel_s)]
    return flt

# ── CHARTS ─────────────────────────────────────────────────────────────────────
def _charts(df):
    if df.empty:
        st.info("此篩選條件下無列印記錄"); return

    st.markdown("""
    <div class="sec-title" style="margin-top:1.5rem">📈 統計分析</div>
    <div class="sec-sub">選擇維度 → 細部選擇要顯示的項目與圖表類型</div>
    """, unsafe_allow_html=True)

    dim = st.radio("維度",
                   ["📅 日期趨勢","👤 人員","🖨️ 機器","🧴 材料"],
                   horizontal=True, label_visibility="collapsed", key="dim")

    # ─ 日期趨勢
    if "日期" in dim:
        chart_opts = st.multiselect(
            "顯示圖表",
            ["每日任務數","每日材料用量","每日成功/失敗"],
            default=["每日任務數","每日材料用量","每日成功/失敗"],
            key="dt_opts",
        )
        if not df.empty and "date" in df.columns:
            daily = (df.groupby("date")
                       .agg(任務數=("guid","count"), 材料用量_ml=("volume_ml","sum"))
                       .reset_index())
            daily["date"] = pd.to_datetime(daily["date"])
            cL,cR = st.columns(2)
            if "每日任務數" in chart_opts:
                f1 = px.bar(daily,x="date",y="任務數",
                            color_discrete_sequence=["#ff4d00"],title="每日列印任務數")
                _lay(f1); f1.update_traces(marker_cornerradius=3)
                cL.plotly_chart(f1,use_container_width=True)
            if "每日材料用量" in chart_opts:
                f2 = px.area(daily,x="date",y="材料用量_ml",
                             color_discrete_sequence=["#ff8c42"],title="每日材料用量 (ml)")
                _lay(f2); f2.update_traces(fill="tozeroy",line_width=2)
                cR.plotly_chart(f2,use_container_width=True)
            if "每日成功/失敗" in chart_opts and "success" in df.columns:
                ds = (df.groupby(["date","success"])["guid"].count()
                        .reset_index().rename(columns={"guid":"件數"}))
                ds["date"] = pd.to_datetime(ds["date"])
                f3 = px.bar(ds,x="date",y="件數",color="success",barmode="stack",
                            title="每日成功 vs 失敗",
                            color_discrete_map={"SUCCESS":"#4ade80","FAILURE":"#ff4d00","UNKNOWN":"#6b7280"})
                _lay(f3); f3.update_traces(marker_cornerradius=2)
                st.plotly_chart(f3,use_container_width=True)
        return

    # ─ 人員 / 機器 / 材料
    dm  = {"👤 人員":"user_name","🖨️ 機器":"printer","🧴 材料":"material_name"}
    dc  = dm.get(dim,"user_name")
    lbl = dim.split(" ",1)[-1]

    if dc not in df.columns:
        st.warning(f"資料中缺少 {dc} 欄位"); return

    # 細部項目多選
    all_items = sorted(df[dc].dropna().unique().tolist())
    sel_items = st.multiselect(
        f"選擇要顯示的{lbl}（留空 = 全選，共 {len(all_items)} 項）",
        all_items, placeholder="全選", key=f"ci_{dc}",
    )
    pdf = df[df[dc].isin(sel_items)].copy() if sel_items else df.copy()

    if pdf.empty:
        st.info("目前選擇無資料"); return

    # 圖表類型多選
    chart_types = st.multiselect(
        "顯示圖表類型",
        ["任務數","材料用量佔比","平均時長","成功率"],
        default=["任務數","材料用量佔比","平均時長","成功率"],
        key=f"ct_{dc}",
    )

    grp = (pdf.groupby(dc)
              .agg(任務數=("guid","count"),
                   材料用量_ml=("volume_ml","sum"),
                   平均時長_h=("duration_h","mean"))
              .reset_index()
              .sort_values("任務數",ascending=False)
              .head(30))

    cL,cR = st.columns(2)
    if "任務數" in chart_types:
        fb = px.bar(grp,x=dc,y="任務數",color=dc,
                    title=f"列印任務數 — 依{lbl}",labels={dc:lbl})
        _lay(fb); fb.update_traces(marker_cornerradius=4)
        fb.update_layout(showlegend=False)
        cL.plotly_chart(fb,use_container_width=True)

    if "材料用量佔比" in chart_types:
        fp = px.pie(grp,names=dc,values="材料用量_ml",
                    title=f"材料用量佔比 — 依{lbl}",hole=.42)
        _lay(fp); fp.update_traces(textfont_color="#e8eaf0",pull=[.03]*len(grp))
        cR.plotly_chart(fp,use_container_width=True)

    c3,c4 = st.columns(2)
    if "平均時長" in chart_types:
        fd = px.bar(grp.sort_values("平均時長_h"),x=dc,y="平均時長_h",color=dc,
                    title=f"平均列印時長 (h) — 依{lbl}",
                    labels={dc:lbl,"平均時長_h":"時長 (h)"})
        _lay(fd); fd.update_traces(marker_cornerradius=4)
        fd.update_layout(showlegend=False)
        c3.plotly_chart(fd,use_container_width=True)

    if "成功率" in chart_types and "success" in pdf.columns:
        s2 = pdf.copy()
        s2["ok"] = s2["success"].apply(lambda x: 1 if x=="SUCCESS" else 0)
        sr = s2.groupby(dc)["ok"].agg(["mean","count"]).reset_index()
        sr.columns = [dc,"成功率","樣本數"]
        sr["成功率"] = (sr["成功率"]*100).round(1)
        fs = px.bar(sr.sort_values("成功率"),x=dc,y="成功率",color=dc,
                    title=f"成功率 (%) — 依{lbl}",labels={dc:lbl},
                    hover_data={"樣本數":True})
        _lay(fs); fs.update_traces(marker_cornerradius=4)
        fs.update_layout(showlegend=False,yaxis_range=[0,105])
        c4.plotly_chart(fs,use_container_width=True)

# ── TABLE + TOTAL ──────────────────────────────────────────────────────────────
def _table(df):
    st.markdown("""
    <div class="sec-title" style="margin-top:1.5rem">📋 列印紀錄</div>
    <div class="sec-sub">依上方篩選條件顯示（最新 300 筆），底部顯示選擇範圍總計</div>
    """, unsafe_allow_html=True)
    if df.empty:
        st.info("無符合條件的列印記錄"); return

    show = df.sort_values("print_started_at",ascending=False).head(300)
    rows = ""
    for _,r in show.iterrows():
        pill = spill(str(r.get("status","")))
        ts   = (str(r.get("print_started_at",""))[:16].replace("T"," ")
                if pd.notna(r.get("print_started_at")) else "—")
        dh   = _sf(r.get("duration_h"))
        vol  = _sf(r.get("volume_ml"))
        mat  = str(r.get("material_name") or r.get("material") or "—")[:32]
        name = str(r.get("name") or "—")[:38]
        suc  = r.get("success","")
        icon = "✅" if suc=="SUCCESS" else "❌" if suc=="FAILURE" else "—"
        rows += (
            f"<tr>"
            f"<td title='{name}' style='max-width:180px;overflow:hidden;"
            f"text-overflow:ellipsis;white-space:nowrap'>{name}</td>"
            f"<td>{r.get('printer','—')}</td>"
            f"<td>{r.get('user_name','—')}</td>"
            f"<td style='max-width:150px;overflow:hidden;text-overflow:ellipsis;"
            f"white-space:nowrap'>{mat}</td>"
            f"<td>{pill}</td>"
            f"<td style='text-align:center'>{icon}</td>"
            f"<td>{ts}</td>"
            f"<td style='text-align:right'>{dh:.1f} h</td>"
            f"<td style='text-align:right'>{vol:.0f} ml</td>"
            f"</tr>"
        )

    # 總計列
    tj   = len(df)
    succ = int((df["success"]=="SUCCESS").sum()) if "success" in df.columns else 0
    fail = int((df["success"]=="FAILURE").sum()) if "success" in df.columns else 0
    tvol = df["volume_ml"].sum()
    thr  = df["duration_h"].sum()
    rate = f"{succ/tj*100:.1f}%" if tj else "—"

    total_row = f"""
    <tr style="background:rgba(255,77,0,0.1);border-top:2px solid rgba(255,77,0,0.5)">
      <td colspan="2" style="color:#ff8c42;font-family:'Syne',sans-serif;
                              font-weight:800;font-size:.78rem;letter-spacing:.04em">
        📊 篩選後總計
      </td>
      <td></td><td></td>
      <td style="color:#ffffff;font-weight:700">共 {tj:,} 筆</td>
      <td style="text-align:center;color:#ffffff;font-weight:700;line-height:1.5">
        ✅ {succ:,}<br>❌ {fail:,}<br>
        <span style="font-size:.67rem;color:#9ca3af">{rate}</span>
      </td>
      <td></td>
      <td style="text-align:right;color:#ffffff;font-weight:700">{thr:,.1f} h</td>
      <td style="text-align:right;color:#ffffff;font-weight:700">{tvol:,.0f} ml</td>
    </tr>"""

    st.markdown(f"""
    <div class="card" style="overflow-x:auto;padding:0">
      <table class="data-table">
        <thead><tr>
          <th>任務名稱</th><th>機器</th><th>操作員</th>
          <th>材料</th><th>狀態</th><th>結果</th>
          <th>開始時間</th><th>時長</th><th>用量</th>
        </tr></thead>
        <tbody>{rows}{total_row}</tbody>
      </table>
    </div>
    <div style="font-size:.68rem;color:#6b7280;margin-top:.35rem;text-align:right">
      顯示 {len(show):,} 筆　|　符合篩選共 {len(df):,} 筆
    </div>""", unsafe_allow_html=True)

# ── MAIN ───────────────────────────────────────────────────────────────────────
def render():
    _init()
    _nav()
    _settings()
    _date_bar()
    st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)

    with st.spinner("資料載入中…"):
        try:
            printers, prints = _load(
                st.session_state.use_demo, st.session_state.api_token,
                str(st.session_state.date_from), str(st.session_state.date_to),
            )
        except Exception as e:
            st.error(f"❌ 資料載入失敗：{e}"); return

    df = _build_df(prints)
    if not df.empty and "date" in df.columns:
        df = df[(df["date"] >= st.session_state.date_from) &
                (df["date"] <= st.session_state.date_to)]

    st.divider()
    _kpi(printers, df)
    _printer_cards(printers)
    st.divider()
    fdf = _filter_bar(df)
    _charts(fdf)
    st.divider()
    _table(fdf)
    st.markdown("""
    <div style="margin-top:1.5rem;padding-bottom:.75rem;font-size:.68rem;
                color:#374151;text-align:center">
      實威國際股份有限公司 台中分公司　|　Powered by Formlabs Web API v0.8.1
    </div>""", unsafe_allow_html=True)
