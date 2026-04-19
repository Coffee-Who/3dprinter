"""
pages/dashboard.py  —  Formlabs 列印儀表板
修正：
1. Live API: printer serial → alias 對照，所有機器都出現
2. 憑證持久化：優先讀 st.secrets，session_state 備份
3. 材料選項來自 material_display 欄位（material_name / material fallback）
4. 機器選項來自 printer_name（alias）
5. 文字加大、對比色提升
6. 列印紀錄：欄位顯示選擇 + 排序切換
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
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)",
               tickfont=dict(size=11, color="#8892a4")),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)",
               tickfont=dict(size=11, color="#8892a4")),
)
def _lay(fig, title=""):
    fig.update_layout(**PCFG, title=dict(text=title, font_color="#ffffff",
                                          font_size=14, font_family="Syne"))
    return fig

STATUS_COLOR = {
    "PRINTING":"#22d3a0","FINISHED":"#60a5fa","IDLE":"#6b7280",
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
    # 嘗試從 st.secrets 預載憑證（Streamlit Cloud Secrets 設定後永久有效）
    try:
        default_cid  = st.secrets.get("FORMLABS_CLIENT_ID",  "")
        default_csec = st.secrets.get("FORMLABS_CLIENT_SECRET", "")
    except Exception:
        default_cid  = ""
        default_csec = ""

    for k, v in {
        "use_demo":        True,
        "api_token":       "",
        "client_id":       default_cid,
        "client_secret":   default_csec,
        "api_connected":   False,
        "date_from":       datetime.now().date() - timedelta(days=30),
        "date_to":         datetime.now().date(),
        "settings_open":   False,
        "printer_map":     {},   # {serial: alias} — 建立一次後快取
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # 若 secrets 有憑證 且 尚未連線 → 自動嘗試連線
    if (default_cid and default_csec
            and not st.session_state.api_connected
            and not st.session_state.use_demo):
        try:
            tok = api.get_access_token(default_cid, default_csec)
            st.session_state.api_token    = tok["access_token"]
            st.session_state.api_connected = True
        except Exception:
            pass

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def _load_printers(use_demo, token):
    if use_demo:
        return api.mock_printers()
    return api.list_printers(token)


@st.cache_data(ttl=300, show_spinner=False)
def _load_prints(use_demo, token, df_s, dt_s):
    if use_demo:
        return api.mock_prints(days=90)
    return api.list_all_prints(token,
               date_gt=df_s+"T00:00:00Z", date_lt=dt_s+"T23:59:59Z")


def _build_df(prints, printer_map):
    if not prints:
        return pd.DataFrame()

    # 先 normalise（serial → printer_name, material_display）
    normed = api.normalise_prints(prints, printer_map)
    df = pd.DataFrame(normed)

    # 時間
    for c in ["print_started_at","print_finished_at"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)

    # 時長
    if "elapsed_duration_ms" in df.columns:
        df["duration_h"] = df["elapsed_duration_ms"].fillna(0) / 3_600_000
    elif "print_started_at" in df.columns and "print_finished_at" in df.columns:
        df["duration_h"] = (
            (df["print_finished_at"]-df["print_started_at"]).dt.total_seconds()/3600
        )
    else:
        df["duration_h"] = 0.0

    # 操作員
    if "user" in df.columns:
        df["user_name"] = df["user"].apply(
            lambda u: (u.get("first_name","")+" "+u.get("last_name","")).strip() or "未知"
            if isinstance(u,dict) else "未知"
        )
    else:
        df["user_name"] = "未知"

    # 日期
    if "print_started_at" in df.columns:
        df["date"] = df["print_started_at"].dt.date

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
    if "status"    not in df.columns: df["status"]    = "UNKNOWN"
    if "volume_ml" not in df.columns: df["volume_ml"] = 0.0
    df["volume_ml"]  = pd.to_numeric(df["volume_ml"],  errors="coerce").fillna(0)
    df["duration_h"] = pd.to_numeric(df["duration_h"], errors="coerce").fillna(0)

    # 確保 printer_name / material_display 存在
    if "printer_name"     not in df.columns: df["printer_name"]     = df.get("printer","未知")
    if "material_display" not in df.columns: df["material_display"] = "未知"
    df["printer_name"]     = df["printer_name"].fillna("未知").replace("","未知")
    df["material_display"] = df["material_display"].fillna("未知").replace("","未知")

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
    _, c2 = st.columns([9, 1])
    with c2:
        lbl = "✕ 關閉" if st.session_state.settings_open else "⚙️ 設定"
        if st.button(lbl, use_container_width=True, key="tog_set"):
            st.session_state.settings_open = not st.session_state.settings_open
            st.rerun()
    if not st.session_state.settings_open:
        return

    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ API 連線設定")

    src = st.radio("資料來源",
                   ["🟡 Demo 模擬資料", "🟢 Live API（Formlabs Dashboard）"],
                   index=0 if st.session_state.use_demo else 1,
                   horizontal=True, label_visibility="collapsed")
    st.session_state.use_demo = "Demo" in src

    if not st.session_state.use_demo:
        st.markdown(
            '<div style="font-size:.85rem;color:#8892a4;margin:.5rem 0 .8rem">'
            '取得憑證：<a href="https://dashboard.formlabs.com/#developer" '
            'target="_blank" style="color:#ff7a35;font-weight:600">'
            'dashboard.formlabs.com/#developer</a> → Create Application<br>'
            '<b style="color:#fbbf24">💡 長期保存：在 Streamlit Cloud → Settings → Secrets 填入憑證，之後開啟自動連線。</b>'
            '</div>', unsafe_allow_html=True)

        a1, a2, a3 = st.columns([3, 3, 1])
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
                        # 清快取，重新抓資料
                        _load_printers.clear()
                        _load_prints.clear()
                        st.success("✅ 連線成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

        if st.session_state.api_connected:
            st.success("✅ 已連線 — 本次工作階段有效")
    else:
        st.info("Demo 模式：模擬資料，無需 API 金鑰。")

    st.markdown("</div>", unsafe_allow_html=True)

# ── DATE BAR ───────────────────────────────────────────────────────────────────
def _date_bar():
    today = datetime.now().date()
    st.markdown(
        '<div style="font-size:.88rem;color:#c8d0e0;margin-bottom:.4rem;font-weight:600">'
        '📅　統計日期區間</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,_,c6,c7 = st.columns([1,1,1,1,.12,2,2])
    def qb(col, label, days):
        with col:
            if st.button(label, use_container_width=True, key=f"qb{days}"):
                st.session_state.date_from = today - timedelta(days=days)
                st.session_state.date_to   = today
                _load_prints.clear(); st.rerun()
    qb(c1,"今天",0); qb(c2,"7 天",6); qb(c3,"30 天",29); qb(c4,"90 天",89)
    nf = c6.date_input("開始日期", value=st.session_state.date_from,
                        label_visibility="collapsed", key="df_in")
    nt = c7.date_input("結束日期", value=st.session_state.date_to,
                        label_visibility="collapsed", key="dt_in")
    if nf != st.session_state.date_from or nt != st.session_state.date_to:
        st.session_state.date_from = nf
        st.session_state.date_to   = nt
        _load_prints.clear(); st.rerun()

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
    <div class="sec-sub">所有連線機台</div>""", unsafe_allow_html=True)
    if not printers:
        st.info("目前無連線機台"); return

    for row_s in range(0, len(printers), 3):
        batch = printers[row_s:row_s+3]
        cols  = st.columns(len(batch))
        for col, p in zip(cols, batch):
            ps     = p.get("printer_status") or {}
            cpr    = ps.get("current_print_run") or {}
            status = ps.get("status","UNKNOWN")
            color  = STATUS_COLOR.get(status,"#6b7280")
            pill   = spill(status)
            credit = _sf(ps.get("material_credit"),0.0)
            bw     = min(int(credit*100),100)
            bc     = "#22d3a0" if bw>30 else "#fbbf24" if bw>10 else "#ff4d00"
            name   = str(p.get("alias") or p.get("serial") or "未知")
            sn     = str(p.get("serial") or "")
            mtype  = str(p.get("machine_type_id") or "")
            mat    = str(cpr.get("material_name") or cpr.get("material") or "—")[:45] if cpr else "—"
            cur    = _si(cpr.get("currently_printing_layer") if cpr else 0)
            tot    = _si(cpr.get("layer_count") if cpr else 0) or 1
            pct    = min(int(cur/tot*100),100)
            eta    = _si(cpr.get("estimated_time_remaining_ms") if cpr else 0)
            etas   = f"{eta/3_600_000:.1f} h" if eta>0 else "—"
            ud     = (cpr.get("user") or {}) if cpr else {}
            op     = ((ud.get("first_name","")+" "+ud.get("last_name","")).strip()) or "—"
            job    = str(cpr.get("name") or "—")[:45] if cpr else "—"
            prog   = (
                f"<div style='margin:.45rem 0 .65rem'>"
                f"<div style='font-size:.75rem;color:#8892a4;margin-bottom:.25rem'>"
                f"{job} · {pct}%</div>"
                f"<div style='background:rgba(255,255,255,.1);border-radius:3px;height:5px'>"
                f"<div style='width:{pct}%;background:#ff4d00;border-radius:3px;height:5px'>"
                f"</div></div></div>"
            ) if cpr else (
                "<div style='font-size:.75rem;color:#6b7280;margin:.4rem 0'>無進行中任務</div>"
            )
            with col:
                st.markdown(f"""
                <div class="card" style="border-left:3px solid {color};margin-bottom:.75rem">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                      <div style="font-family:'Syne',sans-serif;font-weight:800;
                                  font-size:1.05rem;color:#ffffff">{name}</div>
                      <div style="font-size:.72rem;color:#8892a4;margin-top:.1rem">
                        {mtype}　{sn}</div>
                    </div>{pill}
                  </div>
                  {prog}
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:.35rem;
                               font-size:.82rem;margin-top:.25rem">
                    <div><span style="color:#8892a4">操作員</span><br>
                         <b style="color:#ffffff;font-size:.88rem">{op}</b></div>
                    <div><span style="color:#8892a4">預計完成</span><br>
                         <b style="color:#ffffff;font-size:.88rem">{etas}</b></div>
                    <div style="grid-column:span 2"><span style="color:#8892a4">材料</span><br>
                         <b style="color:#ffffff;font-size:.86rem">{mat}</b></div>
                  </div>
                  <div style="margin-top:.65rem">
                    <div style="font-size:.72rem;color:#8892a4;margin-bottom:.2rem">
                      材料餘量 {bw}%</div>
                    <div style="background:rgba(255,255,255,.1);border-radius:3px;height:4px">
                      <div style="width:{bw}%;background:{bc};border-radius:3px;height:4px">
                      </div>
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
    # 機器選項：printer_name（alias）
    machines  = sorted(df["printer_name"].dropna().unique().tolist())
    users     = sorted(df["user_name"].dropna().unique().tolist())
    # 材料選項：material_display
    materials = sorted(df["material_display"].dropna().unique().tolist())
    statuses  = sorted(df["status"].dropna().unique().tolist())

    sel_m = f1.multiselect("🖨️ 機器",  machines,
                            placeholder=f"全部 {len(machines)} 台", key="flt_m")
    sel_u = f2.multiselect("👤 人員",  users,
                            placeholder=f"全部 {len(users)} 人",   key="flt_u")
    sel_a = f3.multiselect("🧴 材料",  materials,
                            placeholder=f"全部 {len(materials)} 種",key="flt_a")
    sel_s = f4.multiselect("📊 狀態",  statuses,
                            placeholder=f"全部 {len(statuses)} 種",key="flt_s")

    flt = df.copy()
    if sel_m: flt = flt[flt["printer_name"].isin(sel_m)]
    if sel_u: flt = flt[flt["user_name"].isin(sel_u)]
    if sel_a: flt = flt[flt["material_display"].isin(sel_a)]
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

    # 日期趨勢
    if "日期" in dim:
        chart_opts = st.multiselect(
            "顯示圖表", ["每日任務數","每日材料用量","每日成功/失敗"],
            default=["每日任務數","每日材料用量","每日成功/失敗"], key="dt_opts")
        if "date" in df.columns:
            daily = (df.groupby("date")
                       .agg(任務數=("guid","count"),材料用量_ml=("volume_ml","sum"))
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
                             color_discrete_sequence=["#ff7a35"],title="每日材料用量 (ml)")
                _lay(f2); f2.update_traces(fill="tozeroy",line_width=2)
                cR.plotly_chart(f2,use_container_width=True)
            if "每日成功/失敗" in chart_opts and "success" in df.columns:
                ds = (df.groupby(["date","success"])["guid"].count()
                        .reset_index().rename(columns={"guid":"件數"}))
                ds["date"] = pd.to_datetime(ds["date"])
                f3 = px.bar(ds,x="date",y="件數",color="success",barmode="stack",
                            title="每日成功 vs 失敗",
                            color_discrete_map={"SUCCESS":"#22d3a0","FAILURE":"#ff4d00","UNKNOWN":"#6b7280"})
                _lay(f3); f3.update_traces(marker_cornerradius=2)
                st.plotly_chart(f3,use_container_width=True)
        return

    # 人員 / 機器 / 材料
    dm  = {"👤 人員":"user_name","🖨️ 機器":"printer_name","🧴 材料":"material_display"}
    dc  = dm.get(dim,"user_name")
    lbl = dim.split(" ",1)[-1]

    if dc not in df.columns:
        st.warning(f"資料中缺少 {dc} 欄位"); return

    all_items = sorted(df[dc].dropna().unique().tolist())
    sel_items = st.multiselect(
        f"選擇要顯示的{lbl}（留空 = 全選，共 {len(all_items)} 項）",
        all_items, placeholder="全選", key=f"ci_{dc}")
    pdf = df[df[dc].isin(sel_items)].copy() if sel_items else df.copy()
    if pdf.empty:
        st.info("目前選擇無資料"); return

    chart_types = st.multiselect(
        "圖表類型", ["任務數","材料用量佔比","平均時長","成功率"],
        default=["任務數","材料用量佔比","平均時長","成功率"],
        key=f"ct_{dc}")

    grp = (pdf.groupby(dc)
              .agg(任務數=("guid","count"),
                   材料用量_ml=("volume_ml","sum"),
                   平均時長_h=("duration_h","mean"))
              .reset_index()
              .sort_values("任務數",ascending=False).head(30))

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
        _lay(fp); fp.update_traces(textfont_color="#ffffff",pull=[.03]*len(grp))
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

# ── TABLE ──────────────────────────────────────────────────────────────────────
# 所有可用欄位定義
ALL_COLS = {
    "任務名稱":  "name",
    "機器":      "printer_name",
    "操作員":    "user_name",
    "材料":      "material_display",
    "狀態":      "status",
    "結果":      "success",
    "開始時間":  "print_started_at",
    "時長 (h)":  "duration_h",
    "用量 (ml)": "volume_ml",
}
SORT_OPTS = {
    "開始時間（最新）": ("print_started_at", False),
    "開始時間（最舊）": ("print_started_at", True),
    "時長（長→短）":   ("duration_h",        False),
    "時長（短→長）":   ("duration_h",        True),
    "用量（多→少）":   ("volume_ml",         False),
    "用量（少→多）":   ("volume_ml",         True),
}

def _table(df):
    st.markdown("""
    <div class="sec-title" style="margin-top:1.5rem">📋 列印紀錄</div>
    <div class="sec-sub">自由選擇顯示欄位、排序方式，底部顯示篩選後總計</div>
    """, unsafe_allow_html=True)
    if df.empty:
        st.info("無符合條件的列印記錄"); return

    # 欄位與排序控制列
    tc1, tc2 = st.columns([3,1])
    sel_cols = tc1.multiselect(
        "顯示欄位（可拖曳調整順序）",
        list(ALL_COLS.keys()),
        default=list(ALL_COLS.keys()),  # 預設全選
        key="tbl_cols",
    )
    sort_key = tc2.selectbox(
        "排序方式", list(SORT_OPTS.keys()), key="tbl_sort")

    if not sel_cols:
        st.warning("請至少選擇一個欄位"); return

    sort_col, sort_asc = SORT_OPTS[sort_key]
    show = df.copy()
    if sort_col in show.columns:
        show = show.sort_values(sort_col, ascending=sort_asc)
    show = show.head(300)

    # 建立 HTML 表頭
    thead = "<tr>" + "".join(f"<th>{c}</th>" for c in sel_cols) + "</tr>"

    # 建立資料列
    rows = ""
    for _, r in show.iterrows():
        cells = ""
        for col_label in sel_cols:
            col_key = ALL_COLS[col_label]
            if col_label == "狀態":
                cells += f"<td>{spill(str(r.get('status','')))}</td>"
            elif col_label == "結果":
                suc  = r.get("success","")
                icon = "✅ 成功" if suc=="SUCCESS" else "❌ 失敗" if suc=="FAILURE" else "—"
                cells += f"<td style='text-align:center'>{icon}</td>"
            elif col_label == "開始時間":
                ts = (str(r.get("print_started_at",""))[:16].replace("T"," ")
                      if pd.notna(r.get("print_started_at")) else "—")
                cells += f"<td>{ts}</td>"
            elif col_label == "時長 (h)":
                cells += f"<td style='text-align:right'>{_sf(r.get('duration_h')):.1f}</td>"
            elif col_label == "用量 (ml)":
                cells += f"<td style='text-align:right'>{_sf(r.get('volume_ml')):.0f}</td>"
            elif col_label == "任務名稱":
                name = str(r.get("name") or "—")[:40]
                cells += (f"<td style='max-width:200px;overflow:hidden;"
                          f"text-overflow:ellipsis;white-space:nowrap' "
                          f"title='{name}'>{name}</td>")
            elif col_label == "材料":
                mat = str(r.get("material_display") or "—")[:35]
                cells += (f"<td style='max-width:180px;overflow:hidden;"
                          f"text-overflow:ellipsis;white-space:nowrap'>{mat}</td>")
            else:
                val = str(r.get(col_key) or "—")
                cells += f"<td>{val}</td>"
        rows += f"<tr>{cells}</tr>"

    # 總計列
    tj   = len(df)
    succ = int((df["success"]=="SUCCESS").sum()) if "success" in df.columns else 0
    fail = int((df["success"]=="FAILURE").sum()) if "success" in df.columns else 0
    tvol = df["volume_ml"].sum()
    thr  = df["duration_h"].sum()
    rate = f"{succ/tj*100:.1f}%" if tj else "—"

    # 依選擇欄位決定總計列的 colspan 與顯示
    ncols = len(sel_cols)
    total_cells = ""
    for i, col_label in enumerate(sel_cols):
        if i == 0:
            total_cells += (
                f"<td colspan='1' style='color:#ff7a35;font-family:\"Syne\",sans-serif;"
                f"font-weight:800;font-size:.82rem'>📊 總計</td>"
            )
        elif col_label == "狀態":
            total_cells += f"<td style='color:#ffffff'>共 {tj:,} 筆</td>"
        elif col_label == "結果":
            total_cells += (
                f"<td style='text-align:center;color:#ffffff'>"
                f"✅{succ:,} / ❌{fail:,}<br>"
                f"<span style='font-size:.72rem;color:#8892a4'>{rate}</span></td>"
            )
        elif col_label == "時長 (h)":
            total_cells += f"<td style='text-align:right;color:#ffffff;font-weight:800'>{thr:,.1f}</td>"
        elif col_label == "用量 (ml)":
            total_cells += f"<td style='text-align:right;color:#ffffff;font-weight:800'>{tvol:,.0f}</td>"
        else:
            total_cells += "<td></td>"
    total_row = f'<tr class="total-row">{total_cells}</tr>'

    st.markdown(f"""
    <div class="card" style="overflow-x:auto;padding:0">
      <table class="data-table">
        <thead>{thead}</thead>
        <tbody>{rows}{total_row}</tbody>
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
    st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)

    # 載入印表機（用來建 serial→alias map）
    with st.spinner("載入印表機資料…"):
        try:
            printers = _load_printers(
                st.session_state.use_demo,
                st.session_state.api_token,
            )
        except Exception as e:
            st.error(f"❌ 印表機資料載入失敗：{e}"); return

    # 建立 serial → alias 對照表並存入 session_state
    printer_map = api.build_printer_map(printers)
    st.session_state.printer_map = printer_map

    # 載入列印紀錄
    with st.spinner("載入列印紀錄…"):
        try:
            prints = _load_prints(
                st.session_state.use_demo,
                st.session_state.api_token,
                str(st.session_state.date_from),
                str(st.session_state.date_to),
            )
        except Exception as e:
            st.error(f"❌ 列印紀錄載入失敗：{e}"); return

    # 正規化（serial → printer_name，material fallback）
    prints = api.normalise_prints(prints, printer_map)
    df     = _build_df(prints, printer_map)

    # 日期篩選
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
    <div style="margin-top:1.5rem;padding-bottom:.75rem;
                font-size:.72rem;color:#374151;text-align:center">
      實威國際股份有限公司 台中分公司　|　Powered by Formlabs Web API v0.8.1
    </div>""", unsafe_allow_html=True)
