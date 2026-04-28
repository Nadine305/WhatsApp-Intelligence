"""
dashboard.py
------------
WhatsApp Intelligence Dashboard
Design: Trust & Professional — Crisp White / Slate Gray / Navy + Emerald
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
from sqlalchemy import text
from src.storage.db_manager import DatabaseManager

st.set_page_config(
    page_title="WhatsApp Intelligence",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Cairo:wght@300;400;500;600;700&display=swap');

/* ── Variables: 60-30-10 Rule ──────────────────────────────
   60% Dominant  → Crisp White  #FFFFFF / Light Gray #F7F8FC
   30% Secondary → Slate Gray   #64748B / Cards #FFFFFF
   10% Accent    → Navy Blue    #1E3A5F / Emerald #10B981
──────────────────────────────────────────────────────────── */

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    background-color: #F7F8FC !important;
    color: #1E293B !important;
}

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Top Navigation Bar ── */
.topbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 0 48px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.topbar-logo {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 18px;
    font-weight: 800;
    color: #1E3A5F;
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: -0.5px;
}

.topbar-logo span {
    color: #10B981;
}

.topbar-status {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 13px;
    color: #166534;
    font-weight: 600;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #10B981;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Page Content Wrapper ── */
.page-content {
    padding: 40px 48px;
    max-width: 1440px;
    margin: 0 auto;
}

/* ── Page Title ── */
.page-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -1px;
    margin-bottom: 4px;
}

.page-subtitle {
    font-size: 15px;
    color: #64748B;
    font-weight: 400;
    margin-bottom: 36px;
}

/* ── Metric Cards ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 36px;
}

.metric-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 24px 28px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.03);
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 20px rgba(30,58,95,0.1);
    border-color: #CBD5E1;
}

.metric-card-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}

.accent-navy   { background: linear-gradient(90deg, #1E3A5F, #2563EB); }
.accent-emerald{ background: linear-gradient(90deg, #10B981, #059669); }
.accent-amber  { background: linear-gradient(90deg, #F59E0B, #D97706); }
.accent-rose   { background: linear-gradient(90deg, #F43F5E, #E11D48); }

.metric-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}

.metric-icon-wrap {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}

.icon-navy    { background: #EFF6FF; }
.icon-emerald { background: #ECFDF5; }
.icon-amber   { background: #FFFBEB; }
.icon-rose    { background: #FFF1F2; }

.metric-number {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 44px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1;
    letter-spacing: -2px;
}

.metric-label {
    font-size: 13px;
    color: #64748B;
    font-weight: 500;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ── Section Header ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
}

.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.3px;
}

.section-count {
    background: #F1F5F9;
    color: #64748B;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 600;
}

/* ── Interest Cards ── */
.interest-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 12px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.25s ease;
    display: flex;
    gap: 16px;
}

.interest-card:hover {
    border-color: #1E3A5F30;
    box-shadow: 0 4px 20px rgba(30,58,95,0.08);
    transform: translateX(3px);
}

.interest-bar {
    width: 4px;
    border-radius: 4px;
    flex-shrink: 0;
}

.interest-body { flex: 1; }

.interest-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #0F172A;
}

.interest-desc {
    font-size: 13px;
    color: #64748B;
    margin-top: 5px;
    line-height: 1.6;
}

.users-row { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 6px; }

.user-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    color: #475569;
    font-weight: 500;
    transition: all 0.2s;
}

.user-chip:hover {
    background: #EFF6FF;
    border-color: #BFDBFE;
    color: #1D4ED8;
}

/* ── Message Cards ── */
.message-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 10px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}

.message-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.msg-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.msg-sender {
    display: flex;
    align-items: center;
    gap: 8px;
}

.msg-avatar {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #1E3A5F, #2563EB);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 13px;
    font-weight: 700;
    font-family: 'Plus Jakarta Sans', sans-serif;
    flex-shrink: 0;
}

.msg-name {
    font-weight: 700;
    color: #0F172A;
    font-size: 13px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.msg-phone {
    color: #94A3B8;
    font-size: 11px;
    margin-top: 1px;
}

.badge-analyzed {
    background: #ECFDF5;
    color: #065F46;
    border: 1px solid #A7F3D0;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
}

.badge-pending {
    background: #FFFBEB;
    color: #92400E;
    border: 1px solid #FDE68A;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
}

.msg-bubble {
    background: #F8FAFC;
    border-radius: 4px 12px 12px 12px;
    padding: 10px 14px;
    font-size: 14px;
    color: #334155;
    direction: rtl;
    text-align: right;
    line-height: 1.7;
    border: 1px solid #F1F5F9;
}

.msg-time {
    color: #CBD5E1;
    font-size: 11px;
    margin-top: 8px;
    text-align: right;
}

/* ── Chart Cards ── */
.chart-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 24px 28px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.chart-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 16px;
}

/* ── Empty State ── */
.empty-state {
    background: #FFFFFF;
    border: 2px dashed #E2E8F0;
    border-radius: 16px;
    padding: 48px 32px;
    text-align: center;
}

.empty-icon { font-size: 40px; margin-bottom: 12px; }
.empty-title { font-weight: 700; color: #0F172A; font-size: 16px; }
.empty-desc  { color: #64748B; font-size: 13px; margin-top: 6px; }

/* ── Footer ── */
.footer {
    text-align: center;
    color: #94A3B8;
    font-size: 12px;
    padding: 32px 0 16px;
    border-top: 1px solid #E2E8F0;
    margin-top: 48px;
}

/* ── Streamlit Overrides ── */
div[data-testid="stSelectbox"] > div > div {
    border-radius: 10px !important;
    border-color: #E2E8F0 !important;
    background: #FFFFFF !important;
    font-size: 14px !important;
}

.stButton > button {
    background: #1E3A5F !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    font-size: 13px !important;
    font-family: 'Cairo', sans-serif !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(30,58,95,0.25) !important;
}

.stButton > button:hover {
    background: #10B981 !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.35) !important;
    transform: translateY(-1px) !important;
}

#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Accent colors for interest bars ──────────────────────────────────────────
ACCENTS = ["#1E3A5F","#10B981","#F59E0B","#F43F5E","#8B5CF6","#06B6D4","#84CC16","#EC4899"]

# ── DB ────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    return DatabaseManager()

db = get_db()

@st.cache_data(ttl=30)
def fetch_messages():
    with db.engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT u.name, u.phone_number, m.content, m.timestamp, m.is_processed
            FROM messages m
            JOIN users u ON m.user_id = u.user_id
            ORDER BY m.timestamp DESC
        """)).fetchall()
    return pd.DataFrame(rows, columns=["name","phone","content","timestamp","processed"])

@st.cache_data(ttl=30)
def fetch_interests():
    with db.engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT i.cluster_label, i.description, u.name, u.phone_number
            FROM user_interests ui
            JOIN users u ON ui.user_id = u.user_id
            JOIN interests i ON ui.interest_id = i.interest_id
            ORDER BY i.cluster_label
        """)).fetchall()
    return pd.DataFrame(rows, columns=["label","description","name","phone"])

@st.cache_data(ttl=30)
def fetch_users():
    with db.engine.connect() as conn:
        rows = conn.execute(text("SELECT user_id, name, phone_number FROM users")).fetchall()
    return pd.DataFrame(rows, columns=["user_id","name","phone"])

# ── Load ──────────────────────────────────────────────────────────────────────
try:
    df_msg = fetch_messages()
    df_int = fetch_interests()
    df_usr = fetch_users()
except Exception as e:
    st.error(f"❌ Database connection error: {e}")
    st.stop()

# ── Top Bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-logo">
        💬 WhatsApp <span>Intelligence</span>
    </div>
    <div class="topbar-status">
        <div class="status-dot"></div>
        Live · Auto-refresh every 30s
    </div>
</div>
""", unsafe_allow_html=True)

# ── Auto Refresh ──────────────────────────────────────────────────────────────
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="autorefresh")
except ImportError:
    pass

# ── Page Content ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-content">', unsafe_allow_html=True)

# Title + Refresh
title_col, btn_col = st.columns([5, 1])
with title_col:
    st.markdown("""
    <div class="page-title">Analytics Overview</div>
    <div class="page-subtitle">Real-time insights from WhatsApp conversations</div>
    """, unsafe_allow_html=True)
with btn_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⟳ Refresh"):
        st.cache_data.clear()
        st.rerun()

# ── Metrics ───────────────────────────────────────────────────────────────────
processed = int(df_msg["processed"].sum()) if not df_msg.empty else 0
n_groups  = df_int["label"].nunique() if not df_int.empty else 0

metrics = [
    ("navy",    "icon-navy",    "📨", len(df_msg),      "Total Messages",   "accent-navy"),
    ("emerald", "icon-emerald", "👥", len(df_usr),      "Active Users",     "accent-emerald"),
    ("amber",   "icon-amber",   "🏷️", n_groups,         "Interest Groups",  "accent-amber"),
    ("rose",    "icon-rose",    "✅", processed,        "Analyzed",         "accent-rose"),
]

cols = st.columns(4, gap="medium")
for col, (_, icon_cls, icon, num, label, accent_cls) in zip(cols, metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-accent {accent_cls}"></div>
            <div class="metric-top">
                <div>
                    <div class="metric-number">{num}</div>
                    <div class="metric-label">{label}</div>
                </div>
                <div class="metric-icon-wrap {icon_cls}">{icon}</div>
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
# ── Most Popular Interest Group ───────────────────────────
if not df_int.empty:
    top_group = df_int["label"].value_counts().idxmax()
    top_count = df_int["label"].value_counts().max()
    top_desc  = df_int[df_int["label"] == top_group]["description"].iloc[0]

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1E3A5F, #2563EB);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 8px 32px rgba(30,58,95,0.25);
    ">
        <div>
            <div style="color:rgba(255,255,255,0.7); font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:2px; margin-bottom:6px;">
                🏆 Most Popular Interest
            </div>
            <div style="color:white; font-family:'Plus Jakarta Sans',sans-serif; font-size:28px; font-weight:800; letter-spacing:-0.5px;">
                {top_group}
            </div>
            <div style="color:rgba(255,255,255,0.65); font-size:14px; margin-top:6px;">
                {top_desc}
            </div>
        </div>
        <div style="text-align:center; background:rgba(255,255,255,0.12); border-radius:12px; padding:16px 24px;">
            <div style="color:white; font-family:'Plus Jakarta Sans',sans-serif; font-size:40px; font-weight:800; line-height:1;">
                {top_count}
            </div>
            <div style="color:rgba(255,255,255,0.7); font-size:12px; font-weight:600; margin-top:4px;">
                USERS
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Charts ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <div class="section-title">Analytics</div>
</div>""", unsafe_allow_html=True)

ch1, ch2 = st.columns(2, gap="large")

with ch1:
    st.markdown('<div class="chart-card"><div class="chart-title">💬 Messages per User</div>', unsafe_allow_html=True)
    if not df_msg.empty:
        data = df_msg["name"].value_counts().reset_index()
        data.columns = ["User","Messages"]
        st.bar_chart(data.set_index("User"), color="#1E3A5F", height=240)
    else:
        st.info("No data yet")
    st.markdown('</div>', unsafe_allow_html=True)

with ch2:
    st.markdown('<div class="chart-card"><div class="chart-title">🏷️ Interests per User</div>', unsafe_allow_html=True)
    if not df_int.empty:
        data = df_int["name"].value_counts().reset_index()
        data.columns = ["User","Interests"]
        st.bar_chart(data.set_index("User"), color="#10B981", height=240)
    else:
        st.info("No data yet")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Main Grid ─────────────────────────────────────────────────────────────────
left, right = st.columns([1.6, 0.4], gap="large")


# ── Interest Groups ───────────────────────────────────────────────────────────
with left:
    n_int = df_int["label"].nunique() if not df_int.empty else 0
    st.markdown(f"""
    <div class="section-header">
        <div class="section-title">Interest Groups</div>
        <div class="section-count">{n_int} groups</div>
    </div>""", unsafe_allow_html=True)

    if df_int.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🏷️</div>
            <div class="empty-title">No interests discovered yet</div>
            <div class="empty-desc">Run <code>python main.py</code> to analyze messages</div>
        </div>""", unsafe_allow_html=True)
    else:
        for i, (label, group) in enumerate(df_int.groupby("label")):
            accent  = ACCENTS[i % len(ACCENTS)]
            desc    = group["description"].iloc[0]
            chips   = "".join([
                f'<span class="user-chip">👤 {r["name"]} · {r["phone"]}</span>'
                for _, r in group.iterrows()
            ])
            st.markdown(f"""
            <div class="interest-card">
                <div class="interest-bar" style="background:{accent}"></div>
                <div class="interest-body">
                    <div class="interest-label">{label}</div>
                    <div class="interest-desc">{desc}</div>
                    <div class="users-row">{chips}</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ── Messages ──────────────────────────────────────────────────────────────────
with right:
    n_msg = len(df_msg)
    st.markdown(f"""
    <div class="section-header">
        <div class="section-title">Messages</div>
        <div class="section-count">{n_msg} total</div>
    </div>""", unsafe_allow_html=True)

    if df_msg.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📨</div>
            <div class="empty-title">No messages yet</div>
            <div class="empty-desc">Send a WhatsApp message to get started</div>
        </div>""", unsafe_allow_html=True)
    else:
        options  = ["All Users"] + sorted(df_msg["name"].dropna().unique().tolist())
        selected = st.selectbox("", options, label_visibility="collapsed")
        filtered = df_msg if selected == "All Users" else df_msg[df_msg["name"] == selected]

        # ── Messages Grid ─────────────────────────────────────────
        msg_cols = st.columns(2, gap="medium")
        for idx, (_, row) in enumerate(filtered.iterrows()):
            name = str(row["name"]) if pd.notna(row["name"]) else "Unknown"
            phone = str(row["phone"]) if pd.notna(row["phone"]) else ""
            content = str(row["content"]) if pd.notna(row["content"]) else ""
            time_s = str(row["timestamp"])[:16] if pd.notna(row["timestamp"]) else ""
            initial = name[0].upper() if name else "?"
            badge = '<span class="badge-analyzed">✅</span>' if row[
                "processed"] else '<span class="badge-pending">⏳</span>'
            accent = ACCENTS[idx % len(ACCENTS)]

            with msg_cols[idx % 2]:
                st.markdown(f"""
                <div class="message-card" style="border-top: 3px solid {accent};">
                    <div class="msg-header">
                        <div class="msg-sender">
                            <div class="msg-avatar" style="background:linear-gradient(135deg,{accent},{accent}99)">
                                {initial}
                            </div>
                            <div>
                                <div class="msg-name">{name}</div>
                                <div class="msg-phone">{phone}</div>
                            </div>
                        </div>
                        {badge}
                    </div>
                    <div class="msg-bubble">{content}</div>
                    <div class="msg-time">🕐 {time_s}</div>
                </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# # ── Charts ────────────────────────────────────────────────────────────────────
# st.markdown("""
# <div class="section-header">
#     <div class="section-title">Analytics</div>
# </div>""", unsafe_allow_html=True)
#
# ch1, ch2 = st.columns(2, gap="large")
#
# with ch1:
#     st.markdown('<div class="chart-card"><div class="chart-title">💬 Messages per User</div>', unsafe_allow_html=True)
#     if not df_msg.empty:
#         data = df_msg["name"].value_counts().reset_index()
#         data.columns = ["User","Messages"]
#         st.bar_chart(data.set_index("User"), color="#1E3A5F", height=240)
#     else:
#         st.info("No data yet")
#     st.markdown('</div>', unsafe_allow_html=True)
#
# with ch2:
#     st.markdown('<div class="chart-card"><div class="chart-title">🏷️ Interests per User</div>', unsafe_allow_html=True)
#     if not df_int.empty:
#         data = df_int["name"].value_counts().reset_index()
#         data.columns = ["User","Interests"]
#         st.bar_chart(data.set_index("User"), color="#10B981", height=240)
#     else:
#         st.info("No data yet")
#     st.markdown('</div>', unsafe_allow_html=True)



# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    WhatsApp Intelligence Dashboard &nbsp;·&nbsp; Built with Streamlit &nbsp;·&nbsp; Powered by AI Clustering
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)