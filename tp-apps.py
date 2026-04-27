import streamlit as st
import math
import pandas as pd
import os
import base64

# 페이지 설정
st.set_page_config(page_title="소파블록 충돌 하중 설계 분석 시스템", layout="wide")

# --- 스마트 파일 탐색 함수 (확장자 무관하게 파일 찾기) ---
def find_image_path(file_name):
    """.png, .jpg, .jpeg 상관없이 이름만 맞으면 파일을 찾아주는 스마트 함수"""
    name_only = os.path.splitext(file_name)[0] # 확장자 떼어내기
    
    # 1. 실행 중인 현재 폴더, 2. 파이썬 파일이 있는 폴더 두 군데 모두 검색
    search_dirs = [os.getcwd()]
    try:
        search_dirs.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass # __file__ 이 없는 환경 예외처리
        
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    
    for directory in search_dirs:
        for ext in extensions:
            full_path = os.path.join(directory, name_only + ext)
            if os.path.exists(full_path):
                return full_path # 파일 찾음!
    return None # 끝내 못 찾음

# --- 조용한 이미지 로딩 함수 (화면 출력용) ---
def safe_image(file_name, img_width=350):
    actual_path = find_image_path(file_name)
    if actual_path:
        st.image(actual_path, width=img_width)
    else:
        st.caption(f"⚠️ 이미지를 찾을 수 없습니다: `{os.path.splitext(file_name)[0]}` (같은 폴더에 그림을 넣어주세요)")

# --- 이미지 Base64 인코딩 함수 (보고서 매립용) ---
def get_image_html(file_name, width=350):
    """이미지 파일을 읽어 보고서 안에 완전히 매립하는 함수"""
    actual_path = find_image_path(file_name)
    if actual_path:
        with open(actual_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            ext = actual_path.split('.')[-1].lower()
            mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
            return f'<div class="img-container"><img src="data:{mime};base64,{b64}" width="{width}"/></div>'
    
    return f'<p style="color:red; font-size:13px; font-weight:bold;">[⚠️ 이미지 파일 누락: {os.path.splitext(file_name)[0]} 그림을 찾지 못해 보고서에 포함하지 못했습니다]</p>'

# --- 헤더 섹션 ---
st.title("🏗️ 소파블록 충돌 하중 및 케이슨 벽체 설계 시스템")
st.write("**작성자: 김창보 (다온기술)**")
st.write("**본 시스템은 소파블록의 다양한 거동 특성과 일본 PARI 논문을 근거로 설계 하중 및 벽체 내력을 산정합니다.**")

st.divider()

# --- 사이드바: 설계 변수 입력 ---
st.sidebar.header("📋 설계 변수 입력 (Input)")

# 소파블록 제원 데이터 (표시이름: (계산용중량, ab값))
block_data = {
    "TTP": {"0.5": (0.5, 0.05), "1": (1.0, 0.06), "2": (2.0, 0.08), "3.2": (3.2, 0.09), "4": (4.0, 0.1), "5": (5.0, 0.11), "6.3": (6.3, 0.11), "8": (8.0, 0.12), "10": (10.0, 0.13), "12.5": (12.5, 0.14), "16": (16.0, 0.16), "20": (20.0, 0.17), "25": (25.0, 0.18), "32": (32.0, 0.2), "40": (40.0, 0.21), "50": (50.0, 0.23), "64": (64.0, 0.25)},
    "SEALOCK": {"1": (1.0, 0.07), "2": (2.0, 0.09), "3": (3.0, 0.1), "4": (4.0, 0.11), "5": (5.0, 0.12), "6": (6.0, 0.13), "8": (8.0, 0.14), "10": (10.0, 0.15), "12": (12.0, 0.16), "15": (15.0, 0.17), "20": (20.0, 0.19), "25": (25.0, 0.2), "30": (30.0, 0.22), "40B": (40.0, 0.36), "50B": (50.0, 0.38), "60B": (60.0, 0.41), "70B": (70.0, 0.43), "80B": (80.0, 0.45), "100B": (100.0, 0.49)},
    "DIMPLE": {"1": (1.0, 0.07), "2": (2.0, 0.09), "3": (3.0, 0.1), "4": (4.0, 0.11), "5": (5.0, 0.12), "6": (6.0, 0.13), "8": (8.0, 0.14), "10": (10.0, 0.15), "12": (12.0, 0.16), "15": (15.0, 0.17), "20": (20.0, 0.19), "25": (25.0, 0.2), "30": (30.0, 0.22), "35": (35.0, 0.23), "40": (40.0, 0.24), "50": (50.0, 0.26), "60": (60.0, 0.27), "80": (80.0, 0.3)},
    "DIMPLE K": {"1": (1.0, 0.06), "2": (2.0, 0.07), "3": (3.0, 0.08), "4": (4.0, 0.09), "5": (5.0, 0.1), "6": (6.0, 0.1), "8": (8.0, 0.11), "10": (10.0, 0.12), "12": (12.0, 0.13), "15": (15.0, 0.14), "20": (20.0, 0.15), "25": (25.0, 0.16), "30": (30.0, 0.17), "35": (35.0, 0.18), "40": (40.0, 0.19), "50": (50.0, 0.21), "60": (60.0, 0.22), "80": (80.0, 0.24)}
}

block_type = st.sidebar.selectbox("1. 소파블록 종류 선택", ["TTP", "SEALOCK", "DIMPLE", "DIMPLE K", "기타 (직접입력)"])

if block_type == "기타 (직접입력)":
    m_ton = st.sidebar.number_input("2. 소파블록 중량 m (ton)", min_value=1.0, value=50.0)
    ab_input = st.sidebar.number_input("3. 소파블록선단반경/2 (ab)", min_value=0.01, value=0.23, format="%.2f")
else:
    weight_keys = list(block_data[block_type].keys())
    # 기본적으로 선택하기 편하도록 리스트의 후반부(큰 중량) 인덱스를 디폴트로 지정
    default_index = len(weight_keys) - 2 if len(weight_keys) > 1 else 0
    selected_weight_str = st.sidebar.selectbox("2. 소파블록 형식/중량 (ton)", weight_keys, index=default_index)
    
    m_ton = block_data[block_type][selected_weight_str][0]
    ab_input = block_data[block_type][selected_weight_str][1]
    
    st.sidebar.info(f"👉 **적용 중량:** {m_ton} ton\n\n👉 **소파블록선단반경/2 (ab):** {ab_input} m")

h_water = st.sidebar.number_input("4. 설치 수심 h (m)", min_value=0.0, value=16.0)
h_sig = st.sidebar.number_input("5. 유의 파고 H1/3 (m)", min_value=0.0, value=7.0)
fc = st.sidebar.number_input("6. 콘크리트 압축강도 fck (MPa)", min_value=1.0, value=35.0)

# --- 계산 엔진 및 상수 ---
E = 25000000.0   # 탄성계수 (kN/m2)
nu = 0.2         # 포아슨비
gamma_p = 0.25   # 충돌력 보정계수
ri = 0.15        # 속도 계수
g = 9.81         # 중력가속도
p_ratio = 0.003  # 철근비 (0.3%)

# 1. 속도 및 하중 계산
h_max = 1.8 * h_sig
v_impact = ri * math.sqrt(g * (h_water + h_max))
term1 = (2 * E * math.sqrt(ab_input)) / (3 * (1 - nu**2))
f_max = gamma_p * (term1**0.4) * ((5 * m_ton / 4)**0.6) * (v_impact**1.2)

def get_detailed_vpcd(f_target, fck, ab_val):
    for d_step in range(40, 501):
        d_m = d_step / 100
        d_mm = d_m * 1000
        u0 = 2 * math.pi * (ab_val * 1000)
        up = u0 + math.pi * d_mm
        bd = min(1.5, (1000 / d_mm)**0.25)
        bp = min(1.5, (100 * p_ratio)**(1/3))
        br = 1 + 1 / (1 + 0.25 * u0 / d_mm)
        f_pcd_val = 0.2 * math.sqrt(fck)
        vp = (bd * bp * br * f_pcd_val * up * d_mm / 1.3) / 1000
        if vp >= f_target:
            return {"d_cm": d_m * 100, "up": up, "u0": u0, "bd": bd, "bp": bp, "br": br, "f_pcd": f_pcd_val, "vp": vp}
    return None

res = get_detailed_vpcd(f_max, fc, ab_input)

# --- 0. 검토 결과 요약 ---
st.header("📌 종합 검토 결과 요약")
sum_col1, sum_col2 = st.columns(2)

with sum_col1:
    st.info("**[설계 입력 조건]**")
    st.write(f"- **소파블록 중량:** {m_ton} ton")
    st.write(f"- **설치 수심 (h):** {h_water} m")
    st.write(f"- **유의 파고 (H1/3):** {h_sig} m (최대파고: {h_max:.2f} m)")
    st.write(f"- **소파블록선단반경/2 (ab):** {ab_input}")
    st.write(f"- **콘크리트 압축강도:** {fc} MPa")

with sum_col2:
    if res:
        st.success("**[설계 산정 결과]**")
        st.write(f"- **충돌 속도 (v):** {v_impact:.2f} m/s")
        st.write(f"- **최대 충돌 하중 (Fmax):** {f_max:,.2f} kN")
        st.write(f"- **요구 전단 내력 (Vpcd):** {res['vp']:,.2f} kN")
        st.markdown(f"### 🎯 소요 최소 벽체 두께: {res['d_cm']:.1f} cm")
    else:
        st.error("**[설계 산정 결과]**\n\n하중이 너무 커서 5m 두께 내에서 내력 확보 불가")

st.divider()

# --- 1. 소파블록의 충돌 메커니즘 및 거동 특성 (상세 분석) ---
st.header("1. 소파블록의 충돌 메커니즘 및 거동 특성")
st.markdown("**제공된 삽도 자료를 바탕으로 소파블록이 케이슨 벽체에 가하는 하중의 종류와 거동 특성을 분석합니다.**")

col1, col2 = st.columns(2)

with col1:
    st.subheader("① 수평 충돌 (Horizontal Collision)")
    safe_image("소파블록의 수평충돌.png", 380)
    st.markdown("**블록 전체가 파랑의 유속에 의해 직선으로 가속되어 벽체를 때리는 방식입니다. 운동 에너지가 가장 크며, 본 설계 시스템의 기준 하중(Fmax)을 결정하는 가장 지배적인 모드입니다.**")

    st.subheader("② 락킹 충돌 (Rocking Collision)")
    safe_image("소파블록의 락킹 충돌.png", 380)
    st.markdown("**블록의 하단이 지지된 상태에서 파도에 의해 윗부분이 까딱거리며 부딪히는 현상입니다. 충돌 에너지는 작지만 반복적인 타격으로 벽체 표면에 피로를 유발할 수 있습니다.**")

with col2:
    st.subheader("③ 전락 충돌 (Overturning Collision)")
    safe_image("소파블록의 전락충돌.png", 380)
    st.markdown("**블록이 파도에 의해 뒤집히거나 위에서 아래로 떨어지며 벽체를 타격하는 방식입니다. 불규칙한 타격 지점으로 인해 국부적인 손상을 일으키기 쉽습니다.**")

    st.subheader("④ 정적 하중 및 케이슨 거동 영향")
    safe_image("기대어 있는 소파블록의 수평 하중.png", 350)
    safe_image("케이슨의 락킹(Rocking) 및 활동에 따른 블록의 수평 하중 변화.png", 350)
    st.markdown("**블록이 벽체에 단순히 기대어 있는 상태에서도 수평 하중이 발생합니다. 또한, 케이슨 자체가 파도에 의해 흔들리거나(Rocking) 밀릴 때, 상대 속도 변화로 인해 충돌 하중의 크기가 변동될 수 있음을 유의해야 합니다.**")

st.divider()

# --- 2. 단계별 상세 설계 검토 및 수치 풀이 ---
st.header("2. 단계별 상세 수식 풀이 및 기호 해설")

if res:
    with st.expander("📝 [1단계] 충돌 속도 (v) 산정 공식 및 기호 설명", expanded=True):
        st.markdown("**설계 유의파고($H_{1/3}$)를 최대파고($H_{max}$)로 환산하여 블록의 이동 속도를 구합니다.**")
        st.latex(r"v = 0.15 \times \sqrt{g \times (h + 1.8 \times H_{1/3})}")
        st.markdown("""
        * **$v$** : 소파블록의 수평 충돌 속도 (m/s)
        * **$g$** : 중력 가속도 ($9.81 m/s^2$)
        * **$h$** : 소파블록 설치 수심 (m)
        * **$H_{1/3}$** : 유의 파고 (m).
        """)
        st.markdown(rf"👉 **풀이:** $v = 0.15 \times \sqrt{{{g} \times ({h_water} + 1.8 \times {h_sig})}} = \mathbf{{{v_impact:.2f}\ m/s}}$")

    with st.expander("📝 [2단계] 최대 충돌 하중 (Fmax) 산정 공식 및 기호 설명", expanded=True):
        st.markdown("**Hertz의 탄성 접촉 이론을 바탕으로 하며, 블록 중량($m$)은 반드시 '톤(ton)' 단위를 대입합니다.**")
        st.latex(r"F_{max} = 0.25 \times \left[ \frac{2E \sqrt{a_b}}{3(1 - \nu^2)} \right]^{0.4} \times \left[ \frac{5m}{4} \right]^{0.6} \times v^{1.2}")
        st.markdown("""
        * **$F_{max}$** : 최대 충돌 하중 (kN)
        * **$E$** : 콘크리트 탄성계수 ($2.5 \\times 10^7 kN/m^2$)
        * **$a_b$** : 소파블록선단반경/2 (m)
        * **$\\nu$** : 포아슨비 (0.2)
        * **$m$** : 소파블록 중량 (ton)
        """)
        st.markdown(rf"👉 **수치 대입:** $F_{{max}} = 0.25 \times \left[ \frac{{2 \times 25,000,000 \times \sqrt{{{ab_input}}}}}{{3 \times (1 - 0.2^2)}} \right]^{{0.4}} \times \left[ \frac{{5 \times {m_ton}}}{{4}} \right]^{{0.6}} \times {v_impact:.2f}^{{1.2}}$")
        st.markdown(rf"👉 **산정 결과:** $\mathbf{{{f_max:,.2f}\ kN}}$")

    with st.expander("📝 [3단계] 압압 전단 내력 (Vpcd) 산정 공식 및 기호 설명", expanded=True):
        st.markdown(f"**결정된 벽체 두께 $d = {res['d_cm']:.1f}\ cm$에 대한 전단 저항 능력 검증입니다.**")
        st.latex(r"V_{pcd} = \frac{\beta_d \times \beta_p \times \beta_r \times f_{pcd} \times u_p \times d}{1.3}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(rf"**1. 치수효과계수 ($\beta_d$):** $(1000 / {res['d_cm']*10:.0f})^{{1/4}} = \mathbf{{{res['bd']:.3f}}}$")
            st.write("**- 벽체가 두꺼울수록 내부 결함 확률이 높아져 강도가 저감되는 현상을 보정합니다.**")
            st.markdown(rf"**2. 철근비계수 ($\beta_p$):** $(100 \times 0.003)^{{1/3}} = \mathbf{{{res['bp']:.3f}}}$")
            st.write("**- 철근(0.3% 기준)이 콘크리트 균열을 잡아주는 인장 저항 효과입니다.**")
        with c2:
            st.markdown(rf"**3. 재하면적계수 ($\beta_r$):** $1 + 1 / (1 + 0.25 \times {res['u0']:,.1f} / {res['d_cm']*10:.0f}) = \mathbf{{{res['br']:.3f}}}$")
            st.write("**- 충돌 하중이 좁은 면적에 집중될수록 펀칭 파괴에 취약해지는 것을 보정합니다.**")
            st.markdown(rf"**4. 콘크리트 전단강도 ($f_{{pcd}}$):** $0.2 \times \sqrt{{{fc}}} = \mathbf{{{res['f_pcd']:.3f}}}\ N/mm^2$")
            st.write("**- 압축강도에 비례하여 재료 고유가 가지는 전단 저항 성능입니다.**")
            st.markdown(rf"**5. 파괴면 둘레 ($u_p$):** $u_0 + \pi \times d = \mathbf{{{res['up']:,.1f}}}\ mm$")
        
        st.markdown(rf"👉 **최종 내력 계산:** $({res['bd']:.3f} \times {res['bp']:.3f} \times {res['br']:.3f} \times {res['f_pcd']:.3f} \times {res['up']:,.1f} \times {res['d_cm']*10:.0f}) / 1.3 \div 1000$")
        st.markdown(rf"👉 **검증 결과:** $V_{{pcd}}(\mathbf{{{res['vp']:,.2f}\ kN}}) \geq F_{{max}}(\mathbf{{{f_max:,.2f}\ kN}}) \Rightarrow$ **[안전성 확보]**")

st.divider()

# --- 3. 데이터 분석 및 비교 검토 ---
st.header("3. 데이터 분석 및 비교 검토")
col_graph, col_table = st.columns([1.5, 1])

# UI 테이블용 데이터 및 보고서 HTML 테이블 동시 생성
comp_html_rows = ""
comp_data = []
for r in [0.8, 0.9, 1.0, 1.1, 1.2]:
    s_f = f_max * r
    s_res = get_detailed_vpcd(s_f, fc, ab_input)
    ratio_str = f"{int(r*100)}%"
    force_str = f"{s_f:,.2f}"
    thick_str = f"{s_res['d_cm']:.1f}" if s_res else "초과"
    
    comp_data.append({"하중 비율": ratio_str, "충돌 하중(kN)": force_str, "필요 두께(cm)": thick_str})
    comp_html_rows += f"<tr><td style='text-align:center;'>{ratio_str}</td><td style='text-align:right;'>{force_str} kN</td><td style='text-align:center; font-weight:bold;'>{thick_str}</td></tr>"

with col_graph:
    st.subheader("📊 벽체 두께별 내력(Vpcd) 변화 추이")
    d_list, v_pcd_list = [], []
    for d_s in range(40, 301):
        d_m = d_s / 100
        d_mm = d_m * 1000
        u0_calc = 2 * math.pi * (ab_input * 1000)
        up_calc = u0_calc + math.pi * d_mm
        bd_c = min(1.5, (1000 / d_mm)**0.25)
        bp_c = min(1.5, (100 * p_ratio)**(1/3))
        br_c = 1 + 1 / (1 + 0.25 * u0_calc / d_mm)
        vp_c = (bd_c * bp_c * br_c * (0.2 * math.sqrt(fc)) * up_calc * d_mm / 1.3) / 1000
        d_list.append(d_m)
        v_pcd_list.append(vp_c)
    
    chart_data = pd.DataFrame({'두께(m)': d_list, '내력(kN)': v_pcd_list, '설계하중(kN)': [f_max]*len(d_list)})
    st.line_chart(chart_data, x='두께(m)')

with col_table:
    st.subheader("📋 하중 변화에 따른 필요 두께")
    st.table(pd.DataFrame(comp_data))

st.divider()

# --- 4. 완벽한 양식의 보고서 다운로드 (HTML/PDF용) ---
st.header("📄 설계 검토 보고서 다운로드")
st.write("아래 버튼을 클릭하여 웹 보고서(HTML)를 다운로드하세요. 열린 창에서 **[Ctrl + P]**를 눌러 **'PDF로 저장'**하시면 깨짐 없이 완벽한 보고서가 완성됩니다.")

if res:
    html_report = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; line-height: 1.6; padding: 40px; max-width: 900px; margin: 0 auto; }}
            h1 {{ text-align: center; color: #2c3e50; border-bottom: 3px solid #2c3e50; padding-bottom: 10px; margin-bottom: 30px; }}
            h2 {{ color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 5px; margin-top: 40px; page-break-before: auto; }}
            h3 {{ color: #e67e22; margin-top: 25px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            th, td {{ border: 1px solid #bdc3c7; padding: 12px; }}
            th {{ background-color: #ecf0f1; font-weight: bold; text-align: center; }}
            .highlight {{ color: #c0392b; font-weight: bold; }}
            .formula {{ background-color: #f9f9f9; padding: 15px; border-left: 5px solid #3498db; margin: 15px 0; font-family: 'Courier New', monospace; font-size: 1.1em; }}
            .img-container {{ text-align: center; margin: 20px 0; }}
            .img-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            /* 인쇄 시 여백 및 페이지 넘김 설정 */
            @media print {{
                body {{ padding: 0; max-width: 100%; }}
                h2 {{ page-break-after: avoid; }}
                img {{ max-width: 80% !important; page-break-inside: avoid; }}
                table {{ page-break-inside: avoid; }}
                @page {{ margin: 2cm; }}
            }}
        </style>
    </head>
    <body>
        <h1>소파블록 충돌 하중 및 케이슨 벽체 설계 검토 보고서</h1>
        <p style="text-align: right; font-weight: bold;">작성자: 김창보 (다온기술)</p>
        
        <h2>1. 종합 검토 결과 요약</h2>
        <table>
            <tr><th width="40%">소파블록 중량 (m)</th><td>{m_ton} ton</td></tr>
            <tr><th>설치 수심 (h)</th><td>{h_water} m</td></tr>
            <tr><th>유의 파고 (H1/3)</th><td>{h_sig} m (최대파고: {h_max:.2f} m)</td></tr>
            <tr><th>콘크리트 압축강도 (fck)</th><td>{fc} MPa</td></tr>
            <tr><th>충돌 속도 (v)</th><td class="highlight">{v_impact:.2f} m/s</td></tr>
            <tr><th>최대 충돌 하중 (Fmax)</th><td class="highlight">{f_max:,.2f} kN</td></tr>
            <tr><th>소요 최소 벽체 두께 (d)</th><td class="highlight" style="font-size: 1.3em;">{res['d_cm']:.1f} cm</td></tr>
        </table>

        <h2>2. 소파블록 충돌 메커니즘 및 거동 특성</h2>
        <p>제공된 삽도 자료를 바탕으로 소파블록이 케이슨 벽체에 가하는 하중의 종류와 거동 특성을 분석합니다.</p>
        
        <h3>① 수평 충돌 (Horizontal Collision / Translation)</h3>
        {get_image_html("소파블록의 수평충돌.png")}
        <p>블록 전체가 파랑의 유속에 의해 직선으로 가속되어 벽체를 때리는 방식입니다. 운동 에너지가 가장 크며, 본 설계 시스템의 기준 하중(Fmax)을 결정하는 가장 지배적인 모드입니다.</p>

        <h3>② 락킹 충돌 (Rocking Collision)</h3>
        {get_image_html("소파블록의 락킹 충돌.png")}
        <p>블록의 하단이 지지된 상태에서 파도에 의해 윗부분이 까딱거리며 부딪히는 현상입니다. 충돌 에너지는 작지만 반복적인 타격으로 벽체 표면에 피로를 유발할 수 있습니다.</p>

        <h3>③ 전락 충돌 (Overturning Collision)</h3>
        {get_image_html("소파블록의 전락충돌.png")}
        <p>블록이 파도에 의해 뒤집히거나 위에서 아래로 떨어지며 벽체를 타격하는 방식입니다. 불규칙한 타격 지점으로 인해 국부적인 손상을 일으키기 쉽습니다.</p>

        <h3>④ 정적 하중 및 케이슨 거동 영향</h3>
        {get_image_html("기대어 있는 소파블록의 수평 하중.png")}
        {get_image_html("케이슨의 락킹(Rocking) 및 활동에 따른 블록의 수평 하중 변화.png")}
        <p>블록이 벽체에 단순히 기대어 있는 상태에서도 수평 하중이 발생합니다. 또한, 케이슨 자체가 파도에 의해 흔들리거나(Rocking) 밀릴 때, 상대 속도 변화로 인해 충돌 하중의 크기가 변동될 수 있음을 유의해야 합니다.</p>

        <h2>3. 단계별 상세 수식 풀이 및 설계 검증</h2>
        
        <h3>[1단계] 충돌 속도 (v) 산정</h3>
        <p>설계 유의파고를 최대파고로 환산하여 속도를 구합니다.</p>
        <div class="formula">v = 0.15 × √(g × (h + 1.8 × H1/3))</div>
        <p>👉 풀이: v = 0.15 × √({g} × ({h_water} + 1.8 × {h_sig})) = <b>{v_impact:.2f} m/s</b></p>

        <h3>[2단계] 최대 충돌 하중 (Fmax) 산정</h3>
        <p>Hertz의 탄성 접촉 이론을 바탕으로 하며, 블록 중량은 톤(ton) 단위를 대입합니다.</p>
        <div class="formula">Fmax = 0.25 × [ 2E√(ab) / 3(1-v^2) ]^0.4 × [ 5m / 4 ]^0.6 × v^1.2</div>
        <p>👉 수치 대입: 0.25 × [ 2×25,000,000×√{ab_input} / 3(1-0.2^2) ]^0.4 × [ 5×{m_ton}/4 ]^0.6 × {v_impact:.2f}^1.2</p>
        <p>👉 산정 결과: <b>{f_max:,.2f} kN</b></p>

        <h3>[3단계] 압압 전단 내력 (Vpcd) 검증</h3>
        <p>결정된 벽체 두께 d = {res['d_cm']:.1f} cm 에 대한 전단 저항 능력 검증입니다.</p>
        <div class="formula">Vpcd = (βd × βp × βr × fpcd × up × d) / 1.3</div>
        <ul>
            <li>치수효과계수 (βd): {res['bd']:.3f} (두께 증가 시 강도 저감 보정)</li>
            <li>철근비계수 (βp): {res['bp']:.3f} (철근의 인장 저항 효과)</li>
            <li>재하면적계수 (βr): {res['br']:.3f} (하중 집중도 보정)</li>
            <li>콘크리트 전단강도 (fpcd): {res['f_pcd']:.3f} N/mm2</li>
            <li>파괴면 둘레 (up): {res['up']:,.1f} mm</li>
        </ul>
        <p>👉 최종 내력 계산: ({res['bd']:.3f} × {res['bp']:.3f} × {res['br']:.3f} × {res['f_pcd']:.3f} × {res['up']:,.1f} × {res['d_cm']*10:.0f}) / 1.3 / 1000</p>
        <p class="highlight">👉 검증 결과: Vpcd ({res['vp']:,.2f} kN) ≥ Fmax ({f_max:,.2f} kN) ⇒ [안전성 확보]</p>

        <h2>4. 데이터 분석 및 비교 검토</h2>
        <p>설계 하중(Fmax)의 증감에 따른 필요 벽체 두께를 분석한 결과입니다.</p>
        <table>
            <tr>
                <th>하중 변동 비율</th>
                <th>예상 충돌 하중</th>
                <th>소요 최소 벽체 두께</th>
            </tr>
            {comp_html_rows}
        </table>
        <p>※ 현장 여건(태풍, 이상 파랑 등)에 의해 하중이 10~20% 증가할 경우를 대비하여 설계 마진을 검토하시기 바랍니다.</p>
    </body>
    </html>
    """
    
    # HTML MIME 타입으로 변경 (.html 확장자)
    b64 = base64.b64encode(html_report.encode('utf-8')).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="소파블록_설계검토보고서.html" style="display: inline-block; padding: 15px 30px; background-color: #2e86de; color: white; text-align: center; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">📥 웹 보고서(HTML) 다운로드 (클릭)</a>'
    st.markdown(href, unsafe_allow_html=True)
    st.info("💡 **이용 팁:** 다운로드된 `.html` 파일을 더블클릭하여 크롬/엣지 브라우저로 엽니다. 그림과 표가 모두 정상적으로 나오는지 확인한 후, **마우스 우클릭 -> [인쇄] -> 대상에서 [PDF로 저장]**을 선택하시면 보고서용 PDF가 완벽하게 만들어집니다.")
