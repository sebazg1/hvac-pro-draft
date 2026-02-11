import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import io
import base64

# --- 1. CONFIG ---
st.set_page_config(layout="wide", page_title="HVAC Pro-Draft v8.1", page_icon="📐", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: 700; }
    .stImage { background-color: white !important; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

if 'collection' not in st.session_state: st.session_state.collection = []
if 'auto_id' not in st.session_state: st.session_state.auto_id = 1

# --- 2. COMPACT DRAWING ENGINE ---
def render_part(w1, h1, w2, h2, length, c_t, c_b, ID, int_val, h_mode, v_mode, off_dir, off_val):
    # Reduced height (5) to keep the aspect ratio tight for 4 rows
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    LABEL_SIZE = 11

    # Offset Logic
    if off_dir == "Left": x_off_b, x_off_t = off_val, 0
    elif off_dir == "Right": x_off_b, x_off_t = 0, off_val
    else:
        max_w = max(w1, w2)
        if h_mode == "Left Side 90°": x_off_t, x_off_b = 0, 0
        elif h_mode == "Right Side 90°": x_off_t, x_off_b = max_w - w1, max_w - w2
        else: x_off_t, x_off_b = (max_w - w1) / 2, (max_w - w2) / 2

    # Draw Body
    verts = [(x_off_b, 0), (x_off_b + w2, 0), (x_off_t + w1, length), (x_off_t, length)]
    ax.add_patch(Polygon(verts, closed=True, fill=False, linewidth=2, edgecolor='black'))

    # Dimensions
    ax.text(x_off_t + w1/2, length + 40, f"{int(w1)}x{int(h1)}", ha="center", fontsize=LABEL_SIZE, fontweight='bold')
    ax.text(x_off_b + w2/2, -70, f"{int(w2)}x{int(h2)}", ha="center", fontsize=LABEL_SIZE, fontweight='bold')
    
    # Red Offset Line
    if off_val > 0:
        if off_dir == "Left":
            ax.plot([x_off_t, x_off_t, x_off_b], [length, -100, -100], color='#dc2626', linestyle='--', linewidth=1)
        elif off_dir == "Right":
            ax.plot([x_off_t + w1, x_off_t + w1, x_off_b + w2], [length, -100, -100], color='#dc2626', linestyle='--', linewidth=1)

    # Center Stamp
    v_txt = "FOT" if v_mode == "Flat on Top" else "FOB" if v_mode == "Flat on Bottom" else "ET"
    stamp = f"ID-{int(ID)} | {v_txt}"
    if int_val != "None": stamp += f" | INT"
    ax.text((x_off_t+w1/2+x_off_b+w2/2)/2, length/2, stamp, ha='center', fontsize=LABEL_SIZE-1, fontweight='bold')

    # Side Length
    reach = max(x_off_t + w1, x_off_b + w2)
    ax.plot([reach + 50, reach + 50], [0, length], color='black', linewidth=1)
    ax.text(reach + 70, length/2, f"L:{int(length)}", rotation=90, va="center", fontsize=LABEL_SIZE-1)
    
    ax.set_aspect('equal')
    ax.axis('off')
    # Tighter vertical limits to prevent whitespace
    ax.set_ylim(-150, length + 180)
    return fig

# --- 3. UI ---
st.title("📐 HVAC Pro-Draft")
proj_name = st.text_input("Project Name", value="New Project")

t_edit, t_list = st.tabs(["🏗️ Build", "📋 Review Sheet"])

with t_edit:
    with st.expander("⚙️ Settings", expanded=True):
        w1, h1 = st.number_input("W1", value=450), st.number_input("H1", value=250)
        w2, h2 = st.number_input("W2", value=450), st.number_input("H2", value=250)
        largo = st.number_input("Length", value=1400)
        s_dir = st.radio("Shift", ["None", "Left", "Right"], horizontal=True)
        s_val = st.number_input("Shift Amount", value=0)
        h_al = st.selectbox("Alignment", ["Equal Taper", "Left Side 90°", "Right Side 90°"])
        v_al = st.selectbox("Vertical Align", ["Equal Taper", "Flat on Top", "Flat on Bottom"])
        c_t = st.selectbox("Top Conn", ["TDF", "SLIDE", "R/E", "None"])
        c_b = st.selectbox("Bottom Conn", ["TDF", "SLIDE", "R/E", "None"])
        i_val = st.selectbox("Int", ["None", "25", "50", "100"])

    fig = render_part(w1, h1, w2, h2, largo, c_t, c_b, st.session_state.auto_id, i_val, h_al, v_al, s_dir, s_val)
    st.pyplot(fig, use_container_width=True)
    
    if st.button("➕ ADD PIECE"):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', dpi=140)
        st.session_state.collection.append(buf.getvalue())
        st.session_state.auto_id += 1
        st.rerun()

with t_list:
    if st.session_state.collection:
        # UPDATED PRINT LOGIC
        if st.button("🖨️ PRINT REPORT (FORCE 1 PAGE)"):
            imgs = [base64.b64encode(i).decode() for i in st.session_state.collection]
            
            # This HTML creates a container that is exactly A4 height.
            # We set each image to 23% height (23% * 4 rows = 92%), leaving room for the title.
            html_content = f"""
            <div style="width: 210mm; height: 290mm; margin: 0; padding: 0; font-family: sans-serif;">
                <h3 style="text-align: center; margin: 5px;">{proj_name}</h3>
                <div style="display: flex; flex-wrap: wrap; width: 100%;">
                    {''.join([f'<div style="width: 31%; height: 23%; border: 1px solid #ccc; margin: 0.5%; box-sizing: border-box;"><img src="data:image/png;base64,{img}" style="width: 100%; height: 100%; object-fit: contain;"></div>' for img in imgs])}
                </div>
            </div>
            <script>window.print();</script>
            """
            st.components.v1.html(html_content, height=0)

        cols = st.columns(3)
        for i, img in enumerate(st.session_state.collection):
            cols[i % 3].image(img)
            
        if st.button("🗑️ RESET ALL"):
            st.session_state.collection = []
            st.session_state.auto_id = 1
            st.rerun()
