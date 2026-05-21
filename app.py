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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

/* ── FORCE LIGHT MODE – override everything ── */
:root {
    color-scheme: light only !important;
}
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"],
section.main,
.main .block-container {
    background-color: #f0f2f5 !important;
    color: #0f172a !important;
}
/* kill dark mode on every element */
* {
    color-scheme: light !important;
}

/* ── Layout ── */
.block-container {
    padding: 0.75rem 0.85rem 5rem !important;
    max-width: 500px !important;
    margin: 0 auto !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── App header ── */
.app-hdr {
    background: #0f172a;
    border-radius: 16px;
    padding: 14px 18px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.app-hdr-title { font-size: 18px; font-weight: 800; color: #fff; letter-spacing: -0.4px; }
.app-hdr-sub   { font-size: 11px; color: #94a3b8; margin-top: 2px; font-weight: 500; }
.app-hdr-badge {
    background: #1e3a5f; color: #60a5fa;
    border-radius: 10px; padding: 5px 12px;
    font-size: 13px; font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    padding: 4px !important;
    border: 1.5px solid #e2e8f0 !important;
    gap: 3px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.07) !important;
    margin-bottom: 14px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 9px 14px !important;
    color: #64748b !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #0f172a !important;
    color: #ffffff !important;
}

/* ── Section headers ── */
.sec-hdr {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 16px 0 8px;
    padding-left: 2px;
}

/* ── White card wrapper ── */
.card-wrap {
    background: #ffffff;
    border-radius: 14px;
    border: 1.5px solid #e8eaed;
    padding: 14px 14px 6px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}

/* ── All inputs – force white background & dark text ── */
input[type="number"],
input[type="text"],
input[type="search"] {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    border: 1.5px solid #dde1e7 !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    -webkit-text-fill-color: #0f172a !important;
}
input[type="number"]:focus,
input[type="text"]:focus {
    border-color: #2563eb !important;
    background-color: #ffffff !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
    outline: none !important;
}
/* Number input wrapper */
div[data-testid="stNumberInput"] > div {
    background: #f8fafc !important;
    border: 1.5px solid #dde1e7 !important;
    border-radius: 10px !important;
    overflow: hidden;
}
div[data-testid="stNumberInput"] > div:focus-within {
    border-color: #2563eb !important;
    background: #fff !important;
}
/* Labels above inputs */
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stCheckbox"] label,
div[data-testid="stTextInput"] label {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #475569 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    margin-bottom: 3px !important;
}
/* +/- buttons */
div[data-testid="stNumberInput"] button {
    background: #f1f5f9 !important;
    color: #334155 !important;
    border: none !important;
    font-weight: 700 !important;
}

/* ── Selectbox ── */
div[data-testid="stSelectbox"] > div > div {
    background: #f8fafc !important;
    border: 1.5px solid #dde1e7 !important;
    border-radius: 10px !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

/* ── Slider ── */
div[data-testid="stSlider"] [data-testid="stSliderThumb"] {
    background: #0f172a !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #0f172a !important;
}

/* ── Radio (type toggle) ── */
div[data-testid="stRadio"] > div {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 4px !important;
    gap: 3px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.06) !important;
    display: flex !important;
}
div[data-testid="stRadio"] label {
    border-radius: 9px !important;
    padding: 9px 10px !important;
    flex: 1 !important;
    text-align: center !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    color: #64748b !important;
    cursor: pointer !important;
    transition: all .15s !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: #0f172a !important;
    color: #fff !important;
}
/* hide the actual radio dot */
div[data-testid="stRadio"] input[type="radio"] { display: none !important; }

/* ── Checkbox ── */
div[data-testid="stCheckbox"] {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 12px;
}
div[data-testid="stCheckbox"] label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #0f172a !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: #0f172a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    padding: 15px !important;
    width: 100% !important;
    letter-spacing: -0.2px !important;
    box-shadow: 0 4px 16px rgba(15,23,42,.3) !important;
    transition: all .15s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1e293b !important;
    box-shadow: 0 6px 24px rgba(15,23,42,.4) !important;
    transform: translateY(-1px) !important;
}
/* Secondary / danger button */
.stButton > button:not([kind="primary"]) {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px !important;
    width: 100% !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #0f172a !important;
    background: #f8fafc !important;
}

/* ── Preview box ── */
.preview-box {
    background: #ffffff;
    border-radius: 14px;
    border: 1.5px solid #e8eaed;
    padding: 10px;
    margin-top: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}
.preview-lbl {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #94a3b8;
    text-align: center;
    margin-bottom: 6px;
}

/* ── Sheet item card ── */
.sheet-item {
    background: #ffffff;
    border-radius: 12px;
    border: 1.5px solid #e8eaed;
    margin-bottom: 8px;
    overflow: hidden;
}
.sheet-item-head {
    background: #f8fafc;
    border-bottom: 1px solid #e8eaed;
    padding: 8px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* ── Info/warning ── */
div[data-testid="stInfo"] {
    background: #eff6ff !important;
    border: 1.5px solid #bfdbfe !important;
    border-radius: 12px !important;
    color: #1e40af !important;
}
div[data-testid="stWarning"] {
    background: #fffbeb !important;
    border: 1.5px solid #fcd34d !important;
    border-radius: 12px !important;
}

/* ── Metric ── */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1.5px solid #e8eaed !important;
    border-radius: 12px !important;
    padding: 12px !important;
    text-align: center !important;
}
div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    font-weight: 700 !important;
    color: #94a3b8 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* ── Text input ── */
div[data-testid="stTextInput"] > div {
    background: #f8fafc !important;
    border: 1.5px solid #dde1e7 !important;
    border-radius: 10px !important;
}
div[data-testid="stTextInput"] > div:focus-within {
    border-color: #2563eb !important;
}

/* divider */
hr { border-color: #f1f5f9 !important; margin: 6px 0 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# 2. DATA MODELS
# ═══════════════════════════════════════════════════════

class BasePiece(BaseModel):
    id:         str   = Field(default_factory=lambda: str(uuid.uuid4()))
    project:    str   = "Job-101"
    piece_type: Literal["Straight", "Bend"]
    qty:        int   = 1
    notes:      str   = ""

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
    h_align:    Literal["Center","Left Flat","Right Flat"] = "Center"
    v_align:    Literal["Center","Flat Top","Flat Bottom"] = "Center"
    shift_side: Literal["None","Left","Right"] = "None"
    shift_val:  float = Field(default=0.0, ge=0)

    @property
    def label(self):
        t = f"{int(self.top_width)}x{int(self.top_height)}"
        b = f"{int(self.btm_width)}x{int(self.btm_height)}"
        return f"{t}/{b} L={int(self.length)}" if t != b else f"{t} L={int(self.length)}"

    @property
    def is_transition(self):
        return not (self.top_width==self.btm_width and self.top_height==self.btm_height)

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
    def label(self):
        return f"{int(self.width)}x{int(self.height)} R{int(self.radius)} {int(self.angle)}deg"


# ═══════════════════════════════════════════════════════
# 3. RENDERER
# ═══════════════════════════════════════════════════════

INK   = "#0d1117"
DIM   = "#2563eb"
ANN   = "#dc2626"
CONN  = "#059669"
HATCH = "#cbd5e1"
LW    = 2.0

class HVACRenderer:

    @staticmethod
    def _fig(w=5, h=7):
        fig = plt.Figure(figsize=(w,h), facecolor="white", dpi=150)
        ax  = fig.add_axes([0.05, 0.05, 0.9, 0.9])
        ax.set_facecolor("white")
        ax.set_aspect("equal")
        ax.axis("off")
        return fig, ax

    @staticmethod
    def _arrow_dim(ax, x1,y1, x2,y2, label, gap=0, perp=80):
        """
        Draw a dimension line OUTSIDE the shape.
        gap   = extra offset perpendicular to the line direction
        perp  = how far off to place the line
        """
        dx, dy = x2-x1, y2-y1
        L = np.hypot(dx,dy)
        if L < 1: return
        # unit normal (perpendicular, pointing outward)
        nx, ny = -dy/L, dx/L
        off = perp + gap
        ox, oy = nx*off, ny*off
        # extension lines
        for px,py in [(x1,y1),(x2,y2)]:
            ax.plot([px, px+ox],[py, py+oy],
                    color=DIM, lw=0.7, zorder=3)
        # dimension line with arrows
        ax.annotate("", xy=(x2+ox, y2+oy), xytext=(x1+ox, y1+oy),
                    arrowprops=dict(arrowstyle="<->", color=DIM, lw=1.0), zorder=4)
        # label
        mx = (x1+x2)/2 + ox*1.0
        my = (y1+y2)/2 + oy*1.0
        ang = np.degrees(np.arctan2(dy,dx))
        if abs(ang) > 90: ang += 180
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=8, color=DIM, weight="bold",
                rotation=ang, rotation_mode="anchor", zorder=5)

    # ── STRAIGHT ────────────────────────────────────
    @staticmethod
    def render_straight(p: StraightPiece):
        fig, ax = HVACRenderer._fig(w=5, h=7.5)

        sv = p.shift_val if p.shift_side != "None" else 0.0
        max_w = max(p.top_width, p.btm_width) + sv
        xt = xb = 0.0
        if p.shift_side == "Left":
            xt, xb = 0.0, sv
        elif p.shift_side == "Right":
            xt, xb = sv, 0.0
        else:
            if p.h_align == "Left Flat":   xt=xb=0.0
            elif p.h_align == "Right Flat":
                xt = max_w - p.top_width
                xb = max_w - p.btm_width
            else:
                xt = (max_w-p.top_width)/2
                xb = (max_w-p.btm_width)/2

        yt, yb = p.length, 0.0
        tl=(xt, yt); tr=(xt+p.top_width, yt)
        bl=(xb, yb); br=(xb+p.btm_width, yb)

        # body
        body = Polygon([bl,br,tr,tl], closed=True,
                       fill=False, lw=LW, edgecolor=INK, zorder=2)
        ax.add_patch(body)

        # transition hatch
        if p.is_transition:
            for f in np.linspace(0.15,0.85,6):
                hx1 = bl[0]+(tl[0]-bl[0])*f
                hx2 = br[0]+(tr[0]-br[0])*f
                hy  = yb+(yt-yb)*f
                ax.plot([hx1,hx2],[hy,hy], color=HATCH, lw=0.5, alpha=0.6, zorder=1)

        # --- dimension lines (placed OUTSIDE the body) ---
        pad = max_w * 0.12   # perpendicular distance from edge

        # top width arrow (above top face)
        HVACRenderer._arrow_dim(ax, tl[0],yt, tr[0],yt,
                                f"{int(p.top_width)}", perp=pad)

        # btm width arrow (below bottom face)
        # normal points DOWN so negate perp
        dx = br[0]-bl[0]; dy = 0
        L  = abs(dx)
        # place below: use negative normal (pointing down)
        off = pad
        ax.plot([bl[0], bl[0]], [yb, yb-off], color=DIM, lw=0.7, zorder=3)
        ax.plot([br[0], br[0]], [yb, yb-off], color=DIM, lw=0.7, zorder=3)
        ax.annotate("", xy=(br[0], yb-off), xytext=(bl[0], yb-off),
                    arrowprops=dict(arrowstyle="<->", color=DIM, lw=1.0), zorder=4)
        ax.text((bl[0]+br[0])/2, yb-off*1.8,
                f"{int(p.btm_width)}", ha="center", va="top",
                fontsize=8, color=DIM, weight="bold", zorder=5)

        # length arrow (right of body)
        right_x = max(tr[0],br[0])
        HVACRenderer._arrow_dim(ax, right_x,yb, right_x,yt,
                                f"L={int(p.length)}", perp=pad*1.5)

        # size labels inside
        ax.text(xt+p.top_width/2, yt-p.length*0.05,
                f"{int(p.top_width)} x {int(p.top_height)}",
                ha="center", va="top", fontsize=9.5, weight="bold", color=INK)
        ax.text(xb+p.btm_width/2, yb+p.length*0.05,
                f"{int(p.btm_width)} x {int(p.btm_height)}",
                ha="center", va="bottom", fontsize=9.5, weight="bold", color=INK)

        # connection labels (left side)
        lx = min(tl[0],bl[0]) - max_w*0.05
        if p.conn_top != "None":
            ax.text(lx, yt, p.conn_top, ha="right", va="center",
                    fontsize=8, color=CONN, weight="bold", style="italic")
        if p.conn_btm != "None":
            ax.text(lx, yb, p.conn_btm, ha="right", va="center",
                    fontsize=8, color=CONN, weight="bold", style="italic")

        # shift annotation
        if sv > 0 and p.shift_side != "None":
            cy = yb + p.length*0.15
            if p.shift_side == "Left":
                ax.annotate("", xy=(bl[0],cy), xytext=(tl[0],cy),
                            arrowprops=dict(arrowstyle="<->", color=ANN, lw=1.2))
                ax.text((tl[0]+bl[0])/2, cy+p.length*0.04,
                        f"{int(sv)} mm", ha="center", fontsize=8,
                        color=ANN, weight="bold")
            else:
                ax.annotate("", xy=(br[0],cy), xytext=(tr[0],cy),
                            arrowprops=dict(arrowstyle="<->", color=ANN, lw=1.2))
                ax.text((tr[0]+br[0])/2, cy+p.length*0.04,
                        f"{int(sv)} mm", ha="center", fontsize=8,
                        color=ANN, weight="bold")

        # watermark
        tags=[]
        if p.v_align=="Flat Top":    tags.append("FOT")
        if p.v_align=="Flat Bottom": tags.append("FOB")
        if p.insulation>0:           tags.append(f"{p.insulation}mm INS")
        if p.is_transition:          tags.append("TRANSITION")
        if tags:
            cx=(tl[0]+tr[0]+bl[0]+br[0])/4
            ax.text(cx, p.length*0.5, "\n".join(tags),
                    ha="center",va="center", fontsize=10,
                    weight="black", alpha=0.06, color=INK)

        ax.autoscale_view(); ax.margins(0.28)
        return fig

    # ── BEND ────────────────────────────────────────
    @staticmethod
    def render_bend(p: BendPiece):
        fig, ax = HVACRenderer._fig(w=6, h=6)
        r_in  = p.radius
        r_out = p.radius + p.width
        rad   = np.radians(p.angle)

        arc_in  = Arc((0,0), 2*r_in,  2*r_in,  angle=0,theta1=0,theta2=p.angle,color=INK,lw=LW)
        arc_out = Arc((0,0), 2*r_out, 2*r_out, angle=0,theta1=0,theta2=p.angle,color=INK,lw=LW)
        ax.add_patch(arc_in); ax.add_patch(arc_out)

        ax.plot([r_in,r_out],[0,0], color=INK, lw=LW)
        ax.plot([r_in*np.cos(rad),r_out*np.cos(rad)],
                [r_in*np.sin(rad),r_out*np.sin(rad)], color=INK, lw=LW)

        if p.vanes:
            n=3
            for i in range(1,n+1):
                rv = r_in + p.width*(i/(n+1))
                ax.add_patch(Arc((0,0),2*rv,2*rv,angle=0,theta1=0,theta2=p.angle,
                                 color=HATCH,lw=0.9,ls=(0,(4,3))))
        # radius callout
        mid = np.radians(p.angle/2)
        rx=r_in*np.cos(mid); ry=r_in*np.sin(mid)
        tr_=max(r_in*0.38,18)
        ax.annotate(f"R{int(r_in)}", xy=(rx,ry),
                    xytext=(tr_*np.cos(mid),tr_*np.sin(mid)),
                    arrowprops=dict(arrowstyle="->",color=ANN,lw=1.3,shrinkB=3),
                    fontsize=9, color=ANN, weight="bold", ha="center", va="center")

        # size + angle label
        lr = r_out + max(p.width*0.38,65)
        ax.text(lr*np.cos(mid), lr*np.sin(mid),
                f"{int(p.width)} x {int(p.height)}\n{p.angle:.0f}°",
                ha="center",va="center",fontsize=10,weight="bold",color=INK)

        # dim arc (dashed, outside)
        da_r = r_out + max(p.width*0.12,35)
        ax.add_patch(Arc((0,0),2*da_r,2*da_r,angle=0,theta1=0,theta2=p.angle,
                         color=DIM,lw=0.9,ls="--"))

        # connection labels
        rm = r_in+p.width/2
        off = max(p.width*0.2,42)
        ax.text(rm,-off, p.conn_in, ha="center",va="top",
                fontsize=8,color=CONN,weight="bold",style="italic")
        ex=rm*np.cos(rad); ey=rm*np.sin(rad)
        ax.text(ex-np.sin(rad)*off, ey+np.cos(rad)*off,
                p.conn_out, ha="center",va="center",
                fontsize=8,color=CONN,weight="bold",style="italic",
                rotation=p.angle-90)

        ax.autoscale_view(); ax.margins(0.28)
        return fig


# ═══════════════════════════════════════════════════════
# 4. HELPERS
# ═══════════════════════════════════════════════════════

def fig_to_png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=160, facecolor="white")
    buf.seek(0); data=buf.getvalue(); plt.close(fig)
    return data

def ins_map():
    return {"None":0,"13 mm":13,"25 mm":25,"50 mm":50}

def build_print_html(project, items, start_num, prepared_by):
    today = date.today().strftime("%d %b %Y")
    n     = len(items)
    cards = ""
    for i,item in enumerate(items):
        num   = start_num+i
        b64   = base64.b64encode(item["image"]).decode()
        qty   = item.get("qty",1)
        notes = item.get("notes","").strip()
        conn  = item.get("connections","")
        ins   = item.get("ins_label","")
        extras= " · ".join(filter(None,[conn,ins]))
        cards += f"""
        <div class="card">
          <div class="card-top">
            <span class="cnum">#{num}</span>
            <span class="ctype">{item['type'].upper()}</span>
            <span class="cqty">QTY {qty}</span>
          </div>
          <div class="cimg"><img src="data:image/png;base64,{b64}"></div>
          <div class="cfoot">
            <div class="cdim">{item['label']}</div>
            {f'<div class="cext">{extras}</div>' if extras else ''}
            {f'<div class="cnotes">{notes}</div>' if notes else ''}
          </div>
        </div>"""

    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8">
<title>{project} – Fabrication Sheet</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
@page{{size:A4 portrait;margin:8mm}}
body{{font-family:'Inter',sans-serif;background:#fff;color:#0f172a;
      -webkit-print-color-adjust:exact;print-color-adjust:exact}}

.hdr{{display:grid;grid-template-columns:1fr auto;align-items:end;
       border-bottom:3px solid #0f172a;padding-bottom:5px;margin-bottom:7px}}
.hdr h1{{font-size:15px;font-weight:800;text-transform:uppercase;letter-spacing:-.3px}}
.hdr .proj{{font-size:10px;color:#64748b;font-weight:600;margin-top:2px}}
.hdr .meta{{text-align:right;font-size:8px;color:#64748b;line-height:1.8}}
.hdr .meta strong{{color:#0f172a}}

.sumbar{{display:flex;gap:5px;margin-bottom:7px}}
.spill{{background:#f1f5f9;border:1px solid #e2e8f0;border-radius:5px;
         padding:3px 8px;font-size:7.5px;font-weight:700;
         text-transform:uppercase;letter-spacing:.05em;color:#475569}}

.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:5px}}

.card{{border:1.5px solid #cbd5e1;border-radius:7px;overflow:hidden;
        display:flex;flex-direction:column;height:84mm;
        break-inside:avoid;page-break-inside:avoid}}

.card-top{{background:#0f172a;display:flex;justify-content:space-between;
            align-items:center;padding:3px 7px;flex-shrink:0}}
.cnum{{font-family:'JetBrains Mono',monospace;font-size:8.5px;
        font-weight:700;color:#94a3b8}}
.ctype{{font-size:7.5px;font-weight:800;color:#e2e8f0;
         text-transform:uppercase;letter-spacing:.08em}}
.cqty{{font-size:8px;font-weight:700;color:#60a5fa;
        font-family:'JetBrains Mono',monospace}}

.cimg{{flex:1;display:flex;align-items:center;justify-content:center;
        padding:4px;background:#fff;min-height:0;overflow:hidden}}
.cimg img{{max-width:100%;max-height:100%;object-fit:contain}}

.cfoot{{border-top:1px solid #e2e8f0;padding:3px 6px;
         background:#f8fafc;flex-shrink:0}}
.cdim{{font-family:'JetBrains Mono',monospace;font-size:7px;
        font-weight:700;color:#0f172a;white-space:nowrap;
        overflow:hidden;text-overflow:ellipsis}}
.cext{{font-size:6.5px;color:#059669;font-weight:700;margin-top:1px;
        white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.cnotes{{font-size:6.5px;color:#d97706;font-style:italic;margin-top:1px;
          white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}

.foot{{margin-top:8px;border-top:1px solid #e2e8f0;padding-top:4px;
        display:flex;justify-content:space-between;
        font-size:7px;color:#94a3b8}}
</style></head><body>

<div class="hdr">
  <div>
    <h1>Fabrication Sheet</h1>
    <div class="proj">Project: {project}</div>
  </div>
  <div class="meta">
    <strong>Date:</strong> {today}<br>
    <strong>By:</strong> {prepared_by or "—"}<br>
    <strong>Items:</strong> #{start_num}–#{start_num+n-1}
  </div>
</div>

<div class="sumbar">
  <div class="spill">Total: {n} pieces</div>
  <div class="spill">Numbers: #{start_num} → #{start_num+n-1}</div>
</div>

<div class="grid">{cards}</div>

<div class="foot">
  <span>HVAC Fabricator Pro</span>
  <span>{project} · {today}</span>
</div>

<script>window.onload=function(){{window.print()}}</script>
</body></html>"""


# ═══════════════════════════════════════════════════════
# 5. MAIN UI
# ═══════════════════════════════════════════════════════

def main():
    for k,v in [("collection",[]),("start_num",1),
                ("project","Job-101"),("prepared_by","")]:
        if k not in st.session_state:
            st.session_state[k] = v

    total = len(st.session_state.collection)

    # header
    st.markdown(f"""
    <div class="app-hdr">
      <div>
        <div class="app-hdr-title">🏗️ HVAC Fabricator</div>
        <div class="app-hdr-sub">{st.session_state.project}</div>
      </div>
      <div class="app-hdr-badge">{total} pcs</div>
    </div>""", unsafe_allow_html=True)

    tab_d, tab_p, tab_s = st.tabs(["✏️ Design", "🖨️ Print Sheet", "⚙️ Settings"])

    # ═══════════════════════════════
    # DESIGN TAB
    # ═══════════════════════════════
    with tab_d:
        mode = st.radio("type",
            ["↔  Straight / Transition", "↩  Elbow / Bend"],
            horizontal=True, label_visibility="collapsed")
        is_s = "Straight" in mode

        fig=None; piece=None

        if is_s:
            # ── Dimensions ──
            st.markdown('<div class="sec-hdr">📐 Dimensions</div>', True)
            c1,c2=st.columns(2)
            tw=c1.number_input("Top W (mm)", value=450,step=10,min_value=1,key="tw")
            th=c2.number_input("Top H (mm)", value=250,step=10,min_value=1,key="th")
            c3,c4=st.columns(2)
            bw=c3.number_input("Btm W (mm)", value=450,step=10,min_value=1,key="bw")
            bh=c4.number_input("Btm H (mm)", value=250,step=10,min_value=1,key="bh")
            L =st.number_input("Length (mm)",value=1400,step=50,min_value=1,key="L")

            # ── Connections ──
            st.markdown('<div class="sec-hdr">🔗 Connections</div>', True)
            opts=["TDF","SLIDE","RAW","None"]
            c5,c6=st.columns(2)
            ct=c5.selectbox("Top",opts,key="ct")
            cb=c6.selectbox("Bottom",opts,key="cb")

            # ── Alignment ──
            st.markdown('<div class="sec-hdr">⚙️ Alignment & Insulation</div>', True)
            c7,c8=st.columns(2)
            ah=c7.selectbox("Horizontal",["Center","Left Flat","Right Flat"],key="ah")
            av=c8.selectbox("Vertical",  ["Center","Flat Top","Flat Bottom"],key="av")
            im=ins_map()
            c9,c10=st.columns(2)
            il=c9.selectbox("Insulation",list(im.keys()),key="ins")
            iv=im[il]
            sd=c10.selectbox("Kick",["None","Left","Right"],key="sd")
            sv=st.number_input("Kick distance (mm)",min_value=0.0,value=0.0,
                               key="sv",disabled=(sd=="None"))

            # ── Qty & Notes ──
            st.markdown('<div class="sec-hdr">📝 Quantity & Notes</div>', True)
            c11,c12=st.columns([1,2])
            qty  =c11.number_input("Qty",min_value=1,value=1,step=1,key="qty_s")
            notes=c12.text_input("Notes",key="ns",placeholder="e.g. paint red end")

            try:
                piece=StraightPiece(
                    project=st.session_state.project,
                    top_width=tw,top_height=th,btm_width=bw,btm_height=bh,length=L,
                    conn_top=ct,conn_btm=cb,h_align=ah,v_align=av,
                    insulation=iv,shift_side=sd,
                    shift_val=sv if sd!="None" else 0.0,qty=qty,notes=notes)
                fig=HVACRenderer.render_straight(piece)
                if piece.is_transition:
                    st.info("Transition piece detected")
            except Exception as e:
                st.error(f"Error: {e}")

        else:
            # ── Bend Dimensions ──
            st.markdown('<div class="sec-hdr">📐 Dimensions</div>', True)
            c1,c2=st.columns(2)
            w =c1.number_input("Width (mm)", value=450,step=10,min_value=1,key="bw2")
            h =c2.number_input("Height (mm)",value=250,step=10,min_value=1,key="bh2")
            c3,c4=st.columns(2)
            rv=c3.number_input("Throat R (mm)",value=150,step=10,min_value=1,key="rv")
            an=c4.slider("Angle",5,180,90,step=5,key="ang")
            if rv<w*0.15: st.warning("Very tight throat radius")

            st.markdown('<div class="sec-hdr">🔗 Connections</div>', True)
            c5,c6=st.columns(2)
            ci=c5.selectbox("Inlet", ["TDF","SLIDE","RAW"],key="ci")
            co=c6.selectbox("Outlet",["TDF","SLIDE","RAW"],key="co")
            vanes=st.checkbox("Turning Vanes",value=True,key="vn")

            st.markdown('<div class="sec-hdr">📝 Quantity & Notes</div>', True)
            c7,c8=st.columns([1,2])
            qty  =c7.number_input("Qty",min_value=1,value=1,step=1,key="qty_b")
            notes=c8.text_input("Notes",key="nb",placeholder="e.g. vanes + splitter")

            try:
                piece=BendPiece(
                    project=st.session_state.project,
                    width=w,height=h,radius=rv,angle=an,
                    conn_in=ci,conn_out=co,vanes=vanes,qty=qty,notes=notes)
                fig=HVACRenderer.render_bend(piece)
            except Exception as e:
                st.error(f"Error: {e}")

        # ── Live Preview ──
        if fig is not None:
            st.markdown('<div class="preview-box"><div class="preview-lbl">Live Preview</div>',True)
            st.pyplot(fig, use_container_width=True)
            st.markdown('</div>',True)

        st.markdown("")
        if fig is not None and piece is not None:
            if st.button("➕  Add to Sheet", type="primary", use_container_width=True):
                png=fig_to_png(fig)
                conn_s = (f"{piece.conn_top}/{piece.conn_btm}"
                          if is_s else f"{piece.conn_in}/{piece.conn_out}")
                ins_l  = (f"{piece.insulation}mm INS"
                          if is_s and piece.insulation else "")
                st.session_state.collection.append({
                    "id":piece.id,"label":piece.label,"image":png,
                    "type":piece.piece_type,"qty":piece.qty,
                    "notes":piece.notes,"connections":conn_s,"ins_label":ins_l
                })
                st.toast(f"Added: {piece.label}")
                st.rerun()

    # ═══════════════════════════════
    # PRINT SHEET TAB
    # ═══════════════════════════════
    with tab_p:
        if not st.session_state.collection:
            st.info("No pieces yet — go to Design tab and add some.")
        else:
            n=len(st.session_state.collection)
            s=st.session_state.start_num
            c1,c2,c3=st.columns(3)
            c1.metric("Pieces",n)
            c2.metric("First",f"#{s}")
            c3.metric("Last", f"#{s+n-1}")
            st.markdown("")

            for idx,item in enumerate(st.session_state.collection):
                num=s+idx
                ca,cb,cc=st.columns([1,4,1])
                with ca: st.image(item["image"],width=55)
                with cb:
                    icon="↔️" if item["type"]=="Straight" else "↩️"
                    st.markdown(f"**{icon} #{num} {item['type']}** · QTY {item.get('qty',1)}")
                    st.caption(item["label"])
                    if item.get("notes"): st.caption(f"✎ {item['notes']}")
                with cc:
                    st.markdown("<br>",True)
                    if st.button("✕",key=f"d_{item['id']}",help="Remove"):
                        st.session_state.collection.pop(idx); st.rerun()
                st.divider()

            if st.button("🖨️  Generate Fabrication Sheet",
                         type="primary",use_container_width=True):
                html=build_print_html(
                    st.session_state.project,
                    st.session_state.collection,
                    st.session_state.start_num,
                    st.session_state.prepared_by)
                st.components.v1.html(html,height=920,scrolling=True)
                st.caption("Print dialog opens automatically. Use Ctrl+P / Cmd+P if needed.")

    # ═══════════════════════════════
    # SETTINGS TAB
    # ═══════════════════════════════
    with tab_s:
        st.markdown('<div class="sec-hdr">Job Details</div>',True)
        np_=st.text_input("Project Reference",value=st.session_state.project,key="pi")
        if np_!=st.session_state.project:
            st.session_state.project=np_
        nb_=st.text_input("Prepared By",value=st.session_state.prepared_by,
                          key="bi",placeholder="Your name or initials")
        if nb_!=st.session_state.prepared_by:
            st.session_state.prepared_by=nb_

        st.markdown('<div class="sec-hdr">Piece Numbering</div>',True)
        ns_=st.number_input("Start numbering from",min_value=1,
                            value=st.session_state.start_num,step=1,key="sni",
                            help="Set this if continuing from a previous order")
        if ns_!=st.session_state.start_num:
            st.session_state.start_num=ns_; st.rerun()
        if st.session_state.start_num>1:
            n=len(st.session_state.collection)
            st.info(f"Pieces numbered #{st.session_state.start_num} → "
                    f"#{st.session_state.start_num+n-1}")

        st.markdown('<div class="sec-hdr">Session</div>',True)
        n_=len(st.session_state.collection)
        s_n=sum(1 for x in st.session_state.collection if x["type"]=="Straight")
        st.caption(f"{n_} pieces total · {s_n} straight · {n_-s_n} bends")
        st.markdown("")
        if st.button("🗑️  Clear All Pieces",type="secondary",
                     use_container_width=True,disabled=(n_==0)):
            st.session_state.collection=[]; st.rerun()

if __name__=="__main__":
    main()
