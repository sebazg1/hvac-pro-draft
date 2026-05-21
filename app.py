import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Arc
import numpy as np
import io, base64, uuid
from datetime import date
from pydantic import BaseModel, Field
from typing import Literal

# ══════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════
st.set_page_config(
    layout="centered",
    page_title="HVAC Fabricator",
    page_icon="🏗️",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

/* ── Layout ── */
.block-container {
    padding: 0.75rem 0.9rem 5rem !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
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
.app-hdr-title { font-size: 18px; font-weight: 800; color: #fff; }
.app-hdr-sub   { font-size: 11px; color: #94a3b8; margin-top: 2px; }
.app-hdr-badge {
    background: #1e3a5f; color: #60a5fa;
    border-radius: 10px; padding: 5px 13px;
    font-size: 14px; font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    padding: 4px !important;
    border: 1.5px solid #e2e8f0 !important;
    gap: 3px !important;
    margin-bottom: 14px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 9px 12px !important;
    color: #64748b !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #0f172a !important;
    color: #ffffff !important;
}

/* ── Section headers ── */
.sec {
    font-size: 10px; font-weight: 800;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #94a3b8; margin: 14px 0 6px; padding-left: 2px;
}

/* ── Radio toggle ── */
div[data-testid="stRadio"] > div {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 4px !important; gap: 3px !important;
    display: flex !important;
}
div[data-testid="stRadio"] label {
    border-radius: 9px !important;
    padding: 9px 10px !important; flex: 1 !important;
    text-align: center !important; font-weight: 700 !important;
    font-size: 13px !important; cursor: pointer !important;
}
div[data-testid="stRadio"] input[type="radio"] { display: none !important; }
div[data-testid="stRadio"] label:has(input:checked) {
    background: #0f172a !important; color: #fff !important;
}

/* ── Number inputs ── */
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stCheckbox"] label {
    font-size: 11px !important; font-weight: 700 !important;
    color: #64748b !important; text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
div[data-testid="stNumberInput"] input {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important; font-size: 16px !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: #0f172a !important; color: #fff !important;
    border: none !important; border-radius: 14px !important;
    font-size: 15px !important; font-weight: 800 !important;
    padding: 15px !important; width: 100% !important;
    box-shadow: 0 4px 16px rgba(15,23,42,.25) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1e293b !important;
    box-shadow: 0 6px 20px rgba(15,23,42,.35) !important;
}
/* Secondary button */
.stButton > button:not([kind="primary"]) {
    background: #fff !important; color: #dc2626 !important;
    border: 1.5px solid #fecaca !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-size: 13px !important; padding: 8px !important; width: 100% !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: #fef2f2 !important; border-color: #dc2626 !important;
}

/* ── Preview ── */
.prev-wrap {
    background: #fff; border-radius: 14px;
    border: 1.5px solid #e8eaed; padding: 10px;
    margin-top: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}
.prev-lbl {
    font-size: 10px; font-weight: 800; letter-spacing: .1em;
    text-transform: uppercase; color: #94a3b8;
    text-align: center; margin-bottom: 6px;
}

/* ── Print sheet item rows ── */
.item-card {
    background: #fff; border-radius: 12px;
    border: 1.5px solid #e8eaed; padding: 10px 12px;
    margin-bottom: 8px;
}
.item-head {
    display: flex; align-items: center;
    justify-content: space-between; margin-bottom: 4px;
}
.item-num  { font-family:'JetBrains Mono',monospace; font-size:13px; font-weight:700; color:#0f172a; }
.item-type { font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; }
.item-qty  { font-size:11px; font-weight:700; color:#2563eb; }
.item-dim  { font-family:'JetBrains Mono',monospace; font-size:12px; color:#475569; }
.item-note { font-size:11px; color:#d97706; font-style:italic; margin-top:2px; }

/* ── Summary strip ── */
.sum-strip {
    background: #fff; border-radius: 12px;
    border: 1.5px solid #e2e8f0; padding: 10px 14px;
    margin-bottom: 12px; display: flex;
    justify-content: space-between; align-items: center;
}
.sum-item { text-align: center; }
.sum-val { font-family:'JetBrains Mono',monospace; font-size:18px; font-weight:800; color:#0f172a; }
.sum-lbl { font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:#94a3b8; }
.sum-div  { width:1px; height:32px; background:#e2e8f0; }

/* ── Checkbox ── */
div[data-testid="stCheckbox"] {
    background: #f8fafc; border:1.5px solid #e2e8f0;
    border-radius: 10px; padding: 10px 12px;
}
div[data-testid="stCheckbox"] label {
    font-size:13px !important; text-transform:none !important;
    letter-spacing:0 !important; color:#0f172a !important;
    font-weight:600 !important;
}

/* ── Info/warning ── */
div[data-testid="stInfo"] { border-radius:10px !important; }
div[data-testid="stWarning"] { border-radius:10px !important; }

hr { margin: 6px 0 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# DATA MODELS
# ══════════════════════════════════════════════════════

class BasePiece(BaseModel):
    id:         str  = Field(default_factory=lambda: str(uuid.uuid4()))
    project:    str  = "Job-101"
    piece_type: Literal["Straight","Bend"]
    qty:        int  = 1
    notes:      str  = ""

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
        t=f"{int(self.top_width)}x{int(self.top_height)}"
        b=f"{int(self.btm_width)}x{int(self.btm_height)}"
        return f"{t}/{b} L={int(self.length)}" if t!=b else f"{t} L={int(self.length)}"

    @property
    def is_transition(self):
        return not(self.top_width==self.btm_width and self.top_height==self.btm_height)

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


# ══════════════════════════════════════════════════════
# RENDERER
# ══════════════════════════════════════════════════════

INK  = "#0d1117"
DIM  = "#2563eb"
ANN  = "#dc2626"
CONN = "#059669"
HATCH= "#cbd5e1"
LW   = 2.0

class HVACRenderer:

    @staticmethod
    def _fig(w=5.0, h=7.0):
        fig = plt.Figure(figsize=(w,h), facecolor="white", dpi=150)
        ax  = fig.add_axes([0.0, 0.0, 1.0, 1.0])
        ax.set_facecolor("white")
        ax.set_aspect("equal")
        ax.axis("off")
        return fig, ax

    # ── Dimension helpers ────────────────────────────

    @staticmethod
    def _hdim(ax, x1, x2, y, label, above=True):
        """Horizontal dimension line at fixed y."""
        sign = 1 if above else -1
        ext  = 30
        # extension lines
        ax.plot([x1,x1],[y, y+sign*ext], color=DIM, lw=0.7, zorder=4)
        ax.plot([x2,x2],[y, y+sign*ext], color=DIM, lw=0.7, zorder=4)
        # arrow line
        ay = y + sign*ext
        ax.annotate("", xy=(x2,ay), xytext=(x1,ay),
                    arrowprops=dict(arrowstyle="<->",color=DIM,lw=1.0), zorder=5)
        # label
        ax.text((x1+x2)/2, ay+sign*18, label,
                ha="center", va="center" if not above else "bottom",
                fontsize=8.5, color=DIM, weight="bold", zorder=6)

    @staticmethod
    def _vdim(ax, y1, y2, x, label):
        """Vertical dimension line at fixed x (always to the right)."""
        ext = 35
        ax.plot([x, x+ext],[y1,y1], color=DIM, lw=0.7, zorder=4)
        ax.plot([x, x+ext],[y2,y2], color=DIM, lw=0.7, zorder=4)
        ax.annotate("", xy=(x+ext,y2), xytext=(x+ext,y1),
                    arrowprops=dict(arrowstyle="<->",color=DIM,lw=1.0), zorder=5)
        ax.text(x+ext+18, (y1+y2)/2, label,
                ha="left", va="center", fontsize=8.5,
                color=DIM, weight="bold", rotation=90,
                rotation_mode="anchor", zorder=6)

    # ── STRAIGHT / TRANSITION ────────────────────────

    @staticmethod
    def render_straight(p: StraightPiece):
        fig, ax = HVACRenderer._fig(w=5.0, h=7.5)

        sv  = p.shift_val if p.shift_side != "None" else 0.0
        mxw = max(p.top_width, p.btm_width) + sv
        xt  = xb = 0.0

        if p.shift_side == "Left":
            xt, xb = 0.0, sv
        elif p.shift_side == "Right":
            xt, xb = sv, 0.0
        else:
            if   p.h_align == "Left Flat":  xt = xb = 0.0
            elif p.h_align == "Right Flat": xt = mxw-p.top_width; xb = mxw-p.btm_width
            else:                           xt = (mxw-p.top_width)/2; xb=(mxw-p.btm_width)/2

        yt,yb = p.length, 0.0
        tl=(xt,yt); tr=(xt+p.top_width,yt)
        bl=(xb,yb); br=(xb+p.btm_width,yb)

        # body
        ax.add_patch(Polygon([bl,br,tr,tl], closed=True,
                             fill=False, lw=LW, edgecolor=INK, zorder=2))

        # transition hatch
        if p.is_transition:
            for f in np.linspace(0.1,0.9,7):
                ax.plot([bl[0]+(tl[0]-bl[0])*f, br[0]+(tr[0]-br[0])*f],
                        [yb+(yt-yb)*f,           yb+(yt-yb)*f],
                        color=HATCH, lw=0.45, alpha=0.55, zorder=1)

        # ── Dimension lines ──
        # top width — above top face
        HVACRenderer._hdim(ax, tl[0], tr[0], yt,
                           f"{int(p.top_width)}", above=True)
        # bottom width — below bottom face
        HVACRenderer._hdim(ax, bl[0], br[0], yb,
                           f"{int(p.btm_width)}", above=False)
        # length — to the right of rightmost edge
        rx = max(tr[0], br[0])
        HVACRenderer._vdim(ax, yb, yt, rx, f"L={int(p.length)}")

        # ── Size labels (inside body) ──
        cx_t = xt + p.top_width/2
        cx_b = xb + p.btm_width/2
        ax.text(cx_t, yt - p.length*0.08,
                f"{int(p.top_width)} x {int(p.top_height)}",
                ha="center", va="top", fontsize=9.5, weight="bold", color=INK, zorder=3)
        ax.text(cx_b, yb + p.length*0.08,
                f"{int(p.btm_width)} x {int(p.btm_height)}",
                ha="center", va="bottom", fontsize=9.5, weight="bold", color=INK, zorder=3)

        # ── Connection labels ──
        lx = min(tl[0],bl[0]) - mxw*0.04
        if p.conn_top != "None":
            ax.text(lx, yt, p.conn_top, ha="right", va="center",
                    fontsize=8, color=CONN, weight="bold", style="italic", zorder=3)
        if p.conn_btm != "None":
            ax.text(lx, yb, p.conn_btm, ha="right", va="center",
                    fontsize=8, color=CONN, weight="bold", style="italic", zorder=3)

        # ── Kick annotation (horizontal arrow at mid-height) ──
        if sv > 0 and p.shift_side != "None":
            cy = yb + p.length * 0.5   # mid-height
            if p.shift_side == "Left":
                # top face is further left — arrow from bl to tl projected at cy
                x_top = tl[0]
                x_btm = bl[0]
            else:
                x_top = tr[0]
                x_btm = br[0]
            # horizontal double-arrow between the two vertical lines
            ax.plot([x_top, x_top],[yt, cy], color=ANN, lw=0.8, ls="--", zorder=3)
            ax.plot([x_btm, x_btm],[yb, cy], color=ANN, lw=0.8, ls="--", zorder=3)
            ax.annotate("", xy=(x_btm, cy), xytext=(x_top, cy),
                        arrowprops=dict(arrowstyle="<->",color=ANN,lw=1.3), zorder=4)
            ax.text((x_top+x_btm)/2, cy + p.length*0.04,
                    f"{int(sv)} mm", ha="center", fontsize=8.5,
                    color=ANN, weight="bold", zorder=5)

        # ── Watermark ──
        tags = []
        if p.v_align=="Flat Top":    tags.append("FOT")
        if p.v_align=="Flat Bottom": tags.append("FOB")
        if p.insulation>0:           tags.append(f"{p.insulation}mm INS")
        if p.is_transition:          tags.append("TRANSITION")
        if tags:
            cx = (tl[0]+tr[0]+bl[0]+br[0])/4
            ax.text(cx, p.length*0.5, "\n".join(tags),
                    ha="center", va="center", fontsize=10,
                    weight="black", alpha=0.06, color=INK, zorder=1)

        ax.autoscale_view(); ax.margins(0.22)
        return fig

    # ── BEND ────────────────────────────────────────

    @staticmethod
    def render_bend(p: BendPiece):
        fig, ax = HVACRenderer._fig(w=6.0, h=6.0)
        r_in  = p.radius
        r_out = p.radius + p.width
        rad   = np.radians(p.angle)

        # body arcs + caps
        ax.add_patch(Arc((0,0),2*r_in, 2*r_in,  angle=0,theta1=0,theta2=p.angle,color=INK,lw=LW))
        ax.add_patch(Arc((0,0),2*r_out,2*r_out,  angle=0,theta1=0,theta2=p.angle,color=INK,lw=LW))
        ax.plot([r_in,r_out],[0,0], color=INK, lw=LW)
        ax.plot([r_in*np.cos(rad),r_out*np.cos(rad)],
                [r_in*np.sin(rad),r_out*np.sin(rad)], color=INK, lw=LW)

        # turning vanes
        if p.vanes:
            n=3
            for i in range(1,n+1):
                rv = r_in + p.width*(i/(n+1))
                ax.add_patch(Arc((0,0),2*rv,2*rv,angle=0,theta1=0,theta2=p.angle,
                                 color=HATCH,lw=0.9,ls=(0,(4,3))))

        # radius callout
        mid = np.radians(p.angle/2)
        rx  = r_in*np.cos(mid); ry=r_in*np.sin(mid)
        tr_ = max(r_in*0.38, 18)
        ax.annotate(f"R{int(r_in)}", xy=(rx,ry),
                    xytext=(tr_*np.cos(mid), tr_*np.sin(mid)),
                    arrowprops=dict(arrowstyle="->",color=ANN,lw=1.3,shrinkB=3),
                    fontsize=9, color=ANN, weight="bold", ha="center", va="center")

        # size + angle label
        lr = r_out + max(p.width*0.38, 65)
        ax.text(lr*np.cos(mid), lr*np.sin(mid),
                f"{int(p.width)} x {int(p.height)}\n{p.angle:.0f}°",
                ha="center", va="center", fontsize=10, weight="bold", color=INK)

        # dashed angle arc
        da = r_out + max(p.width*0.12, 35)
        ax.add_patch(Arc((0,0),2*da,2*da,angle=0,theta1=0,theta2=p.angle,
                         color=DIM,lw=0.9,ls="--"))

        # connection labels
        rm  = r_in + p.width/2
        off = max(p.width*0.2, 42)
        ax.text(rm, -off, p.conn_in, ha="center", va="top",
                fontsize=8, color=CONN, weight="bold", style="italic")
        ex=rm*np.cos(rad); ey=rm*np.sin(rad)
        ax.text(ex-np.sin(rad)*off, ey+np.cos(rad)*off,
                p.conn_out, ha="center", va="center",
                fontsize=8, color=CONN, weight="bold", style="italic",
                rotation=p.angle-90)

        ax.autoscale_view(); ax.margins(0.28)
        return fig


# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════

def fig_to_png(fig) -> bytes:
    buf=io.BytesIO()
    fig.savefig(buf,format="png",bbox_inches="tight",dpi=160,facecolor="white")
    buf.seek(0); data=buf.getvalue(); plt.close(fig); return data

def ins_map(): return {"None":0,"13 mm":13,"25 mm":25,"50 mm":50}

def build_html(project, items, start, by):
    today=date.today().strftime("%d %b %Y")
    n=len(items)
    cards=""
    for i,item in enumerate(items):
        num=start+i
        b64=base64.b64encode(item["image"]).decode()
        qty=item.get("qty",1); notes=item.get("notes","").strip()
        conn=item.get("connections",""); ins=item.get("ins_label","")
        extras=" · ".join(filter(None,[conn,ins]))
        cards+=f"""
        <div class="card">
          <div class="ctop">
            <span class="cnum">#{num}</span>
            <span class="ctype">{item['type'].upper()}</span>
            <span class="cqty">QTY {qty}</span>
          </div>
          <div class="cimg"><img src="data:image/png;base64,{b64}"></div>
          <div class="cfoot">
            <div class="cdim">{item['label']}</div>
            {f'<div class="cext">{extras}</div>' if extras else ''}
            {f'<div class="cnote">✎ {notes}</div>' if notes else ''}
          </div>
        </div>"""

    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><title>{project} – Fabrication Sheet</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
@page{{size:A4 portrait;margin:8mm}}
body{{font-family:'Inter',sans-serif;background:#fff;color:#0f172a;
      -webkit-print-color-adjust:exact;print-color-adjust:exact}}
.hdr{{display:grid;grid-template-columns:1fr auto;align-items:end;
       border-bottom:3px solid #0f172a;padding-bottom:5px;margin-bottom:7px}}
.hdr h1{{font-size:15px;font-weight:800;text-transform:uppercase}}
.proj{{font-size:10px;color:#64748b;font-weight:600;margin-top:2px}}
.meta{{text-align:right;font-size:8px;color:#64748b;line-height:1.8}}
.meta strong{{color:#0f172a}}
.sumbar{{display:flex;gap:5px;margin-bottom:7px}}
.pill{{background:#f1f5f9;border:1px solid #e2e8f0;border-radius:5px;
        padding:3px 8px;font-size:7.5px;font-weight:700;
        text-transform:uppercase;letter-spacing:.05em;color:#475569}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:5px}}
.card{{border:1.5px solid #cbd5e1;border-radius:7px;overflow:hidden;
        display:flex;flex-direction:column;height:85mm;
        break-inside:avoid;page-break-inside:avoid}}
.ctop{{background:#0f172a;display:flex;justify-content:space-between;
        align-items:center;padding:3px 7px;flex-shrink:0}}
.cnum{{font-family:'JetBrains Mono',monospace;font-size:8.5px;font-weight:700;color:#94a3b8}}
.ctype{{font-size:7.5px;font-weight:800;color:#e2e8f0;text-transform:uppercase;letter-spacing:.08em}}
.cqty{{font-size:8px;font-weight:700;color:#60a5fa;font-family:'JetBrains Mono',monospace}}
.cimg{{flex:1;display:flex;align-items:center;justify-content:center;
        padding:3px;background:#fff;min-height:0;overflow:hidden}}
.cimg img{{max-width:100%;max-height:100%;object-fit:contain}}
.cfoot{{border-top:1px solid #e2e8f0;padding:3px 6px;background:#f8fafc;flex-shrink:0}}
.cdim{{font-family:'JetBrains Mono',monospace;font-size:7px;font-weight:700;
        color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.cext{{font-size:6.5px;color:#059669;font-weight:700;margin-top:1px;
        white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.cnote{{font-size:6.5px;color:#d97706;font-style:italic;margin-top:1px;
         white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.foot{{margin-top:8px;border-top:1px solid #e2e8f0;padding-top:4px;
        display:flex;justify-content:space-between;font-size:7px;color:#94a3b8}}
</style></head><body>
<div class="hdr">
  <div><h1>Fabrication Sheet</h1><div class="proj">Project: {project}</div></div>
  <div class="meta">
    <strong>Date:</strong> {today}<br>
    <strong>By:</strong> {by or "—"}<br>
    <strong>Items:</strong> #{start}–#{start+n-1}
  </div>
</div>
<div class="sumbar">
  <div class="pill">Total: {n} pieces</div>
  <div class="pill">Ref: #{start} → #{start+n-1}</div>
</div>
<div class="grid">{cards}</div>
<div class="foot"><span>HVAC Fabricator Pro</span><span>{project} · {today}</span></div>
<script>window.onload=function(){{window.print()}}</script>
</body></html>"""


# ══════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════

def main():
    for k,v in [("collection",[]),("start_num",1),
                ("project","Job-101"),("prepared_by","")]:
        if k not in st.session_state:
            st.session_state[k]=v

    total=len(st.session_state.collection)

    # header
    st.markdown(f"""<div class="app-hdr">
      <div>
        <div class="app-hdr-title">🏗️ HVAC Fabricator</div>
        <div class="app-hdr-sub">{st.session_state.project}</div>
      </div>
      <div class="app-hdr-badge">{total} pcs</div>
    </div>""", unsafe_allow_html=True)

    tab_d, tab_p, tab_s = st.tabs(["✏️ Design","🖨️ Print Sheet","⚙️ Settings"])

    # ══════════════ DESIGN ══════════════
    with tab_d:
        mode=st.radio("t",["↔  Straight","↩  Elbow / Bend"],
                      horizontal=True, label_visibility="collapsed")
        is_s="Straight" in mode
        fig=None; piece=None

        if is_s:
            st.markdown('<p class="sec">📐 Dimensions</p>',True)
            c1,c2=st.columns(2)
            tw=c1.number_input("Top W (mm)", value=450,step=10,min_value=1,key="tw")
            th=c2.number_input("Top H (mm)", value=250,step=10,min_value=1,key="th")
            c3,c4=st.columns(2)
            bw=c3.number_input("Btm W (mm)", value=450,step=10,min_value=1,key="bw")
            bh=c4.number_input("Btm H (mm)", value=250,step=10,min_value=1,key="bh")
            L =st.number_input("Length (mm)",value=1400,step=50,min_value=1,key="L")

            st.markdown('<p class="sec">🔗 Connections</p>',True)
            opts=["TDF","SLIDE","RAW","None"]
            c5,c6=st.columns(2)
            ct=c5.selectbox("Top",   opts, key="ct")
            cb=c6.selectbox("Bottom",opts, key="cb")

            st.markdown('<p class="sec">⚙️ Alignment & Insulation</p>',True)
            c7,c8=st.columns(2)
            ah=c7.selectbox("Horizontal",["Center","Left Flat","Right Flat"],key="ah")
            av=c8.selectbox("Vertical",  ["Center","Flat Top","Flat Bottom"],key="av")
            im=ins_map()
            c9,c10=st.columns(2)
            il=c9.selectbox("Insulation",list(im.keys()),key="ins")
            sd=c10.selectbox("Kick dir",["None","Left","Right"],key="sd")
            sv=st.number_input("Kick distance (mm)",min_value=0.0,value=0.0,
                               key="sv",disabled=(sd=="None"))

            st.markdown('<p class="sec">📝 Quantity & Notes</p>',True)
            ca,cb2=st.columns([1,2])
            qty  =ca.number_input("Qty",min_value=1,value=1,step=1,key="qs")
            notes=cb2.text_input("Notes",key="ns",placeholder="e.g. paint red end")

            try:
                piece=StraightPiece(
                    project=st.session_state.project,
                    top_width=tw,top_height=th,btm_width=bw,btm_height=bh,length=L,
                    conn_top=ct,conn_btm=cb,h_align=ah,v_align=av,
                    insulation=im[il],shift_side=sd,
                    shift_val=sv if sd!="None" else 0.0,qty=qty,notes=notes)
                fig=HVACRenderer.render_straight(piece)
                if piece.is_transition:
                    st.info("⚡ Transition piece detected")
            except Exception as e:
                st.error(f"Error: {e}")

        else:
            st.markdown('<p class="sec">📐 Dimensions</p>',True)
            c1,c2=st.columns(2)
            w =c1.number_input("Width (mm)", value=450,step=10,min_value=1,key="bw2")
            h =c2.number_input("Height (mm)",value=250,step=10,min_value=1,key="bh2")
            c3,c4=st.columns(2)
            rv=c3.number_input("Throat R (mm)",value=150,step=10,min_value=1,key="rv")
            an=c4.slider("Angle (°)",5,180,90,step=5,key="ang")
            if rv<w*0.15: st.warning("⚠️ Very tight throat radius")

            st.markdown('<p class="sec">🔗 Connections</p>',True)
            c5,c6=st.columns(2)
            ci=c5.selectbox("Inlet", ["TDF","SLIDE","RAW"],key="ci")
            co=c6.selectbox("Outlet",["TDF","SLIDE","RAW"],key="co")
            vanes=st.checkbox("Turning Vanes",value=True,key="vn")

            st.markdown('<p class="sec">📝 Quantity & Notes</p>',True)
            ca,cb2=st.columns([1,2])
            qty  =ca.number_input("Qty",min_value=1,value=1,step=1,key="qb")
            notes=cb2.text_input("Notes",key="nb",placeholder="e.g. vanes + splitter")

            try:
                piece=BendPiece(
                    project=st.session_state.project,
                    width=w,height=h,radius=rv,angle=an,
                    conn_in=ci,conn_out=co,vanes=vanes,qty=qty,notes=notes)
                fig=HVACRenderer.render_bend(piece)
            except Exception as e:
                st.error(f"Error: {e}")

        # preview
        if fig is not None:
            st.markdown('<div class="prev-wrap"><div class="prev-lbl">Live Preview</div>',True)
            st.pyplot(fig, use_container_width=True)
            st.markdown('</div>',True)

        st.markdown("")
        if fig is not None and piece is not None:
            if st.button("➕  Add to Sheet",type="primary",use_container_width=True):
                png=fig_to_png(fig)
                conn_s=(f"{piece.conn_top}/{piece.conn_btm}"
                        if is_s else f"{piece.conn_in}/{piece.conn_out}")
                ins_l=(f"{piece.insulation}mm INS"
                       if is_s and piece.insulation else "")
                st.session_state.collection.append({
                    "id":piece.id,"label":piece.label,"image":png,
                    "type":piece.piece_type,"qty":piece.qty,
                    "notes":piece.notes,"connections":conn_s,"ins_label":ins_l})
                st.toast(f"Added: {piece.label}")
                st.rerun()

    # ══════════════ PRINT SHEET ══════════════
    with tab_p:
        if not st.session_state.collection:
            st.info("No pieces yet — go to Design and add some.")
        else:
            n=len(st.session_state.collection)
            s=st.session_state.start_num
            # compact summary strip
            st.markdown(f"""<div class="sum-strip">
              <div class="sum-item">
                <div class="sum-val">{n}</div>
                <div class="sum-lbl">Pieces</div>
              </div>
              <div class="sum-div"></div>
              <div class="sum-item">
                <div class="sum-val">#{s}</div>
                <div class="sum-lbl">First</div>
              </div>
              <div class="sum-div"></div>
              <div class="sum-item">
                <div class="sum-val">#{s+n-1}</div>
                <div class="sum-lbl">Last</div>
              </div>
            </div>""", unsafe_allow_html=True)

            for idx,item in enumerate(st.session_state.collection):
                num=s+idx
                icon="↔️" if item["type"]=="Straight" else "↩️"
                ca,cb,cc=st.columns([1,4,1])
                with ca: st.image(item["image"],width=58)
                with cb:
                    st.markdown(
                        f"**{icon} #{num} — {item['type']}**  "
                        f"<span style='font-size:11px;color:#2563eb;font-weight:700;'>"
                        f"QTY {item.get('qty',1)}</span>",
                        unsafe_allow_html=True)
                    st.caption(item["label"])
                    if item.get("notes"): st.caption(f"✎ {item['notes']}")
                with cc:
                    st.markdown("<br>",True)
                    if st.button("✕",key=f"d_{item['id']}",help="Remove"):
                        st.session_state.collection.pop(idx); st.rerun()
                st.divider()

            if st.button("🖨️  Generate Fabrication Sheet",
                         type="primary",use_container_width=True):
                html=build_html(st.session_state.project,
                                st.session_state.collection,
                                st.session_state.start_num,
                                st.session_state.prepared_by)
                st.components.v1.html(html,height=920,scrolling=True)
                st.caption("Print dialog opens automatically. Use Ctrl+P / Cmd+P if needed.")

    # ══════════════ SETTINGS ══════════════
    with tab_s:
        st.markdown('<p class="sec">Job Details</p>',True)
        np_=st.text_input("Project Reference",value=st.session_state.project,key="pi")
        if np_!=st.session_state.project: st.session_state.project=np_
        nb_=st.text_input("Prepared By",value=st.session_state.prepared_by,
                          key="bi",placeholder="Your name or initials")
        if nb_!=st.session_state.prepared_by: st.session_state.prepared_by=nb_

        st.markdown('<p class="sec">Piece Numbering</p>',True)
        ns_=st.number_input("Start numbering from",min_value=1,
                            value=st.session_state.start_num,step=1,key="sni",
                            help="Set this to continue from a previous order")
        if ns_!=st.session_state.start_num:
            st.session_state.start_num=ns_; st.rerun()
        n_=len(st.session_state.collection)
        if st.session_state.start_num>1:
            st.info(f"Pieces: #{st.session_state.start_num} → #{st.session_state.start_num+n_-1}")

        st.markdown('<p class="sec">Session</p>',True)
        s_n=sum(1 for x in st.session_state.collection if x["type"]=="Straight")
        st.caption(f"{n_} pieces · {s_n} straight · {n_-s_n} bends")
        st.markdown("")
        if st.button("🗑️  Clear All Pieces",type="secondary",
                     use_container_width=True,disabled=(n_==0)):
            st.session_state.collection=[]; st.rerun()

if __name__=="__main__":
    main()
