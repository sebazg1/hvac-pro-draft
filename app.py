import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import io
import base64

# --- 1. CONFIG ---
st.set_page_config(layout="wide", page_title="HVAC Pro-Draft v8.1", page_icon="📐", initial_sidebar_state="collapsed")

# Simple, clean CSS for mobile view
st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: 700; }
    .stImage { background-color: white !important; border: 1px solid #eee; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

if 'collection' not in st.session_state: st.session_state.collection = []
if 'auto_id' not in st.session_state: st.session_state.auto_id = 1

# --- 2. DRAWING ENGINE ---
def render_part(w1, h1, w2, h2, length, c_t, c_b, ID, int_val, h_mode, v_mode, off_dir, off_val):
    # Fixed figure size to ensure proportions stay consistent
    fig, ax = plt.subplots(figsize=(5, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    LABEL_SIZE = 12

    # Calculations for Offset
    if off_dir == "Left": x_off_b, x_off_t = off_val, 0
    elif off_dir == "Right": x_off_b, x_off_t = 0, off_val
    else:
        max_w = max(w1, w2)
        if h_mode == "Left Side 90°": x_off_t, x_off_b = 0, 0
        elif h_mode == "Right Side 90°": x_off_t, x_off_b = max_w - w1, max_w - w2
        else: x_off_t, x_off_b = (max_w - w1) / 2, (max_w - w2) / 2

    # Draw Shape
    verts = [(x_off_b, 0), (x_off_b + w2, 0), (x_off_t + w1, length), (x_off_t, length)]
    ax.add_patch(Polygon(verts, closed=True, fill=False, linewidth=2, edgecolor='black'))

    # Dimensions
    ax.text(x_off_t + w1/2, length + 40, f"{int(w1)}x{int(h1)}", ha="center", fontsize=LABEL_SIZE, fontweight='bold')
    ax.text(x_off_b + w2/2, -60, f"{int(w2)}x{int(h2)}", ha="center", fontsize=LABEL_SIZE, fontweight='bold')
    
    # Red Offset Line
    if off_val > 0:
        accent = '#dc2626'
        if off_dir == "Left":
            ax.plot([x_off_t, x_off_t, x_off_b], [length, -90, -90], color=accent, linestyle='--', linewidth=1)
        elif off_dir == "Right":
            ax.plot([x_off_t + w1, x_off_t + w1, x_off_b + w2], [length, -90, -90], color=accent, linestyle='--', linewidth=1)

    # Info Center Label
    v_txt = "FOT" if v_mode == "Flat on Top" else "FOB" if v_mode == "Flat on Bottom" else "ET"
    info = f"ID-{int(ID)} | {v_txt} | {'INT' if int_val != 'None' else ''}"
    ax.text((x_off_t+w1/2+x_off_b+w2/2)/2, length/2, info, ha='center', fontsize=LABEL_SIZE-1, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    # Length Label
    reach = max(x_off_t + w1, x_off_b + w2)
    ax.plot([reach + 50, reach + 50], [0, length], color='black', linewidth=1)
    ax.text(reach + 70, length/2, f"L:{int(length)}", rotation=90, va="center", fontsize=LABEL_SIZE-1)
    
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_ylim(-180, length + 200)
    return fig

# --- 3. MOBILE UI ---
st.title("📐 HVAC Pro-Draft")

t_edit, t_list = st.tabs(["🏗️ Build", "📋 Review Sheet"])

with t_edit:
    with st.expander("⚙️ Settings", expanded=True):
        w1 = st.number_input("W1", value=450)
        h1 = st.number_input("H1", value=250)
        w2 = st.number_input("W2", value=450)
        h2 = st.number_input("H2", value=250)
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
        fig.savefig(buf, format="png", bbox_inches='tight', dpi=150)
        st.session_state.collection.append(buf.getvalue())
        st.session_state.auto_id += 1
        st.rerun()

with t_list:
    if st.session_state.collection:
        # THE PRINT BUTTON: Uses a simple 3-column table which is very stable for PDF
        if st.button("🖨️ PRINT REPORT (A4)"):
            imgs = [base64.b64encode(i).decode() for i in st.session_state.collection]
            
            # Simple HTML grid that forces 3 items per row
            html_content = f"""
            <div style="width: 100%; font-family: sans-serif;">
                <h2 style="text-align: center;">{proj_name if 'proj_name' in locals() else 'HVAC Project'}</h2>
                <div style="display: flex; flex-wrap: wrap; justify-content: flex-start;">
                    {''.join([f'<div style="width: 31%; border: 1px solid #ccc; margin: 1%;"><img src="data:image/png;base64,{img}" style="width: 100%;"></div>' for img in imgs])}
                </div>
            </div>
            <script>window.print();</script>
            """
            st.components.v1.html(html_content, height=0)

        # App Display
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.collection):
            cols[i % 3].image(img)
            
        if st.button("🗑️ RESET ALL"):
            st.session_state.collection = []
            st.session_state.auto_id = 1
            st.rerun()
