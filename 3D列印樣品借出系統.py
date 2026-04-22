import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="3D列印樣品管理", layout="wide")

# =========================
# SESSION STATE
# =========================
if "samples" not in st.session_state:
    st.session_state.samples = [
        {"id":1,"name":"FDM 齒輪組","desc":"PLA材料","status":"available","borrower":"","borrow_date":"","return_date":"","note":"請輕拿輕放","image":""},
        {"id":2,"name":"SLA 透明殼體","desc":"光固化樹脂","status":"borrowed","borrower":"王小明","borrow_date":"2025-04-10","return_date":"","note":"需歸還盒裝","image":""},
        {"id":3,"name":"SLS 結構件","desc":"尼龍粉末","status":"available","borrower":"","borrow_date":"","return_date":"","note":"","image":""},
        {"id":4,"name":"MJF 彩色件","desc":"多噴嘴列印","status":"borrowed","borrower":"李美華","borrow_date":"2025-04-15","return_date":"","note":"勿受潮","image":""},
    ]

if "borrowers" not in st.session_state:
    st.session_state.borrowers = ["王小明","李美華","張大偉","陳怡君"]

if "history" not in st.session_state:
    st.session_state.history = []

if "admin" not in st.session_state:
    st.session_state.admin = False


# =========================
# TITLE
# =========================
st.title("🧩 實威國際 3D列印樣品管理系統")

col1, col2, col3, col4 = st.columns(4)
col1.metric("總樣品", len(st.session_state.samples))
col2.metric("借出中", len([s for s in st.session_state.samples if s["status"]=="borrowed"]))
col3.metric("在庫", len([s for s in st.session_state.samples if s["status"]=="available"]))
col4.button("🔐 管理員切換", on_click=lambda: st.session_state.update(admin=not st.session_state.admin))


st.divider()


# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["📦 樣品管理", "📤 借用/歸還", "📊 分析"])


# =========================
# TAB 1 - SAMPLE CARDS
# =========================
with tab1:
    st.subheader("樣品卡片")

    for s in st.session_state.samples:

        with st.container(border=True):

            colA, colB = st.columns([1,3])

            with colA:
                if s["image"]:
                    st.image(s["image"])
                else:
                    st.write("🖨️")

                if st.session_state.admin:
                    img = st.file_uploader("上傳圖片", key=f"img_{s['id']}")
                    if img:
                        s["image"] = img.getvalue()

            with colB:
                st.markdown(f"### {s['name']}")
                st.write(s["desc"])

                status = "📤 借出中" if s["status"]=="borrowed" else "📥 在庫"
                st.write(status)

                st.write(f"借用人：{s['borrower'] or '-'}")
                st.write(f"借出日：{s['borrow_date'] or '-'}")
                st.write(f"歸還日：{s['return_date'] or '-'}")

                if st.session_state.admin:
                    s["note"] = st.text_input("備註", value=s["note"], key=f"note_{s['id']}")
                    if st.button("🗑 刪除", key=f"del_{s['id']}"):
                        st.session_state.samples.remove(s)
                        st.rerun()


# =========================
# TAB 2 - BORROW / RETURN
# =========================
with tab2:
    st.subheader("借用 / 歸還")

    sample_name = st.selectbox("選擇樣品", [s["name"] for s in st.session_state.samples])
    user = st.selectbox("借用人", st.session_state.borrowers)
    action = st.radio("動作", ["借用","歸還"])
    d = st.date_input("日期", date.today())

    if st.button("送出"):

        for s in st.session_state.samples:
            if s["name"] == sample_name:

                if action == "借用":
                    s["status"] = "borrowed"
                    s["borrower"] = user
                    s["borrow_date"] = str(d)

                else:
                    s["status"] = "available"
                    s["return_date"] = str(d)

                    st.session_state.history.append({
                        "name": s["name"],
                        "user": s["borrower"],
                        "borrow": s["borrow_date"],
                        "return": str(d)
                    })

                    s["borrower"] = ""
                    s["borrow_date"] = ""

        st.success("已更新")


# =========================
# TAB 3 - ANALYTICS
# =========================
with tab3:
    st.subheader("借用分析")

    df = pd.DataFrame(st.session_state.history)

    if not df.empty:
        st.dataframe(df)

        st.subheader("依人員統計")
        st.bar_chart(df["user"].value_counts())

        st.subheader("依樣品統計")
        st.bar_chart(df["name"].value_counts())
    else:
        st.info("尚無紀錄")


# =========================
# BORROWER MANAGEMENT
# =========================
if st.session_state.admin:
    st.divider()
    st.subheader("👤 借用人管理")

    new_user = st.text_input("新增借用人")
    if st.button("新增人員"):
        if new_user and new_user not in st.session_state.borrowers:
            st.session_state.borrowers.append(new_user)
            st.success("已新增")
            st.rerun()

    st.write(st.session_state.borrowers)
