"""
pages/dashboard.py — Formlabs 列印儀表板
修正：
1. printer_name 完全依賴 normalise_prints，不再重複處理
2. 憑證持久化：Streamlit Secrets（Streamlit Cloud 永久儲存）
3. 顯示格式對齊 Dashboard 截圖（Print Name / Printer Name / Material / User / Status / Date）
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import formlabs_api as api

# ── Plotly theme ───────────────────────────────────────────────────────────────
PCFG = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#8892a4", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    colorway=["#ff4d00","#ff7a35","#60a5fa","#22d3a0","#f472b6","#a78bfa","#fbbf24","#34d399"],
    legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#e0e6f0", font_size=12),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)"),
)
def _lay(fig, title=""):
    fig.update_layout(**PCFG, title=dict(text=title, font_color="#fff",
                                          font_size=14, font_family="Syne"))
    return fig

STATUS_COLOR = {
    "PRINTING":"#22d3a0","FINISHED":"#60a5fa","PRINTED":"#60a5fa",
    "IDLE":"#6b7280","ABORTED":"#ff4d00","ERROR":"#ff4d00",
    "PAUSED":"#fbbf24","QUEUED":"#a78bfa",
}
PILL_MAP = {
    "PRINTING":"pill-printing","FINISHED":"pill-finished","PRINTED":"pill-printed",
    "IDLE":"pill-idle","ABORTED":"pill-aborted","ERROR":"pill-error",
    "PAUSED":"pill-paused","QUEUED":"pill-queued",
}
def spill(s):
    return f'<span class="status-pill {PILL_MAP.get(s.upper(),"pill-idle")}">{s}</span>'

def suc_pill(s):
    cls = {"SUCCESS":"pill-success","FAILURE":"pill-failure"}.get(s,"pill-unknown")
    icon = {"SUCCESS":"✅ Successful","FAILURE":"❌ Failed"}.get(s, s or "—")
    return f'<span class="status-pill {cls}">{icon}</span>'

def _sf(v,d=0.0):
    try: return float(v or d)
    except: return d
def _si(v,d=0):
    try: return int(v or d)
    except: return d

# ── 持久化憑證讀取 ─────────────────────────────────────────────────────────────
def _read_secrets():
    """
    從 Streamlit Secrets 讀取 API 憑證。
    在 Streamlit Cloud → Settings → Secrets 中設定：
        FORMLABS_CLIENT_ID = "your_client_id"
        FORMLABS_CLIENT_SECRET = "your_secret"
    """
    try:
        cid  = st.secrets.get("FORMLABS_CLIENT_ID",  "") or ""
        csec = st.secrets.get("FORMLABS_CLIENT_SECRET","") or ""
        return cid.strip(), csec.strip()
    except Exception:
        return "", ""

# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    sec_cid, sec_csec = _read_secrets()
    defaults = {
        "use_demo":      True,
        "api_token":     "",
        "client_id":     sec_cid,    # 從 Secrets 預填
        "client_secret": sec_csec,
        "api_connected": False,
        "date_from":     datetime.now().date() - timedelta(days=30),
        "date_to":       datetime.now().date(),
        "settings_open": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # 若 Secrets 有憑證且尚未連線 → 自動連線（只做一次）
    if (sec_cid and sec_csec
            and not st.session_state.api_connected
            and st.session_state.api_token == ""):
        try:
            tok = api.get_access_token(sec_cid, sec_csec)
            st.session_state.api_token    = tok["access_token"]
            st.session_state.api_connected = True
            st.session_state.use_demo      = False
        except Exception:
            pass  # 靜默失敗，使用者可手動連線

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def _load_printers(use_demo, token):
    if use_demo: return api.mock_printers()
    return api.list_printers(token)

@st.cache_data(ttl=300, show_spinner=False)
def _load_prints_raw(use_demo, token, df_s, dt_s):
    if use_demo: return api.mock_prints(days=90)
    return api.list_all_prints(token,
               date_gt=df_s+"T00:00:00Z", date_lt=dt_s+"T23:59:59Z")

def _build_df(prints_normed: list) -> pd.DataFrame:
    """
    prints_normed 已經過 normalise_prints，
    包含 printer_name / material_display / user_display / success_status。
    """
    if not prints_normed:
        return pd.DataFrame()
    df = pd.DataFrame(prints_normed)

    for c in ["print_started_at","print_finished_at"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)

    if "elapsed_duration_ms" in df.columns:
        df["duration_h"] = df["elapsed_duration_ms"].fillna(0) / 3_600_000
    elif "print_started_at" in df.columns and "print_finished_at" in df.columns:
        df["duration_h"] = (df["print_finished_at"]-df["print_started_at"]).dt.total_seconds()/3600
    else:
        df["duration_h"] = 0.0

    if "print_started_at" in df.columns:
        df["date"] = df["print_started_at"].dt.date

    # 欄位保險
    for col, default in [("guid",""), ("status","UNKNOWN"),
                          ("volume_ml",0.0), ("duration_h",0.0),
                          ("printer_name","未知"), ("material_display","未知"),
                          ("user_display","Unknown"), ("success_status","UNKNOWN")]:
        if col not in df.columns:
            df[col] = default

    if "guid" not in df.columns or df["guid"].eq("").all():
        df["guid"] = df.index.astype(str)

    df["volume_ml"]  = pd.to_numeric(df["volume_ml"],  errors="coerce").fillna(0)
    df["duration_h"] = pd.to_numeric(df["duration_h"], errors="coerce").fillna(0)
    df["printer_name"]     = df["printer_name"].fillna("未知").replace("","未知")
    df["material_display"] = df["material_display"].fillna("未知").replace("","未知")
    df["user_display"]     = df["user_display"].fillna("Unknown").replace("","Unknown")
    return df

# ── NAV ────────────────────────────────────────────────────────────────────────
def _nav():
    mode = "🟡 Demo" if st.session_state.use_demo else "🟢 Live API"
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"""
    <div class="nav-bar">
      <div class="nav-logo">🖨️ FORMLABS<span>HUB</span>
        <span class="nav-badge">{mode}</span>
      </div>
      <div class="nav-ts">最後更新　{ts}</div>
    </div>""", unsafe_allow_html=True)

# ── SETTINGS ───────────────────────────────────────────────────────────────────
def _settings():
    _, c2 = st.columns([9,1])
    with c2:
        lbl = "✕ 關閉" if st.session_state.settings_open else "⚙️ 設定"
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
        # 永久儲存說明
        st.markdown("""
        <div style="background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.3);
                    border-radius:8px;padding:.75rem 1rem;margin:.5rem 0 .9rem;font-size:.84rem">
          💡 <b style="color:#fbbf24">長期保存憑證（重開網頁不需重新輸入）：</b><br>
          Streamlit Cloud → 你的 App → <b>Settings → Secrets</b>，新增：<br>
          <code style="background:rgba(0,0,0,.3);padding:.15rem .4rem;border-radius:4px">
          FORMLABS_CLIENT_ID = "your_client_id"<br>
          FORMLABS_CLIENT_SECRET = "your_client_secret"</code>
        </div>
        """, unsafe_allow_html=True)

        a1,a2,a3 = st.columns([3,3,1])
        cid  = a1.text_input("Client ID",     value=st.session_state.client_id,
                              placeholder="貼上 Client ID", key="inp_cid")
        csec = a2.text_input("Client Secret", value=st.session_state.client_secret,
                              placeholder="貼上 Client Secret", type="password", key="inp_csec")
        st.session_state.client_id     = cid
        st.session_state.client_secret = csec

        with a3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("🔐 連線", use_container_width=True, type="primary"):
                with st.spinner("連線中…"):
                    try:
                        tok = api.get_access_token(cid, csec)
                        st.session_state.api_token     = tok["access_token"]
                        st.session_state.api_connected  = True
                        st.session_state.settings_open  = False
                        _load_printers.clear(); _load_prints_raw.clear()
                        st.success("✅ 連線成功！"); st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

        if st.session_state.api_connected:
            st.success("✅ 已連線 — 本次 Session 有效")
    else:
        st.info("Demo 模式：不需 API 金鑰。")
    st.markdown("</div>", unsafe_allow_html=True)

# ── DATE BAR ───────────────────────────────────────────────────────────────────
def _date_bar():
    today = datetime.now().date()
    st.markdown('<div style="font-size:.9rem;color:#c8d0e0;margin-bottom:.4rem;'
                'font-weight:600">📅　統計日期區間</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,_,c6,c7 = st.columns([1,1,1,1,.12,2,2])
    def qb(col, label, days):
        with col:
            if st.button(label, use_container_width=True, key=f"qb{days}"):
                st.session_state.date_from = today-timedelta(days=days)
                st.session_state.date_to   = today
                _load_prints_raw.clear(); st.rerun()
    qb(c1,"今天",0); qb(c2,"7 天",6); qb(c3,"30 天",29); qb(c4,"90 天",89)
    nf = c6.date_input("開始", value=st.session_state.date_from,
                        label_visibility="collapsed", key="df_in")
    nt = c7.date_input("結束", value=st.session_state.date_to,
                        label_visibility="collapsed", key="dt_in")
    if nf!=st.session_state.date_from or nt!=st.session_state.date_to:
        st.session_state.date_from=nf; st.session_state.date_to=nt
        _load_prints_raw.clear(); st.rerun()

# ── KPI ────────────────────────────────────────────────────────────────────────
def _kpi(printers, df):
    total    = len(printers)
    printing = sum(1 for p in printers
                   if (p.get("printer_status") or {}).get("status","")=="PRINTING")
    jobs  = len(df)
    succ  = int((df["success_status"]=="SUCCESS").sum()) if not df.empty else 0
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
    <div class="sec-sub">所有連線機台</div>""", unsafe_allow_html=True)
    if not printers: st.info("目前無連線機台"); return

    for row_s in range(0, len(printers), 3):
        batch = printers[row_s:row_s+3]
        cols  = st.columns(len(batch))
        for col, p in zip(cols, batch):
            ps    = p.get("printer_status") or {}
            cpr   = ps.get("current_print_run") or {}
            status= ps.get("status","UNKNOWN")
            color = STATUS_COLOR.get(status,"#6b7280")
            pill  = spill(status)
            credit= _sf(ps.get("material_credit"),0.0)
            bw    = min(int(credit*100),100)
            bc    = "#22d3a0" if bw>30 else "#fbbf24" if bw>10 else "#ff4d00"
            name  = str(p.get("alias") or p.get("serial") or "未知")
            sn    = str(p.get("serial") or "")
            mtype = str(p.get("machine_type_id") or "")
            mat   = str(cpr.get("material_name") or cpr.get("material") or "—")[:45] if cpr else "—"
            cur   = _si(cpr.get("currently_printing_layer") if cpr else 0)
            tot   = _si(cpr.get("layer_count") if cpr else 0) or 1
            pct   = min(int(cur/tot*100),100)
            eta   = _si(cpr.get("estimated_time_remaining_ms") if cpr else 0)
            etas  = f"{eta/3_600_000:.1f} h" if eta>0 else "—"
            ud    = (cpr.get("user") or {}) if cpr else {}
            fn    = (ud.get("first_name","")+" "+ud.get("last_name","")).strip() if isinstance(ud,dict) else ""
            op    = fn or "—"
            job   = str(cpr.get("name") or "—")[:45] if cpr else "—"
            prog  = (f"<div style='margin:.45rem 0 .65rem'>"
                     f"<div style='font-size:.76rem;color:#8892a4;margin-bottom:.25rem'>"
                     f"{job} · {pct}%</div>"
                     f"<div style='background:rgba(255,255,255,.1);border-radius:3px;height:5px'>"
                     f"<div style='width:{pct}%;background:#ff4d00;border-radius:3px;height:5px'>"
                     f"</div></div></div>") if cpr else (
                     "<div style='font-size:.76rem;color:#6b7280;margin:.4rem 0'>無進行中任務</div>")
            with col:
                st.markdown(f"""
                <div class="card" style="border-left:3px solid {color};margin-bottom:.75rem">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.05rem;color:#fff">{name}</div>
                      <div style="font-size:.72rem;color:#8892a4;margin-top:.1rem">{mtype}　{sn}</div>
                    </div>{pill}
                  </div>
                  {prog}
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:.35rem;font-size:.84rem;margin-top:.25rem">
                    <div><span style="color:#8892a4">操作員</span><br><b style="color:#fff">{op}</b></div>
                    <div><span style="color:#8892a4">預計完成</span><br><b style="color:#fff">{etas}</b></div>
                    <div style="grid-column:span 2"><span style="color:#8892a4">材料</span><br>
                    <b style="color:#fff">{mat}</b></div>
                  </div>
                  <div style="margin-top:.65rem">
                    <div style="font-size:.72rem;color:#8892a4;margin-bottom:.2rem">材料餘量 {bw}%</div>
                    <div style="background:rgba(255,255,255,.1);border-radius:3px;height:4px">
                      <div style="width:{bw}%;background:{bc};border-radius:3px;height:4px"></div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

# ── FILTER BAR ─────────────────────────────────────────────────────────────────
def _filter_bar(df):
    if df.empty: return df
    st.markdown("""
    <div class="sec-title" style="margin-top:1.5rem">🔍 資料篩選</div>
    <div class="sec-sub">可複選，留空代表全選；同時套用至圖表與列印紀錄</div>
    """, unsafe_allow_html=True)
    f1,f2,f3,f4 = st.columns(4)
    machines  = sorted(df["printer_name"].dropna().unique().tolist())
    users     = sorted(df["user_display"].dropna().unique().tolist())
    materials = sorted(df["material_display"].dropna().unique().tolist())
    statuses  = sorted(df["status"].dropna().unique().tolist())

    sel_m = f1.multiselect("🖨️ Printer Name", machines,
                            placeholder=f"全部 {len(machines)} 台", key="flt_m")
    sel_u = f2.multiselect("👤 User",          users,
                            placeholder=f"全部 {len(users)} 人",   key="flt_u")
    sel_a = f3.multiselect("🧴 Material",      materials,
                            placeholder=f"全部 {len(materials)} 種",key="flt_a")
    sel_s = f4.multiselect("📊 Status",        statuses,
                            placeholder=f"全部 {len(statuses)} 種",key="flt_s")

    flt = df.copy()
    if sel_m: flt=flt[flt["printer_name"].isin(sel_m)]
    if sel_u: flt=flt[flt["user_display"].isin(sel_u)]
    if sel_a: flt=flt[flt["material_display"].isin(sel_a)]
    if sel_s: flt=flt[flt["status"].isin(sel_s)]
    return flt

# ── CHARTS ─────────────────────────────────────────────────────────────────────
def _charts(df):
    if df.empty: st.info("此篩選條件下無列印記錄"); return
    st.markdown("""
    <div class="sec-title" style="margin-top:1.5rem">📈 統計分析</div>
    <div class="sec-sub">選擇維度 → 下方細部選擇項目與圖表類型</div>
    """, unsafe_allow_html=True)

    dim = st.radio("維度",["📅 日期趨勢","👤 User","🖨️ Printer","🧴 Material"],
                   horizontal=True, label_visibility="collapsed", key="dim")

    if "日期" in dim:
        chart_opts = st.multiselect("顯示圖表",
            ["每日任務數","每日材料用量","每日成功/失敗"],
            default=["每日任務數","每日材料用量","每日成功/失敗"], key="dt_opts")
        if "date" in df.columns:
            daily=(df.groupby("date").agg(任務數=("guid","count"),
                   材料用量_ml=("volume_ml","sum")).reset_index())
            daily["date"]=pd.to_datetime(daily["date"])
            cL,cR=st.columns(2)
            if "每日任務數" in chart_opts:
                f1=px.bar(daily,x="date",y="任務數",
                           color_discrete_sequence=["#ff4d00"],title="每日列印任務數")
                _lay(f1); f1.update_traces(marker_cornerradius=3)
                cL.plotly_chart(f1,use_container_width=True)
            if "每日材料用量" in chart_opts:
                f2=px.area(daily,x="date",y="材料用量_ml",
                            color_discrete_sequence=["#ff7a35"],title="每日材料用量 (ml)")
                _lay(f2); f2.update_traces(fill="tozeroy",line_width=2)
                cR.plotly_chart(f2,use_container_width=True)
            if "每日成功/失敗" in chart_opts:
                ds=(df.groupby(["date","success_status"])["guid"].count()
                      .reset_index().rename(columns={"guid":"件數"}))
                ds["date"]=pd.to_datetime(ds["date"])
                f3=px.bar(ds,x="date",y="件數",color="success_status",barmode="stack",
                           title="每日成功 vs 失敗",
                           color_discrete_map={"SUCCESS":"#22d3a0","FAILURE":"#ff4d00","UNKNOWN":"#6b7280"})
                _lay(f3); f3.update_traces(marker_cornerradius=2)
                st.plotly_chart(f3,use_container_width=True)
        return

    dm  = {"👤 User":"user_display","🖨️ Printer":"printer_name","🧴 Material":"material_display"}
    dc  = dm.get(dim,"user_display")
    lbl = dim.split(" ",1)[-1]
    if dc not in df.columns: st.warning(f"缺少 {dc} 欄位"); return

    all_items = sorted(df[dc].dropna().unique().tolist())
    sel_items = st.multiselect(f"選擇 {lbl}（留空 = 全選，共 {len(all_items)} 項）",
                                all_items, placeholder="全選", key=f"ci_{dc}")
    pdf = df[df[dc].isin(sel_items)].copy() if sel_items else df.copy()
    if pdf.empty: st.info("目前選擇無資料"); return

    chart_types=st.multiselect("圖表類型",["任務數","材料用量佔比","平均時長","成功率"],
                                default=["任務數","材料用量佔比","平均時長","成功率"],
                                key=f"ct_{dc}")
    grp=(pdf.groupby(dc).agg(任務數=("guid","count"),材料用量_ml=("volume_ml","sum"),
          平均時長_h=("duration_h","mean")).reset_index().sort_values("任務數",ascending=False).head(30))

    cL,cR=st.columns(2)
    if "任務數" in chart_types:
        fb=px.bar(grp,x=dc,y="任務數",color=dc,title=f"列印任務數 — {lbl}",labels={dc:lbl})
        _lay(fb); fb.update_traces(marker_cornerradius=4); fb.update_layout(showlegend=False)
        cL.plotly_chart(fb,use_container_width=True)
    if "材料用量佔比" in chart_types:
        fp=px.pie(grp,names=dc,values="材料用量_ml",title=f"材料用量佔比 — {lbl}",hole=.42)
        _lay(fp); fp.update_traces(textfont_color="#fff",pull=[.03]*len(grp))
        cR.plotly_chart(fp,use_container_width=True)
    c3,c4=st.columns(2)
    if "平均時長" in chart_types:
        fd=px.bar(grp.sort_values("平均時長_h"),x=dc,y="平均時長_h",color=dc,
                   title=f"平均時長 (h) — {lbl}",labels={dc:lbl,"平均時長_h":"h"})
        _lay(fd); fd.update_traces(marker_cornerradius=4); fd.update_layout(showlegend=False)
        c3.plotly_chart(fd,use_container_width=True)
    if "成功率" in chart_types:
        s2=pdf.copy(); s2["ok"]=s2["success_status"].apply(lambda x:1 if x=="SUCCESS" else 0)
        sr=s2.groupby(dc)["ok"].agg(["mean","count"]).reset_index()
        sr.columns=[dc,"成功率","樣本數"]; sr["成功率"]=(sr["成功率"]*100).round(1)
        fs=px.bar(sr.sort_values("成功率"),x=dc,y="成功率",color=dc,
                   title=f"成功率 (%) — {lbl}",labels={dc:lbl},hover_data={"樣本數":True})
        _lay(fs); fs.update_traces(marker_cornerradius=4)
        fs.update_layout(showlegend=False,yaxis_range=[0,105])
        c4.plotly_chart(fs,use_container_width=True)

# ── TABLE ──────────────────────────────────────────────────────────────────────
ALL_COLS = {
    "Print Name":    "name",
    "Printer Name":  "printer_name",
    "Material":      "material_display",
    "User":          "user_display",
    "Print Status":  "status",
    "Outcome":       "success_status",
    "Date / Time":   "print_started_at",
    "Duration":      "duration_h",
    "Volume (ml)":   "volume_ml",
}
SORT_OPTS = {
    "Date / Time（最新）": ("print_started_at",False),
    "Date / Time（最舊）": ("print_started_at",True),
    "Duration（長→短）":   ("duration_h",False),
    "Duration（短→長）":   ("duration_h",True),
    "Volume（多→少）":     ("volume_ml",False),
    "Volume（少→多）":     ("volume_ml",True),
}

def _table(df):
    st.markdown("""
    <div class="sec-title" style="margin-top:1.5rem">📋 列印紀錄</div>
    <div class="sec-sub">自由選擇欄位與排序，底部顯示篩選後總計</div>
    """, unsafe_allow_html=True)
    if df.empty: st.info("無符合條件的列印記錄"); return

    tc1,tc2 = st.columns([3,1])
    sel_cols = tc1.multiselect("顯示欄位",list(ALL_COLS.keys()),
                                default=list(ALL_COLS.keys()), key="tbl_cols")
    sort_key = tc2.selectbox("排序",list(SORT_OPTS.keys()), key="tbl_sort")
    if not sel_cols: st.warning("請至少選擇一個欄位"); return

    sort_col,sort_asc = SORT_OPTS[sort_key]
    show = df.copy()
    if sort_col in show.columns:
        show = show.sort_values(sort_col, ascending=sort_asc)
    show = show.head(300)

    thead = "<tr>"+"".join(f"<th>{c}</th>" for c in sel_cols)+"</tr>"

    rows=""
    for _,r in show.iterrows():
        cells=""
        for cl in sel_cols:
            ck=ALL_COLS[cl]
            if cl=="Print Status":
                cells+=f"<td>{spill(str(r.get('status','')))}</td>"
            elif cl=="Outcome":
                cells+=f"<td>{suc_pill(str(r.get('success_status','')))}</td>"
            elif cl=="Date / Time":
                ts=(str(r.get("print_started_at",""))[:16].replace("T"," ")
                    if pd.notna(r.get("print_started_at")) else "—")
                cells+=f"<td>{ts}</td>"
            elif cl=="Duration":
                cells+=f"<td style='text-align:right'>{_sf(r.get('duration_h')):.1f} h</td>"
            elif cl=="Volume (ml)":
                cells+=f"<td style='text-align:right'>{_sf(r.get('volume_ml')):.0f}</td>"
            elif cl=="Print Name":
                nm=str(r.get("name") or "—")[:45]
                cells+=(f"<td style='max-width:200px;overflow:hidden;text-overflow:ellipsis;"
                         f"white-space:nowrap' title='{nm}'>{nm}</td>")
            elif cl=="Material":
                mat=str(r.get("material_display") or "—")[:40]
                cells+=(f"<td style='max-width:170px;overflow:hidden;text-overflow:ellipsis;"
                         f"white-space:nowrap'>{mat}</td>")
            else:
                cells+=f"<td>{str(r.get(ck) or '—')}</td>"
        rows+=f"<tr>{cells}</tr>"

    # 總計列
    tj   = len(df)
    succ = int((df["success_status"]=="SUCCESS").sum())
    fail = int((df["success_status"]=="FAILURE").sum())
    tvol = df["volume_ml"].sum()
    thr  = df["duration_h"].sum()
    rate = f"{succ/tj*100:.1f}%" if tj else "—"
    total_cells=""
    for i,cl in enumerate(sel_cols):
        if i==0:
            total_cells+=f"<td style='color:#ff7a35;font-family:Syne,sans-serif;font-weight:800'>📊 Total</td>"
        elif cl=="Print Status":
            total_cells+=f"<td style='color:#fff'>{tj:,} 筆</td>"
        elif cl=="Outcome":
            total_cells+=(f"<td style='text-align:center;color:#fff'>"
                           f"✅{succ:,} / ❌{fail:,}<br>"
                           f"<span style='font-size:.72rem;color:#8892a4'>{rate}</span></td>")
        elif cl=="Duration":
            total_cells+=f"<td style='text-align:right;color:#fff;font-weight:800'>{thr:,.1f} h</td>"
        elif cl=="Volume (ml)":
            total_cells+=f"<td style='text-align:right;color:#fff;font-weight:800'>{tvol:,.0f}</td>"
        else:
            total_cells+="<td></td>"

    st.markdown(f"""
    <div class="card" style="overflow-x:auto;padding:0">
      <table class="data-table">
        <thead>{thead}</thead>
        <tbody>{rows}<tr class="total-row">{total_cells}</tr></tbody>
      </table>
    </div>
    <div style="font-size:.78rem;color:#8892a4;margin-top:.4rem;text-align:right">
      顯示 {len(show):,} 筆　|　符合篩選共 {len(df):,} 筆
    </div>""", unsafe_allow_html=True)

# ── MAIN ───────────────────────────────────────────────────────────────────────
def render():
    _init()
    _nav()
    _settings()
    _date_bar()

    # 載入印表機
    with st.spinner("載入印表機…"):
        try:
            printers = _load_printers(st.session_state.use_demo, st.session_state.api_token)
        except Exception as e:
            st.error(f"❌ 印表機載入失敗：{e}"); return

    printer_map = api.build_printer_map(printers)

    # 載入列印紀錄（raw）
    with st.spinner("載入列印紀錄…"):
        try:
            prints_raw = _load_prints_raw(
                st.session_state.use_demo, st.session_state.api_token,
                str(st.session_state.date_from), str(st.session_state.date_to))
        except Exception as e:
            st.error(f"❌ 列印紀錄載入失敗：{e}"); return

    # ── Debug expander（Live 模式）
    if not st.session_state.use_demo:
        with st.expander("🔍 API 原始資料（排查用）", expanded=False):
            st.markdown("**印表機清單**")
            pd_dbg = [{"serial":p.get("serial",""),"alias":p.get("alias",""),
                        "type":p.get("machine_type_id",""),
                        "status":(p.get("printer_status") or {}).get("status","")}
                       for p in printers]
            st.dataframe(pd.DataFrame(pd_dbg), use_container_width=True)
            st.markdown(f"**printer_map**（共 {len(printer_map)} 個 key）")
            st.json(printer_map)
            if prints_raw:
                pvals = sorted({pr.get("printer","") for pr in prints_raw})
                st.markdown(f"**prints[].printer 欄位值**（共 {len(pvals)} 種）：`{pvals}`")
                mvals = sorted({(pr.get("material_name") or pr.get("material","")) for pr in prints_raw})
                st.markdown(f"**材料欄位**（共 {len(mvals)} 種）：`{mvals}`")
            else:
                st.warning("此日期範圍無列印紀錄")

    # normalise（只做一次）
    prints_normed = api.normalise_prints(prints_raw, printer_map)
    df = _build_df(prints_normed)

    # 日期篩選
    if not df.empty and "date" in df.columns:
        df = df[(df["date"]>=st.session_state.date_from) &
                (df["date"]<=st.session_state.date_to)]

    st.divider()
    _kpi(printers, df)
    _printer_cards(printers)
    st.divider()
    fdf = _filter_bar(df)
    _charts(fdf)
    st.divider()
    _table(fdf)
    st.markdown("""<div style="margin-top:1.5rem;padding-bottom:.75rem;
      font-size:.72rem;color:#374151;text-align:center">
      實威國際股份有限公司 台中分公司　|　Powered by Formlabs Web API v0.8.1
    </div>""", unsafe_allow_html=True)
