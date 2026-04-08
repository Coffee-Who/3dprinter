import streamlit as st
from stl import mesh
import tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="3D列印快速估價工具", layout="centered")

st.title("🧠 3D列印快速估價工具（業務版）")

# 客戶資訊
st.subheader("👤 客戶資訊")
customer_name = st.text_input("客戶名稱")
project_name = st.text_input("專案名稱")

# 上傳 STL
st.subheader("📦 上傳模型")
uploaded_file = st.file_uploader("上傳 STL 檔案", type=["stl"])

volume = None

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    your_mesh = mesh.Mesh.from_file(tmp_path)

    volume_mm3, _, _ = your_mesh.get_mass_properties()
    volume = volume_mm3 / 1000  # 轉 cm³

    st.success(f"✅ 模型體積：約 {volume:.2f} cm³")

# 參數
st.subheader("⚙️ 列印需求")

material = st.selectbox("材料", [
    "標準樹脂",
    "高強度樹脂",
    "耐溫樹脂"
])

usage = st.selectbox("用途", [
    "外觀件",
    "功能件"
])

# 成本設定
material_cost = {
    "標準樹脂": 20,
    "高強度樹脂": 35,
    "耐溫樹脂": 40
}

machine_rate = 300

# PDF 產生
def generate_pdf(customer, project, price, lead_time):
    file_path = "quotation.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("3D列印報價單", styles["Title"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"客戶：{customer}", styles["Normal"]))
    content.append(Paragraph(f"專案：{project}", styles["Normal"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"報價：NTD {price}", styles["Normal"]))
    content.append(Paragraph(f"交期：{lead_time}", styles["Normal"]))

    doc.build(content)
    return file_path

# 估價
if st.button("💰 立即估價"):

    if volume is None:
        st.error("請先上傳 STL 檔案")
    else:
        print_time = volume * 0.1

        material_price = volume * material_cost[material]
        machine_price = print_time * machine_rate
        post_process = 500 if usage == "功能件" else 300

        total_cost = material_price + machine_price + post_process
        final_price = int(total_cost * 1.3)

        lead_time = "2~3 天" if volume < 100 else "3~5 天"

        st.success("✅ 估價完成")

        st.subheader("📊 報價結果")

        st.markdown(f"""
        ### 💰 預估價格：**NTD {final_price}**
        ### ⏱ 交期：**{lead_time}**

        ---
        ### 🔍 成本分析
        - 材料：NTD {int(material_price)}
        - 機台：NTD {int(machine_price)}
        - 後處理：NTD {post_process}

        ---
        ### 🧠 建議製程
        SLA 光固化列印（高精度）
        """)

        pdf_path = generate_pdf(customer_name, project_name, final_price, lead_time)

        with open(pdf_path, "rb") as f:
            st.download_button("📄 下載報價單", f, file_name="報價單.pdf")
