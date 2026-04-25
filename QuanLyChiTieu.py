import streamlit as st
import pandas as pd
import plotly.express as px
import os
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Quản Lý Chi Tiêu", page_icon="💰", layout="wide")

# --- 1. HỆ THỐNG XÁC THỰC ---
CONFIG_FILE = "config.yaml"

def load_auth_config():
    if not os.path.exists(CONFIG_FILE):
        config = {
            'credentials': {'usernames': {}},
            'cookie': {'expiry_days': 30, 'key': 'secret_key_2001', 'name': 'finance_auth'},
            'preauthorized': {'emails': []}
        }
        with open(CONFIG_FILE, 'w') as file:
            yaml.dump(config, file)
    
    with open(CONFIG_FILE) as file:
        return yaml.load(file, Loader=SafeLoader)

config = load_auth_config()

# Khởi tạo Authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- 2. GIAO DIỆN AUTH ---
st.sidebar.title("🔐 Xác thực / 驗證")
auth_mode = st.sidebar.selectbox("Lựa chọn / 選擇", ["Đăng nhập / 登入", "Đăng ký / 註冊"])

# Xử lý Đăng ký
if auth_mode == "Đăng ký / 註冊":
    try:
        # register_user trong bản mới trả về (email, username, name) nếu thành công
        result = authenticator.register_user(location='main')
        if result:
            # result trả về dữ liệu user mới, lúc này config['credentials'] đã được cập nhật tự động trong bộ nhớ
            with open(CONFIG_FILE, 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('Đăng ký thành công! Vui lòng chọn Đăng nhập ở menu bên trái.')
    except Exception as e:
        st.error(f"Lỗi đăng ký: {e}")

# Xử lý Đăng nhập
if auth_mode == "Đăng nhập / 登入":
    authenticator.login(location='main')

    if st.session_state["authentication_status"]:
        # --- NỘI DUNG CHÍNH SAU KHI ĐĂNG NHẬP ---
        user_full_name = st.session_state["name"]
        user_id = st.session_state["username"]
        DATA_FILE = f"data_{user_id}.csv"
        CAT_IDS = ["ESSENTIAL", "SAVINGS", "EDUCATION", "ENJOY", "INVEST"]

        with st.sidebar:
            st.markdown(f"### 👤 Xin chào, **{user_full_name}**")
            authenticator.logout('Đăng xuất / 登出', 'sidebar')
            st.markdown("---")
            sel_lang = st.selectbox("🌐 Ngôn ngữ", ["Tiếng Việt", "繁體中文"])

        # --- 3. TỪ ĐIỂN NGÔN NGỮ ---
        LANG = {
            "Tiếng Việt": {
                "title": f"📑 Quản Lý Chi Tiêu - {user_full_name}",
                "sidebar_header": "➕ Giao Dịch Mới",
                "date": "Ngày", "member": "Người thực hiện", "content": "Nội dung",
                "amount": "Số tiền (VNĐ)", "category": "Hạng mục",
                "type": "Loại", "income": "Thu nhập (Chia hũ)", "expense": "Chi tiêu (Trừ hũ)",
                "btn_save": "Ghi sổ", "unit": "đ", "rate": 1.0,
                "members": ["Chồng", "Vợ", "Con cái", "Khác"],
                "categories": ["🏠 Thiết yếu (55%)", "💰 Tiết kiệm (15%)", "📚 Giáo dục (10%)", "🍹 Hưởng thụ (10%)", "📈 Đầu tư (10%)"],
                "tab_overview": "📊 Tổng Quan", "tab_history": "📅 Lịch Sử", "tab_manage": "🛠️ Quản Trị",
                "chart_bar": "📊 Cơ cấu tài chính", "chart_pie": "🍕 Tỷ lệ chi tiêu",
                "prefix_income": "Phân bổ: ", "id_label": "Dòng ID", "btn_delete": "Xác nhận xóa"
            },
            "繁體中文": {
                "title": f"📑 財務支出管理 - {user_full_name}",
                "sidebar_header": "➕ 新增交易",
                "date": "日期", "member": "執行者", "content": "詳細內容",
                "amount": "金額 (TWD)", "category": "類別",
                "type": "類型", "income": "收入 (分配)", "expense": "支出 (扣除)",
                "btn_save": "儲存記錄", "unit": "NT$", "rate": 0.00125,
                "members": ["丈夫", "妻子", "孩子", "其他"],
                "categories": ["生活必要 (55%)", "長期儲蓄 (15%)", "教育學習 (10%)", "休閒娛樂 (10%)", "財務自由 (10%)"],
                "tab_overview": "📊 概覽", "tab_history": "📅 歷史記錄", "tab_manage": "🛠️ 數據管理",
                "chart_bar": "📊 財務結構", "chart_pie": "🍕 支出比例",
                "prefix_income": "分配: ", "id_label": "編號 ID", "btn_delete": "確認刪除"
            }
        }
        t = LANG[sel_lang]

        # --- 4. TẢI DỮ LIỆU ---
        def load_data():
            if os.path.exists(DATA_FILE):
                df_load = pd.read_csv(DATA_FILE)
                df_load['Ngày'] = pd.to_datetime(df_load['Ngày']).dt.date
                return df_load
            return pd.DataFrame(columns=["Ngày", "Người thực hiện", "Nội dung", "Số tiền", "Hạng mục", "Loại"])

        df = load_data()

        # --- 5. SIDEBAR: NHẬP LIỆU ---
        st.sidebar.header(t["sidebar_header"])
        with st.sidebar.form("input_form", clear_on_submit=True):
            date_val = st.date_input(t["date"], datetime.now())
            member_val = st.selectbox(t["member"], t["members"]) 
            content_val = st.text_input(t["content"])
            amount_val = st.number_input(t["amount"], min_value=0, step=1000, format="%d")
            type_val = st.radio(t["type"], [t["income"], t["expense"]])
            category_val = st.selectbox(t["category"], t["categories"])

            if st.form_submit_button(t["btn_save"]):
                idx = t["categories"].index(category_val)
                cat_id = CAT_IDS[idx]
                amt_base = float(amount_val) / t["rate"]
                
                new_entries = []
                if type_val == t["income"]:
                    ratios = [0.55, 0.15, 0.10, 0.10, 0.10]
                    for i, cid in enumerate(CAT_IDS):
                        split_amt = amt_base * ratios[i]
                        new_entries.append([date_val, member_val, f"Phân bổ: {content_val}", split_amt, cid, t["income"]])
                else:
                    new_entries.append([date_val, member_val, content_val, -amt_base, cat_id, t["expense"]])

                df = pd.concat([df, pd.DataFrame(new_entries, columns=df.columns)], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.toast("✅ Đã ghi sổ!")
                st.rerun()

        # --- 6. GIAO DIỆN CHÍNH ---
        st.title(t["title"])
        df_dis = df.copy()
        df_dis["Số tiền"] = df_dis["Số tiền"] * t["rate"]
        
        tab_dash, tab_hist, tab_manage = st.tabs([t["tab_overview"], t["tab_history"], t["tab_manage"]])

        with tab_dash:
            jar_balances = df_dis.groupby("Hạng mục")["Số tiền"].sum()
            icons = ["🏠", "💰", "📚", "🍹", "📈"]
            colors = ["#FF4B4B", "#FFA41B", "#2563EB", "#059669", "#7C3AED"]
            
            cols = st.columns(5)
            for i, jar_id in enumerate(CAT_IDS):
                balance_val = jar_balances.get(jar_id, 0.0)
                balance_fmt = f"{balance_val:,.0f}".replace(",", ".")
                with cols[i]:
                    st.markdown(f"""
                        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 12px; 
                                    border-bottom: 5px solid {colors[i]}; text-align: center;">
                            <div style="font-size: 30px;">{icons[i]}</div>
                            <div style="color: #666; font-size: 12px; font-weight: bold;">{t['categories'][i].split(' (')[0]}</div>
                            <div style="font-size: 16px; font-weight: bold; color: #333;">{balance_fmt}{t['unit']}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            c1, c2 = st.columns(2)
            
            chart_df = df_dis.copy()
            chart_df["Hạng mục"] = chart_df["Hạng mục"].apply(lambda x: t["categories"][CAT_IDS.index(x)] if x in CAT_IDS else x)
            
            with c1:
                st.subheader(t["chart_bar"])
                if not chart_df.empty:
                    fig1 = px.bar(chart_df.groupby("Hạng mục")["Số tiền"].sum().reset_index(), x="Hạng mục", y="Số tiền", color="Hạng mục")
                    st.plotly_chart(fig1, use_container_width=True)
            with c2:
                st.subheader(t["chart_pie"])
                exp_df = chart_df[chart_df["Số tiền"] < 0].copy()
                if not exp_df.empty:
                    exp_df["Số tiền"] = exp_df["Số tiền"].abs()
                    fig2 = px.pie(exp_df, values="Số tiền", names="Hạng mục", hole=0.4)
                    st.plotly_chart(fig2, use_container_width=True)

        with tab_hist:
            df_hist = df_dis.copy()
            df_hist["Hạng mục"] = df_hist["Hạng mục"].apply(lambda x: t["categories"][CAT_IDS.index(x)] if x in CAT_IDS else x)
            # Format tiền tệ để hiển thị
            df_hist["Số tiền"] = df_hist["Số tiền"].apply(lambda x: f"{x:,.0f} {t['unit']}".replace(",", "."))
            st.dataframe(df_hist.sort_values("Ngày", ascending=False), use_container_width=True)

        with tab_manage:
            st.subheader(t["tab_manage"])
            if not df.empty:
                df_m = df.copy().reset_index()
                row_idx = st.selectbox(t["id_label"], options=df_m["index"], 
                                       format_func=lambda x: f"ID {x}: {df_m.loc[x, 'Nội dung']}")
                if st.button(t["btn_delete"], type="primary"):
                    df = df.drop(row_idx)
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Đã xóa! / 已刪除！")
                    st.rerun()

    elif st.session_state["authentication_status"] is False:
        st.error('Sai thông tin đăng nhập! / 帳號密碼錯誤！')
    elif st.session_state["authentication_status"] is None:
        st.info('Vui lòng Đăng nhập để tiếp tục. / 請先登入。')