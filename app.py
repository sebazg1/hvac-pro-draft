import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, RegularPolygon, Arc
import numpy as np
import io
import base64
import uuid
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List, Tuple

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(layout="wide", page_title="HVAC Master v2.0", page_icon="🏗️")

st.markdown("""
    <style>
    /* Global Reset & Typography */
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; font-weight: 600; color: #1e293b; }
    
    /* Custom Button Styling */
    .stButton>button { 
        border-radius: 8px; 
        font-weight: 600; 
        border: 1px solid #cbd5e1;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { 
        border-color: #3b82f6; 
        color: #3b82f6; 
        background-color: #eff6ff;
    }
    
    /* Input Field Styling */
    div[data-testid="stNumberInput"] input { font-weight: 600; color: #334155; }
    
    /* Card/Container Styling */
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* Print View Grid */
    @media print {
        @page { size: A4; margin: 10mm; }
        .no-print { display: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA MODELS (PYDANTIC) ---

# --- 2. DATA MODELS (PYDANTIC) ---

class BasePiece(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project: str = "Default Project"
    piece_type: Literal["Straight", "Bend"]

class StraightPiece(BasePiece):
    piece_type: Literal["Straight"] = "Straight"
    
    # Dimensions
    top_width: float = Field(..., gt=0, description="Top Width (mm)")
    top_height: float = Field(..., gt=0, description="Top Height (mm)")
    btm_width: float = Field(..., gt=0, description="Bottom Width (mm)")
    btm_height: float = Field(..., gt=0, description="Bottom Height (mm)")
    length: float = Field(..., gt=0, description="Length (mm)")
    
    # Connections & Options
    conn_top: str = "TDF"
    conn_btm: str = "TDF"
    insulation: str = "None"
    
    # Offsets & Alignment
    h_align: Literal["Center", "Left Flat", "Right Flat"] = "Center"
    v_align: Literal["Center", "Flat Top", "Flat Bottom"] = "Center"
    shift_side: Literal["None", "Left", "Right"] = "None"
    shift_val: float = Field(default=0.0, ge=0)

    @property
    def label(self):
        return f"{int(self.top_width)}x{int(self.top_height)} / {int(self.btm_width)}x{int(self.btm_height)} L={int(self.length)}"

class BendPiece(BasePiece):
    piece_type: Literal["Bend"] = "Bend"
    
    # Dimensions
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    radius: float = Field(..., gt=0)
    angle: float = Field(..., gt=0, le=180)
    
    # Options
    conn_in: str = "TDF"
    conn_out: str = "TDF"
    vanes: bool = False

    @property
    def label(self):
        return f"{int(self.width)}x{int(self.height)} R={int(self.radius)} {int(self.angle)}°"

# --- 3. RENDERING ENGINE (OO-MATPLOTLIB) ---

class HVACRenderer:
    @staticmethod
    def _create_fig(size=(6, 8.5)):
        fig = plt.Figure(figsize=size)
        ax = fig.subplots()
        fig.patch.set_facecolor('white')
        ax.set_aspect('equal')
        ax.axis('off')
        return fig, ax

    @staticmethod
    def render_straight(p: StraightPiece):
        fig, ax = HVACRenderer._create_fig()
        
        # 1. Calculate Geometry
        max_w = max(p.top_width, p.btm_width) + p.shift_val
        
        xt, xb = 0.0, 0.0
        
        if p.shift_side == "Left":
            xt, xb = 0, p.shift_val
        elif p.shift_side == "Right":
            xt, xb = p.shift_val, 0
        else:
            if p.h_align == "Left Flat":
                xt, xb = 0, 0
            elif p.h_align == "Right Flat":
                xt = max_w - p.top_width
                xb = max_w - p.btm_width
            else: # Center
                xt = (max_w - p.top_width) / 2
                xb = (max_w - p.btm_width) / 2

        yt, yb = p.length, 0
        tl, tr, bl, br = (xt, yt), (xt + p.top_width, yt), (xb, yb), (xb + p.btm_width, yb)
        
        # Draw
        poly = Polygon([bl, br, tr, tl], closed=True, fill=False, linewidth=2.5, edgecolor='#1e293b')
        ax.add_patch(poly)
        
        if p.shift_val > 0:
            shift_color = '#dc2626'
            if p.shift_side == "Left":
                # Points: (tl[0], tl[1]) -> (tl[0], bl[1]) -> (bl[0], bl[1])
                # Horizontal segment is (tl[0], bl[0]) at y=bl[1]
                ax.plot([tl[0], tl[0], bl[0]], [tl[1], bl[1], bl[1]], color=shift_color, ls='--', lw=1.5, marker='o')
                
                # Text below horizontal segment
                mid_x = (tl[0] + bl[0]) / 2
                ax.text(mid_x, bl[1] - 40, f"{int(p.shift_val)}", ha='center', va='top', color=shift_color, fontsize=10, weight='bold')
                
            elif p.shift_side == "Right":
                # Points: (tr[0], tr[1]) -> (tr[0], br[1]) -> (br[0], br[1])
                # Horizontal segment is (tr[0], br[0]) at y=br[1]
                ax.plot([tr[0], tr[0], br[0]], [tr[1], br[1], br[1]], color=shift_color, ls='--', lw=1.5, marker='o')

                # Text below horizontal segment
                mid_x = (tr[0] + br[0]) / 2
                ax.text(mid_x, br[1] - 40, f"{int(p.shift_val)}", ha='center', va='top', color=shift_color, fontsize=10, weight='bold')

        ax.text(xt + p.top_width/2, yt + 100, f"{int(p.top_width)} x {int(p.top_height)}", ha="center", fontsize=12, weight='bold')
        ax.text(xb + p.btm_width/2, yb - 120, f"{int(p.btm_width)} x {int(p.btm_height)}", ha="center", fontsize=12, weight='bold')
        
        dim_x = max(tr[0], br[0]) + 150
        ax.plot([dim_x, dim_x], [0, p.length], color='#64748b', lw=1.5)
        ax.plot([dim_x-20, dim_x+20], [0, 0], color='#64748b', lw=1.5)
        ax.plot([dim_x-20, dim_x+20], [p.length, p.length], color='#64748b', lw=1.5)
        ax.text(dim_x + 30, p.length/2, f"L = {int(p.length)}", rotation=90, va="center", fontsize=11, color='#475569')

        if p.conn_top != "None": ax.text(xt-50, yt+20, p.conn_top, ha='right', fontsize=10, style='italic', color='#64748b')
        if p.conn_btm != "None": ax.text(xb-50, yb-20, p.conn_btm, ha='right', fontsize=10, style='italic', color='#64748b')

        cx = (tl[0] + tr[0] + bl[0] + br[0]) / 4
        tags = []
        if p.v_align == "Flat Top": tags.append("FOT")
        if p.v_align == "Flat Bottom": tags.append("FOB")
        if p.insulation != "None": tags.append(f"{p.insulation} mm INT")
        
        if tags:
             ax.text(cx, p.length*0.4, "\n".join(tags), ha='center', fontsize=14, weight='heavy', alpha=0.15, color='black')

        ax.autoscale_view()
        ax.margins(0.2)
        return fig

    @staticmethod
    def render_bend(p: BendPiece):
        fig, ax = HVACRenderer._create_fig()
        
        r_out = p.radius + p.width
        center = (0, 0)
        
        # Arcs
        arc_in = Arc(center, 2*p.radius, 2*p.radius, angle=0, theta1=0, theta2=p.angle, color='#1e293b', lw=2.5)
        arc_out = Arc(center, 2*r_out, 2*r_out, angle=0, theta1=0, theta2=p.angle, color='#1e293b', lw=2.5)
        ax.add_patch(arc_in)
        ax.add_patch(arc_out)
        
        # End Lines
        rad = np.radians(p.angle)
        ax.plot([p.radius, r_out], [0, 0], color='#1e293b', lw=2.5)
        ax.plot([p.radius*np.cos(rad), r_out*np.cos(rad)], 
                [p.radius*np.sin(rad), r_out*np.sin(rad)], color='#1e293b', lw=2.5)
        
        # Vanes
        if p.vanes:
            for i in range(1, 4):
                r_vane = p.radius + (p.width * (i / 4))
                ax.add_patch(Arc(center, 2*r_vane, 2*r_vane, angle=0, theta1=0, theta2=p.angle, 
                               color='#94a3b8', ls='--', lw=1))

        # Text
        mid_ang = np.radians(p.angle/2)
        text_r = r_out + 100 
        ax.text(text_r*np.cos(mid_ang), text_r*np.sin(mid_ang), 
                f"{int(p.width)}x{int(p.height)}\n{p.angle:.0f}°", 
                ha='center', va='center', fontsize=11, weight='bold')

        # Connections Labels
        ax.text(p.radius + p.width/2, -60, p.conn_in, ha='center', fontsize=10, color='#64748b')
        
        exit_mid_x = (p.radius + p.width/2) * np.cos(rad)
        exit_mid_y = (p.radius + p.width/2) * np.sin(rad)
        dx_text = -np.sin(rad) * 80
        dy_text = np.cos(rad) * 80
        
        ax.text(exit_mid_x + dx_text, exit_mid_y + dy_text, p.conn_out, 
                ha='center', va='center', fontsize=10, color='#64748b', rotation=p.angle-90)

        ax.autoscale_view()
        ax.margins(0.2)
        return fig

# --- 4. TESTS (Sanity Check) ---
def run_self_tests():
    try:
        # Test 1: Straight Piece Creation
        s = StraightPiece(top_width=500, top_height=200, btm_width=500, btm_height=200, length=1000, piece_type="Straight")
        # Test 2: Bend Piece Creation
        b = BendPiece(width=500, height=200, radius=150, angle=90, piece_type="Bend")
        return True
    except Exception as e:
        st.error(f"System Self-Test Failed: {e}")
        return False

# --- 5. STREAMLIT UI ---

def main():
    if not run_self_tests(): return

    # Sidebar: Global Project Settings
    with st.sidebar:
        st.markdown("## HVAC MASTER v2.0")
        st.caption("Professional Fabrication Tool")
        
        project_name = st.text_input("Project Reference", "Job-101")
        
        st.divider()
        st.caption("Session Stats")
        if 'collection' not in st.session_state: st.session_state.collection = []
        st.metric("Total Pieces", len(st.session_state.collection))
        
        if st.button("Clear All Pieces", type="secondary"):
            st.session_state.collection = []
            st.rerun()

    # Main Area Tabs
    tab_design, tab_print = st.tabs(["Design", "Print Sheet"])

    # --- DESIGNER TAB ---
    with tab_design:
        mode = st.radio("Component Type", ["Straight / Transition", "Elbow / Bend"], horizontal=True, label_visibility="collapsed")
        
        c_left, c_right = st.columns([1, 1.2])
        
        with c_left:
            with st.container(border=True):
                if mode == "Straight / Transition":
                    st.markdown("#### Dimensions")
                    c1, c2 = st.columns(2)
                    tw = c1.number_input("Top Width", value=450, step=10)
                    th = c2.number_input("Top Height", value=250, step=10)
                    c3, c4 = st.columns(2)
                    bw = c3.number_input("Btm Width", value=450, step=10)
                    bh = c4.number_input("Btm Height", value=250, step=10)
                    L = st.number_input("Length", value=1400, step=50)
                    
                    st.markdown("#### Connections")
                    c5, c6 = st.columns(2)
                    ct = c5.selectbox("Top Conn", ["TDF", "SLIDE", "RAW", "None"])
                    cb = c6.selectbox("Btm Conn", ["TDF", "SLIDE", "RAW", "None"])
                    
                    with st.expander("Offset & Alignment"):
                        align_h = st.selectbox("Side Alignment", ["Center", "Left Flat", "Right Flat"])
                        align_v = st.selectbox("Vertical Alignment", ["Center", "Flat Top", "Flat Bottom"])
                        ins = st.selectbox("Insulation", ["None", "13mm", "25mm", "50mm"])
                        
                        st.markdown("**Shift / Kick**")
                        cc1, cc2 = st.columns([1, 2])
                        shift_dir = cc1.selectbox("Dir", ["None", "Left", "Right"])
                        shift_val = cc2.number_input("Distance", min_value=0.0, value=0.0, disabled=(shift_dir=="None"))

                    current_piece = StraightPiece(
                        project=project_name,
                        top_width=tw, top_height=th, btm_width=bw, btm_height=bh, length=L,
                        conn_top=ct, conn_btm=cb,
                        h_align=align_h, v_align=align_v, insulation=ins,
                        shift_side=shift_dir, shift_val=shift_val
                    )
                    
                    fig = HVACRenderer.render_straight(current_piece)

                else: # BEND
                    st.markdown("#### Dimensions")
                    c1, c2 = st.columns(2)
                    w = c1.number_input("Width", value=450, step=10)
                    h = c2.number_input("Height", value=250, step=10)
                    
                    c3, c4 = st.columns(2)
                    rad_val = c3.number_input("Throat Radius", value=150, step=10)
                    ang = c4.slider("Angle", 0, 180, 90, step=15)
                    
                    st.markdown("#### Options")
                    conn_in = st.selectbox("In Conn", ["TDF", "SLIDE", "RAW"])
                    conn_out = st.selectbox("Out Conn", ["TDF", "SLIDE", "RAW"])
                    vanes = st.checkbox("Turning Vanes", value=True)
                    
                    current_piece = BendPiece(
                        project=project_name,
                        width=w, height=h, radius=rad_val, angle=ang,
                        conn_in=conn_in, conn_out=conn_out, vanes=vanes
                    )
                    
                    fig = HVACRenderer.render_bend(current_piece)
            
            st.markdown("###")
            if st.button("Add to Sheet", type="primary", use_container_width=True):
                # Save fig to buffer
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches='tight', dpi=100)
                plt.close(fig) # Clean up
                
                # Store data
                item_data = {
                    "id": current_piece.id,
                    "label": current_piece.label,
                    "image": buf.getvalue(),
                    "type": current_piece.piece_type
                }
                st.session_state.collection.append(item_data)
                st.toast(f"Added {current_piece.label} to sheet!")

        with c_right:
            st.markdown("##### Live Preview")
            st.pyplot(fig, use_container_width=True)

    # --- PRINT TAB ---
    with tab_print:
        if len(st.session_state.collection) == 0:
            st.info("No pieces added yet. Go to Designer tab to add some.")
        else:
            st.subheader(f"Job Sheet: {project_name}")
            
            # 1. Edit List
            st.markdown("#### Review Items")
            for idx, item in enumerate(st.session_state.collection):
                col_img, col_desc, col_del = st.columns([1, 3, 1])
                with col_img:
                    st.image(item['image'], width=80)
                with col_desc:
                    st.write(f"**#{idx+1} {item['type']}**")
                    st.caption(item['label'])
                with col_del:
                    # Use ID for key to prevent delete bug
                    if st.button("Remove", key=f"del_{item['id']}"):
                        st.session_state.collection.pop(idx)
                        st.rerun()
                st.divider()

            # 2. Print Generation
            st.markdown("#### Export")
            if st.button("🖨️ Generate Print View (A4 Grid)", type="primary"):
                # Generate HTML base64
                encoded_imgs = [base64.b64encode(x['image']).decode() for x in st.session_state.collection]
                
                # CSS for A4 Grid
                html_template = f"""
                <html>
                <head>
                    <title>{project_name} - Fabrication Sheet</title>
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
                        /* Force size and margins */
                        @page {{ 
                            size: auto; 
                            margin: 0mm; 
                        }}
                        
                        body {{ 
                            font-family: 'Inter', sans-serif; 
                            margin: 10mm; /* Browser visual margin */
                            padding: 0; 
                            background: #fff; 
                            -webkit-print-color-adjust: exact;
                        }}
                        
                        /* Layout Container matches US Letter Safe Area */
                        .page {{
                            width: 190mm; 
                            height: 250mm; /* Very safe height for Letter/A4 */
                            margin: 0 auto;
                            display: flex;
                            flex-direction: column;
                            outline: 1px dotted #ccc; /* Visual aid, doesn't print */
                        }}
                        
                        .header {{ 
                            text-align: center; 
                            border-bottom: 2px solid #000; 
                            margin-bottom: 2mm; 
                            padding-bottom: 2mm; 
                            flex-shrink: 0;
                        }}
                        .header h1 {{ margin: 0; font-size: 14px; text-transform: uppercase; }}
                        .meta {{ display: flex; justify-content: space-between; font-size: 8px; margin-top: 2px; }}
                        
                        .grid {{
                            display: grid;
                            grid-template-columns: repeat(3, 1fr);
                            gap: 2mm; /* Tiny gap */
                            flex-grow: 1; 
                        }}
                        
                        .card {{
                            border: 1px solid #9ca3af;
                            padding: 2px;
                            text-align: center;
                            height: 70mm; /* Main constraint */
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                            break-inside: avoid;
                            box-sizing: border-box;
                            overflow: hidden;
                        }}
                        
                        .card img {{
                            max-width: 95%;
                            max-height: 55mm; /* Leave room for label */
                            object-fit: contain;
                        }}
                        
                        .card-label {{
                            margin-top: 2px;
                            font-size: 8px;
                            font-weight: bold;
                            color: #000;
                            border-top: 1px solid #e5e7eb;
                            width: 100%;
                            padding-top: 2px;
                            white-space: nowrap;
                            overflow: hidden;
                            text-overflow: ellipsis;
                        }}

                        @media print {{
                            body {{ background: none; }}
                            .no-print {{ display: none; }}
                            /* Hide browser headers/footers if possible */
                            @page {{ margin: 5mm; }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="page">
                        <div class="header">
                            <h1>Fabrication Ticket</h1>
                            <div class="meta">
                                <span><b>Project:</b> {project_name}</span>
                                <span><b>Date:</b> {st.session_state.get('date', '')}</span>
                                <span><b>Items:</b> {len(st.session_state.collection)}</span>
                            </div>
                        </div>
                        
                        <div class="grid">
                """
                
                # Add items
                for i, (img, data) in enumerate(zip(encoded_imgs, st.session_state.collection)):
                    html_template += f"""
                        <div class="card">
                            <img src="data:image/png;base64,{img}">
                            <div class="card-label">
                                #{i+1} | {data['label']}
                            </div>
                        </div>
                    """
                
                html_template += """
                        </div>
                    </div>
                    <script>window.print();</script>
                </body>
                </html>
                """
                
                st.components.v1.html(html_template, height=800, scrolling=True)

if __name__ == "__main__":
    main()
