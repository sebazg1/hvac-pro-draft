import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, RegularPolygon, Rectangle
import io
import base64
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="HVAC Pro-Draft v8.1", page_icon="📐")

# Professional Styling
st.markdown("""
    <style>
    section[data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
    .stButton>button { border-radius: 6px; font-weight: 600; }
    .stMetric { background-color: white; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0; }
    .stImage { border: 1px solid #e2e8f0; border-radius: 4px; padding: 5px; background: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'collection' not in st.session_state: st.session_state.collection = []
if 'auto_id' not in st.session_state: st.session_state.auto_id = 1

# --- HEADER ---
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    proj_name = st.text_input("Project Name", value="New Ventilation Project")
with h_col2:
    st.metric("Sheet Capacity", f"{len(st.session_state.collection)} / 20")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("🛠️ Part Settings")
    
    with st.container(border=True):
        st.subheader("Dimensions (mm)")
        w_top = st.number_input("Ancho superior (W1)", min_value=1, value=450)
        h_top = st.number_input("Alto superior (H1)", min_value=1, value=250)
        w_bottom = st.number_input("Ancho inferior (W2)", min_value=1, value=450)
        h_bottom = st.number_input("Alto inferior (H2)", min_value=1, value=250)
        length = st.number_input("Largo (L)", min_value=1, value=1400)

    with st.expander("↔️ Offset / Shift", expanded=True):
        off_dir = st.radio("Shift Direction", ["None", "Left", "Right"], horizontal=True)
        off_val = st.number_input("Shift Value (mm)", min_value=0, value=0)

    # Taper Logic
    is_h_taper = (w_top != w_bottom) and (off_dir == "None")
    is_v_taper = (h_top != h_bottom)

    if is_h_taper or is_v_taper:
        with st.expander("📐 Alignment"):
            h_taper = st.radio("Horizontal", ["Equal Taper", "Left Side 90°", "Right Side 90°"]) if is_h_taper else "Equal Taper"
            v_taper = st.radio("Vertical Label", ["Equal Taper (ET)", "Top 90° (FOT)", "Bottom 90° (FOB)"]) if is_v_taper else None
    else:
        h_taper, v_taper = "Equal Taper", None

    with st.expander("🏷️ Identification"):
        st.session_state.auto_id = st.number_input("Part ID", value=st.session_state.auto_id)
        inner_val = st.selectbox("Valor interior (int)", ["50", "100", "25", "None"])
        # Standard Connection Dropdowns
        conn_list = ["TDF", "SLIDE", "R/E", "None"]
        conn_top = st.selectbox("Top Connection", conn_list)
        conn_bottom = st.selectbox("Bottom Connection", conn_list)

    if st.button("🗑️ Reset All", type="secondary", use_container_width=True):
        st.session_state.collection = []
        st.rerun()

# --- DRAWING ENGINE ---
def render_part(w_t, h_t, w_b, h_b, L, c_t, c_b, ID, val, f_size, h_mode, v_mode, off_dir, off_val, is_print=False):
    fig, ax = plt.subplots(figsize=(f_size, f_size))
    ax.set_facecolor('white')
    txt_size = 8 if is_print else 10
    
    # Calculate Coordinate Offsets
    if off_dir == "Left":
        x_off_b, x_off_t = off_val, 0
    elif off_dir == "Right":
        x_off_b, x_off_t = 0, off_val
    else:
        max_w = max(w_t, w_b)
        if w_t != w_b:
            if h_mode == "Left Side 90°": x_off_t, x_off_b = 0, 0
            elif h_mode == "Right Side 90°": x_off_t, x_off_b = max_w - w_t, max_w - w_b
            else: x_off_t, x_off_b = (max_w - w_t) / 2, (max_w - w_b) / 2
        else: x_off_t, x_off_b = 0, 0
    
    # Main Duct Geometry
    verts = [(x_off_b, 0), (x_off_b + w_b, 0), (x_off_t + w_t, L), (x_off_t, L)]
    ax.add_patch(Polygon(verts, closed=True, fill=False, linewidth=2, edgecolor='black', zorder=3))
    
    # 90° Corner Symbols
    sq_size = 40
    if off_dir == "None":
        if h_mode == "Left Side 90°" or (w_t == w_b and h_mode == "Equal Taper"):
            ax.add_patch(Rectangle((x_off_b, 0), sq_size, sq_size, fill=False, color='black', linewidth=1))
        if h_mode == "Right Side 90°" or (w_t == w_b and h_mode == "Equal Taper"):
            ax.add_patch(Rectangle((x_off_b + w_b - sq_size, 0), sq_size, sq_size, fill=False, color='black', linewidth=1))

    # Offset Plumb Line Path (Dotted Red Line)
    if off_val > 0:
        accent = '#dc2626'
        if off_dir == "Left":
            ax.plot([x_off_t, x_off_t, x_off_b], [L, -120, -120], color=accent, linestyle='--', linewidth=1.2)
            ax.text((x_off_t + x_off_b)/2, -145, f"{int(off_val)}", color=accent, ha='center', fontweight='bold', fontsize=txt_size)
        elif off_dir == "Right":
            ax.plot([x_off_t + w_t, x_off_t + w_t, x_off_b + w_b], [L, -120, -120], color=accent, linestyle='--', linewidth=1.2)
            ax.text((x_off_t + w_t + x_off_b + w_b)/2, -145, f"{int(off_val)}", color=accent, ha='center', fontweight='bold', fontsize=txt_size)

    # Simplified Dimension Labels
    ax.text(x_off_t + w_t/2, L + 50, f"{int(w_t)} x {int(h_t)}", ha="center", va="bottom", fontsize=txt_size, fontweight='bold')
    ax.text(x_off_b + w_b/2, -50, f"{int(w_b)} x {int(h_b)}", ha="center", va="top", fontsize=txt_size, fontweight='bold')
    
    # Vertical Length Dimension Line
    max_reach = max(x_off_t + w_t, x_off_b + w_b)
    dim_x = max_reach + 180
    ax.plot([max_reach + 80, dim_x + 40], [0, 0], color='#94a3b8', linewidth=0.8)
    ax.plot([max_reach + 80, dim_x + 40], [L, L], color='#94a3b8', linewidth=0.8)
    ax.plot([dim_x, dim_x], [0, L], color='black', linewidth=1.5)
    ax.text(dim_x + 15, L/2, f"{int(L)}", rotation=90, va="center", ha="left", fontsize=txt_size, fontweight='bold')
    
    # Internal Triangle
    cx = (x_off_t + w_t/2 + x_off_b + w_b/2) / 2
    if val != "None":
        ty = L * 0.72
        ax.add_patch(RegularPolygon((cx, ty), 3, radius=60, orientation=0, fill=False, linewidth=1.2))
        ax.text(cx, ty-5, val, ha="center", va="center", fontsize=txt_size-1, fontweight='bold')
        ax.text(cx, ty-80, "int", ha="center", va="top", fontsize=txt_size-1)
    
    if v_mode:
        label = v_mode.split('(')[-1].replace(')', '')
        ax.text(cx, L*0.5, label, ha="center", fontsize=txt_size+2, fontweight='bold', color='#64748b')

    # Connection and ID Stamps
    if c_t != "None": ax.text(x_off_t - 25, L, c_t, fontsize=txt_size-1, ha='right', fontweight='bold')
    if c_b != "None": ax.text(x_off_b - 25, 0, c_b, fontsize=txt_size-1, ha='right', fontweight='bold')
    ax.text(max_reach, L * 0.95, f"ID-{int(ID)}", fontsize=16, color='#ea580c', fontweight="black", ha="right")
    
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_ylim(-350, L + 250)
    return fig

# --- WORKSPACE ---
col_ed, col_prev = st.columns([1, 1])

with col_ed:
    st.subheader("🎨 Editor")
    fig = render_part(w_top, h_top, w_bottom, h_bottom, length, conn_top, conn_bottom, st.session_state.auto_id, inner_val, 7, h_taper, v_taper, off_dir, off_val)
    st.pyplot(fig)
    
    ed_b1, ed_b2 = st.columns(2)
    with ed_b1:
        if st.button("➕ Add Piece", type="primary", use_container_width=True):
            if len(st.session_state.collection) < 20:
                buf = io.BytesIO()
                render_part(w_top, h_top, w_bottom, h_bottom, length, conn_top, conn_bottom, st.session_state.auto_id, inner_val, 5, h_taper, v_taper, off_dir, off_val, is_print=True).savefig(buf, format="png", bbox_inches='tight', dpi=140)
                st.session_state.collection.append(buf.getvalue())
                st.session_state.auto_id += 1
                st.rerun()
    with ed_b2:
        if st.button("🔙 Undo Last", use_container_width=True) and st.session_state.collection:
            st.session_state.collection.pop()
            st.session_state.auto_id -= 1
            st.rerun()

with col_prev:
    st.subheader("📋 Print Preview")
    if st.session_state.collection:
        p_cols = st.columns(4)
        for i, img in enumerate(st.session_state.collection):
            p_cols[i % 4].image(img, use_container_width=True)
        
        if st.button("🖨️ Print Report", type="secondary", use_container_width=True):
            encoded = [base64.b64encode(img).decode() for img in st.session_state.collection]
            html = f"""
            <div style="font-family: sans-serif; padding: 20px;">
                <h2 style="border-bottom: 2px solid #334155;">{proj_name}</h2>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                    {''.join([f'<div><img src="data:image/png;base64,{img}" style="width:100%;"></div>' for img in encoded])}
                </div>
            </div><script>window.print();</script>"""
            st.components.v1.html(html, height=0)
    else:
        st.info("Your print sheet is empty. Add pieces to see them here.")
