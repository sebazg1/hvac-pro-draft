import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon, Arc, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import io
import base64
import uuid
from datetime import date
from pydantic import BaseModel, Field
from typing import Literal

# ═══════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ═══════════════════════════════════════════════════════
st.set_page_config(
    layout="centered",
    page_title="HVAC Fabricator",
    page_icon="🏗️",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Force light mode always ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #f5f6f8 !important;
    color: #0f172a !important;
}
[data-testid="stSidebar"] { background: #ffffff !important; }

/* ── Typography ── */
*, body, p, div, span, label {
    font-family: 'Inter', sans-serif !important;
    color: #0f172a;
}

/* ── Top padding ── */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 4rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 520px !important;
    margin: 0 auto;
}

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── App header bar ── */
.app-header {
    background: #0f172a;
    color: white;
    padding: 14px 18px;
    border-radius: 14px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.app-header-title {
    font-size: 17px;
    font-weight: 700;
    color: white;
    letter-spacing: -0.3px;
}
.app-header-sub {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 1px;
}
.app-header-badge {
    background: #1e3a5f;
    color: #60a5fa;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #e2e8f0;
    gap: 2px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    color: #64748b !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #0f172a !important;
    color: #ffffff !important;
}

/* ── Section cards ── */
.section-card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e8eaed;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.section-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── Type selector ── */
.stRadio > div {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    padding: 4px;
    gap: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.stRadio > div > label {
    border-radius: 9px !important;
    padding: 8px 14px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    flex: 1;
    text-align: center;
    cursor: pointer;
    border: none !important;
}
[data-testid="stRadio"] label[data-checked="true"] {
    background: #0f172a !important;
    color: white !important;
}

/* ── Number inputs ── */
div[data-testid="stNumberInput"] {
    background: #f8fafc;
    border-radius: 10px;
    border: 1.5px solid #e2e8f0;
    overflow: hidden;
    transition: border-color 0.15s;
}
div[data-testid="stNumberInput"]:focus-within {
    border-color: #3b82f6;
    background: #fff;
}
div[data-testid="stNumberInput"] input {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    color: #0f172a !important;
    background: transparent !important;
    border: none !important;
}
div[data-testid="stNumberInput"] label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    margin-bottom: 4px !important;
}

/* ── Selectbox ── */
div[data-testid="stSelectbox"] > div > div {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #0f172a !important;
}
div[data-testid="stSelectbox"] label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #475569 !important;
}

/* ── Slider ── */
div[data-testid="stSlider"] label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #475569 !important;
}
div[data-testid="stSlider"] [data-testid="stSliderThumb"] {
    background: #0f172a !important;
}

/* ── Checkbox ── */
div[data-testid="stCheckbox"] label {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #0f172a !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 12px 20px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #ffffff !important;
    color: #0f172a !important;
    transition: all 0.15s ease !important;
    width: 100%;
}
.stButton > button:hover {
    border-color: #0f172a !important;
    background: #0f172a !important;
    color: white !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}
.stButton > button[kind="primary"] {
    background: #0f172a !important;
    color: white !important;
    border-color: #0f172a !important;
    font-size: 15px !important;
    padding: 14px 20px !important;
    box-shadow: 0 4px 14px rgba(15,23,42,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1e293b !important;
    box-shadow: 0 6px 20px rgba(15,23,42,0.35) !important;
}

/* ── Preview container ── */
.preview-wrap {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e8eaed;
    padding: 12px;
    margin-top: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.preview-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 8px;
    text-align: center;
}

/* ── Sheet item rows ── */
.item-row {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e8eaed;
    padding: 10px 12px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.item-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
    min-width: 28px;
}
.item-info { flex: 1; }
.item-type {
    font-size: 12px;
    font-weight: 700;
    color: #0f172a;
}
.item-dim {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #64748b;
    margin-top: 1px;
}

/* ── Info / warning boxes ── */
div[data-testid="stInfo"] {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 10px !important;
    color: #1e40af !important;
}
div[data-testid="stWarning"] {
    background: #fffbeb !important;
    border: 1px solid #fcd34d !important;
    border-radius: 10px !important;
}

/* ── Expander ── */
details {
    background: #f8fafc;
    border-radius: 10px;
    border: 1px solid #e2e8f0 !important;
    padding: 2px 12px !important;
}
details summary {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #64748b !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 10px 0 !important;
}

/* ── Metric ── */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e8eaed;
    border-radius: 12px;
    padding: 12px 14px;
    text-align: center;
}
div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Divider ── */
hr { border-color: #f1f5f9 !important; margin: 8px 0 !important; }

/* ── Text input ── */
div[data-testid="stTextInput"] input {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    color: #0f172a !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# 2. DATA MODELS
# ═══════════════════════════════════════════════════════

class BasePiece(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project: str = "Job-101"
    piece_type: Literal["Straight", "Bend"]
    qty: int = 1
    notes: str = ""


class StraightPiece(BasePiece):
    piece_type: Literal["Straight"] = "Straight"
    top_width:  float = Field(..., gt=0)
    top_height: float = Field(..., gt=0)
    btm_width:  float = Field(..., gt=0)
    btm_height: float = Field(..., gt=0)
    length:     float = Field(..., gt=0)
    conn_top:   str   = "TDF"
    conn_btm:   str   = "TDF"
    insulation: int   = 0
    h_align:    Literal["Center", "Left Flat", "Right Flat"] = "Center"
    v_align:    Literal["Center", "Flat Top", "Flat Bottom"] = "Center"
    shift_side: Literal["None", "Left", "Right"] = "None"
    shift_val:  float = Field(default=0.0, ge=0)

    @property
    def label(self) -> str:
        top = f"{int(self.top_width)}×{int(self.top_height)}"
        btm = f"{int(self.btm_width)}×{int(self.btm_height)}"
        if top == btm:
            return f"{top}  L={int(self.length)}"
        return f"{top} / {btm}  L={int(self.length)}"

    @property
    def is_transition(self) -> bool:
        return not (self.top_width == self.btm_width and
                    self.top_height == self.btm_height)


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
        return (f"{int(self.width)}×{int(self.height)}"
                f"  R{int(self.radius)}  {int(self.angle)}°")


# ═══════════════════════════════════════════════════════
# 3. RENDERING ENGINE  (engineering drawing style)
# ═══════════════════════════════════════════════════════

# Colour palette – technical drawing on white
INK    = "#0d1117"   # body lines
DIM    = "#2563eb"   # dimension lines & text
ANN    = "#dc2626"   # annotations / radius callout
HATCH  = "#94a3b8"   # light hatch / vane lines
CONN   = "#059669"   # connection labels

LW_BODY = 2.2
LW_DIM  = 1.0
LW_THIN = 0.7


class HVACRenderer:

    @staticmethod
    def _create_fig(w=5.5, h=7.5):
        fig = plt.Figure(figsize=(w, h), facecolor="white", dpi=150)
        ax  = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor("white")
        ax.set_aspect("equal")
        ax.axis("off")
        return fig, ax

    # ── dimension line helper ────────────────────────
    @staticmethod
    def _dim_line(ax, x1, y1, x2, y2, label, offset=80, side="right"):
        """Draw a dimension line with arrows and label."""
        dx, dy = x2 - x1, y2 - y1
        length = np.hypot(dx, dy)
        if length == 0:
            return
        nx, ny = -dy / length, dx / length   # normal
        if side == "left":
            nx, ny = -nx, -ny
        ox, oy = nx * offset, ny * offset

        # extension lines
        ax.plot([x1, x1 + ox], [y1, y1 + oy], color=DIM, lw=LW_THIN, zorder=3)
        ax.plot([x2, x2 + ox], [y2, y2 + oy], color=DIM, lw=LW_THIN, zorder=3)
        # main line with arrows
        ax.annotate("", xy=(x2 + ox, y2 + oy), xytext=(x1 + ox, y1 + oy),
                    arrowprops=dict(arrowstyle="<->", color=DIM, lw=LW_DIM),
                    zorder=4)
        # label
        mx, my = (x1 + x2) / 2 + ox * 1.4, (y1 + y2) / 2 + oy * 1.4
        angle  = np.degrees(np.arctan2(dy, dx))
        if abs(angle) > 90:
            angle += 180
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=8.5, color=DIM, weight="bold",
                rotation=angle, rotation_mode="anchor", zorder=5)

    # ── STRAIGHT / TRANSITION ───────────────────────
    @staticmethod
    def render_straight(p: StraightPiece):
        fig, ax = HVACRenderer._create_fig()

        # geometry
        sv = p.shift_val if p.shift_side != "None" else 0.0
        max_w = max(p.top_width, p.btm_width) + sv
        xt = xb = 0.0

        if p.shift_side == "Left":
            xt, xb = 0.0, sv
        elif p.shift_side == "Right":
            xt, xb = sv, 0.0
        else:
            if p.h_align == "Left Flat":
                xt = xb = 0.0
            elif p.h_align == "Right Flat":
                xt = max_w - p.top_width
                xb = max_w - p.btm_width
            else:
                xt = (max_w - p.top_width)  / 2
                xb = (max_w - p.btm_width) / 2

        yt, yb = p.length, 0.0
        tl = (xt,               yt)
        tr = (xt + p.top_width, yt)
        bl = (xb,               yb)
        br = (xb + p.btm_width, yb)

        # ── body ──
        body = Polygon([bl, br, tr, tl], closed=True,
                       fill=False, linewidth=LW_BODY, edgecolor=INK, zorder=2)
        ax.add_patch(body)

        # ── light interior hatch for transition ──
        if p.is_transition:
            for frac in np.linspace(0.2, 0.8, 5):
                hx1 = bl[0] + (tl[0] - bl[0]) * frac
                hx2 = br[0] + (tr[0] - br[0]) * frac
                hy  = yb + (yt - yb) * frac
                ax.plot([hx1, hx2], [hy, hy],
                        color=HATCH, lw=0.4, alpha=0.5, zorder=1)

        # ── width dimension lines (top & btm) ──
        gap = p.length * 0.08
        HVACRenderer._dim_line(ax, tl[0], yt + gap, tr[0], yt + gap,
                               f"{int(p.top_width)}", offset=0, side="right")
        HVACRenderer._dim_line(ax, bl[0], yb - gap, br[0], yb - gap,
                               f"{int(p.btm_width)}", offset=0, side="left")

        # ── length dimension line (right side) ──
        right_x = max(tr[0], br[0])
        HVACRenderer._dim_line(ax, right_x, yb, right_x, yt,
                               f"L = {int(p.length)}", offset=max_w * 0.18)

        # ── size labels (bold, inside) ──
        cx_top = xt + p.top_width  / 2
        cx_btm = xb + p.btm_width / 2
        ax.text(cx_top, yt - p.length * 0.06,
                f"{int(p.top_width)} × {int(p.top_height)}",
                ha="center", va="top",
                fontsize=10, weight="bold", color=INK, zorder=5)
        ax.text(cx_btm, yb + p.length * 0.06,
                f"{int(p.btm_width)} × {int(p.btm_height)}",
                ha="center", va="bottom",
                fontsize=10, weight="bold", color=INK, zorder=5)

        # ── connection labels ──
        left_x = min(tl[0], bl[0])
        if p.conn_top != "None":
            ax.text(left_x - max_w * 0.05, yt,
                    p.conn_top, ha="right", va="center",
                    fontsize=8.5, color=CONN, weight="bold",
                    style="italic", zorder=5)
        if p.conn_btm != "None":
            ax.text(left_x - max_w * 0.05, yb,
                    p.conn_btm, ha="right", va="center",
                    fontsize=8.5, color=CONN, weight="bold",
                    style="italic", zorder=5)

        # ── kick / shift annotation ──
        if sv > 0 and p.shift_side != "None":
            if p.shift_side == "Left":
                ax.annotate("", xy=(bl[0], yb + p.length * 0.04),
                            xytext=(tl[0], yb + p.length * 0.04),
                            arrowprops=dict(arrowstyle="<->", color=ANN, lw=1.3))
                ax.plot([tl[0], tl[0]], [yt, yb + p.length * 0.04],
                        color=ANN, lw=0.8, ls="--")
                mx = (tl[0] + bl[0]) / 2
                ax.text(mx, yb + p.length * 0.09,
                        f"⟵ {int(sv)} mm", ha="center",
                        fontsize=8, color=ANN, weight="bold")
            else:
                ax.annotate("", xy=(br[0], yb + p.length * 0.04),
                            xytext=(tr[0], yb + p.length * 0.04),
                            arrowprops=dict(arrowstyle="<->", color=ANN, lw=1.3))
                ax.plot([tr[0], tr[0]], [yt, yb + p.length * 0.04],
                        color=ANN, lw=0.8, ls="--")
                mx = (tr[0] + br[0]) / 2
                ax.text(mx, yb + p.length * 0.09,
                        f"{int(sv)} mm ⟶", ha="center",
                        fontsize=8, color=ANN, weight="bold")

        # ── watermark tags ──
        tags = []
        if p.v_align == "Flat Top":    tags.append("FOT")
        if p.v_align == "Flat Bottom": tags.append("FOB")
        if p.insulation > 0:           tags.append(f"{p.insulation}mm INS")
        if p.is_transition:            tags.append("TRANSITION")
        if tags:
            cx = (tl[0] + tr[0] + bl[0] + br[0]) / 4
            ax.text(cx, p.length * 0.5, "\n".join(tags),
                    ha="center", va="center",
                    fontsize=11, weight="black", alpha=0.07,
                    color=INK, zorder=1)

        ax.autoscale_view()
        ax.margins(0.25)
        return fig

    # ── ELBOW / BEND ────────────────────────────────
    @staticmethod
    def render_bend(p: BendPiece):
        fig, ax = HVACRenderer._create_fig(w=6, h=6)

        r_in  = p.radius
        r_out = p.radius + p.width
        center = (0.0, 0.0)
        rad    = np.radians(p.angle)

        # ── body arcs ──
        arc_in  = Arc(center, 2*r_in,  2*r_in,
                      angle=0, theta1=0, theta2=p.angle,
                      color=INK, lw=LW_BODY, zorder=2)
        arc_out = Arc(center, 2*r_out, 2*r_out,
                      angle=0, theta1=0, theta2=p.angle,
                      color=INK, lw=LW_BODY, zorder=2)
        ax.add_patch(arc_in)
        ax.add_patch(arc_out)

        # ── end caps ──
        ax.plot([r_in, r_out], [0, 0],
                color=INK, lw=LW_BODY, zorder=2)
        ax.plot([r_in  * np.cos(rad), r_out * np.cos(rad)],
                [r_in  * np.sin(rad), r_out * np.sin(rad)],
                color=INK, lw=LW_BODY, zorder=2)

        # ── turning vanes ──
        if p.vanes:
            n = 3
            for i in range(1, n + 1):
                rv = r_in + p.width * (i / (n + 1))
                vane = Arc(center, 2*rv, 2*rv,
                           angle=0, theta1=0, theta2=p.angle,
                           color=HATCH, lw=0.9, ls=(0, (4, 3)), zorder=1)
                ax.add_patch(vane)
            # label
            mid_ang = np.radians(p.angle / 2)
            rv_mid  = r_in + p.width * 0.5
            ax.text(rv_mid * np.cos(mid_ang) * 0.6,
                    rv_mid * np.sin(mid_ang) * 0.6,
                    "TV", ha="center", va="center",
                    fontsize=7, color=HATCH, weight="bold", alpha=0.7)

        # ── throat radius callout ──
        mid_ang  = np.radians(p.angle / 2)
        rt_x = r_in * np.cos(mid_ang)
        rt_y = r_in * np.sin(mid_ang)
        txt_r = max(r_in * 0.4, 20)
        ax.annotate(f"R{int(r_in)}",
                    xy=(rt_x, rt_y),
                    xytext=(txt_r * np.cos(mid_ang), txt_r * np.sin(mid_ang)),
                    arrowprops=dict(arrowstyle="->", color=ANN,
                                   lw=1.3, shrinkA=2, shrinkB=3),
                    fontsize=9, color=ANN, weight="bold",
                    ha="center", va="center", zorder=5)

        # ── size label ──
        text_r = r_out + max(p.width * 0.4, 70)
        ax.text(text_r * np.cos(mid_ang), text_r * np.sin(mid_ang),
                f"{int(p.width)} × {int(p.height)}\n{p.angle:.0f}°",
                ha="center", va="center",
                fontsize=10, weight="bold", color=INK, zorder=5)

        # ── angle dimension arc ──
        arc_dim_r = r_out + max(p.width * 0.15, 40)
        arc_ang   = Arc(center, 2*arc_dim_r, 2*arc_dim_r,
                        angle=0, theta1=0, theta2=p.angle,
                        color=DIM, lw=LW_DIM, ls="--", zorder=3)
        ax.add_patch(arc_ang)

        # ── connection labels ──
        r_mid = r_in + p.width / 2
        ax.text(r_mid, -max(p.width * 0.22, 45),
                p.conn_in, ha="center", va="top",
                fontsize=8.5, color=CONN, weight="bold", style="italic")
        ex = r_mid * np.cos(rad)
        ey = r_mid * np.sin(rad)
        off = max(p.width * 0.22, 45)
        ax.text(ex - np.sin(rad) * off, ey + np.cos(rad) * off,
                p.conn_out, ha="center", va="center",
                fontsize=8.5, color=CONN, weight="bold",
                style="italic", rotation=p.angle - 90)

        ax.autoscale_view()
        ax.margins(0.25)
        return fig


# ═══════════════════════════════════════════════════════
# 4. HELPERS
# ═══════════════════════════════════════════════════════

def fig_to_png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight",
                dpi=160, facecolor="white")
    buf.seek(0)
    data = buf.getvalue()
    plt.close(fig)
    return data


def insulation_map() -> dict:
    return {"None": 0, "13 mm": 13, "25 mm": 25, "50 mm": 50}


def _build_print_html(project: str, items: list,
                       start_num: int, prepared_by: str) -> str:
    today = date.today().strftime("%d %b %Y")
    total = len(items)

    cards_html = ""
    for i, item in enumerate(items):
        num     = start_num + i
        img_b64 = base64.b64encode(item["image"]).decode()
        qty_str = f"QTY: {item.get('qty', 1)}"
        notes   = item.get("notes", "").strip()
        conn    = item.get("connections", "")
        ins     = item.get("insulation_label", "")
        extras  = "  |  ".join(filter(None, [conn, ins]))

        cards_html += f"""
        <div class="card">
          <div class="card-head">
            <span class="card-num">#{num}</span>
            <span class="card-type">{item['type']}</span>
            <span class="card-qty">{qty_str}</span>
          </div>
          <div class="card-img-wrap">
            <img src="data:image/png;base64,{img_b64}" alt="piece {num}">
          </div>
          <div class="card-foot">
            <div class="card-dim">{item['label']}</div>
            {f'<div class="card-extras">{extras}</div>' if extras else ''}
            {f'<div class="card-notes">✎ {notes}</div>' if notes else ''}
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{project} — Fabrication Sheet</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  @page {{ size: A4 portrait; margin: 8mm; }}

  body {{
    font-family: 'Inter', sans-serif;
    background: #fff;
    color: #0f172a;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  /* ── Page header ── */
  .page-header {{
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: end;
    border-bottom: 3px solid #0f172a;
    padding-bottom: 5px;
    margin-bottom: 8px;
  }}
  .ph-left h1 {{
    font-size: 16px;
    font-weight: 800;
    letter-spacing: -0.3px;
    text-transform: uppercase;
  }}
  .ph-left .project {{
    font-size: 11px;
    color: #475569;
    margin-top: 1px;
    font-weight: 600;
  }}
  .ph-right {{
    text-align: right;
    font-size: 8.5px;
    color: #64748b;
    line-height: 1.7;
  }}
  .ph-right strong {{ color: #0f172a; }}

  /* ── Summary bar ── */
  .summary-bar {{
    display: flex;
    gap: 6px;
    margin-bottom: 8px;
    font-size: 8px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #475569;
  }}
  .summary-pill {{
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 3px 8px;
  }}

  /* ── Grid ── */
  .grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
  }}

  /* ── Card ── */
  .card {{
    border: 1.5px solid #cbd5e1;
    border-radius: 6px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 85mm;
    break-inside: avoid;
    page-break-inside: avoid;
  }}

  .card-head {{
    background: #0f172a;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 3px 6px;
    flex-shrink: 0;
  }}
  .card-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    font-weight: 600;
    color: #94a3b8;
  }}
  .card-type {{
    font-size: 8px;
    font-weight: 700;
    color: #e2e8f0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  .card-qty {{
    font-size: 8px;
    font-weight: 700;
    color: #60a5fa;
    font-family: 'JetBrains Mono', monospace;
  }}

  .card-img-wrap {{
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
    background: #fff;
    min-height: 0;
    overflow: hidden;
  }}
  .card-img-wrap img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }}

  .card-foot {{
    border-top: 1px solid #e2e8f0;
    padding: 3px 5px;
    background: #f8fafc;
    flex-shrink: 0;
  }}
  .card-dim {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 7.5px;
    font-weight: 600;
    color: #0f172a;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .card-extras {{
    font-size: 7px;
    color: #059669;
    font-weight: 600;
    margin-top: 1px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .card-notes {{
    font-size: 7px;
    color: #d97706;
    font-style: italic;
    margin-top: 1px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  /* ── Footer ── */
  .page-footer {{
    margin-top: 10px;
    border-top: 1px solid #e2e8f0;
    padding-top: 4px;
    display: flex;
    justify-content: space-between;
    font-size: 7.5px;
    color: #94a3b8;
  }}

  @media print {{
    .no-print {{ display: none !important; }}
  }}
</style>
</head>
<body>

<div class="page-header">
  <div class="ph-left">
    <h1>Fabrication Sheet</h1>
    <div class="project">Project: {project}</div>
  </div>
  <div class="ph-right">
    <strong>Date:</strong> {today}<br>
    <strong>Prepared by:</strong> {prepared_by or '—'}<br>
    <strong>Items:</strong> #{start_num} – #{start_num + total - 1}
  </div>
</div>

<div class="summary-bar">
  <div class="summary-pill">Total pieces: {total}</div>
  <div class="summary-pill">Numbers: #{start_num} → #{start_num + total - 1}</div>
</div>

<div class="grid">
  {cards_html}
</div>

<div class="page-footer">
  <span>HVAC Fabricator Pro</span>
  <span>{project} · {today}</span>
  <span>Page 1</span>
</div>

<script>window.onload = function(){{ window.print(); }}</script>
</body>
</html>"""


# ═══════════════════════════════════════════════════════
# 5. MAIN UI
# ═══════════════════════════════════════════════════════

def main():
    # session state
    if "collection" not in st.session_state:
        st.session_state.collection = []
    if "start_num" not in st.session_state:
        st.session_state.start_num = 1
    if "project" not in st.session_state:
        st.session_state.project = "Job-101"
    if "prepared_by" not in st.session_state:
        st.session_state.prepared_by = ""

    total = len(st.session_state.collection)

    # ── App header ────────────────────────────────────
    st.markdown(f"""
    <div class="app-header">
      <div>
        <div class="app-header-title">🏗️ HVAC Fabricator</div>
        <div class="app-header-sub">{st.session_state.project}</div>
      </div>
      <div class="app-header-badge">{total} pcs</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────
    tab_design, tab_sheet, tab_settings = st.tabs(
        ["✏️ Design", "🖨️ Print Sheet", "⚙️ Settings"])

    # ═══════════════════════════════════════════════
    # DESIGNER TAB
    # ═══════════════════════════════════════════════
    with tab_design:

        # type toggle
        mode = st.radio(
            "type", ["↔  Straight / Transition", "↩  Elbow / Bend"],
            horizontal=True, label_visibility="collapsed",
            key="mode_radio"
        )
        is_straight = "Straight" in mode

        fig           = None
        current_piece = None

        # ── STRAIGHT form ────────────────────────────
        if is_straight:
            st.markdown('<div class="section-card">'
                        '<div class="section-title">📐 Dimensions</div>', True)

            c1, c2 = st.columns(2)
            tw = c1.number_input("Top W (mm)",  value=450, step=10, min_value=1, key="tw")
            th = c2.number_input("Top H (mm)",  value=250, step=10, min_value=1, key="th")
            c3, c4 = st.columns(2)
            bw = c3.number_input("Btm W (mm)",  value=450, step=10, min_value=1, key="bw")
            bh = c4.number_input("Btm H (mm)",  value=250, step=10, min_value=1, key="bh")
            L  = st.number_input("Length (mm)", value=1400, step=50, min_value=1, key="L")

            st.markdown('</div>', True)

            st.markdown('<div class="section-card">'
                        '<div class="section-title">🔗 Connections</div>', True)
            opts = ["TDF", "SLIDE", "RAW", "None"]
            c5, c6 = st.columns(2)
            ct = c5.selectbox("Top", opts, key="ct")
            cb = c6.selectbox("Bottom", opts, key="cb")
            st.markdown('</div>', True)

            with st.expander("⚙️  OFFSET · ALIGNMENT · INSULATION"):
                align_h   = st.selectbox("Horizontal", ["Center","Left Flat","Right Flat"], key="ah")
                align_v   = st.selectbox("Vertical",   ["Center","Flat Top","Flat Bottom"], key="av")
                ins_map   = insulation_map()
                ins_label = st.selectbox("Insulation", list(ins_map.keys()), key="ins")
                ins_val   = ins_map[ins_label]
                st.markdown("**Kick / Shift**")
                ca, cb2 = st.columns([1, 2])
                shift_dir = ca.selectbox("Dir", ["None","Left","Right"], key="sd")
                shift_val = cb2.number_input("Distance (mm)", min_value=0.0,
                                             value=0.0, key="sv",
                                             disabled=(shift_dir == "None"))

            with st.expander("📝  QUANTITY & NOTES"):
                qty   = st.number_input("Quantity", min_value=1, value=1, step=1, key="qty_s")
                notes = st.text_input("Notes (optional)", key="notes_s",
                                      placeholder="e.g. galv sheet, paint red end…")

            try:
                current_piece = StraightPiece(
                    project=st.session_state.project,
                    top_width=tw, top_height=th,
                    btm_width=bw, btm_height=bh, length=L,
                    conn_top=ct, conn_btm=cb,
                    h_align=align_h, v_align=align_v,
                    insulation=ins_val,
                    shift_side=shift_dir,
                    shift_val=shift_val if shift_dir != "None" else 0.0,
                    qty=qty, notes=notes,
                )
                fig = HVACRenderer.render_straight(current_piece)
            except Exception as e:
                st.error(f"⚠️ {e}")

        # ── BEND form ────────────────────────────────
        else:
            st.markdown('<div class="section-card">'
                        '<div class="section-title">📐 Dimensions</div>', True)
            c1, c2 = st.columns(2)
            w   = c1.number_input("Width (mm)",  value=450, step=10, min_value=1, key="bw2")
            h   = c2.number_input("Height (mm)", value=250, step=10, min_value=1, key="bh2")
            c3, c4 = st.columns(2)
            rad_v = c3.number_input("Throat R (mm)", value=150, step=10, min_value=1, key="rad")
            ang   = c4.slider("Angle (°)", 5, 180, 90, step=5, key="ang")

            if rad_v < w * 0.15:
                st.warning("⚠️ Very tight throat radius.")
            st.markdown('</div>', True)

            st.markdown('<div class="section-card">'
                        '<div class="section-title">🔗 Connections</div>', True)
            opts = ["TDF", "SLIDE", "RAW"]
            c5, c6 = st.columns(2)
            conn_in  = c5.selectbox("Inlet",  opts, key="ci")
            conn_out = c6.selectbox("Outlet", opts, key="co")
            vanes    = st.checkbox("Turning Vanes", value=True, key="vanes")
            st.markdown('</div>', True)

            with st.expander("📝  QUANTITY & NOTES"):
                qty   = st.number_input("Quantity", min_value=1, value=1, step=1, key="qty_b")
                notes = st.text_input("Notes (optional)", key="notes_b",
                                      placeholder="e.g. vanes + splitter…")

            try:
                current_piece = BendPiece(
                    project=st.session_state.project,
                    width=w, height=h, radius=rad_v, angle=ang,
                    conn_in=conn_in, conn_out=conn_out,
                    vanes=vanes, qty=qty, notes=notes,
                )
                fig = HVACRenderer.render_bend(current_piece)
            except Exception as e:
                st.error(f"⚠️ {e}")

        # ── Live preview ──────────────────────────────
        if fig is not None:
            st.markdown('<div class="preview-wrap">'
                        '<div class="preview-label">Live Preview</div>', True)
            st.pyplot(fig, use_container_width=True)
            st.markdown('</div>', True)

        # ── Add button ────────────────────────────────
        st.markdown("")
        if fig is not None and current_piece is not None:
            if st.button("➕  Add to Sheet", type="primary",
                         use_container_width=True):
                png = fig_to_png(fig)

                # build connection string for print
                if is_straight:
                    conn_str = f"{current_piece.conn_top} / {current_piece.conn_btm}"
                    ins_lbl  = (f"{current_piece.insulation}mm INS"
                                if current_piece.insulation else "")
                else:
                    conn_str = f"{current_piece.conn_in} / {current_piece.conn_out}"
                    ins_lbl  = ""

                st.session_state.collection.append({
                    "id":               current_piece.id,
                    "label":            current_piece.label,
                    "image":            png,
                    "type":             current_piece.piece_type,
                    "qty":              current_piece.qty,
                    "notes":            current_piece.notes,
                    "connections":      conn_str,
                    "insulation_label": ins_lbl,
                })
                st.toast(f"✅ Added: {current_piece.label}")
                st.rerun()

    # ═══════════════════════════════════════════════
    # PRINT SHEET TAB
    # ═══════════════════════════════════════════════
    with tab_sheet:
        if not st.session_state.collection:
            st.info("No pieces yet. Go to **Design** tab and add some.")
        else:
            n = len(st.session_state.collection)
            start = st.session_state.start_num

            # summary metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Pieces", n)
            c2.metric("First #", f"#{start}")
            c3.metric("Last #",  f"#{start + n - 1}")

            st.markdown("")

            # item list
            for idx, item in enumerate(st.session_state.collection):
                num = start + idx
                c_img, c_info, c_del = st.columns([1, 4, 1])
                with c_img:
                    st.image(item["image"], width=60)
                with c_info:
                    icon = "↔️" if item["type"] == "Straight" else "↩️"
                    st.markdown(
                        f"**{icon} #{num} — {item['type']}**  "
                        f"<span style='font-size:11px;color:#64748b;'>"
                        f"QTY {item.get('qty',1)}</span>",
                        unsafe_allow_html=True)
                    st.caption(item["label"])
                    if item.get("notes"):
                        st.caption(f"✎ {item['notes']}")
                with c_del:
                    st.markdown("<br>", True)
                    if st.button("✕", key=f"del_{item['id']}",
                                 help="Remove"):
                        st.session_state.collection.pop(idx)
                        st.rerun()
                st.divider()

            # export
            if st.button("🖨️  Generate Fabrication Sheet",
                         type="primary", use_container_width=True):
                html = _build_print_html(
                    project=st.session_state.project,
                    items=st.session_state.collection,
                    start_num=start,
                    prepared_by=st.session_state.prepared_by,
                )
                st.components.v1.html(html, height=900, scrolling=True)
                st.caption("Print dialog opens automatically. "
                           "Use Ctrl+P / Cmd+P if not.")

    # ═══════════════════════════════════════════════
    # SETTINGS TAB
    # ═══════════════════════════════════════════════
    with tab_settings:
        st.markdown("#### Job Settings")

        new_proj = st.text_input("Project Reference",
                                 value=st.session_state.project, key="proj_input")
        if new_proj != st.session_state.project:
            st.session_state.project = new_proj

        new_by = st.text_input("Prepared By",
                               value=st.session_state.prepared_by, key="by_input",
                               placeholder="Your name or initials")
        if new_by != st.session_state.prepared_by:
            st.session_state.prepared_by = new_by

        st.markdown("#### Piece Numbering")
        new_start = st.number_input(
            "Start numbering from",
            min_value=1, value=st.session_state.start_num, step=1,
            help="Set this if continuing from a previous order.",
            key="start_num_input"
        )
        if new_start != st.session_state.start_num:
            st.session_state.start_num = new_start
            st.rerun()

        if st.session_state.start_num > 1:
            st.info(f"Pieces will be numbered #{st.session_state.start_num} "
                    f"→ #{st.session_state.start_num + total - 1}")

        st.markdown("#### Session")
        total_s = len(st.session_state.collection)
        s_n = sum(1 for x in st.session_state.collection if x["type"] == "Straight")
        b_n = total_s - s_n
        st.caption(f"**{total_s} pieces** in sheet   ·   "
                   f"{s_n} straight / {b_n} bends")

        st.markdown("")
        if st.button("🗑️  Clear All Pieces", type="secondary",
                     use_container_width=True, disabled=(total_s == 0)):
            st.session_state.collection = []
            st.rerun()


if __name__ == "__main__":
    main()
