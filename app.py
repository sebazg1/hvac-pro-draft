import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Arc
import numpy as np
import io
import base64
import uuid
from datetime import date
from pydantic import BaseModel, Field
from typing import Literal

# ─────────────────────────────────────────────
# 1. PAGE CONFIG & GLOBAL CSS
# ─────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="HVAC Master v3.0", page_icon="🏗️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root tokens ── */
:root {
    --bg:       #f8fafc;
    --surface:  #ffffff;
    --border:   #e2e8f0;
    --text:     #0f172a;
    --muted:    #64748b;
    --accent:   #2563eb;
    --accent-l: #eff6ff;
    --danger:   #dc2626;
    --success:  #16a34a;
    --radius:   10px;
    --shadow:   0 1px 3px rgba(0,0,0,.08), 0 4px 12px rgba(0,0,0,.06);
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text);
}
.block-container { padding: 1.5rem 2rem 4rem; max-width: 1400px; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--bg);
    border-radius: var(--radius);
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 6px 20px;
    color: var(--muted);
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--accent) !important;
    box-shadow: var(--shadow);
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.88rem;
    border: 1px solid var(--border);
    transition: all .15s ease;
    letter-spacing: .01em;
}
.stButton > button:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: var(--accent-l);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(37,99,235,.15);
}
/* Primary */
.stButton > button[kind="primary"] {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
}
.stButton > button[kind="primary"]:hover {
    background: #1d4ed8;
    color: white;
    border-color: #1d4ed8;
}

/* ── Inputs ── */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    font-family: 'DM Mono', monospace !important;
    font-weight: 500;
    font-size: 0.92rem;
    border-radius: 7px;
}
.stSelectbox select, div[data-baseweb="select"] {
    border-radius: 7px !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem;
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px 16px;
}
div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; }

/* ── Dividers ── */
hr { border-color: var(--border); margin: 1rem 0; }

/* ── Expander ── */
details summary {
    font-weight: 600;
    color: var(--muted);
    font-size: 0.88rem;
    letter-spacing: .02em;
    text-transform: uppercase;
}

/* ── Toast / success ── */
div[data-testid="stToast"] { border-radius: var(--radius); }

/* ── Preview panel ── */
.preview-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}

/* ── Print sheet item row ── */
.sheet-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 2. DATA MODELS
# ─────────────────────────────────────────────

class BasePiece(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project: str = "Default Project"
    piece_type: Literal["Straight", "Bend"]


class StraightPiece(BasePiece):
    piece_type: Literal["Straight"] = "Straight"
    top_width:  float = Field(..., gt=0)
    top_height: float = Field(..., gt=0)
    btm_width:  float = Field(..., gt=0)
    btm_height: float = Field(..., gt=0)
    length:     float = Field(..., gt=0)
    conn_top:   str   = "TDF"
    conn_btm:   str   = "TDF"
    insulation: int   = 0          # 0 = None, else mm (int, clean for math)
    h_align:    Literal["Center", "Left Flat", "Right Flat"] = "Center"
    v_align:    Literal["Center", "Flat Top", "Flat Bottom"] = "Center"
    shift_side: Literal["None", "Left", "Right"] = "None"
    shift_val:  float = Field(default=0.0, ge=0)

    @property
    def label(self) -> str:
        return (f"{int(self.top_width)}×{int(self.top_height)} / "
                f"{int(self.btm_width)}×{int(self.btm_height)}  L={int(self.length)}")


class BendPiece(BasePiece):
    piece_type: Literal["Bend"] = "Bend"
    width:   float = Field(..., gt=0)
    height:  float = Field(..., gt=0)
    radius:  float = Field(..., gt=0)
    angle:   float = Field(..., gt=0, le=180)
    conn_in:  str  = "TDF"
    conn_out: str  = "TDF"
    vanes:   bool  = False

    @property
    def label(self) -> str:
        return f"{int(self.width)}×{int(self.height)}  R={int(self.radius)}  {int(self.angle)}°"


# ─────────────────────────────────────────────
# 3. RENDERING ENGINE
# ─────────────────────────────────────────────

DARK   = "#0f172a"
SLATE  = "#475569"
MUTED  = "#94a3b8"
RED    = "#dc2626"
BLUE   = "#2563eb"

class HVACRenderer:

    @staticmethod
    def _create_fig(size=(6, 8.5)):
        fig = plt.Figure(figsize=size, facecolor="white")
        ax  = fig.subplots()
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("white")
        return fig, ax

    # ── STRAIGHT / TRANSITION ──────────────────
    @staticmethod
    def render_straight(p: StraightPiece):
        fig, ax = HVACRenderer._create_fig()

        # ── Geometry ──────────────────────────
        max_w = max(p.top_width, p.btm_width) + p.shift_val
        xt, xb = 0.0, 0.0

        if p.shift_side == "Left":
            xt, xb = 0.0, p.shift_val
        elif p.shift_side == "Right":
            xt, xb = p.shift_val, 0.0
        else:
            if p.h_align == "Left Flat":
                xt, xb = 0.0, 0.0
            elif p.h_align == "Right Flat":
                xt = max_w - p.top_width
                xb = max_w - p.btm_width
            else:                                    # Center
                xt = (max_w - p.top_width)  / 2
                xb = (max_w - p.btm_width) / 2

        yt, yb = p.length, 0.0
        tl = (xt,              yt)
        tr = (xt + p.top_width, yt)
        bl = (xb,              yb)
        br = (xb + p.btm_width, yb)

        # ── Body ──────────────────────────────
        body = Polygon([bl, br, tr, tl], closed=True,
                       fill=False, linewidth=2.5, edgecolor=DARK)
        ax.add_patch(body)

        # ── Watermark tags ────────────────────
        tags = []
        if p.v_align == "Flat Top":    tags.append("FOT")
        if p.v_align == "Flat Bottom": tags.append("FOB")
        if p.insulation > 0:           tags.append(f"{p.insulation}mm INT")
        if tags:
            cx = (tl[0] + tr[0] + bl[0] + br[0]) / 4
            ax.text(cx, p.length * 0.45, "\n".join(tags),
                    ha="center", fontsize=13, weight="heavy",
                    alpha=0.12, color=DARK)

        # ── Shift annotation (FIXED) ───────────
        # The kick line runs from ONE corner of the top face straight down
        # to the same X, then across to the bottom-face corner — showing
        # the horizontal offset clearly.
        if p.shift_val > 0 and p.shift_side != "None":
            sc = RED
            if p.shift_side == "Left":
                # top-left corner kicks LEFT vs bottom-left
                # vertical: tl down to bl-y; horizontal: tl-x → bl-x
                ax.annotate("", xy=(bl[0], bl[1]),
                            xytext=(tl[0], bl[1]),
                            arrowprops=dict(arrowstyle="<->", color=sc, lw=1.5))
                ax.plot([tl[0], tl[0]], [tl[1], bl[1]],
                        color=sc, ls="--", lw=1.2, alpha=.7)
                mid_x = (tl[0] + bl[0]) / 2
                ax.text(mid_x, bl[1] - p.length * 0.06,
                        f"⟵ {int(p.shift_val)} mm",
                        ha="center", va="top", color=sc,
                        fontsize=9, weight="bold")
            else:  # Right
                ax.annotate("", xy=(br[0], br[1]),
                            xytext=(tr[0], br[1]),
                            arrowprops=dict(arrowstyle="<->", color=sc, lw=1.5))
                ax.plot([tr[0], tr[0]], [tr[1], br[1]],
                        color=sc, ls="--", lw=1.2, alpha=.7)
                mid_x = (tr[0] + br[0]) / 2
                ax.text(mid_x, br[1] - p.length * 0.06,
                        f"{int(p.shift_val)} mm ⟶",
                        ha="center", va="top", color=sc,
                        fontsize=9, weight="bold")

        # ── Size labels ───────────────────────
        ax.text(xt + p.top_width / 2, yt + p.length * 0.07,
                f"{int(p.top_width)} × {int(p.top_height)}",
                ha="center", fontsize=12, weight="bold", color=DARK)
        ax.text(xb + p.btm_width / 2, yb - p.length * 0.09,
                f"{int(p.btm_width)} × {int(p.btm_height)}",
                ha="center", fontsize=12, weight="bold", color=DARK)

        # ── Length dimension line ──────────────
        dim_x = max(tr[0], br[0]) + max(p.top_width, p.btm_width) * 0.18
        tick  = p.length * 0.015
        ax.plot([dim_x, dim_x], [0, p.length], color=SLATE, lw=1.5)
        for y in (0, p.length):
            ax.plot([dim_x - tick, dim_x + tick], [y, y], color=SLATE, lw=1.5)
        ax.text(dim_x + tick * 2, p.length / 2,
                f"L = {int(p.length)} mm",
                rotation=90, va="center", fontsize=10, color=SLATE)

        # ── Connection labels ──────────────────
        label_offset_x = min(tl[0], bl[0]) - max(p.top_width, p.btm_width) * 0.06
        if p.conn_top != "None":
            ax.text(label_offset_x, yt,
                    p.conn_top, ha="right", va="center",
                    fontsize=9, style="italic", color=MUTED)
        if p.conn_btm != "None":
            ax.text(label_offset_x, yb,
                    p.conn_btm, ha="right", va="center",
                    fontsize=9, style="italic", color=MUTED)

        ax.autoscale_view()
        ax.margins(0.22)
        return fig

    # ── ELBOW / BEND ──────────────────────────
    @staticmethod
    def render_bend(p: BendPiece):
        fig, ax = HVACRenderer._create_fig()

        r_out  = p.radius + p.width
        center = (0.0, 0.0)

        # ── Arcs ──────────────────────────────
        arc_in  = Arc(center, 2*p.radius, 2*p.radius,
                      angle=0, theta1=0, theta2=p.angle,
                      color=DARK, lw=2.5)
        arc_out = Arc(center, 2*r_out, 2*r_out,
                      angle=0, theta1=0, theta2=p.angle,
                      color=DARK, lw=2.5)
        ax.add_patch(arc_in)
        ax.add_patch(arc_out)

        # ── End caps ──────────────────────────
        rad = np.radians(p.angle)
        ax.plot([p.radius, r_out], [0, 0], color=DARK, lw=2.5)
        ax.plot([p.radius * np.cos(rad), r_out * np.cos(rad)],
                [p.radius * np.sin(rad), r_out * np.sin(rad)],
                color=DARK, lw=2.5)

        # ── Turning vanes ─────────────────────
        if p.vanes:
            n_vanes = 3
            for i in range(1, n_vanes + 1):
                r_v = p.radius + p.width * (i / (n_vanes + 1))
                ax.add_patch(Arc(center, 2*r_v, 2*r_v,
                                 angle=0, theta1=0, theta2=p.angle,
                                 color=MUTED, ls="--", lw=1.0))

        # ── Size label ────────────────────────
        mid_ang  = np.radians(p.angle / 2)
        text_r   = r_out + max(p.width * 0.35, 80)
        ax.text(text_r * np.cos(mid_ang), text_r * np.sin(mid_ang),
                f"{int(p.width)} × {int(p.height)}\n{p.angle:.0f}°",
                ha="center", va="center", fontsize=11, weight="bold", color=DARK)

        # ── Throat radius annotation ───────────
        rt_x     = p.radius * np.cos(mid_ang)
        rt_y     = p.radius * np.sin(mid_ang)
        text_r_in = max(p.radius * 0.45, 20)
        ax.annotate(f"R{int(p.radius)}",
                    xy=(rt_x, rt_y), xycoords="data",
                    xytext=(text_r_in * np.cos(mid_ang),
                            text_r_in * np.sin(mid_ang)),
                    textcoords="data",
                    arrowprops=dict(arrowstyle="->", color=RED, lw=1.5),
                    color=RED, fontsize=10, weight="bold",
                    ha="center", va="center")

        # ── Connection labels ──────────────────
        r_mid = p.radius + p.width / 2
        ax.text(r_mid, -max(p.width * 0.25, 55),
                p.conn_in, ha="center", fontsize=9,
                color=MUTED, style="italic")

        exit_x = r_mid * np.cos(rad)
        exit_y = r_mid * np.sin(rad)
        off    = max(p.width * 0.25, 55)
        ax.text(exit_x - np.sin(rad) * off,
                exit_y + np.cos(rad) * off,
                p.conn_out, ha="center", va="center",
                fontsize=9, color=MUTED, style="italic",
                rotation=p.angle - 90)

        ax.autoscale_view()
        ax.margins(0.22)
        return fig


# ─────────────────────────────────────────────
# 4. HELPERS
# ─────────────────────────────────────────────

def fig_to_png(fig) -> bytes:
    """Render a matplotlib Figure to PNG bytes and close it."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    buf.seek(0)
    data = buf.getvalue()
    plt.close(fig)
    return data


def _insulation_options() -> dict:
    return {"None": 0, "13 mm": 13, "25 mm": 25, "50 mm": 50}


def _build_print_html(project: str, items: list) -> str:
    today      = date.today().strftime("%d %b %Y")
    cards_html = ""
    for i, item in enumerate(items):
        img_b64 = base64.b64encode(item["image"]).decode()
        cards_html += f"""
        <div class="card">
            <div class="card-num">#{i+1}</div>
            <img src="data:image/png;base64,{img_b64}" alt="">
            <div class="card-label">{item['label']}</div>
        </div>"""

    # Multi-page: chunk cards into groups of 9 (3×3)
    # We embed all cards and let CSS handle page breaks.
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{project} — Fabrication Sheet</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; }}
  @page {{ size: A4 portrait; margin: 8mm; }}
  body {{
    font-family: 'DM Sans', sans-serif;
    margin: 0; padding: 8mm;
    background: #fff;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-bottom: 2px solid #0f172a;
    padding-bottom: 4px;
    margin-bottom: 6px;
  }}
  .header h1 {{ margin: 0; font-size: 13px; text-transform: uppercase; letter-spacing: .08em; }}
  .meta {{ font-size: 8px; color: #475569; text-align: right; line-height: 1.6; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 4px;
  }}
  .card {{
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 4px;
    text-align: center;
    height: 78mm;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    break-inside: avoid;
    overflow: hidden;
    position: relative;
  }}
  .card-num {{
    position: absolute;
    top: 3px; left: 5px;
    font-size: 7px;
    font-weight: 700;
    color: #94a3b8;
  }}
  .card img {{
    max-width: 95%;
    flex: 1;
    object-fit: contain;
    min-height: 0;
  }}
  .card-label {{
    font-size: 7.5px;
    font-weight: 700;
    color: #0f172a;
    border-top: 1px solid #e2e8f0;
    width: 100%;
    padding-top: 3px;
    margin-top: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  @media print {{
    body {{ padding: 0; }}
    .no-print {{ display: none !important; }}
  }}
</style>
</head>
<body>
  <div class="header">
    <h1>🏗 Fabrication Ticket</h1>
    <div class="meta">
      <b>Project:</b> {project}<br>
      <b>Date:</b> {today}<br>
      <b>Items:</b> {len(items)}
    </div>
  </div>
  <div class="grid">
    {cards_html}
  </div>
  <script>window.onload = function(){{ window.print(); }}</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# 5. STREAMLIT UI
# ─────────────────────────────────────────────

def main():
    # ── Session state bootstrap ───────────────
    if "collection" not in st.session_state:
        st.session_state.collection = []

    # ── Sidebar ───────────────────────────────
    with st.sidebar:
        st.markdown("## 🏗️ HVAC Master")
        st.caption("Professional Fabrication Tool · v3.0")
        st.divider()

        project_name = st.text_input("Project Reference", "Job-101",
                                     help="This appears on the fabrication sheet.")
        st.divider()

        total = len(st.session_state.collection)
        st.metric("Pieces in sheet", total)

        if total:
            straight_n = sum(1 for x in st.session_state.collection if x["type"] == "Straight")
            bend_n     = total - straight_n
            c1, c2 = st.columns(2)
            c1.metric("Straights", straight_n)
            c2.metric("Bends",     bend_n)

        st.divider()
        if st.button("🗑 Clear All", type="secondary", use_container_width=True,
                     disabled=(total == 0)):
            st.session_state.collection = []
            st.rerun()

    # ── Tabs ──────────────────────────────────
    tab_design, tab_sheet = st.tabs(["✏️  Designer", "🖨️  Print Sheet"])

    # ═══════════════════════════════════════════
    # DESIGNER TAB
    # ═══════════════════════════════════════════
    with tab_design:

        mode = st.radio(
            "Component type",
            ["Straight / Transition", "Elbow / Bend"],
            horizontal=True,
            label_visibility="collapsed",
        )

        fig          = None
        current_piece = None

        c_form, c_prev = st.columns([1, 1.15], gap="large")

        # ── Form panel ────────────────────────
        with c_form:
            with st.container(border=True):

                # ─── STRAIGHT ─────────────────
                if mode == "Straight / Transition":
                    st.markdown("#### 📐 Dimensions")
                    c1, c2 = st.columns(2)
                    tw = c1.number_input("Top Width (mm)",   value=450, step=10, min_value=1)
                    th = c2.number_input("Top Height (mm)",  value=250, step=10, min_value=1)
                    c3, c4 = st.columns(2)
                    bw = c3.number_input("Btm Width (mm)",   value=450, step=10, min_value=1)
                    bh = c4.number_input("Btm Height (mm)",  value=250, step=10, min_value=1)
                    L  = st.number_input("Length (mm)",      value=1400, step=50, min_value=1)

                    # Transition flag
                    is_transition = not (tw == bw and th == bh)
                    if is_transition:
                        st.caption("⚠️ Transition detected — top ≠ bottom.")

                    st.markdown("#### 🔗 Connections")
                    conn_opts = ["TDF", "SLIDE", "RAW", "None"]
                    c5, c6 = st.columns(2)
                    ct = c5.selectbox("Top Connection", conn_opts, key="ct")
                    cb = c6.selectbox("Btm Connection", conn_opts, key="cb")

                    with st.expander("⚙️ Offset, Alignment & Insulation"):
                        align_h   = st.selectbox("Horizontal Alignment",
                                                 ["Center", "Left Flat", "Right Flat"])
                        align_v   = st.selectbox("Vertical Alignment",
                                                 ["Center", "Flat Top", "Flat Bottom"])
                        ins_opts  = _insulation_options()
                        ins_label = st.selectbox("Insulation", list(ins_opts.keys()))
                        ins_val   = ins_opts[ins_label]

                        st.markdown("**Kick / Shift**")
                        cc1, cc2 = st.columns([1, 2])
                        shift_dir = cc1.selectbox("Direction", ["None", "Left", "Right"],
                                                  key="shift_dir")
                        shift_val = cc2.number_input(
                            "Distance (mm)", min_value=0.0, value=0.0,
                            disabled=(shift_dir == "None"), key="shift_val")

                    try:
                        current_piece = StraightPiece(
                            project=project_name,
                            top_width=tw, top_height=th,
                            btm_width=bw, btm_height=bh,
                            length=L,
                            conn_top=ct, conn_btm=cb,
                            h_align=align_h, v_align=align_v,
                            insulation=ins_val,
                            shift_side=shift_dir,
                            shift_val=shift_val if shift_dir != "None" else 0.0,
                        )
                        fig = HVACRenderer.render_straight(current_piece)
                    except Exception as e:
                        st.error(f"Invalid input: {e}")

                # ─── BEND ─────────────────────
                else:
                    st.markdown("#### 📐 Dimensions")
                    c1, c2 = st.columns(2)
                    w   = c1.number_input("Width (mm)",         value=450, step=10, min_value=1)
                    h   = c2.number_input("Height (mm)",        value=250, step=10, min_value=1)
                    c3, c4 = st.columns(2)
                    rad_val = c3.number_input("Throat Radius (mm)", value=150, step=10, min_value=1)
                    ang     = c4.slider("Angle (°)", min_value=5, max_value=180,
                                        value=90, step=5)

                    # Warn if throat radius is very small vs width
                    if rad_val < w * 0.2:
                        st.warning("⚠️ Throat radius is very tight relative to duct width.")

                    st.markdown("#### 🔗 Connections")
                    conn_opts = ["TDF", "SLIDE", "RAW"]
                    c5, c6 = st.columns(2)
                    conn_in  = c5.selectbox("Inlet Connection",  conn_opts, key="ci")
                    conn_out = c6.selectbox("Outlet Connection", conn_opts, key="co")
                    vanes    = st.checkbox("Include Turning Vanes", value=True)

                    try:
                        current_piece = BendPiece(
                            project=project_name,
                            width=w, height=h,
                            radius=rad_val, angle=ang,
                            conn_in=conn_in, conn_out=conn_out,
                            vanes=vanes,
                        )
                        fig = HVACRenderer.render_bend(current_piece)
                    except Exception as e:
                        st.error(f"Invalid input: {e}")

            # ── Add to sheet button ────────────
            st.markdown("")
            if fig is not None and current_piece is not None:
                if st.button("➕  Add to Sheet", type="primary",
                             use_container_width=True):
                    png = fig_to_png(fig)
                    st.session_state.collection.append({
                        "id":    current_piece.id,
                        "label": current_piece.label,
                        "image": png,
                        "type":  current_piece.piece_type,
                    })
                    st.toast(f"✅ Added: {current_piece.label}", icon="✅")
                    st.rerun()

        # ── Preview panel ─────────────────────
        with c_prev:
            st.markdown('<p class="preview-label">Live Preview</p>',
                        unsafe_allow_html=True)
            if fig is not None:
                st.pyplot(fig, use_container_width=True)
            else:
                st.info("Fill in the form to see a live preview.")

    # ═══════════════════════════════════════════
    # PRINT SHEET TAB
    # ═══════════════════════════════════════════
    with tab_sheet:
        if not st.session_state.collection:
            st.info("No pieces added yet. Go to the **Designer** tab to add some.")
        else:
            st.subheader(f"Job Sheet — {project_name}")
            st.caption(f"{len(st.session_state.collection)} piece(s) · "
                       f"Today: {date.today().strftime('%d %b %Y')}")

            # ── Item list ─────────────────────
            st.markdown("#### Review Items")
            for idx, item in enumerate(st.session_state.collection):
                c_img, c_info, c_del = st.columns([1, 4, 1])
                with c_img:
                    st.image(item["image"], width=72)
                with c_info:
                    type_icon = "↔️" if item["type"] == "Straight" else "↩️"
                    st.markdown(f"**{type_icon} #{idx+1} — {item['type']}**")
                    st.caption(item["label"])
                with c_del:
                    st.markdown("")   # vertical nudge
                    if st.button("✕", key=f"del_{item['id']}",
                                 help="Remove this piece"):
                        st.session_state.collection.pop(idx)
                        st.rerun()
                st.divider()

            # ── Export ────────────────────────
            st.markdown("#### Export")
            if st.button("🖨️  Generate Fabrication Sheet (A4)",
                         type="primary", use_container_width=True):
                html = _build_print_html(project_name,
                                         st.session_state.collection)
                st.components.v1.html(html, height=820, scrolling=True)
                st.success("Print dialog should open automatically. "
                           "If not, use Ctrl+P / Cmd+P in the preview frame.")


if __name__ == "__main__":
    main()
