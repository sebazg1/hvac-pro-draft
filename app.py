import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, RegularPolygon, Rectangle
import io
import base64

# --- 1. MOBILE-OPTIMIZED PAGE CONFIG ---
st.set_page_config(
    layout="wide", 
    page_title="HVAC Pro-Draft v8.1", 
    page_icon="📐",
    initial_sidebar_state="collapsed"
)

# Professional CSS for Mobile
st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: 700; }
    [data-testid="stMetricValue"] { font-size: 1.5rem; }
    /* Force white background on drawings for visibility */
    .stImage { background-color: white !important; border-radius: 8px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Link PWA Manifest
st.markdown('<link rel="manifest" href="manifest.json">', unsafe_allow_html=True)

if 'collection' not in st.session_state: st.session_state.collection = []
if 'auto_id' not in st.session_state: st.session_state.auto_id = 1

# --- 2. DRAWING ENGINE (Visibility Fix) ---
def render_part(w_t, h_t, w_b, h_b, L, c_t, c_b, ID, val, h_mode, off_dir, off_val):
    # Use a slightly taller figure for mobile verticality
    fig, ax = plt.subplots(figsize=(8, 10)) 
    fig.patch.set_facecolor('white') # Force background white
    ax.set_facecolor('white')
    
    # Increase font sizes globally for mobile visibility
    TITLE_SIZE = 16
    LABEL_SIZE = 14
    ID_SIZE = 22

    # Calculate Coordinates
    if off_dir == "Left": x_off_b, x_off_t = off_val, 0
    elif off_dir == "Right": x_off_b, x_off_t = 0, off_val
    else:
        max_w = max(w_t, w_b)
        if h_mode == "Left Side 90°": x_off_t, x_off_b = 0, 0
        elif h_mode == "Right Side 90°": x_off_t, x_off_b = max_w - w_t, max_w - w_b
        else: x_off_t, x_off_b = (max_w - w_t) / 2, (max_w - w_b) / 2

    # Draw Duct
    verts = [(x_off_b, 0), (x_off_b + w_b, 0), (x_off_t + w_t, L), (x_off_t, L)]
    ax.add_patch(Polygon(verts, closed=True, fill=False, linewidth=3, edgecolor='black'))

    # Dimensions (Bold & Black for high contrast)
    ax.text(x_off_t + w_t/2, L + 60, f"{int(w_t)} x {int(h_t)}", ha="center", fontsize=LABEL_SIZE, fontweight='bold', color='black')
    ax.text(x_off_b + w_b/2, -80, f"{int(w_b)} x {int(h_b)}", ha="center", fontsize=LABEL_SIZE, fontweight='bold', color='black')
    
    # Vertical Length
    max_reach = max(x_off_t + w_t, x_off_b + w_b)
    ax.plot([max_reach + 100, max_reach + 100], [0, L], color='black', linewidth=2)
    ax.text(max_reach + 130, L/2, f"L: {int(L)}", rotation=90, va="center", fontsize=LABEL_SIZE, fontweight='bold')

    # ID Stamp (Big and Bright)
    ax.text(max_reach, L + 150, f"ID-{int(ID)}", fontsize=ID_SIZE, color='#ea580c', fontweight="black", ha="right")
    
    ax.set_aspect('equal')
    ax.axis('off')
    # Extra padding to ensure text isn't cut off on small screens
    ax.set_ylim(-250, L + 300)
    ax.set_xlim(-150, max_reach + 300)
    return fig

# --- 3. HEADER & TABS ---
st.title("📐 HVAC Pro-Draft")
proj_name = st.text_input("Project Name", value="New Ventilation Project")

tab_edit, tab_view = st.tabs(["🏗️ Build Piece", "📋 Review Sheet"])

with tab_edit:
    # Use Sidebar for inputs (Collapsible)
    with st.expander("⚙️ Adjust Dimensions", expanded=True):
        c1, c2 = st.columns(2)
        w_top = c1.number_input("W1 (Top)", value=450)
        h_top = c2.number_input("H1 (Top)", value=250)
        w_bottom = c1.number_input("W2 (Bottom)", value=450)
        h_bottom = c2.number_input("H2 (Bottom)", value=250)
        length = st.number_input("Length (L)", value=1400)
        off_dir = st.radio("Shift", ["None", "Left", "Right"], horizontal=True)
        off_val = st.number_input("Shift Amount", value=0)
        h_taper = st.selectbox("Alignment", ["Equal Taper", "Left Side 90°", "Right Side 90°"])
        conn_top = st.selectbox("Connection Top", ["TDF", "SLIDE", "None"])
        conn_bottom = st.selectbox("Connection Bottom", ["TDF", "SLIDE", "None"])
        inner_val = st.selectbox("Int Value", ["50", "100", "None"])

    # Drawing Area
    fig = render_part(w_top, h_top, w_bottom, h_bottom, length, conn_top, conn_bottom, st.session_state.auto_id, inner_val, h_taper, off_dir, off_val)
    st.pyplot(fig, use_container_width=True)
    
    if st.button("➕ Add to Project", type="primary"):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', dpi=150)
        st.session_state.collection.append(buf.getvalue())
        st.session_state.auto_id += 1
        st.rerun()

with tab_view:
    st.metric("Pieces Collected", len(st.session_state.collection))
    if st.session_state.collection:
        for i, img in enumerate(st.session_state.collection):
            st.image(img, caption=f"Piece ID: {i+1}")
        
        if st.button("🗑️ Clear All"):
            st.session_state.collection = []
            st.session_state.auto_id = 1
            st.rerun()
    else:
        st.info("No pieces added yet.")
