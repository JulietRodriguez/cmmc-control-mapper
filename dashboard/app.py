"""CMMC Control Mapper — Streamlit Dashboard."""
import json
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.cmmc_mapper.mapper import (
    load_controls, get_domain_summary, search_controls, DOMAINS, get_controls_by_level
)
from src.cmmc_mapper.oscal_export import generate_oscal_component_definition

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CMMC Control Mapper",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background: #0d1117; }

  .metric-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
  }
  .metric-number {
    font-size: 2.4rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, #58a6ff, #79c0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
  }
  .metric-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 6px;
  }
  .control-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 3px solid #58a6ff;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
  }
  .control-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    color: #58a6ff;
  }
  .domain-badge {
    display: inline-block;
    background: #1f2d3d;
    color: #79c0ff;
    border: 1px solid #1f6feb;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 500;
    margin-left: 8px;
  }
  .level-badge-1 {
    display: inline-block;
    background: #1a2f1a;
    color: #56d364;
    border: 1px solid #2ea043;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
  }
  .level-badge-2 {
    display: inline-block;
    background: #2d1f00;
    color: #e3b341;
    border: 1px solid #9e6a03;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
  }
  .aws-chip {
    display: inline-block;
    background: #1c2a1c;
    color: #7ee787;
    border: 1px solid #238636;
    border-radius: 4px;
    padding: 1px 8px;
    font-size: 0.7rem;
    font-weight: 500;
    margin: 2px;
  }
  .section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e6edf3;
    border-bottom: 1px solid #30363d;
    padding-bottom: 8px;
    margin-bottom: 16px;
  }
  .hero-title {
    font-size: 2rem;
    font-weight: 700;
    color: #e6edf3;
    line-height: 1.2;
  }
  .hero-sub {
    font-size: 1rem;
    color: #8b949e;
    margin-top: 6px;
  }
  .stSelectbox label, .stMultiSelect label { color: #8b949e !important; font-size: 0.82rem !important; }
  div[data-testid="stSidebar"] { background: #0d1117; border-right: 1px solid #21262d; }
  .stButton > button {
    background: linear-gradient(135deg, #238636, #2ea043);
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    padding: 8px 20px;
  }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    controls = load_controls()
    summary = get_domain_summary()
    return controls, summary

controls, summary = get_data()
df = pd.DataFrame(controls)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ CMMC Control Mapper")
    st.markdown("<span style='color:#8b949e;font-size:0.8rem'>v1.0.0 · CMMC 2.0 · OSCAL 1.1.2</span>", unsafe_allow_html=True)
    st.divider()

    page = st.radio("Navigation", ["📊 Overview", "🗂️ Control Explorer", "🔍 Search", "📤 OSCAL Export"], label_visibility="collapsed")
    st.divider()

    st.markdown("<span style='color:#8b949e;font-size:0.75rem'>CMMC LEVEL FILTER</span>", unsafe_allow_html=True)
    level_filter = st.selectbox("Level", ["All", "Level 1 Only", "Level 2 Only"], label_visibility="collapsed")

    st.markdown("<span style='color:#8b949e;font-size:0.75rem;margin-top:12px;display:block'>DOMAIN FILTER</span>", unsafe_allow_html=True)
    domain_filter = st.multiselect("Domains", DOMAINS, label_visibility="collapsed")

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = controls.copy()
if level_filter == "Level 1 Only":
    filtered = [c for c in filtered if c["level"] == 1]
elif level_filter == "Level 2 Only":
    filtered = [c for c in filtered if c["level"] == 2]
if domain_filter:
    filtered = [c for c in filtered if c["domain"] in domain_filter]
df_filtered = pd.DataFrame(filtered) if filtered else pd.DataFrame()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown('<div class="hero-title">CMMC 2.0 Control Mapper</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Maps all CMMC Level 2 practices to AWS services and OSCAL Component Definitions</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Metrics
    total = len(controls)
    l1 = len([c for c in controls if c["level"] == 1])
    l2 = len([c for c in controls if c["level"] == 2])
    domains_count = len(set(c["domain"] for c in controls))
    all_services = set(s for c in controls for s in c.get("aws_services", []))

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, num, label in [
        (c1, total, "Total Controls"),
        (c2, l1, "Level 1 Practices"),
        (c3, l2, "Level 2 Practices"),
        (c4, domains_count, "CMMC Domains"),
        (c5, len(all_services), "AWS Services"),
    ]:
        col.markdown(f'<div class="metric-card"><div class="metric-number">{num}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown('<div class="section-header">Controls by Domain</div>', unsafe_allow_html=True)
        sum_df = pd.DataFrame(summary)
        fig_bar = px.bar(
            sum_df, x="total", y="domain", orientation="h",
            color="level_1",
            color_continuous_scale=["#1f6feb", "#58a6ff"],
            labels={"total": "Controls", "domain": "", "level_1": "L1 Count"},
            height=420,
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8b949e", size=11),
            xaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">Level Distribution</div>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["Level 1", "Level 2"],
            values=[l1, l2],
            hole=0.6,
            marker=dict(colors=["#2ea043", "#e3b341"], line=dict(color="#0d1117", width=2)),
            textinfo="label+percent",
            textfont=dict(color="#e6edf3", size=12),
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8b949e"),
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=200,
            annotations=[dict(text=f"<b>{total}</b><br>Controls", x=0.5, y=0.5, font_size=14, font_color="#e6edf3", showarrow=False)],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown('<div class="section-header" style="margin-top:8px">AWS Services per Domain</div>', unsafe_allow_html=True)
        fig_svc = px.bar(
            sum_df.sort_values("aws_service_count", ascending=True).tail(8),
            x="aws_service_count", y="domain", orientation="h",
            color="aws_service_count",
            color_continuous_scale=["#1a3a1a", "#56d364"],
            labels={"aws_service_count": "Services", "domain": ""},
            height=200,
        )
        fig_svc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8b949e", size=10),
            xaxis=dict(gridcolor="#21262d"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig_svc, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CONTROL EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🗂️ Control Explorer":
    st.markdown('<div class="section-header">Control Explorer</div>', unsafe_allow_html=True)

    if df_filtered.empty:
        st.warning("No controls match the current filters.")
    else:
        st.markdown(f"<span style='color:#8b949e;font-size:0.85rem'>Showing {len(filtered)} controls</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        for control in filtered:
            level_badge = f'<span class="level-badge-1">L1</span>' if control["level"] == 1 else f'<span class="level-badge-2">L2</span>'
            aws_chips = " ".join(f'<span class="aws-chip">{s}</span>' for s in control.get("aws_services", []))
            config_rules = ", ".join(control.get("aws_config_rules", [])) or "None"

            st.markdown(f"""
            <div class="control-card">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                <span class="control-id">{control['id']}</span>
                {level_badge}
                <span class="domain-badge">{control['domain']}</span>
              </div>
              <div style="color:#c9d1d9;font-size:0.87rem;line-height:1.5;margin-bottom:10px">{control['practice']}</div>
              <div style="margin-bottom:6px">{aws_chips}</div>
              <div style="color:#8b949e;font-size:0.75rem">
                <strong style="color:#6e7681">NIST:</strong> {', '.join(control.get('nist_mapping', []))} &nbsp;|&nbsp;
                <strong style="color:#6e7681">Config Rules:</strong> {config_rules}
              </div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SEARCH
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Search":
    st.markdown('<div class="section-header">Search Controls</div>', unsafe_allow_html=True)
    query = st.text_input("Search by keyword, AWS service, NIST control, or domain", placeholder="e.g. MFA, GuardDuty, AC-2, encryption...")

    if query:
        results = search_controls(query)
        st.markdown(f"<span style='color:#8b949e'>Found {len(results)} results for <strong style='color:#58a6ff'>'{query}'</strong></span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        for control in results:
            level_badge = f'<span class="level-badge-1">L1</span>' if control["level"] == 1 else f'<span class="level-badge-2">L2</span>'
            aws_chips = " ".join(f'<span class="aws-chip">{s}</span>' for s in control.get("aws_services", []))
            st.markdown(f"""
            <div class="control-card">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                <span class="control-id">{control['id']}</span>
                {level_badge}
                <span class="domain-badge">{control['domain']}</span>
              </div>
              <div style="color:#c9d1d9;font-size:0.87rem;margin-bottom:8px">{control['practice']}</div>
              <div>{aws_chips}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<span style='color:#8b949e'>Enter a search term above to find controls.</span>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OSCAL EXPORT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📤 OSCAL Export":
    st.markdown('<div class="section-header">Export OSCAL Component Definition</div>', unsafe_allow_html=True)
    st.markdown("<span style='color:#8b949e;font-size:0.87rem'>Generate an OSCAL 1.1.2 Component Definition document mapping CMMC controls to your AWS environment.</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        export_level = st.selectbox("CMMC Level", [1, 2], index=1)
        system_name = st.text_input("System Name", value="AWS Cloud Environment")
    with col2:
        org_name = st.text_input("Organization Name", value="My Organization")

    if st.button("Generate OSCAL JSON"):
        doc = generate_oscal_component_definition(export_level, system_name, org_name)
        doc_json = json.dumps(doc, indent=2)
        st.download_button(
            label="⬇️ Download OSCAL JSON",
            data=doc_json,
            file_name=f"cmmc_level{export_level}_component_definition.json",
            mime="application/json",
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Preview</div>', unsafe_allow_html=True)
        st.code(doc_json[:3000] + "\n\n// ... truncated for preview", language="json")
