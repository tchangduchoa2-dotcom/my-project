import streamlit as st
import pandas as pd
import plotly.express as px
import os
import yaml
import base64
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Quản Lý Chi Tiêu", page_icon="💰", layout="wide")

# --- 🛠️ HÀM XỬ LÝ ẢNH ---
def get_base64_image(image_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, image_path)
    if not os.path.exists(full_path):
        full_path = image_path 
    if os.path.exists(full_path):
        with open(full_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

bin_str = get_base64_image("banner.png") or get_base64_image("banner.jpg")

# --- 🎨 CSS GIAO DIỆN (PHÓNG TO BANNER & TÁCH CHỮ) ---
st.markdown(f"""
    <style>
    /* Metric Cards */
    .metric-card {{
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-bottom: 5px solid #ccc;
        text-align: center;
        transition: transform 0.3s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }}
    
    /* Banner Wrapper - Phóng to cực đại */
    .banner-wrapper {{
        width: 100%;
        height: 450px; /* Tăng chiều cao banner */
        border-radius: 25px;
        overflow: hidden;
        margin-bottom: 20px;
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }}
    .banner-img {{
        width: 100%;
        height: 100%;
        object-fit: cover; /* Lấp đầy khung hình */
        object-position: center;
    }}

    /* Tiêu đề nằm dưới banner */
    .title-section {{
        text-align: center;
        padding: 10px 0 30px 0;
    }}
    .main-title {{
        color: #1E3A8A;
        font-size: 3.5rem;
        font-weight: 850;
        margin: 0;
        letter-spacing: -1px;
    }}
    .main-subtitle {{
        color: #64748B;
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 5px;
    }}
    .title-divider {{
        width: 120px;
        height: 5px;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        margin: 20px auto;
        border-radius: 10px;
    }}
    
    .stButton>button {{
        width: 100%;
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 1. XÁC THỰC ---
CONFIG_FILE = "config.yaml"
def load_auth_config():
    if not os.path.exists(CONFIG_FILE):
        config = {'credentials': {'usernames': {}}, 'cookie': {'expiry_days': 30, 'key': 'secret_key_2001', 'name': 'finance_auth'}, 'preauthorized': {'emails': []}}
        with open(CONFIG_FILE, 'w') as file: yaml.dump(config, file)
    with open(CONFIG_FILE) as file: return yaml.load(file, Loader=SafeLoader)

config = load_auth_config()
authenticator = stauth.Authenticate(config['credentials'], config['cookie']['name'], config['cookie']['key'], config['cookie']['expiry_days'])

# --- 2. GIAO DIỆN AUTH ---
st.sidebar.title("🔐 Xác thực / 驗證")
auth_mode = st.sidebar.selectbox("Lựa chọn / 選擇", ["Đăng nhập / 登入", "Đăng ký / 註冊"])

if auth_mode == "Đăng ký / 註冊":
    try:
        result = authenticator.register_user(location='main')
        if result:
            with open(CONFIG_FILE, 'w') as file: yaml.dump(config, file, default_flow_style=False)
            st.success('Đăng ký thành công!')
    except Exception as e: st.error(f"Lỗi: {e}")

if auth_mode == "Đăng nhập / 登入":
    authenticator.login(location='main')
    if st.session_state["authentication_status"]:
        user_full_name = st.session_state["name"]
        user_id = st.session_state["username"]
        DATA_FILE = f"data_{user_id}.csv"
        CAT_IDS = ["ESSENTIAL", "SAVINGS", "EDUCATION", "ENJOY", "INVEST"]

        with st.sidebar:
            st.markdown(f"### 👤 Xin chào, **{user_full_name}**")
            sel_lang = st.selectbox("🌐 Ngôn ngữ", ["Tiếng Việt", "繁體中文"])
            authenticator.logout('Đăng xuất / 登出', 'sidebar')
            st.markdown("---")

        LANG = {
            "Tiếng Việt": {
                "title": "Quản Lý Chi Tiêu", "subtitle": "Hệ thống quản lý tài chính cá nhân thông minh",
                "sidebar_header": "➕ Giao Dịch Mới", "date": "Ngày", "member": "Người thực hiện", 
                "content": "Nội dung", "amount": "Số tiền (VNĐ)", "category": "Hạng mục",
                "type": "Loại", "income": "Thu nhập (Chia hũ)", "expense": "Chi tiêu (Trừ hũ)",
                "btn_save": "Ghi sổ", "unit": "đ", "rate": 1.0,
                "members": ["Chồng", "Vợ", "Con cái", "Khác"],
                "categories": ["🏠 Thiết yếu (55%)", "💰 Tiết kiệm (15%)", "📚 Giáo dục (10%)", "🍹 Hưởng thụ (10%)", "📈 Đầu tư (10%)"],
                "tab_overview": "📊 Tổng Quan", "tab_history": "📅 Lịch Sử", "tab_manage": "🛠️ Quản Trị",
                "chart_bar": "📊 Cơ cấu tài chính", "chart_pie": "🍕 Tỷ lệ chi tiêu",
                "prefix_income": "Phân bổ: ", "id_label": "Dòng ID", "btn_delete": "Xác nhận xóa"
            },
            "繁體中文": {
                "title": "財務支出管理", "subtitle": "個人智慧財務管理系統",
                "sidebar_header": "➕ 新增交易", "date": "日期", "member": "執行者",
                "content": "詳細內容", "amount": "金額 (TWD)", "category": "類別",
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

        def load_data():
            if os.path.exists(DATA_FILE):
                df_load = pd.read_csv(DATA_FILE)
                df_load['Ngày'] = pd.to_datetime(df_load['Ngày']).dt.date
                return df_load
            return pd.DataFrame(columns=["Ngày", "Người thực hiện", "Nội dung", "Số tiền", "Hạng mục", "Loại"])

        df = load_data()

        # --- 4. SIDEBAR INPUT ---
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
                        new_entries.append([date_val, member_val, f"{t['prefix_income']}{content_val}", split_amt, cid, t["income"]])
                else:
                    new_entries.append([date_val, member_val, content_val, -amt_base, cat_id, t["expense"]])
                df = pd.concat([df, pd.DataFrame(new_entries, columns=df.columns)], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.toast("✅ Đã ghi sổ!")
                st.rerun()

        # --- 5. HIỂN THỊ BANNER PHÓNG TO & TIÊU ĐỀ TÁCH BIỆT ---
        if bin_str:
            st.markdown(f"""
                <div class="banner-wrapper">
                    <img class="banner-img" src="data:image/jpeg;base64,{bin_str}">
                </div>
                <div class="title-section">
                    <h1 class="main-title">{t["title"]}</h1>
                    <p class="main-subtitle">{t["subtitle"]}</p>
                    <div class="title-divider"></div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.title(t["title"])
            st.caption(t["subtitle"])

        # --- 6. NỘI DUNG CHÍNH (Metrics & Charts) ---
        df_dis = df.copy()
        df_dis["Số tiền"] = df_dis["Số tiền"] * t["rate"]
        tab_dash, tab_hist, tab_manage = st.tabs([t["tab_overview"], t["tab_history"], t["tab_manage"]])

        with tab_dash:
            jar_balances = df_dis.groupby("Hạng mục")["Số tiền"].sum() if not df_dis.empty else pd.Series()
            icons, colors = ["🏠", "💰", "📚", "🍹", "📈"], ["#FF4B4B", "#FFA41B", "#2563EB", "#059669", "#7C3AED"]
            cols = st.columns(5)
            for i, jar_id in enumerate(CAT_IDS):
                balance_val = jar_balances.get(jar_id, 0.0)
                with cols[i]:
                    st.markdown(f"""
                        <div class="metric-card" style="border-bottom-color: {colors[i]};">
                            <div style="font-size: 35px; margin-bottom: 5px;">{icons[i]}</div>
                            <div style="color: #666; font-size: 13px; font-weight: bold;">{t['categories'][i].split(' (')[0]}</div>
                            <div style="font-size: 18px; font-weight: 800; color: #333;">{balance_val:,.0f}{t['unit']}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            c1, c2 = st.columns(2)
            chart_df = df_dis.copy()
            chart_df["Hạng mục"] = chart_df["Hạng mục"].apply(lambda x: t["categories"][CAT_IDS.index(x)] if x in CAT_IDS else x)
            with c1:
                st.subheader(t["chart_bar"])
                if not chart_df.empty:
                    fig1 = px.bar(chart_df.groupby("Hạng mục")["Số tiền"].sum().reset_index(), x="Hạng mục", y="Số tiền", color="Hạng mục", color_discrete_sequence=colors)
                    fig1.update_layout(showlegend=False)
                    st.plotly_chart(fig1, use_container_width=True)
            with c2:
                st.subheader(t["chart_pie"])
                exp_df = chart_df[chart_df["Số tiền"] < 0].copy()
                if not exp_df.empty:
                    exp_df["Số tiền"] = exp_df["Số tiền"].abs()
                    fig2 = px.pie(exp_df, values="Số tiền", names="Hạng mục", hole=0.5, color_discrete_sequence=colors)
                    st.plotly_chart(fig2, use_container_width=True)

        with tab_hist:
            df_hist = df_dis.copy()
            df_hist["Hạng mục"] = df_hist["Hạng mục"].apply(lambda x: t["categories"][CAT_IDS.index(x)] if x in CAT_IDS else x)
            df_hist["Số tiền"] = df_hist["Số tiền"].apply(lambda x: f"{x:,.0f} {t['unit']}".replace(",", "."))
            st.dataframe(df_hist.sort_values("Ngày", ascending=False), use_container_width=True)

        with tab_manage:
            st.subheader(t["tab_manage"])
            if not df.empty:
                df_m = df.copy().reset_index()
                row_idx = st.selectbox(t["id_label"], options=df_m["index"], format_func=lambda x: f"ID {x}: {df_m.loc[x, 'Nội dung']}")
                if st.button(t["btn_delete"], type="primary"):
                    df = df.drop(row_idx)
                    df.to_csv(DATA_FILE, index=False)
                    st.success("Đã xóa thành công!")
                    st.rerun()

    elif st.session_state["authentication_status"] is False:
        st.error('Sai thông tin đăng nhập!')
    elif st.session_state["authentication_status"] is None:
        st.info('Vui lòng Đăng nhập để tiếp tục.')