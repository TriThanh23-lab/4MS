import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. Cấu hình trang web (Phải nằm ở đầu tiên)
st.set_page_config(page_title="Tiệm Quản Lý Tài Chính", layout="wide")

# 2. Xử lý dữ liệu
DATA_FILE = "finance_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=["Ngày", "Loại", "Hạng mục", "Số tiền", "Ghi chú"])
    return pd.DataFrame(columns=["Ngày", "Loại", "Hạng mục", "Số tiền", "Ghi chú"])

def save_data(df_to_save):
    df_to_save.to_csv(DATA_FILE, index=False)

# Tải dữ liệu vào ứng dụng
df = load_data()

# 3. Giao diện Sidebar (Thanh nhập liệu)
st.sidebar.header("🎨 Nhập Giao Dịch")
with st.sidebar.form("my_form", clear_on_submit=True):
    date = st.date_input("Ngày", datetime.now())
    t_type = st.selectbox("Loại", ["Chi phí", "Thu nhập"])
    category = st.selectbox("Hạng mục", [
        "Ăn uống", "Di chuyển", "Tiền nhà", "Lương", 
        "Mua sắm", "Sức khỏe", "Giải trí", "Khác"
    ])
    amount = st.number_input("Số tiền (VNĐ)", min_value=0, step=1000)
    note = st.text_input("Ghi chú")
    
    submitted = st.form_submit_button("Lưu vào sổ")
    if submitted:
        new_row = pd.DataFrame([[str(date), t_type, category, amount, note]], 
                              columns=["Ngày", "Loại", "Hạng mục", "Số tiền", "Ghi chú"])
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.sidebar.success("Đã ghi sổ thành công!")
        st.rerun()

# 4. Giao diện chính (Dashboard)
st.title("✨ Tiệm Quản Lý Tài Chính Cá Nhân")
st.markdown("---")

if not df.empty:
    # Tính toán con số
    income = df[df["Loại"] == "Thu nhập"]["Số tiền"].sum()
    expense = df[df["Loại"] == "Chi phí"]["Số tiền"].sum()
    balance = income - expense

    # Hiển thị 3 cột thông tin
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Tổng Thu", f"{income:,.0f} đ")
    c2.metric("💸 Tổng Chi", f"-{expense:,.0f} đ")
    c3.metric("🏠 Còn Lại", f"{balance:,.0f} đ")

    st.markdown("### 📊 Phân Tích Chi Tiêu")
    col_a, col_b = st.columns(2)

    with col_a:
        # Biểu đồ tròn
        expense_df = df[df["Loại"] == "Chi phí"]
        if not expense_df.empty:
            fig_pie = px.pie(expense_df, values='Số tiền', names='Hạng mục', 
                             title='Tỷ lệ các khoản chi', hole=0.5,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu chi tiêu.")

    with col_b:
        # Biểu đồ cột theo ngày
        df['Ngày'] = pd.to_datetime(df['Ngày'])
        daily = df.groupby(['Ngày', 'Loại'])['Số tiền'].sum().reset_index()
        fig_bar = px.bar(daily, x='Ngày', y='Số tiền', color='Loại',
                          title='Biến động tài chính', barmode='group',
                          color_discrete_map={'Thu nhập': '#2ecc71', 'Chi phí': '#e74c3c'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # Lịch sử
    st.markdown("### 📝 Lịch Sử Giao Dịch")
    st.dataframe(df.sort_values(by="Ngày", ascending=False), use_container_width=True)

    if st.button("Xóa hết dữ liệu (Làm lại từ đầu)"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.rerun()
else:
    st.info("💡 Bạn chưa có giao dịch nào. Hãy nhập thông tin ở bên trái nhé!")

# 5. Làm đẹp giao diện bằng CSS
st.markdown("""
<style>
    .stApp { background-color: #fcfcfc; }
    [data-testid="stMetricValue"] { color: #2c3e50; font-weight: bold; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)
