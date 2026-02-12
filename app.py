import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, RegularPolygon
import io
import base64

# --- 1. APP CONFIG & STYLING ---
st.set_page_config(layout="wide", page_title="HVAC Pro-Draft v22.0", page_icon="🏗️")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { border-radius: 8px; font-weight: 700; height: 3em; }
    div[data-testid="stVerticalBlock"] { gap: 0.8rem; }
    h3 { padding-top: 0; }
    </style>
    """, unsafe_allow_html=True)

if 'collection' not in st.session_state: st.session_state.collection = []
if 'auto_id' not in st.session_state: st.session_state.auto_id = 1

# --- 2. THE MASTER DRAWING ENGINE ---
def render_piece(tw, th, bw, bh, L, ct, cb, ID, insulation, h_align, v_align, s_side, s_val):
    # FIXED CANVAS SIZE: Ensures every 'Snapshot' has identical proportions
    fig, ax = plt.subplots(figsize=(6, 8.5))
    fig.patch.set_facecolor('white')
    
    # 1. CALCULATE GEOMETRY
    if s_side == "Left": xt, xb = 0, s_val
    elif s_side == "Right": xt, xb = s_val, 0
    else:
        max_w = max(tw, bw)
        if h_align == "Left Side 90°": xt, xb = 0, 0
        elif h_align == "Right Side 90°": xt, xb = max_w - tw, max_w - bw
        else: xt, xb = (max_w - tw) / 2, (max_w - bw) / 2

    tl, tr = (xt, L), (xt + tw, L)
    bl, br = (xb, 0), (xb + bw, 0)

    # 2. DRAW MAIN BODY
    ax.add_patch(Polygon([bl, br, tr, tl], closed=True, fill=False, linewidth=3, edgecolor='black'))

    # 3. DRAW RED OFFSET (The "Nailed" Logic from v19)
    if s_val > 0:
        red = '#dc2626'
        if s_side == "Left":
            # Top-Left -> Drop Down -> Bottom-Left
            ax.plot([tl[0], tl[0], bl[0]], [tl[1], bl[1], bl[1]], 
                    color=red, ls='--', lw=2.5, marker='o', ms=9, zorder=10)
        elif s_side == "Right":
            # Top-Right -> Drop Down -> Bottom-Right
            ax.plot([tr[0], tr[0], br[0]], [tr[1], br[1], br[1]], 
                    color=red, ls='--', lw=2.5, marker='o', ms=9, zorder=10)

    # 4. SMART LABELS (Jump to safe side)
    ha = 'left' if s_side in ["Left", "None"] else 'right'
    # Dynamic margin based on duct width to prevent overlap
    margin = tw * 0.15 + 40
    label_x = tr[0] + margin if ha == 'left' else tl[0] - margin

    # Connection Text
    if ct != "None": ax.text(label_x, L + 20, ct, ha=ha, fontsize=13, weight='bold')
    if cb != "None": ax.text(label_x, -50, cb, ha=ha, fontsize=13, weight='bold')

    # Dimensions
    ax.text(xt + tw/2, L + 140, f"{int(tw)} x {int(th)}", ha="center", fontsize=15, weight='bold')
    ax.text(xb + bw/2, -160, f"{int(bw)} x {int(bh)}", ha="center", fontsize=15, weight='bold')

    # 5. RESTORED FEATURES (Taper & Insulation)
    cx = (tl[0] + tr[0] + bl[0] + br[0]) / 4
    
    # Taper Label (FOT/FOB) - Restored & Bold
    taper_txt = ""
    if v_align == "Flat on Top": taper_txt = "FOT"
    elif v_align == "Flat on Bottom": taper_txt = "FOB"
    elif v_align == "Equal Taper" and (tw != bw or th != bh): taper_txt = "ET"
    
    if taper_txt:
        ax.text(cx, L*0.4, taper_txt, ha='center', fontsize=20, weight='heavy', alpha=0.35, color='black')

    # Insulation (Triangle) - Restored
    if insulation != "None":
        ax.add_patch(RegularPolygon((cx, L*0.7), 3, radius=60, fill=False, edgecolor='black', lw=2))
        ax.text(cx, L*0.7 - 110, f"{insulation} int", ha='center', fontsize=13, weight='bold')

    # 6. ID & RULER
    ax.text(tr[0] + 80, L + 80, f"{int(ID)}", color='#d97706', fontsize=30, weight='black')
    
    ruler_x = max(tr[0], br[0]) + 180
    ax.plot([ruler_x, ruler_x], [0, L], color='black', lw=2)
    ax.text(ruler_x + 50, L/2, f"{int(L)}", rotation=90, va="center", fontsize=15, weight='bold')

    # 7. VIEWPORT LOCK
    ax.set_aspect('equal')
    ax.axis('off')
    # Strict limits ensure every snapshot has the same 'zoom level' relative to the duct
    ax.set_ylim(-400, L + 500)
    ax.set_xlim(min(xt, xb) - 400, max(tr[0], br[0]) + 400)
    
    return fig

# --- 3. UI LAYOUT ---
st.title("🏗️ HVAC Pro-Draft v22.0 (Production)")
proj_name = st.sidebar.text_input("Project Name/Reference", "Job #1234")

col_ui, col_prev = st.columns([1, 1.8])

with col_ui:
    with st.container(border=True):
        st.subheader("📐 Dimensions (mm)")
        c1, c2 = st.columns(2)
        tw = c1.number_input("Top Width", value=450, step=50)
        th = c2.number_input("Top Height", value=250, step=50)
        bw = c1.number_input("Bot Width", value=450, step=50)
        bh = c2.number_input("Bot Height", value=250, step=50)
        L_val = st.number_input("Length", value=1400, step=100)
    
    with st.container(border=True):
        st.subheader("⚙️ Alignment")
        s_side = st.radio("Offset Side", ["None", "Left", "Right"], horizontal=True)
        s_dist = st.number_input("Offset Distance", value=0, step=10)
        h_al = st.selectbox("Horizontal Type", ["Equal Taper", "Left Side 90°", "Right Side 90°"])
        v_al = st.selectbox("Vertical Type (FOT/FOB)", ["Equal Taper", "Flat on Top", "Flat on Bottom"])
        
    with st.container(border=True):
        st.subheader("🔩 Fittings")
        c3, c4 = st.columns(2)
        ct = c3.selectbox("Top Conn", ["TDF", "SLIDE", "None"])
        cb = c4.selectbox("Bot Conn", ["TDF", "SLIDE", "None"])
        ins = st.selectbox("Lining", ["None", "25", "50", "100"])

    # PRIMARY ACTION
    if st.button("📸 SNAPSHOT & ADD TO GRID", type="primary", use_container_width=True):
        if len(st.session_state.collection) < 9:
            buf = io.BytesIO()
            # Capture High-Res Snapshot
            fig = render_piece(tw, th, bw, bh, L_val, ct, cb, st.session_state.auto_id, ins, h_al, v_al, s_side, s_dist)
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=150)
            st.session_state.collection.append(buf.getvalue())
            st.session_state.auto_id += 1
            st.rerun()
        else:
            st.warning("Sheet is full (9/9). Please print or clear.")

with col_prev:
    st.subheader("Live Preview")
    # Live render for adjustment
    live_fig = render_piece(tw, th, bw, bh, L_val, ct, cb, st.session_state.auto_id, ins, h_al, v_al, s_side, s_dist)
    st.pyplot(live_fig, use_container_width=True)

# --- 4. THE 3x3 GRID PRINT ENGINE ---
st.divider()
st.subheader(f"📋 Print Sheet ({len(st.session_state.collection)}/9)")

if st.session_state.collection:
    # Review Grid
    r_cols = st.columns(3)
    for i, img in enumerate(st.session_state.collection):
        with r_cols[i % 3]:
            st.image(img, use_container_width=True)
            if st.button(f"Remove #{i+1}", key=f"del_{i}"):
                st.session_state.collection.pop(i)
                st.rerun()

    # PRINT LOGIC
    if st.button("🖨️ PRINT FINAL SHEET (A4)", type="primary", use_container_width=True):
        encoded_imgs = [base64.b64encode(img).decode() for img in st.session_state.collection]
        
        # CSS Grid Layout (More stable than tables for exact sizing)
        grid_items = ""
        for img in encoded_imgs:
            grid_items += f"""
            <div class="grid-item">
                <img src="data:image/png;base64,{img}">
            </div>
            """
            
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @page {{ size: A4; margin: 0; }}
                body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
                
                .page-container {{
                    width: 210mm;
                    height: 296mm; /* Exact A4 Height */
                    padding: 10mm;
                    box-sizing: border-box;
                    display: flex;
                    flex-direction: column;
                }}
                
                h2 {{ text-align: center; margin: 0 0 5mm 0; font-size: 24px; }}
                
                .grid-wrapper {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    grid-template-rows: 1fr 1fr 1fr;
                    gap: 2mm;
                    flex-grow: 1;
                    height: 100%;
                }}
                
                .grid-item {{
                    border: 1px solid #ccc;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 90mm; /* Hard-coded height to force 3 rows fits perfectly */
                    overflow: hidden;
                }}
                
                .grid-item img {{
                    max-width: 98%;
                    max-height: 98%;
                    object-fit: contain;
                }}
            </style>
        </head>
        <body>
            <div class="page-container">
                <h2>{proj_name}</h2>
                <div class="grid-wrapper">
                    {grid_items}
                </div>
            </div>
            <script>window.print();</script>
        </body>
        </html>
        """
        st.components.v1.html(html_content, height=0)

    if st.button("🗑️ START NEW SHEET", use_container_width=True):
        st.session_state.collection = []
        st.session_state.auto_id = 1
        st.rerun()
