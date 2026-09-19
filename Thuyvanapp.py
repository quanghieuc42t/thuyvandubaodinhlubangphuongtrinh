import streamlit as st
import pandas as pd
from io import BytesIO

# Cấu hình trang web
st.set_page_config(
    page_title="Dự Báo Mực Nước Đỉnh Lũ",
    page_icon="🌊",  # Bạn có thể thay bằng link ảnh PNG/JPG logo của đơn vị nếu có
    layout="wide",
    initial_sidebar_state="collapsed"
)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Tiêu đề ứng dụng
st.markdown("<h2 style='text-align: center; color: #1d4ed8;'>HỆ THỐNG DỰ BÁO MỰC NƯỚC ĐỈNH LŨ BẰNG PHƯƠNG TRÌNH</h2>", unsafe_allow_html=True)
st.markdown("---")

# Khung thông tin đợt mưa lũ chung
st.subheader("📋 Thông tin đợt mưa lũ")
col_info1, col_info2, col_info3, col_info4 = st.columns(4)
with col_info1:
    ten_lu = st.text_input("Tên đợt mưa/lũ", value="Đợt lũ chính vụ năm 2026")
with col_info2:
    bat_dau = st.text_input("Bắt đầu", value="15/10/2026")
with col_info3:
    ket_thuc = st.text_input("Kết thúc", value="18/10/2026")
with col_info4:
    nguoi_thuc_hien = st.text_input("Thực hiện", value="Đài KTTV Quảng Trị")

st.markdown("---")

# Định nghĩa cấu hình lưu vực và các trạm
basins_config = {
    "Sông Gianh": [
        {"name": "Đồng Tâm", "type": "independent", "need_xtr": True, "need_xdr": False, "need_hc": True, "bd1": 7.0, "bd2": 13.0, "bd3": 16.0},
        {"name": "Mai Hóa", "type": "dependent", "parent": "Đồng Tâm", "need_xtr": False, "need_xdr": True, "need_hc": True, "bd1": 3.0, "bd2": 5.0, "bd3": 6.5}
    ],
    "Sông Kiến Giang": [
        {"name": "Kiến Giang", "type": "independent", "need_xtr": True, "need_xdr": False, "need_hc": True, "bd1": 8.0, "bd2": 11.0, "bd3": 13.0},
        {"name": "Lệ Thủy", "type": "dependent", "parent": "Kiến Giang", "need_xtr": True, "need_xdr": True, "need_hc": True, "bd1": 1.2, "bd2": 2.2, "bd3": 2.7}
    ],
    "Sông Bến Hải": [
        {"name": "Bến Quan", "type": "independent", "need_xtr": True, "need_xdr": False, "need_hc": True, "bd1": 4.0, "bd2": 5.5, "bd3": 6.5},
        {"name": "Gia Vòng", "type": "independent", "need_xtr": True, "need_xdr": False, "need_hc": True, "bd1": 5.0, "bd2": 8.0, "bd3": 11.0},
        {"name": "Hiền Lương", "type": "dependent", "parent": "Gia Vòng", "need_xtr": True, "need_xdr": True, "need_hc": True, "bd1": 1.0, "bd2": 2.0, "bd3": 2.5}
    ],
    "Sông Hiếu": [
        {"name": "Đầu Mầu", "type": "independent", "need_xtr": True, "need_xdr": False, "need_hc": True, "bd1": 21.0, "bd2": 22.5, "bd3": 23.5},
        {"name": "Đông Hà", "type": "dependent", "parent": "Đầu Mầu", "need_xtr": True, "need_xdr": True, "need_hc": True, "bd1": 2.0, "bd2": 3.0, "bd3": 4.0}
    ],
    "Sông Thạch Hãn": [
        {"name": "Đakrông", "type": "independent", "need_xtr": True, "need_xdr": False, "need_hc": True, "bd1": 29.5, "bd2": 31.5, "bd3": 33.5},
        {"name": "Thạch Hãn", "type": "dependent", "parent": "Đakrông", "need_xtr": True, "need_xdr": True, "need_hc": True, "bd1": 3.0, "bd2": 4.5, "bd3": 6.0}
    ],
    "Sông Ô Lâu": [
        {"name": "Mỹ Chánh", "type": "independent", "need_xtr": True, "need_xdr": False, "need_hc": True, "bd1": 2.5, "bd2": 4.0, "bd3": 5.3},
        {"name": "Hải Tân", "type": "dependent", "parent": "Mỹ Chánh", "need_xtr": True, "need_xdr": True, "need_hc": True, "bd1": 1.8, "bd2": 2.8, "bd3": 3.4}
    ]
}

default_values = {
    "Đồng Tâm": {"xtr": 120.0, "xdr": 0.0, "hc": 320.0},
    "Mai Hóa": {"xtr": 0.0, "xdr": 120.0, "hc": -20.0},
    "Kiến Giang": {"xtr": 200.0, "xdr": 0.0, "hc": 570.0},
    "Lệ Thủy": {"xtr": 200.0, "xdr": 260.0, "hc": 2.0},
    "Bến Quan": {"xtr": 250.0, "xdr": 0.0, "hc": 265.0},
    "Gia Vòng": {"xtr": 260.0, "xdr": 0.0, "hc": 180.0},
    "Hiền Lương": {"xtr": 260.0, "xdr": 250.0, "hc": -20.0},
    "Đầu Mầu": {"xtr": 260.0, "xdr": 0.0, "hc": 2000.0},
    "Đông Hà": {"xtr": 260.0, "xdr": 250.0, "hc": -15.0},
    "Đakrông": {"xtr": 220.0, "xdr": 0.0, "hc": 2410.0},
    "Thạch Hãn": {"xtr": 220.0, "xdr": 263.0, "hc": -10.0},
    "Mỹ Chánh": {"xtr": 240.0, "xdr": 0.0, "hc": 5.0},
    "Hải Tân": {"xtr": 240.0, "xdr": 250.0, "hc": 70.0},
}

# Khởi tạo lưu trữ dữ liệu nhập trên session_state
if "input_data" not in st.session_state:
    st.session_state.input_data = default_values.copy()

if "all_results" not in st.session_state:
    st.session_state.all_results = {}

# Giao diện chọn lưu vực để nhập liệu
selected_basin = st.selectbox("📂 Chọn Lưu vực sông để nhập số liệu:", list(basins_config.keys()))

st.markdown(f"### Nhập số liệu thủy văn cho: **{selected_basin}**")
stations = basins_config[selected_basin]

basin_inputs = {}
for st_cfg in stations:
    name = st_cfg["name"]
    st.markdown(f"**Trạm: {name}** (`{'Trạm độc lập' if st_cfg['type']=='independent' else 'Trạm phụ thuộc'}`)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        xtr_val = st.number_input(
            f"Mưa trạm trên / Xtrtrên (mm) - {name}", 
            value=st.session_state.input_data[name]["xtr"],
            disabled=not st_cfg["need_xtr"],
            key=f"xtr_{name}"
        )
    with col2:
        xdr_val = st.number_input(
            f"Mưa trạm dưới / Xtrdưới (mm) - {name}", 
            value=st.session_state.input_data[name]["xdr"],
            disabled=not st_cfg["need_xdr"],
            key=f"xdr_{name}"
        )
    with col3:
        hc_val = st.number_input(
            f"Hcdưới (cm) - {name}", 
            value=st.session_state.input_data[name]["hc"],
            key=f"hc_{name}"
        )
    
    basin_inputs[name] = {"xtr": xtr_val, "xdr": xdr_val, "hc": hc_val}
    st.markdown("---")

# Nút tính toán cho lưu vực hiện tại
if st.button(f"▶ TÍNH TOÁN DỰ BÁO CHO {selected_basin.upper()}", type="primary", use_container_width=True):
    # Cập nhật session state
    for k, v in basin_inputs.items():
        st.session_state.input_data[k] = v
        
    basin_raw = st.session_state.input_data
    basin_hmaxdb = {}
    
    try:
        if selected_basin == "Sông Gianh":
            c1 = basin_raw["Đồng Tâm"]
            basin_hmaxdb["Đồng Tâm"] = round(-0.3059 * c1["hc"] + 0.6499 * c1["xtr"] + 1169, 0)
            h_tren = basin_hmaxdb["Đồng Tâm"]
            c2 = basin_raw["Mai Hóa"]
            basin_hmaxdb["Mai Hóa"] = 0.3934 * h_tren - 0.0954 * c2["hc"] + 0.1597 * c2["xdr"] + 61.2

        elif selected_basin == "Sông Kiến Giang":
            c1 = basin_raw["Kiến Giang"]
            basin_hmaxdb["Kiến Giang"] = round(0.2242 * c1["hc"] + 0.339 * c1["xtr"] + 925.7, 0)
            h_tren = basin_hmaxdb["Kiến Giang"]
            c2 = basin_raw["Lệ Thủy"]
            basin_hmaxdb["Lệ Thủy"] = 0.1267 * h_tren + 0.3542 * c2["hc"] + 0.1869 * c2["xdr"] + 34

        elif selected_basin == "Sông Bến Hải":
            c_bq = basin_raw["Bến Quan"]
            basin_hmaxdb["Bến Quan"] = 1.8463 * c_bq["hc"] + 1.1474 * c_bq["xtr"] + 7.63
            c_gv = basin_raw["Gia Vòng"]
            basin_hmaxdb["Gia Vòng"] = 1.127028 * c_gv["hc"] + 1.155697 * c_gv["xtr"] + 132.868
            h_tren = basin_hmaxdb["Gia Vòng"]
            c_hl = basin_raw["Hiền Lương"]
            basin_hmaxdb["Hiền Lương"] = 0.144359 * h_tren + 0.364048 * c_hl["hc"] - 0.07845 * c_hl["xtr"] + 0.069222 * c_hl["xdr"] + 18.5648

        elif selected_basin == "Sông Hiếu":
            c1 = basin_raw["Đầu Mầu"]
            basin_hmaxdb["Đầu Mầu"] = 1.050523 * c1["hc"] + 0.506759 * c1["xtr"]
            h_tren = basin_hmaxdb["Đầu Mầu"]
            c2 = basin_raw["Đông Hà"]
            basin_hmaxdb["Đông Hà"] = 0.405748 * h_tren + 0.314155 * c2["hc"] + 0.324489 * c2["xtr"] - 0.01984 * c2["xdr"] - 732.391

        elif selected_basin == "Sông Thạch Hãn":
            c1 = basin_raw["Đakrông"]
            basin_hmaxdb["Đakrông"] = 1.147107 * c1["hc"] + 1.167879 * c1["xtr"] - 126.962
            h_tren = basin_hmaxdb["Đakrông"]
            c2 = basin_raw["Thạch Hãn"]
            basin_hmaxdb["Thạch Hãn"] = 0.283505 * h_tren + 0.27769 * c2["hc"] + 0.136653 * c2["xtr"] + 0.150167 * c2["xdr"] - 517.952

        elif selected_basin == "Sông Ô Lâu":
            c1 = basin_raw["Mỹ Chánh"]
            basin_hmaxdb["Mỹ Chánh"] = 0.8071 * c1["hc"] + 0.6325 * c1["xtr"] + 69.98
            h_tren = basin_hmaxdb["Mỹ Chánh"]
            c2 = basin_raw["Hải Tân"]
            basin_hmaxdb["Hải Tân"] = 0.4287 * h_tren + 0.1229 * c2["hc"] - 0.018 * c2["xtr"] + 0.0291 * c2["xdr"] + 78.6

        # Lưu kết quả
        for st_cfg in stations:
            name = st_cfg["name"]
            hmaxdb = basin_hmaxdb[name]
            hdb = hmaxdb / 100.0
            mn_ht = hmaxdb if st_cfg["type"] == "independent" else basin_hmaxdb[st_cfg["parent"]]

            bd1, bd2, bd3 = st_cfg["bd1"], st_cfg["bd2"], st_cfg["bd3"]
            if hdb >= bd3: cap_bd = "BĐ III"
            elif hdb >= bd2: cap_bd = "BĐ II"
            elif hdb >= bd1: cap_bd = "BĐ I"
            else: cap_bd = "Dưới BĐ I"

            diff1, diff2, diff3 = hdb - bd1, hdb - bd2, hdb - bd3
            comp1 = f"≥ BĐ I: +{diff1:.2f} m" if diff1 >= 0 else f"< BĐ I: {diff1:.2f} m"
            comp2 = f"≥ BĐ II: +{diff2:.2f} m" if diff2 >= 0 else f"< BĐ II: {diff2:.2f} m"
            comp3 = f"≥ BĐ III: +{diff3:.2f} m" if diff3 >= 0 else f"< BĐ III: {diff3:.2f} m"

            st.session_state.all_results[name] = {
                "Lưu vực": selected_basin,
                "Trạm": name,
                "MN Hiện tại (cm)": round(mn_ht, 1),
                "Mực nước dự báo (m)": round(hdb, 2),
                "BĐ I": bd1, "BĐ II": bd2, "BĐ III": bd3,
                "Cấp BĐ": cap_bd,
                "So với BĐ I": comp1, "So với BĐ II": comp2, "So với BĐ III": comp3
            }
        
        st.success(f"✅ Đã tính toán xong dự báo đỉnh lũ cho lưu vực [{selected_basin}]!")
    except Exception as e:
        st.error(f"Lỗi tính toán: {str(e)}")

# --- BẢNG TỔNG HỢP TOÀN BỘ KẾT QUẢ ---
st.markdown("---")
st.subheader("📊 BẢNG TỔNG HỢP KẾT QUẢ TOÀN BỘ CÁC LƯU VỰC SÔNG")

if st.session_state.all_results:
    df_result = pd.DataFrame(list(st.session_state.all_results.values()))
    st.dataframe(df_result, use_container_width=True)

    # Xuất file Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_result.to_excel(writer, sheet_name="TongHopLuuVu", index=False)
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Tải xuống tệp Excel kết quả (.xlsx)",
        data=excel_data,
        file_name="KetQuaDuBaoDinhLu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("💡 Chưa có dữ liệu tính toán. Vui lòng chọn lưu vực và nhấn nút 'Tính toán dự báo' ở trên.")
