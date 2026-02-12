import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, RegularPolygon
import io
import base64

# --- 1. APP CONFIGURATION & MOBILE STYLING ---
st.set_page_config(layout="wide", page_title="HVAC Pro-Draft Master", page_icon="🏗️")

st.markdown("""
    <style>
    /* Mobile-First Adjustments */
    .main { background-color: #f8fafc; }
    
    /* Bigger, thumb-friendly buttons */
    .stButton>button { 
        border-radius: 12px; 
        font-weight: 700; 
        height: 3.5em; 
        font-size: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Clean Input Groups */
    div[data-testid="stVerticalBlock"] { gap: 0.8rem; }
    
    /* Headings */
    h3 { 
        padding-top: 0; 
        font-size: 1.2rem !important; 
        color: #1e293b;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'collection' not in st.session_state: st.session_state.collection = []
if 'auto_id' not in st.session_state: st.session_state.auto_id = 1

# --- 2. THE MASTER DRAWING ENGINE ---
def render_piece(tw, th, bw, bh, L, ct, cb, ID, insulation, h_align, v_align, s_side, s_val):
    # FIXED CANVAS: Ensures 100% consistency in the printed grid
    fig, ax = plt.subplots(figsize=(6, 8.5))
    fig.patch.set_facecolor('white')
    
    # --- GEOMETRY LOGIC ---
    if s_side == "Left": xt, xb = 0, s_val
    elif s_side == "Right": xt, xb = s_val, 0
    else:
        max_w = max(tw, bw)
        if h_align == "Left Side Flat": xt, xb = 0, 0
        elif h_align == "Right Side Flat": xt, xb = max_w - tw, max_w - bw
        else: xt, xb = (max_w - tw) / 2, (max_w - bw) / 2  # Center/Equal Taper

    tl, tr = (xt, L), (xt + tw, L)
    bl, br = (xb, 0), (xb + bw, 0)

    # --- DRAWING ---
    # 1. Main Duct Body
    ax.add_patch(Polygon([bl, br, tr, tl], closed=True, fill=False, linewidth=3, edgecolor='black'))

    # 2. Red Offset Indicator (Corner-to-Corner Snap)
    if s_val > 0:
        red = '#dc2626'
        if s_side == "Left":
            ax.plot([tl[0], tl[0], bl[0]], [tl[1], bl[1], bl[1]], 
                    color=red, ls='--', lw=2.5, marker='o', ms=9, zorder=10)
        elif s_side == "Right":
            ax.plot([tr[0], tr[0], br[0]], [tr[1], br[1], br[1]], 
                    color=red, ls='--', lw=2.5, marker='o', ms=9, zorder=10)

    # 3. Intelligent Labelling
    ha = 'left' if s_side in ["Left", "None"] else 'right'
    margin = tw * 0.15 + 40
    label_x = tr[0] + margin if ha == 'left' else tl[0] - margin

    # Connections
    if ct != "None": ax.text(label_x, L + 20, ct, ha=ha, fontsize=13, weight='bold')
    if cb != "None": ax.text(label_x, -50, cb, ha=ha, fontsize=13, weight='bold')

    # Dimensions (W x H)
    ax.text(xt + tw/2, L + 140, f"{int(tw)} x {int(th)}", ha="center", fontsize=15, weight='bold')
    ax.text(xb + bw/2, -160, f"{int(bw)} x {int(bh)}", ha="center", fontsize=15, weight='bold')

    # Center Markers (Taper & Insulation)
    cx = (tl[0] + tr[0] + bl[0] + br[0]) / 4
    
    # Taper Style (FOT/FOB)
    taper_txt = ""
    if v_align == "Flat on Top": taper_txt = "FOT"
    elif v_align == "Flat on Bottom": taper_txt = "FOB"
    elif v_align == "Center Taper" and (tw != bw or th != bh): taper_txt = "ET"
    
    if taper_txt:
        ax.text(cx, L*0.4, taper_txt, ha='center', fontsize=20, weight='heavy', alpha=0.35, color='black')

    # Insulation Triangle
    if insulation != "None":
        ax.add_patch(RegularPolygon((cx, L*0.7), 3, radius=60, fill=False, edgecolor='black', lw=2))
        ax.text(cx, L*0.7 - 110, f"{insulation} int", ha='center', fontsize=13, weight='bold')

    # ID & Ruler
    ax.text(tr[0] + 80, L + 80, f"{int(ID)}", color='#d97706', fontsize=30, weight='black')
    
    ruler_x = max(tr[0], br[0]) + 180
    ax.plot([ruler_x, ruler_x], [0, L], color='black', lw=2)
    ax.text(ruler_x + 50, L/2, f"{int(L)}", rotation=90, va="center", fontsize=15, weight='bold')

    # Viewport Lock
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_ylim(-400, L + 500)
    ax.set_xlim(min(xt, xb) - 400, max(tr[0], br[0]) + 400)
    
    return fig

# --- 3. MOBILE-OPTIMIZED INTERFACE ---
st.title("🏗️ HVAC Pro-Draft Master")
proj_name = st.text_input("Project Name / Reference", "Job #1234")

# Tabs for cleaner mobile navigation
tab1, tab2 = st.tabs(["✏️ Input & Create", "📋 Review & Print"])

with tab1:
    # GROUP 1: TOP DIMENSIONS
    with st.container(border=True):
        st.subheader("1. Top Opening")
        c1, c2 = st.columns(2)
        tw = c1.number_input("Top Width (mm)", value=450, step=50, key="tw")
        th = c2.number_input("Top Height (mm)", value=250, step=50, key="th")
        ct = st.selectbox("Top Flange/Conn", ["TDF", "SLIDE", "None"], key="ct")

    # GROUP 2: BOTTOM DIMENSIONS
    with st.container(border=True):
        st.subheader("2. Bottom Opening")
        c3, c4 = st.columns(2)
        bw = c3.number_input("Bot Width (mm)", value=450, step=50, key="bw")
        bh = c4.number_input("Bot Height (mm)", value=250, step=50, key="bh")
        cb = st.selectbox("Bot Flange/Conn", ["TDF", "SLIDE", "None"], key="cb")

    # GROUP 3: LENGTH & SPECS
    with st.container(border=True):
        st.subheader("3. Length & Specs")
        L_val = st.number_input("Duct Length (mm)", value=1400, step=100)
        ins = st.selectbox("Internal Lining", ["None", "25", "50", "100"])
        
    # GROUP 4: OFFSETS (The Tricky Part Made Simple)
    with st.container(border=True):
        st.subheader("4. Offsets & Tapers")
        
        st.write("**Horizontal Offset (Left/Right Shift)**")
        col_s1, col_s2 = st.columns([1, 1])
        s_side = col_s1.selectbox("Shift Direction", ["None", "Left", "Right"])
        s_dist = col_s2.number_input("Shift Distance (mm)", value=0, step=10)
        
        # CLEARER NAMES for Taper Options
        h_al = st.selectbox("Horizontal Side Style", ["Center Taper", "Left Side Flat", "Right Side Flat"])
        v_al = st.selectbox("Vertical Taper Style", ["Center Taper", "Flat on Top", "Flat on Bottom"])

    # PREVIEW (Expandable to save space on mobile)
    with st.expander("👀 View Live Preview", expanded=True):
        live_fig = render_piece(tw, th, bw, bh, L_val, ct, cb, st.session_state.auto_id, ins, h_al, v_al, s_side, s_dist)
        st.pyplot(live_fig, use_container_width=True)

    # ACTION BUTTON
    st.write("---")
    if st.button("📸 SNAPSHOT & ADD PIECE", type="primary", use_container_width=True):
        if len(st.session_state.collection) < 9:
            buf = io.BytesIO()
            fig = render_piece(tw, th, bw, bh, L_val, ct, cb, st.session_state.auto_id, ins, h_al, v_al, s_side, s_dist)
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=150)
            st.session_state.collection.append(buf.getvalue())
            st.session_state.auto_id += 1
            st.success("Piece Added!")
            st.rerun()
        else:
            st.error("Sheet Full! Go to 'Review & Print' tab.")

with tab2:
    st.subheader(f"Current Sheet: {len(st.session_state.collection)} / 9 Pieces")
    
    if st.session_state.collection:
        # Gallery
        r_cols = st.columns(3)
        for i, img in enumerate(st.session_state.collection):
            with r_cols[i % 3]:
                st.image(img, use_container_width=True)
                if st.button(f"🗑️ Del #{i+1}", key=f"del_{i}"):
                    st.session_state.collection.pop(i)
                    st.rerun()

        st.write("---")
        # PRINT BUTTON (CSS GRID ENGINE)
        if st.button("🖨️ GENERATE PDF SHEET", type="primary", use_container_width=True):
            encoded_imgs = [base64.b64encode(img).decode() for img in st.session_state.collection]
            
            grid_items = ""
            for img in encoded_imgs:
                grid_items += f"""<div class="grid-item"><img src="data:image/png;base64,{img}"></div>"""
                
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    @page {{ size: A4; margin: 0; }}
                    body {{ margin: 0; padding: 0; font-family: Helvetica, Arial, sans-serif; }}
                    .page {{ width: 210mm; height: 296mm; padding: 10mm; box-sizing: border-box; display: flex; flex-direction: column; }}
                    h2 {{ text-align: center; margin: 0 0 10px 0; text-transform: uppercase; border-bottom: 2px solid black; padding-bottom: 5px; }}
                    .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; grid-template-rows: 1fr 1fr 1fr; gap: 4px; flex-grow: 1; height: 100%; }}
                    .grid-item {{ border: 1px solid #333; display: flex; align-items: center; justify-content: center; height: 90mm; overflow: hidden; }}
                    .grid-item img {{ max-width: 98%; max-height: 98%; object-fit: contain; }}
                </style>
            </head>
            <body>
                <div class="page">
                    <h2>{proj_name}</h2>
                    <div class="grid">{grid_items}</div>
                </div>
                <script>window.print();</script>
            </body>
            </html>
            """
            st.components.v1.html(html_content, height=0)

        if st.button("❌ CLEAR SHEET", use_container_width=True):
            st.session_state.collection = []
            st.session_state.auto_id = 1
            st.rerun()
    else:
        st.info("No pieces added yet. Go to 'Input & Create' to start.")
