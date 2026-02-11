import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, RegularPolygon, Rectangle
import io
import base64

# --- 1. CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="HVAC Pro-Draft v8.1", page_icon="📐", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: 700; }
    .stImage { background-color: white !important; border: 1px solid #ddd; border-radius: 8px; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

if 'collection' not in st.session_state: st.session_state.collection = []
if 'auto_id' not in st.session_state: st.session_state.auto_id = 1

# --- 2. RESTORED DRAWING ENGINE ---
def render_part(w_t, h_t, w_b, h_b, L, c_t, c_b, ID, val, h_mode, off_dir, off_val):
    fig, ax = plt.subplots(figsize=(8, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    LABEL_SIZE, ID_SIZE = 14, 22

    # Coordinate Calculation
    if off_dir == "Left": x_off_b, x_off_t = off_val, 0
    elif off_dir == "Right": x_off_b, x_off_t = 0, off_val
    else:
        max_w = max(w_t, w_b)
        if h_mode == "Left Side 90°": x_off_t, x_off_b = 0, 0
        elif h_mode == "Right Side 90°": x_off_t, x_off_b = max_w - w_t, max_w - w_b
        else: x_off_t, x_off_b = (max_w - w_t) / 2, (max_w - w_b) / 2

    # Draw Duct Body
    verts = [(x_off_b, 0), (x_off_b + w_b, 0), (x_off_t + w_t, L), (x_off_t, L)]
    ax.add_patch(Polygon(verts, closed=True, fill=False, linewidth=3, edgecolor='black'))

    # RED OFFSET LINES (Restored)
    if off_val > 0:
        accent = '#dc2626' # Red
        if off_dir == "Left":
            ax.plot([x_off_t, x_off_t, x_off_b], [L, -120, -120], color=accent, linestyle='--', linewidth=1.5)
            ax.text((x_off_t + x_off_b)/2, -145, f"Offset: {int(off_val)}", color=accent, ha='center', fontweight='bold', fontsize=LABEL_SIZE)
        elif off_dir == "Right":
            ax.plot([x_off_t + w_t, x_off_t + w_t, x_off_b + w_b], [L, -120, -120], color=accent, linestyle='--', linewidth=1.5)
            ax.text((x_off_t + w_t + x_off_b + w_b)/2, -145, f"Offset: {int(off_val)}", color=accent, ha='center', fontweight='bold', fontsize=LABEL_SIZE)

    # Labels
    ax.text(x_off_t + w_t/2, L + 60, f"{int(w_t)} x {int(h_t)} ({c_t})", ha="center", fontsize=LABEL_SIZE, fontweight='bold', color='black')
    ax.text(x_off_b + w_b/2, -80, f"{int(w_b)} x {int(h_b)} ({c_b})", ha="center", fontsize=LABEL_SIZE, fontweight='bold', color='black')
    
    max_reach = max(x_off_t + w_t, x_off_b + w_b)
    ax.plot([max_reach + 100, max_reach + 100], [0, L], color='black', linewidth=2)
    ax.text(max_reach + 130, L/2, f"L: {int(L)}", rotation=90, va="center", fontsize=LABEL_SIZE, fontweight='bold')
    ax.text(max_reach, L + 150, f"ID-{int(ID)}", fontsize=ID_SIZE, color='#ea580c', fontweight="black", ha="right")
    
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_ylim(-300, L + 350)
    return fig

# --- 3. TABS INTERFACE ---
st.title("📐 HVAC Pro-Draft")
proj_name = st.text_input("Project Name", value="New Ventilation Project")

tab_edit, tab_view = st.tabs(["🏗️ Build Piece", "📋 Review Sheet"])

with tab_edit:
    with st.expander("⚙️ Settings", expanded=True):
        c1, c2 = st.columns(2)
        w_top, h_top = c1.number_input("W1", value=450), c2.number_input("H1", value=250)
        w_bottom, h_bottom = c1.number_input("W2", value=450), c2.number_input("H2", value=250)
        length = st.number_input("Length (L)", value=1400)
        off_dir = st.radio("Shift", ["None", "Left", "Right"], horizontal=True)
        off_val = st.number_input("Shift Amount", value=0)
        h_taper = st.selectbox("Alignment", ["Equal Taper", "Left Side 90°", "Right Side 90°"])
        conn_top = st.selectbox("Top Conn", ["TDF", "SLIDE", "R/E", "None"])
        conn_bottom = st.selectbox("Bottom Conn", ["TDF", "SLIDE", "R/E", "None"])
        inner_val = st.selectbox("Int", ["50", "100", "None"])

    fig = render_part(w_top, h_top, w_bottom, h_bottom, length, conn_top, conn_bottom, st.session_state.auto_id, inner_val, h_taper, off_dir, off_val)
    st.pyplot(fig, use_container_width=True)
    
    if st.button("➕ Add to Project", type="primary"):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', dpi=150)
        st.session_state.collection.append(buf.getvalue())
        st.session_state.auto_id += 1
        st.rerun()

with tab_view:
    st.subheader(f"Project: {proj_name}")
    if st.session_state.collection:
        # PRINT BUTTON (Restored)
        if st.button("🖨️ Print / Save PDF", type="secondary"):
            encoded = [base64.b64encode(img).decode() for img in st.session_state.collection]
            html = f"<div>{''.join([f'<img src=\"data:image/png;base64,{img}\" style=\"width:100%;margin-bottom:20px;\">' for img in encoded])}</div><script>window.print();</script>"
            st.components.v1.html(html, height=0)

        for i, img in enumerate(st.session_state.collection):
            st.image(img)
        
        if st.button("🗑️ Clear All"):
            st.session_state.collection = []
            st.rerun()
    else:
        st.info("No pieces added yet.")
