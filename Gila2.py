# -*- coding: utf-8 -*-
"""
نظام إدارة مدرسة التوكل جيلا للتعليم والتدريب المزدوج
الإصدار: 3.1.0
"""

import hashlib
import re
import random
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

# ==========================================================
# ثوابت
# ==========================================================
APP_NAME = "التوكل جيلا"
APP_FULL = "مدرسة التوكل جيلا للتعليم والتدريب المزدوج"
APP_LOCATION = "داخل شركة التوكل للكهربائيات — العاشر من رمضان — الشرقية"
APP_FIELD = "قسم الكهرباء"
APP_VERSION = "3.1.0"

GRADES = ["الأول", "الثاني", "الثالث"]
SPECIALTIES = ["كهرباء", "إلكترونيات", "تحكم آلي"]
PERIODS = [f"الحصة {i}" for i in range(1, 9)]
ROLES = {
    "admin": "مدير المدرسة",
    "teacher": "معلم",
    "accountant": "محاسب",
    "viewer": "مشاهد",
}

ATT_OPTIONS = ["حاضر", "غائب", "متأخر"]

# ==========================================================
# إعداد الصفحة
# ==========================================================
st.set_page_config(
    page_title=f"{APP_NAME} | نظام الإدارة",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# CSS ثابت (وضع داكن فقط)
# ==========================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg: #0a0f1c;
    --bg-2: #060912;
    --surface: #101828;
    --surface-2: #0d1523;
    --surface-3: #17213a;
    --border: #1e2a44;
    --border-2: #2a3a5c;
    --text: #f1f5fb;
    --text-2: #cbd5e6;
    --muted: #8ea0bf;
    --faint: #5e6f8e;
    --primary: #3b82f6;
    --primary-2: #60a5fa;
    --primary-soft: rgba(59,130,246,0.16);
    --primary-glow: rgba(59,130,246,0.4);
    --accent: #f59e0b;
    --accent-2: #fbbf24;
    --accent-soft: rgba(245,158,11,0.16);
    --success: #22c55e;
    --success-soft: rgba(34,197,94,0.14);
    --danger: #ef4444;
    --danger-soft: rgba(239,68,68,0.14);
    --warning: #f97316;
    --warning-soft: rgba(249,115,22,0.14);
    --info: #06b6d4;
    --info-soft: rgba(6,182,212,0.14);
    --sb-bg: #050810;
    --sb-bg-2: #0a1224;
    --sb-text: #e8eefc;
    --sb-muted: #8494b6;
    --sb-border: rgba(255,255,255,0.07);
    --sb-hover: rgba(59,130,246,0.15);
    --sb-active: rgba(59,130,246,0.22);
    --sb-active-bar: #fbbf24;
    --input-bg: #0d1523;
    --input-border: #1e2a44;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.5);
    --shadow: 0 6px 20px rgba(0,0,0,0.45);
    --shadow-lg: 0 18px 45px rgba(0,0,0,0.55);
}

html, body, [class*="css"], .stApp, .stApp * {
    font-family: 'Cairo', system-ui, -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
html, body { font-size: 15.5px !important; }
.stApp { background: var(--bg) !important; color: var(--text) !important; }

p, span, li, td, th, .stMarkdown, .stText,
[data-testid="stMarkdownContainer"] *,
[data-testid="stCaptionContainer"] *,
[data-testid="stWidgetLabel"] * { color: var(--text-2) !important; }

h1, h2, h3, h4, h5, h6, strong, b { color: var(--text) !important; font-weight: 800 !important; }
h1 { font-size: 26px !important; font-weight: 900 !important; }
h2 { font-size: 22px !important; }
h3 { font-size: 19px !important; }

[data-testid="stWidgetLabel"] p,
label[data-baseweb="form-control-label"],
.stTextInput label, .stSelectbox label,
.stNumberInput label, .stDateInput label, .stTextArea label {
    color: var(--text) !important;
    font-size: 14.5px !important;
    font-weight: 700 !important;
}

/* ===================== Layout: sidebar RIGHT ===================== */
[data-testid="stAppViewContainer"] {
    display: flex !important;
    flex-direction: row !important;
    background: var(--bg) !important;
}
[data-testid="stAppViewContainer"] > section[data-testid="stSidebar"] {
    order: 2 !important;
    flex: 0 0 280px !important;
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    background: linear-gradient(180deg, var(--sb-bg) 0%, var(--sb-bg-2) 100%) !important;
    border-left: 1px solid var(--sb-border) !important;
    border-right: none !important;
    direction: rtl !important;
    text-align: right !important;
}
[data-testid="stAppViewContainer"] > [data-testid="stMain"],
[data-testid="stAppViewContainer"] > section.main,
[data-testid="stAppViewContainer"] > .main {
    order: 1 !important;
    flex: 1 1 auto !important;
    min-width: 0 !important;
    direction: rtl !important;
    background: var(--bg) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--sb-text) !important;
    direction: rtl !important;
    text-align: right !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] button[kind="header"],
section[data-testid="stSidebar"] button[kind="headerNoPadding"] {
    display: none !important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    position: fixed !important;
    top: 16px !important;
    right: 16px !important;
    left: auto !important;
    z-index: 99999 !important;
}
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow) !important;
    border-radius: 12px !important;
    color: var(--primary) !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg {
    fill: var(--primary) !important;
    color: var(--primary) !important;
}

#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    padding-inline: 2rem !important;
    max-width: 1500px !important;
}

/* ===================== Sidebar ===================== */
.sb-brand {
    display: flex; align-items: center; gap: 12px;
    padding: 8px 2px 16px 2px;
    border-bottom: 1px solid var(--sb-border);
    margin-bottom: 14px;
}
.sb-brand .brand-text { display: flex; flex-direction: column; }
.sb-brand .name {
    font-weight: 900 !important; font-size: 17px !important;
    color: var(--sb-text) !important; line-height: 1.15;
}
.sb-brand .tag {
    font-size: 11.5px !important; color: var(--sb-muted) !important;
    font-weight: 600 !important; margin-top: 3px;
}
.sb-user {
    background: rgba(255,255,255,0.045);
    border: 1px solid var(--sb-border);
    border-radius: 14px;
    padding: 13px 14px;
    margin-bottom: 12px;
}
.sb-user .n { font-weight: 800 !important; font-size: 15px !important; color: var(--sb-text) !important; }
.sb-user .r {
    display: inline-block; margin-top: 6px;
    font-size: 11.5px !important; color: #c7d2fe !important;
    font-weight: 700 !important;
    background: rgba(59,130,246,0.25);
    padding: 3px 10px; border-radius: 999px;
}
.sb-user .e {
    font-size: 11.5px !important; color: var(--sb-muted) !important;
    margin-top: 8px; direction: ltr; text-align: right; word-break: break-all;
}

section[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 4px; display: flex; flex-direction: column;
}
section[data-testid="stSidebar"] .stRadio > label:first-child { display: none !important; }
section[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    flex-direction: row-reverse !important;
    justify-content: flex-start !important;
    align-items: center; gap: 10px;
    padding: 11px 14px !important;
    margin: 0 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all .15s ease;
    color: var(--sb-text) !important;
    position: relative;
}
section[data-testid="stSidebar"] .stRadio label p {
    font-size: 15px !important; font-weight: 600 !important;
    color: var(--sb-text) !important;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: var(--sb-hover) !important; }
section[data-testid="stSidebar"] .stRadio label > div:first-child { display: none !important; }
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: var(--sb-active) !important;
    border-color: rgba(59,130,246,0.4);
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked)::before {
    content: ''; position: absolute;
    right: 0; top: 20%; bottom: 20%;
    width: 3px; border-radius: 3px;
    background: var(--sb-active-bar);
}
section[data-testid="stSidebar"] hr {
    border: none; border-top: 1px solid var(--sb-border); margin: 14px 0;
}

.sb-footer {
    text-align: center; font-size: 11.5px !important;
    color: var(--sb-muted) !important;
    padding: 14px 0 4px 0;
    border-top: 1px solid var(--sb-border);
    margin-top: 14px; line-height: 1.9;
}
.sb-footer .ver {
    display: inline-block; padding: 3px 12px;
    border-radius: 999px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: #0a0f1c !important;
    font-weight: 900 !important; font-size: 10.5px !important;
}

/* ===================== Logo ===================== */
.school-logo { display: inline-flex; align-items: center; justify-content: center; border-radius: 14px; flex-shrink: 0; }
.school-logo svg { width: 100%; height: 100%; display: block; }
@keyframes brand-pulse {
    0%, 100% { filter: drop-shadow(0 0 0 rgba(245,158,11,0)); transform: scale(1); }
    50% { filter: drop-shadow(0 0 14px rgba(245,158,11,0.55)) drop-shadow(0 0 26px rgba(59,130,246,0.35)); transform: scale(1.04); }
}
.brand-pulse { animation: brand-pulse 2.6s ease-in-out infinite; }

/* ===================== Inputs ===================== */
input, textarea,
.stTextInput input, .stNumberInput input,
.stDateInput input, .stTextArea textarea,
.stTimeInput input, .stPasswordInput input {
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--input-border) !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
    direction: rtl !important;
    text-align: right !important;
}
input::placeholder, textarea::placeholder { color: var(--faint) !important; font-weight: 500 !important; }
input:focus, textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px var(--primary-soft) !important;
    outline: none !important;
}
div[data-baseweb="input"], div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border-color: var(--input-border) !important;
    border-radius: 10px !important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"]:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px var(--primary-soft) !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] div {
    color: var(--text) !important;
    font-weight: 600 !important; font-size: 15px !important;
}
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] [role="listbox"],
div[data-baseweb="menu"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    direction: rtl !important;
}
div[data-baseweb="popover"] li, div[data-baseweb="menu"] li {
    color: var(--text) !important;
    font-size: 14.5px !important; font-weight: 600 !important;
    padding: 10px 14px !important;
}
div[data-baseweb="popover"] li:hover, div[data-baseweb="menu"] li:hover { background: var(--primary-soft) !important; }

/* ===================== Buttons ===================== */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    font-family: 'Cairo', sans-serif !important;
    font-size: 14.5px !important; font-weight: 700 !important;
    border-radius: 10px !important; padding: 9px 18px !important;
    border: 1px solid var(--border-2) !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    transition: all .15s ease !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    border-color: var(--primary) !important;
    color: var(--primary) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 18px var(--primary-glow) !important;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 26px var(--primary-glow) !important;
}

/* ===================== Metrics ===================== */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 16px 18px !important;
    box-shadow: var(--shadow-sm);
}
[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    font-weight: 700 !important; font-size: 13.5px !important;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-weight: 900 !important; font-size: 24px !important;
}

/* ===================== Tabs / Expander / Alerts ===================== */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 2px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    font-family: 'Cairo', sans-serif !important;
    font-weight: 700 !important; font-size: 14.5px !important;
    padding: 12px 20px !important;
    color: var(--muted) !important;
    border-radius: 10px 10px 0 0;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom-color: var(--primary) !important;
    background: var(--primary-soft) !important;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    background: var(--surface) !important;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}
[data-testid="stExpander"] summary {
    font-weight: 700 !important; font-size: 14.5px !important;
    color: var(--text) !important;
    padding: 14px 18px !important;
}
[data-testid="stExpander"] summary p {
    font-size: 14.5px !important; font-weight: 700 !important;
    color: var(--text) !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: var(--surface-2) !important;
    padding: 16px 18px !important;
}
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    font-size: 14.5px !important; font-weight: 600 !important;
}
[data-testid="stAlert"] p { font-size: 14.5px !important; font-weight: 600 !important; }
[data-testid="stForm"] {
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 22px !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-sm);
}

/* ===================== Custom tables ===================== */
.tbl-wrap {
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: var(--surface);
    box-shadow: var(--shadow-sm);
}
table.data-tbl { width: 100%; border-collapse: collapse; direction: rtl; }
table.data-tbl thead th {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    font-size: 14.5px !important; font-weight: 800 !important;
    padding: 14px 16px !important;
    text-align: right !important;
    border-bottom: 1.5px solid var(--border) !important;
    white-space: nowrap;
}
table.data-tbl tbody td {
    padding: 13px 16px !important;
    font-size: 14.5px !important; font-weight: 600 !important;
    color: var(--text-2) !important;
    border-bottom: 1px solid var(--border) !important;
    text-align: right !important;
    line-height: 1.55;
}
table.data-tbl tbody tr:last-child td { border-bottom: none !important; }
table.data-tbl tbody tr:hover td {
    background: var(--primary-soft) !important;
    color: var(--text) !important;
}

/* ===================== Chips ===================== */
.chip {
    display: inline-block; padding: 4px 12px;
    border-radius: 999px; font-size: 12px !important;
    font-weight: 800 !important; line-height: 1.5;
}
.chip.ok  { background: var(--success-soft); color: var(--success) !important; }
.chip.no  { background: var(--danger-soft);  color: var(--danger) !important; }
.chip.wrn { background: var(--warning-soft); color: var(--warning) !important; }
.chip.inf { background: var(--primary-soft); color: var(--primary) !important; }
.chip.gold { background: var(--accent-soft); color: var(--accent) !important; }
.chip.mut { background: var(--surface-3); color: var(--muted) !important; }

/* ===================== Page head / sections / stats ===================== */
.page-head {
    display: flex; align-items: center; justify-content: space-between;
    margin: 4px 0 22px 0;
    padding-bottom: 18px;
    border-bottom: 1px solid var(--border);
}
.page-head .titles { display: flex; flex-direction: column; gap: 4px; }
.page-head .title {
    font-size: 24px; font-weight: 900; color: var(--text) !important;
    letter-spacing: -0.01em; line-height: 1.2;
}
.page-head .sub {
    font-size: 13.5px; color: var(--muted) !important;
    font-weight: 600;
}
.page-head .badge {
    font-size: 11.5px; font-weight: 800;
    color: var(--accent) !important;
    background: var(--accent-soft);
    padding: 5px 14px; border-radius: 999px;
    letter-spacing: .3px;
    border: 1px solid rgba(245,158,11,0.25);
}
.section-title {
    display: flex; align-items: center; gap: 12px;
    font-size: 17px; font-weight: 800; color: var(--text) !important;
    margin: 26px 0 14px 0;
}
.section-title::before {
    content: ''; width: 4px; height: 20px; border-radius: 2px;
    background: linear-gradient(180deg, var(--primary), var(--accent));
}
.stat {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: var(--shadow-sm);
    display: flex; align-items: center; gap: 16px;
    transition: transform .15s ease, box-shadow .15s ease;
    min-height: 84px;
}
.stat:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
.stat .icon {
    width: 48px; height: 48px; border-radius: 13px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    background: var(--primary-soft); color: var(--primary);
    flex-shrink: 0;
}
.stat .icon.success { background: var(--success-soft); color: var(--success); }
.stat .icon.danger  { background: var(--danger-soft);  color: var(--danger); }
.stat .icon.warning { background: var(--warning-soft); color: var(--warning); }
.stat .icon.gold    { background: var(--accent-soft);  color: var(--accent); }
.stat .icon.info    { background: var(--info-soft);    color: var(--info); }
.stat .val {
    font-size: 25px; font-weight: 900; color: var(--text) !important;
    line-height: 1.1;
}
.stat .lbl {
    font-size: 13.5px; color: var(--muted) !important;
    font-weight: 700; margin-top: 4px;
}
.empty {
    padding: 34px 22px; text-align: center;
    color: var(--muted) !important;
    background: var(--surface-2);
    border: 1px dashed var(--border-2);
    border-radius: 14px;
    font-size: 14.5px; font-weight: 600;
}

/* ===================== Attendance row ===================== */
.att-row {
    display: flex; align-items: center; gap: 14px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 8px;
    transition: border-color .15s ease, background .15s ease;
}
.att-row:hover { border-color: var(--border-2); }
.att-row .code {
    font-family: 'Cairo', monospace;
    background: var(--primary-soft);
    color: var(--primary) !important;
    padding: 6px 12px;
    border-radius: 8px;
    font-weight: 800; font-size: 13px;
    min-width: 82px; text-align: center;
}
.att-row .name {
    flex: 1;
    font-weight: 700; font-size: 15px;
    color: var(--text) !important;
}
.att-row .grade {
    color: var(--muted) !important;
    font-size: 13px; font-weight: 600;
    min-width: 60px;
}

/* Radio group in attendance row */
.att-row-wrap [role="radiogroup"] {
    display: flex !important;
    flex-direction: row-reverse !important;
    gap: 6px !important;
    justify-content: flex-start !important;
}
.att-row-wrap [role="radiogroup"] label {
    display: flex !important;
    flex-direction: row-reverse !important;
    gap: 6px !important;
    align-items: center !important;
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    padding: 6px 12px !important;
    border-radius: 10px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all .12s ease !important;
}
.att-row-wrap [role="radiogroup"] label:hover {
    border-color: var(--border-2) !important;
}
.att-row-wrap [role="radiogroup"] label p {
    font-size: 13.5px !important; font-weight: 700 !important;
    color: var(--text-2) !important;
    margin: 0 !important;
}
.att-row-wrap [role="radiogroup"] label:has(input:checked) {
    background: var(--primary-soft) !important;
    border-color: var(--primary) !important;
}
.att-row-wrap [role="radiogroup"] label:has(input:checked) p {
    color: var(--primary) !important;
    font-weight: 800 !important;
}
/* Hide the radio circle */
.att-row-wrap [role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* ===================== Login ===================== */
.login-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 38px 34px 30px 34px;
    box-shadow: var(--shadow-lg);
    position: relative; overflow: hidden;
}
.login-card::before {
    content: ''; position: absolute; inset: 0 0 auto 0; height: 6px;
    background: linear-gradient(90deg, var(--primary), var(--accent));
}
.login-brand { text-align: center; margin-bottom: 22px; }
.login-brand .logo-wrap { display: inline-flex; margin-bottom: 16px; }
.login-brand .t1 {
    font-size: 24px; font-weight: 900; color: var(--text) !important;
    letter-spacing: -0.01em;
}
.login-brand .t2 {
    font-size: 13.5px; color: var(--muted) !important;
    margin-top: 6px; font-weight: 600; line-height: 1.6;
}
.login-brand .t3 {
    font-size: 12.5px; color: var(--faint) !important;
    margin-top: 8px; font-weight: 600;
}
.login-foot {
    text-align: center; font-size: 12px;
    color: var(--faint) !important; margin-top: 18px; font-weight: 600;
}

::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

@media (max-width: 900px) {
    .block-container { padding-inline: 1rem !important; }
    .page-head .title { font-size: 20px; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ==========================================================
# اللوجو (سطر واحد، بدون مسافات بادئة)
# ==========================================================
def school_logo(size=48, pulse=False):
    cls = "brand-pulse" if pulse else ""
    return (
        f"<div class='school-logo {cls}' style='width:{size}px;height:{size}px;'>"
        "<svg viewBox='0 0 120 120' xmlns='http://www.w3.org/2000/svg'>"
        "<defs>"
        "<linearGradient id='sg' x1='0%' y1='0%' x2='100%' y2='100%'>"
        "<stop offset='0%' stop-color='#3b82f6'/>"
        "<stop offset='55%' stop-color='#1e40af'/>"
        "<stop offset='100%' stop-color='#0f172a'/>"
        "</linearGradient>"
        "<linearGradient id='bg' x1='0%' y1='0%' x2='0%' y2='100%'>"
        "<stop offset='0%' stop-color='#fde047'/>"
        "<stop offset='50%' stop-color='#facc15'/>"
        "<stop offset='100%' stop-color='#f59e0b'/>"
        "</linearGradient>"
        "</defs>"
        "<path d='M60,8 L108,24 L108,60 C108,88 88,108 60,116 C32,108 12,88 12,60 L12,24 Z' fill='url(#sg)'/>"
        "<path d='M60,15 L100,29 L100,60 C100,84 83,101 60,108 C37,101 20,84 20,60 L20,29 Z' fill='none' stroke='#fbbf24' stroke-width='1.2' opacity='0.65'/>"
        "<path d='M66,28 L38,62 L54,62 L50,92 L84,54 L66,54 Z' fill='url(#bg)'/>"
        "</svg>"
        "</div>"
    )


# ==========================================================
# Helpers
# ==========================================================
def hp(pw): return hashlib.sha256(pw.encode("utf-8")).hexdigest()
def verify(pw, h): return hp(pw) == h

def split_phones(text):
    if not text: return []
    return [p.strip() for p in re.split(r"[,،;/\n]+", text) if p.strip()]

def attendance_totals(student):
    a = student.get("attendance", {})
    return (
        sum(1 for v in a.values() if v == "حاضر"),
        sum(1 for v in a.values() if v == "غائب"),
        sum(1 for v in a.values() if v == "متأخر"),
    )

def build_attendance(seed, days=21):
    rnd = random.Random(seed * 7919 + 13)
    res = {}
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=i)
        if d.weekday() == 4: continue
        res[d.isoformat()] = rnd.choices(
            ATT_OPTIONS, weights=[80, 10, 10]
        )[0]
    return res

def month_prefix(d): return f"{d.year}-{d.month:02d}"
def teacher_by_id(tid): return next((t for t in st.session_state.teachers if t["id"] == tid), None)

def user_by_login(identifier):
    ident = (identifier or "").strip().lower()
    for u in st.session_state.users:
        if u["email"].lower() == ident: return u
        if u.get("username", "").lower() == ident and u.get("username"): return u
    return None

def count_teacher_month(tid, y, m):
    p = f"{y}-{m:02d}"
    return sum(1 for s in st.session_state.sessions
               if s["teacher_id"] == tid and s["date"].startswith(p))

def count_teacher_week(tid):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    return sum(1 for s in st.session_state.sessions
               if s["teacher_id"] == tid
               and start.isoformat() <= s["date"] <= today.isoformat())

def gen_demo_sessions(teachers):
    rnd = random.Random(2025)
    out = []
    sid = 1
    today = date.today()
    for off in range(30):
        d = today - timedelta(days=off)
        if d.weekday() == 4: continue
        for t in teachers:
            for _ in range(rnd.randint(2, 5)):
                out.append({
                    "id": sid, "teacher_id": t["id"], "date": d.isoformat(),
                    "grade": rnd.choice(GRADES),
                    "specialty": rnd.choice(SPECIALTIES),
                    "subject": rnd.choice(["ورشة عملية", "رسم فني", "دوائر كهربائية",
                                            "حصة نظري", "تدريب ميداني", "مشروع"]),
                    "period": rnd.choice(PERIODS),
                    "duration_minutes": rnd.choice([45, 60, 90]),
                    "notes": "", "logged_by": "demo",
                    "logged_at": datetime.now().isoformat(timespec="seconds"),
                })
                sid += 1
    return out


# ==========================================================
# جدول HTML
# ==========================================================
def data_table(headers, rows):
    thead = "".join(f"<th>{h}</th>" for h in headers)
    body = ""
    for r in rows:
        cells = ""
        for c in r:
            cs = str(c)
            if cs in ("مفعّل", "حاضر", "نشط"):
                cells += f"<td><span class='chip ok'>{cs}</span></td>"
            elif cs in ("معطّل", "غائب", "موقوف"):
                cells += f"<td><span class='chip no'>{cs}</span></td>"
            elif cs == "متأخر":
                cells += f"<td><span class='chip wrn'>{cs}</span></td>"
            else:
                cells += f"<td>{cs}</td>"
        body += f"<tr>{cells}</tr>"
    html = (
        "<div class='tbl-wrap'><table class='data-tbl'>"
        f"<thead><tr>{thead}</tr></thead><tbody>{body}</tbody>"
        "</table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# ==========================================================
# مكونات موحدة — ملاحظة: كل HTML بسطر واحد بدون مسافات بادئة
# ==========================================================
def page_head(title, subtitle="", badge=""):
    b = f"<span class='badge'>{badge}</span>" if badge else ""
    s = f"<span class='sub'>{subtitle}</span>" if subtitle else ""
    html = f"<div class='page-head'><div class='titles'><span class='title'>{title}</span>{s}</div>{b}</div>"
    st.markdown(html, unsafe_allow_html=True)

def section(title):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)

def stat(icon, label, value, tone=""):
    cls = f"icon {tone}".strip()
    html = f"<div class='stat'><div class='{cls}'>{icon}</div><div><div class='val'>{value}</div><div class='lbl'>{label}</div></div></div>"
    st.markdown(html, unsafe_allow_html=True)

def empty_state(text):
    st.markdown(f"<div class='empty'>{text}</div>", unsafe_allow_html=True)


# ==========================================================
# تهيئة البيانات
# ==========================================================
def init_data():
    if st.session_state.get("_init_v31"):
        return
    st.session_state._init_v31 = True

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = ""
    st.session_state.display_name = ""
    st.session_state.email = ""
    st.session_state.current_teacher_id = None

    st.session_state.manager = {
        "name": "أ. عبد الرحمن محمد التوكل",
        "national_id": "28001011234567",
        "phone": "01001234567",
        "code": "MGR-001",
        "qualification": "بكالوريوس هندسة كهربائية",
        "grad_year": "2004",
        "email": "admin@tawakkol.edu",
    }

    users = [{
        "id": 1, "name": "أ. عبد الرحمن محمد التوكل",
        "email": "admin@tawakkol.edu", "username": "admin",
        "password_hash": hp("admin123"), "role": "admin",
        "teacher_id": None, "active": True,
        "created_at": date.today().isoformat(),
    }]

    teachers_seed = [
        ("أ. خالد سعيد رمضان", "28501011234567", "01099887766", "TCH-001",
         "بكالوريوس تربية صناعية", "2008", 75.0, "كهرباء"),
        ("أ. منى عبد الحميد علي", "28702021234567", "01088776655", "TCH-002",
         "بكالوريوس علوم — فيزياء", "2010", 70.0, "إلكترونيات"),
        ("أ. مصطفى كامل الجندي", "28403031234567", "01077665544", "TCH-003",
         "دبلوم فني صناعي متقدم", "2006", 85.0, "تحكم آلي"),
        ("أ. هدى إبراهيم شاكر", "28904041234567", "01066554433", "TCH-004",
         "ليسانس آداب — إنجليزي", "2012", 65.0, "كهرباء"),
        ("أ. طارق ياسر عبد الفتاح", "28305051234567", "01055443322", "TCH-005",
         "بكالوريوس هندسة كهربائية", "2007", 90.0, "إلكترونيات"),
    ]

    teachers = []
    for idx, s in enumerate(teachers_seed, start=1):
        teachers.append({
            "id": idx, "name": s[0], "national_id": s[1], "phone": s[2],
            "code": s[3], "qualification": s[4], "grad_year": s[5],
            "session_price": s[6], "specialty": s[7], "active": True,
        })
        users.append({
            "id": idx + 1, "name": s[0],
            "email": f"teacher{idx}@tawakkol.edu",
            "username": f"teacher{idx}",
            "password_hash": hp(f"teach{idx}123"),
            "role": "teacher", "teacher_id": idx, "active": True,
            "created_at": date.today().isoformat(),
        })
    st.session_state.teachers = teachers
    st.session_state.users = users

    students_seed = [
        ("أحمد محمود السيد", "STD-001", "30101011234567", "الأول", "كهرباء",
         ["01011112222"], ["01211112222"], "نجار"),
        ("مريم خالد عبد الله", "STD-002", "30201021234567", "الأول", "إلكترونيات",
         ["01022223333"], ["01222223333"], "مدرسة"),
        ("يوسف إبراهيم حسن", "STD-003", "30101031234567", "الثاني", "تحكم آلي",
         ["01033334444"], ["01233334444"], "حداد"),
        ("سلمى أحمد فتحي", "STD-004", "30201041234567", "الثاني", "كهرباء",
         ["01044445555"], ["01244445555"], "تاجر"),
        ("عمر سامي رشاد", "STD-005", "30101051234567", "الثالث", "إلكترونيات",
         ["01055556666"], ["01255556666"], "كهربائي"),
        ("نور الهدى مصطفى", "STD-006", "30201061234567", "الأول", "كهرباء",
         ["01066667777"], ["01266667777"], "محاسب"),
        ("محمد عادل شعبان", "STD-007", "30101071234567", "الثاني", "تحكم آلي",
         ["01077778888"], ["01277778888"], "سباك"),
        ("حبيبة وليد أنور", "STD-008", "30201081234567", "الثالث", "كهرباء",
         ["01088889999"], ["01288889999"], "صيدلي"),
    ]

    students = []
    for idx, s in enumerate(students_seed, start=1):
        students.append({
            "id": idx, "name": s[0], "code": s[1], "national_id": s[2],
            "grade": s[3], "specialty": s[4], "phones": s[5],
            "parent_phones": s[6], "father_job": s[7],
            "attendance": build_attendance(idx),
            "penalties": (
                [{"date": (date.today() - timedelta(days=3)).isoformat(),
                  "reason": "التأخر عن الطابور الصباحي"}] if idx % 3 == 0 else []
            ),
            "notes": "منتظم ومتفاعل." if idx % 2 == 1 else "يحتاج متابعة بالورشة.",
        })
    st.session_state.students = students
    st.session_state.sessions = gen_demo_sessions(teachers)


# ==========================================================
# صفحة الدخول
# ==========================================================
def login_page():
    st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.15, 1])
    with c2:
        brand_html = (
            "<div class='login-card'>"
            "<div class='login-brand'>"
            f"<div class='logo-wrap'>{school_logo(78, pulse=True)}</div>"
            f"<div class='t1'>{APP_FULL}</div>"
            f"<div class='t2'>{APP_FIELD} — التعليم والتدريب المزدوج</div>"
            f"<div class='t3'>{APP_LOCATION}</div>"
            "</div></div>"
        )
        st.markdown(brand_html, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            identifier = st.text_input("اسم المستخدم أو البريد الإلكتروني")
            password = st.text_input("كلمة المرور", type="password")
            ok = st.form_submit_button("تسجيل الدخول",
                                       use_container_width=True, type="primary")

        st.markdown(
            f"<div class='login-foot'>الإصدار {APP_VERSION}</div>",
            unsafe_allow_html=True,
        )

        if ok:
            identifier = (identifier or "").strip()
            password = (password or "").strip()
            if not identifier or not password:
                st.error("أدخل بيانات الدخول كاملة.")
                return
            user = user_by_login(identifier)
            if user is None or not verify(password, user["password_hash"]):
                st.error("بيانات الدخول غير صحيحة.")
                return
            if not user.get("active", True):
                st.error("هذا الحساب معطّل.")
                return
            st.session_state.logged_in = True
            st.session_state.user_id = user["id"]
            st.session_state.role = user["role"]
            st.session_state.display_name = user["name"]
            st.session_state.email = user["email"]
            st.session_state.current_teacher_id = user.get("teacher_id")
            st.rerun()


# ==========================================================
# Sidebar
# ==========================================================
def render_sidebar():
    role = st.session_state.role
    with st.sidebar:
        brand_html = (
            "<div class='sb-brand'>"
            f"{school_logo(46, pulse=True)}"
            "<div class='brand-text'>"
            f"<div class='name'>{APP_NAME}</div>"
            "<div class='tag'>تعليم وتدريب مزدوج</div>"
            "</div></div>"
        )
        user_html = (
            "<div class='sb-user'>"
            f"<div class='n'>👤 {st.session_state.display_name}</div>"
            f"<div class='r'>{ROLES.get(role, role)}</div>"
            f"<div class='e'>{st.session_state.email}</div>"
            "</div>"
        )
        st.markdown(brand_html + user_html, unsafe_allow_html=True)

        if role == "admin":
            pages = ["لوحة التحكم", "ملف المدير", "الطلاب", "المدرسون",
                     "دفتر الجلسات", "الحضور والغياب", "المستحقات المالية",
                     "إدارة المستخدمين"]
        elif role == "teacher":
            pages = ["دفتر الجلسات", "الحضور والغياب", "مستحقاتي"]
        elif role == "accountant":
            pages = ["لوحة التحكم", "دفتر الجلسات", "المستحقات المالية"]
        else:
            pages = ["لوحة التحكم", "الطلاب", "المدرسون"]

        icons = {"لوحة التحكم": "🏠", "ملف المدير": "👤", "الطلاب": "🎓",
                 "المدرسون": "👨‍🏫", "دفتر الجلسات": "📚", "الحضور والغياب": "✅",
                 "المستحقات المالية": "💰", "إدارة المستخدمين": "🔐", "مستحقاتي": "💵"}
        labels = [f"{icons.get(p, '•')}  {p}" for p in pages]
        choice_label = st.radio("nav", labels, label_visibility="collapsed")
        choice = pages[labels.index(choice_label)]

        footer_html = (
            "<div class='sb-footer'>"
            f"<span class='ver'>v {APP_VERSION}</span>"
            f"<div style='margin-top:8px;'>{APP_NAME} © {date.today().year}</div>"
            "</div>"
        )
        st.markdown(footer_html, unsafe_allow_html=True)

        if st.button("🚪  تسجيل الخروج", use_container_width=True, key="logout"):
            for k in ["logged_in", "user_id", "role", "display_name",
                      "email", "current_teacher_id"]:
                st.session_state[k] = None if k != "logged_in" else False
            st.session_state.role = ""
            st.session_state.display_name = ""
            st.session_state.email = ""
            st.rerun()

    return choice


# ==========================================================
# لوحة التحكم
# ==========================================================
def page_dashboard():
    page_head("لوحة التحكم", "نظرة عامة على المدرسة", f"v {APP_VERSION}")

    students = st.session_state.students
    teachers = st.session_state.teachers
    sessions = st.session_state.sessions
    today_str = date.today().isoformat()
    cur_prefix = month_prefix(date.today())

    p_t = sum(1 for s in students if s["attendance"].get(today_str) == "حاضر")
    a_t = sum(1 for s in students if s["attendance"].get(today_str) == "غائب")
    l_t = sum(1 for s in students if s["attendance"].get(today_str) == "متأخر")

    month_sessions = [s for s in sessions if s["date"].startswith(cur_prefix)]
    due = sum(sum(1 for s in month_sessions if s["teacher_id"] == t["id"]) * t["session_price"]
              for t in teachers)

    c1, c2, c3, c4 = st.columns(4)
    with c1: stat("🎓", "إجمالي الطلاب", len(students), "info")
    with c2: stat("👨‍🏫", "إجمالي المدرسين", len(teachers), "gold")
    with c3: stat("⚡", "جلسات الشهر", len(month_sessions), "warning")
    with c4: stat("💰", "مستحقات الشهر", f"{due:,.0f} ج.م", "success")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5: stat("✅", "حضور اليوم", p_t, "success")
    with c6: stat("❌", "غياب اليوم", a_t, "danger")
    with c7: stat("⏰", "تأخير اليوم", l_t, "warning")
    with c8: stat("👥", "حسابات نشطة",
                  sum(1 for u in st.session_state.users if u.get("active", True)), "info")

    section("ترتيب المدرسين حسب الحصص هذا الشهر")
    rows = []
    for t in teachers:
        c = sum(1 for s in month_sessions if s["teacher_id"] == t["id"])
        rows.append([t["name"], t["specialty"], c])
    rows.sort(key=lambda r: r[2], reverse=True)
    data_table(["المدرس", "التخصص", "عدد الحصص"], rows)


# ==========================================================
# ملف المدير
# ==========================================================
def page_manager_profile():
    page_head("ملف المدير", "بيانات المدير الشخصية والمهنية")
    m = st.session_state.manager

    with st.form("manager_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("الاسم بالكامل", value=m["name"])
        nid = c2.text_input("الرقم القومي", value=m["national_id"])
        phone = c1.text_input("رقم التليفون", value=m["phone"])
        code = c2.text_input("الكود", value=m["code"])
        qual = c1.text_input("المؤهل الدراسي", value=m["qualification"])
        gy = c2.text_input("سنة الحصول على المؤهل", value=m["grad_year"])
        email = c1.text_input("البريد الإلكتروني", value=m.get("email", ""))
        save = st.form_submit_button("حفظ التغييرات", type="primary", use_container_width=True)

    if save:
        st.session_state.manager = {
            "name": name.strip(), "national_id": nid.strip(),
            "phone": phone.strip(), "code": code.strip(),
            "qualification": qual.strip(), "grad_year": gy.strip(),
            "email": email.strip(),
        }
        for u in st.session_state.users:
            if u["id"] == st.session_state.user_id:
                u["name"] = name.strip()
                if email.strip(): u["email"] = email.strip()
        st.success("تم حفظ البيانات.")


# ==========================================================
# الطلاب
# ==========================================================
def page_students():
    page_head("الطلاب", "إدارة بيانات الطلاب")
    tabs = st.tabs(["القائمة", "إضافة طالب", "الملف الشخصي"])

    with tabs[0]:
        students = st.session_state.students
        if not students:
            empty_state("لا يوجد طلاب مسجلون.")
        else:
            c1, c2 = st.columns([2, 1])
            q = c1.text_input("بحث بالاسم أو الكود").strip().lower()
            gr = c2.selectbox("الصف", ["الكل"] + GRADES)
            filtered = [s for s in students
                        if (not q or q in s["name"].lower() or q in s["code"].lower())
                        and (gr == "الكل" or s.get("grade") == gr)]
            if not filtered:
                empty_state("لا توجد نتائج مطابقة.")
            else:
                rows = []
                for s in filtered:
                    p, a, l = attendance_totals(s)
                    rows.append([s["code"], s["name"], s.get("grade", "-"),
                                 s.get("specialty", "-"), p, a, l, len(s["penalties"])])
                data_table(["الكود", "الاسم", "الصف", "التخصص",
                            "حضور", "غياب", "تأخير", "جزاءات"], rows)

    with tabs[1]:
        with st.form("add_student", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم الطالب")
            code = c2.text_input("الكود")
            nid = c1.text_input("الرقم القومي")
            fj = c2.text_input("مهنة الأب")
            grade = c1.selectbox("الصف", GRADES)
            spec = c2.selectbox("التخصص", SPECIALTIES)
            phones = c1.text_input("تليفون الطالب (افصل بفاصلة)")
            pphones = c2.text_input("تليفون ولي الأمر (افصل بفاصلة)")
            notes = st.text_area("ملاحظات", height=80)
            ok = st.form_submit_button("إضافة الطالب", type="primary", use_container_width=True)

        if ok:
            name = (name or "").strip(); code = (code or "").strip()
            if not name or not code:
                st.error("الاسم والكود مطلوبان.")
            elif any(s["code"] == code for s in st.session_state.students):
                st.error("الكود مستخدم بالفعل.")
            else:
                new_id = max((s["id"] for s in st.session_state.students), default=0) + 1
                st.session_state.students.append({
                    "id": new_id, "name": name, "code": code,
                    "national_id": (nid or "").strip(),
                    "grade": grade, "specialty": spec,
                    "phones": split_phones(phones),
                    "parent_phones": split_phones(pphones),
                    "father_job": (fj or "").strip(),
                    "attendance": {}, "penalties": [],
                    "notes": notes.strip(),
                })
                st.success(f"تمت إضافة {name}.")

    with tabs[2]:
        students = st.session_state.students
        if not students:
            empty_state("لا يوجد طلاب.")
            return
        opts = {f"{s['name']} — {s['code']}": s["id"] for s in students}
        sel = st.selectbox("اختر الطالب", list(opts.keys()), key="p_stu")
        s = next(x for x in students if x["id"] == opts[sel])
        p, a, l = attendance_totals(s)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("حضور", p); c2.metric("غياب", a)
        c3.metric("تأخير", l); c4.metric("جزاءات", len(s["penalties"]))

        section("البيانات الشخصية")
        A, B = st.columns(2)
        A.markdown(f"**الاسم:** {s['name']}")
        B.markdown(f"**الكود:** {s['code']}")
        A.markdown(f"**الرقم القومي:** {s['national_id'] or '-'}")
        B.markdown(f"**مهنة الأب:** {s['father_job'] or '-'}")
        A.markdown(f"**الصف:** {s.get('grade', '-')}")
        B.markdown(f"**التخصص:** {s.get('specialty', '-')}")
        A.markdown(f"**تليفون الطالب:** {' / '.join(s['phones']) or '-'}")
        B.markdown(f"**تليفون ولي الأمر:** {' / '.join(s['parent_phones']) or '-'}")

        section("سجل الحضور")
        if s["attendance"]:
            rows = [[k, v] for k, v in sorted(s["attendance"].items(), reverse=True)]
            data_table(["التاريخ", "الحالة"], rows)
        else:
            empty_state("لا يوجد سجل.")

        section("الجزاءات")
        if s["penalties"]:
            rows = [[x["date"], x["reason"]] for x in s["penalties"]]
            data_table(["التاريخ", "السبب"], rows)
        else:
            empty_state("لا توجد جزاءات.")

        with st.form("pen_form", clear_on_submit=True):
            c1, c2 = st.columns([3, 1])
            reason = c1.text_input("سبب الجزاء")
            pdate = c2.date_input("التاريخ", value=date.today())
            ok = st.form_submit_button("إضافة", use_container_width=True)
        if ok and reason.strip():
            s["penalties"].append({"date": pdate.isoformat(), "reason": reason.strip()})
            st.rerun()

        section("الملاحظات")
        nn = st.text_area("ملاحظات", value=s.get("notes", ""),
                          key=f"n_{s['id']}", height=80)
        if st.button("حفظ", key=f"sn_{s['id']}"):
            s["notes"] = nn.strip()
            st.success("تم الحفظ.")


# ==========================================================
# المدرسون
# ==========================================================
def page_teachers():
    page_head("المدرسون", "بيانات المدرسين")
    tabs = st.tabs(["القائمة", "إضافة مدرس"])

    with tabs[0]:
        teachers = st.session_state.teachers
        if not teachers:
            empty_state("لا يوجد مدرسون.")
        else:
            rows = []
            for t in teachers:
                m_c = count_teacher_month(t["id"], date.today().year, date.today().month)
                w_c = count_teacher_week(t["id"])
                rows.append([t["code"], t["name"], t["specialty"], t["phone"],
                             w_c, m_c, f"{t['session_price']:,.0f}",
                             f"{m_c * t['session_price']:,.0f}",
                             "مفعّل" if t.get("active", True) else "معطّل"])
            data_table(["الكود", "الاسم", "التخصص", "التليفون",
                        "حصص/أسبوع", "حصص/شهر", "ثمن الحصة", "المستحق", "الحالة"], rows)

            section("تعديل مدرس")
            edit_opts = {f"{t['name']} — {t['code']}": t["id"] for t in teachers}
            sel = st.selectbox("اختر", list(edit_opts.keys()), key="et")
            t = teacher_by_id(edit_opts[sel])
            if t:
                with st.form("et_form"):
                    c1, c2 = st.columns(2)
                    nm = c1.text_input("الاسم", value=t["name"])
                    nid = c2.text_input("الرقم القومي", value=t["national_id"])
                    ph = c1.text_input("التليفون", value=t["phone"])
                    cd = c2.text_input("الكود", value=t["code"])
                    ql = c1.text_input("المؤهل", value=t["qualification"])
                    gy = c2.text_input("سنة التخرج", value=t["grad_year"])
                    sp = c1.selectbox(
                        "التخصص", SPECIALTIES,
                        index=SPECIALTIES.index(t["specialty"])
                        if t["specialty"] in SPECIALTIES else 0,
                    )
                    pr = c2.number_input("ثمن الحصة", min_value=0.0,
                                         value=float(t["session_price"]),
                                         step=5.0, format="%.2f")
                    ac = st.checkbox("الحساب مفعّل", value=t.get("active", True))
                    sv = st.form_submit_button("حفظ", type="primary", use_container_width=True)
                if sv:
                    t.update({"name": nm.strip(), "national_id": nid.strip(),
                              "phone": ph.strip(), "code": cd.strip(),
                              "qualification": ql.strip(), "grad_year": gy.strip(),
                              "specialty": sp, "session_price": float(pr), "active": ac})
                    st.success("تم الحفظ.")

    with tabs[1]:
        with st.form("at_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nm = c1.text_input("الاسم")
            nid = c2.text_input("الرقم القومي")
            ph = c1.text_input("التليفون")
            cd = c2.text_input("الكود")
            ql = c1.text_input("المؤهل")
            gy = c2.text_input("سنة التخرج")
            sp = c1.selectbox("التخصص", SPECIALTIES)
            pr = c2.number_input("ثمن الحصة", min_value=0.0, value=75.0, step=5.0)
            ok = st.form_submit_button("إضافة المدرس", type="primary", use_container_width=True)
        if ok:
            nm = (nm or "").strip(); cd = (cd or "").strip()
            if not nm or not cd:
                st.error("الاسم والكود مطلوبان.")
            elif any(x["code"] == cd for x in st.session_state.teachers):
                st.error("الكود مستخدم.")
            else:
                nid_new = max((x["id"] for x in st.session_state.teachers), default=0) + 1
                st.session_state.teachers.append({
                    "id": nid_new, "name": nm, "national_id": (nid or "").strip(),
                    "phone": (ph or "").strip(), "code": cd,
                    "qualification": (ql or "").strip(),
                    "grad_year": (gy or "").strip(), "specialty": sp,
                    "session_price": float(pr), "active": True,
                })
                st.success(f"تمت إضافة {nm}.")


# ==========================================================
# دفتر الجلسات
# ==========================================================
def page_sessions():
    page_head("دفتر الجلسات", "تسجيل الحصص التي تم تدريسها فعلياً")
    role = st.session_state.role
    is_teacher = role == "teacher"
    my_tid = st.session_state.current_teacher_id

    with st.expander("تسجيل جلسة جديدة", expanded=True):
        with st.form("add_session", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            if is_teacher:
                t = teacher_by_id(my_tid)
                c1.text_input("المدرس", value=t["name"] if t else "-", disabled=True)
                s_tid = my_tid
            else:
                t_opts = {x["name"]: x["id"] for x in st.session_state.teachers}
                s_tid = t_opts[c1.selectbox("المدرس", list(t_opts.keys()))]

            s_date = c2.date_input("التاريخ", value=date.today())
            s_grade = c3.selectbox("الصف", GRADES)
            s_spec = c1.selectbox("التخصص", SPECIALTIES)
            s_subj = c2.text_input("الوصف", value="ورشة عملية")
            s_per = c3.selectbox("الحصة", PERIODS)
            s_dur = c1.number_input("المدة (دقيقة)", 15, 300, 90, 15)
            s_notes = c2.text_input("ملاحظات")
            ok = st.form_submit_button("حفظ الجلسة", type="primary", use_container_width=True)
        if ok:
            nid = max((s["id"] for s in st.session_state.sessions), default=0) + 1
            st.session_state.sessions.append({
                "id": nid, "teacher_id": s_tid, "date": s_date.isoformat(),
                "grade": s_grade, "specialty": s_spec,
                "subject": s_subj.strip() or "—", "period": s_per,
                "duration_minutes": int(s_dur), "notes": s_notes.strip(),
                "logged_by": st.session_state.display_name,
                "logged_at": datetime.now().isoformat(timespec="seconds"),
            })
            st.success("تم تسجيل الجلسة.")
            st.rerun()

    section("سجل الجلسات")
    c1, c2, c3 = st.columns(3)
    if is_teacher:
        c1.text_input("المدرس", value=teacher_by_id(my_tid)["name"], disabled=True)
        f_tid = my_tid
    else:
        t_opts = {"الكل": None}
        for t in st.session_state.teachers:
            t_opts[t["name"]] = t["id"]
        f_tid = t_opts[c1.selectbox("المدرس", list(t_opts.keys()), key="f_t")]

    cur = date.today()
    f_year = c2.number_input("السنة", 2020, 2100, cur.year, 1)
    f_month = c3.selectbox("الشهر", list(range(1, 13)), index=cur.month - 1)
    prefix = f"{int(f_year)}-{int(f_month):02d}"

    rows_all = [s for s in st.session_state.sessions
                if s["date"].startswith(prefix)
                and (f_tid is None or s["teacher_id"] == f_tid)]
    rows_all.sort(key=lambda x: x["date"], reverse=True)

    if not rows_all:
        empty_state("لا توجد جلسات في هذه الفترة.")
    else:
        data = []
        for s in rows_all:
            t = teacher_by_id(s["teacher_id"])
            data.append([s["date"], t["name"] if t else "—",
                         s["grade"], s["specialty"], s["subject"],
                         s["period"], f"{s['duration_minutes']} د"])
        data_table(["التاريخ", "المدرس", "الصف", "التخصص",
                    "الوصف", "الحصة", "المدة"], data)

        total = len(rows_all)
        due = sum((teacher_by_id(s["teacher_id"])["session_price"]
                   if teacher_by_id(s["teacher_id"]) else 0) for s in rows_all)
        cA, cB = st.columns(2)
        cA.metric("عدد الجلسات", total)
        cB.metric("القيمة", f"{due:,.2f} ج.م")


# ==========================================================
# الحضور والغياب — واجهة مخصصة (لا data_editor)
# ==========================================================
def page_attendance():
    page_head("الحضور والغياب", "تسجيل الحضور اليومي للطلاب")
    students = st.session_state.students
    if not students:
        empty_state("لا يوجد طلاب.")
        return

    c1, c2 = st.columns(2)
    sel_date = c1.date_input("التاريخ", value=date.today())
    gr = c2.selectbox("الصف", ["الكل"] + GRADES, key="att_gr")
    dstr = sel_date.isoformat()
    filtered = students if gr == "الكل" else [s for s in students if s.get("grade") == gr]

    if not filtered:
        empty_state("لا يوجد طلاب في هذا الصف.")
        return

    section("تسجيل الحضور")

    qa1, qa2, qa3, qa4 = st.columns(4)
    if qa1.button("✅ الكل حاضر", use_container_width=True, key="qa_p"):
        for s in filtered:
            s["attendance"][dstr] = "حاضر"
        st.rerun()
    if qa2.button("❌ الكل غائب", use_container_width=True, key="qa_a"):
        for s in filtered:
            s["attendance"][dstr] = "غائب"
        st.rerun()
    if qa3.button("⏰ الكل متأخر", use_container_width=True, key="qa_l"):
        for s in filtered:
            s["attendance"][dstr] = "متأخر"
        st.rerun()
    if qa4.button("🗑️ إلغاء تسجيل اليوم", use_container_width=True, key="qa_clr"):
        for s in filtered:
            s["attendance"].pop(dstr, None)
        st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # رأس الجدول
    h1, h2, h3, h4 = st.columns([1, 3.5, 1.2, 3])
    h1.markdown("<div style='font-weight:800; font-size:14.5px; color:var(--muted); padding-right:6px;'>الكود</div>", unsafe_allow_html=True)
    h2.markdown("<div style='font-weight:800; font-size:14.5px; color:var(--muted); padding-right:6px;'>الطالب</div>", unsafe_allow_html=True)
    h3.markdown("<div style='font-weight:800; font-size:14.5px; color:var(--muted); padding-right:6px;'>الصف</div>", unsafe_allow_html=True)
    h4.markdown("<div style='font-weight:800; font-size:14.5px; color:var(--muted); padding-right:6px;'>الحالة</div>", unsafe_allow_html=True)

    # الصفوف
    for s in filtered:
        cur_val = s["attendance"].get(dstr, "حاضر")
        row_html = (
            "<div class='att-row'>"
            f"<div class='code'>{s['code']}</div>"
            f"<div class='name'>{s['name']}</div>"
            f"<div class='grade'>{s.get('grade', '-')}</div>"
            "</div>"
        )
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(row_html, unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='att-row-wrap'>", unsafe_allow_html=True)
            new_val = st.radio(
                "",
                ATT_OPTIONS,
                index=ATT_OPTIONS.index(cur_val),
                horizontal=True,
                key=f"att_{dstr}_{s['id']}",
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)
            if new_val != cur_val:
                s["attendance"][dstr] = new_val
                st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if st.button("💾 حفظ ومتابعة", type="primary", use_container_width=True, key="save_att"):
        st.success(f"تم حفظ حضور {dstr}.")

    section("ملخص تراكمي")
    rows = []
    for s in students:
        p, a, l = attendance_totals(s)
        rows.append([s["code"], s["name"], s.get("grade", "-"), p, a, l])
    data_table(["الكود", "الطالب", "الصف", "حضور", "غياب", "تأخير"], rows)


# ==========================================================
# المستحقات
# ==========================================================
def page_payroll():
    page_head("المستحقات المالية", "كشف حساب المدرسين الشهري")
    teachers = st.session_state.teachers
    if not teachers:
        empty_state("لا يوجد مدرسون.")
        return

    cur = date.today()
    c1, c2 = st.columns(2)
    year = c1.number_input("السنة", 2020, 2100, cur.year, 1)
    month = c2.selectbox("الشهر", list(range(1, 13)), index=cur.month - 1)
    prefix = f"{int(year)}-{int(month):02d}"

    rows = []
    grand = 0.0
    total = 0
    for t in teachers:
        c = sum(1 for s in st.session_state.sessions
                if s["teacher_id"] == t["id"] and s["date"].startswith(prefix))
        due = c * t["session_price"]
        grand += due; total += c
        rows.append([t["code"], t["name"], t["specialty"],
                     c, f"{t['session_price']:,.2f}", f"{due:,.2f}"])
    data_table(["الكود", "المدرس", "التخصص",
                "عدد الحصص", "ثمن الحصة", "المستحق"], rows)

    cA, cB = st.columns(2)
    cA.metric("إجمالي الحصص", total)
    cB.metric("إجمالي المستحقات", f"{grand:,.2f} ج.م")

    st.download_button(
        "تحميل الكشف (CSV)",
        pd.DataFrame(rows, columns=["الكود", "المدرس", "التخصص",
                                     "عدد الحصص", "ثمن الحصة", "المستحق"]
                     ).to_csv(index=False).encode("utf-8-sig"),
        file_name=f"payroll_{prefix}.csv",
        mime="text/csv",
    )


# ==========================================================
# مستحقاتي
# ==========================================================
def page_my_payroll():
    tid = st.session_state.current_teacher_id
    t = teacher_by_id(tid)
    if not t:
        empty_state("لا يوجد ملف مدرس مرتبط بحسابك.")
        return

    page_head("مستحقاتي", "كشف حسابك الشهري")

    cur = date.today()
    c1, c2 = st.columns(2)
    year = c1.number_input("السنة", 2020, 2100, cur.year, 1)
    month = c2.selectbox("الشهر", list(range(1, 13)), index=cur.month - 1)
    prefix = f"{int(year)}-{int(month):02d}"

    mine = [s for s in st.session_state.sessions
            if s["teacher_id"] == tid and s["date"].startswith(prefix)]

    cA, cB, cC = st.columns(3)
    cA.metric("عدد الحصص", len(mine))
    cB.metric("ثمن الحصة", f"{t['session_price']:,.0f} ج.م")
    cC.metric("المستحق", f"{len(mine) * t['session_price']:,.0f} ج.م")

    section("سجل جلساتي")
    if mine:
        data = [[s["date"], s["grade"], s["specialty"], s["subject"], s["period"]]
                for s in sorted(mine, key=lambda x: x["date"], reverse=True)]
        data_table(["التاريخ", "الصف", "التخصص", "الوصف", "الحصة"], data)
    else:
        empty_state("لا توجد جلسات في هذا الشهر.")


# ==========================================================
# إدارة المستخدمين
# ==========================================================
def page_users():
    page_head("إدارة المستخدمين", "الصلاحيات والحسابات")
    users = st.session_state.users

    section("المستخدمون")
    rows = []
    for u in users:
        rows.append([u["name"], u["email"], u.get("username", ""),
                     ROLES.get(u["role"], u["role"]),
                     "مفعّل" if u.get("active", True) else "معطّل"])
    data_table(["الاسم", "البريد", "اسم المستخدم", "الدور", "الحالة"], rows)

    section("تعديل مستخدم")
    sel = st.selectbox("اختر المستخدم",
                       [f"{u['name']} — {u['email']}" for u in users], key="mg_u")
    u = users[[f"{x['name']} — {x['email']}" for x in users].index(sel)]

    with st.form("edit_user_form"):
        c1, c2 = st.columns(2)
        nm = c1.text_input("الاسم", value=u["name"])
        em = c2.text_input("البريد", value=u["email"])
        un = c1.text_input("اسم المستخدم", value=u.get("username", ""))
        pw = c2.text_input("كلمة مرور جديدة (اتركها فارغة لعدم التغيير)",
                           value="", type="password")
        rl = c1.selectbox("الدور", list(ROLES.keys()),
                          format_func=lambda x: ROLES[x],
                          index=list(ROLES.keys()).index(u["role"]))
        ac = c2.checkbox("مفعّل", value=u.get("active", True))
        sv = st.form_submit_button("حفظ", type="primary", use_container_width=True)

    if sv:
        conflict = any(x["id"] != u["id"] and (
            x["email"].lower() == em.strip().lower()
            or (un.strip() and x.get("username", "").lower() == un.strip().lower())
        ) for x in users)
        if conflict:
            st.error("البريد أو اسم المستخدم مستخدم مسبقاً.")
        else:
            u["name"] = nm.strip(); u["email"] = em.strip()
            u["username"] = un.strip(); u["role"] = rl; u["active"] = ac
            if pw.strip(): u["password_hash"] = hp(pw.strip())
            st.success("تم التحديث.")
            st.rerun()

    if u["id"] != st.session_state.user_id:
        if st.button("حذف المستخدم", key="du"):
            st.session_state.users = [x for x in users if x["id"] != u["id"]]
            st.rerun()

    section("إضافة مستخدم")
    with st.form("add_user", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n_nm = c1.text_input("الاسم")
        n_em = c2.text_input("البريد الإلكتروني")
        n_un = c1.text_input("اسم المستخدم")
        n_pw = c2.text_input("كلمة المرور", type="password")
        n_rl = c1.selectbox("الدور", list(ROLES.keys()), format_func=lambda x: ROLES[x])
        link_tid = None
        if n_rl == "teacher":
            t_opts = {"— بدون ربط —": None}
            for t in st.session_state.teachers:
                t_opts[t["name"]] = t["id"]
            link_tid = t_opts[c2.selectbox("ربط بمدرس", list(t_opts.keys()))]
        ok = st.form_submit_button("إضافة", type="primary", use_container_width=True)

    if ok:
        n_nm = (n_nm or "").strip(); n_em = (n_em or "").strip(); n_pw = (n_pw or "").strip()
        if not n_nm or not n_em or not n_pw:
            st.error("الاسم والبريد وكلمة المرور مطلوبة.")
        elif any(x["email"].lower() == n_em.lower() for x in st.session_state.users):
            st.error("البريد مستخدم بالفعل.")
        else:
            nid = max((x["id"] for x in st.session_state.users), default=0) + 1
            st.session_state.users.append({
                "id": nid, "name": n_nm, "email": n_em,
                "username": (n_un or "").strip() or n_em.split("@")[0],
                "password_hash": hp(n_pw), "role": n_rl,
                "teacher_id": link_tid, "active": True,
                "created_at": date.today().isoformat(),
            })
            st.success("تم إضافة المستخدم.")


# ==========================================================
# Router
# ==========================================================
def main():
    init_data()
    if not st.session_state.get("logged_in"):
        login_page()
        return

    choice = render_sidebar()
    role = st.session_state.role

    if role == "teacher":
        {"دفتر الجلسات": page_sessions, "الحضور والغياب": page_attendance,
         "مستحقاتي": page_my_payroll}.get(choice, lambda: None)()
        return
    if role == "accountant":
        {"لوحة التحكم": page_dashboard, "دفتر الجلسات": page_sessions,
         "المستحقات المالية": page_payroll}.get(choice, lambda: None)()
        return
    if role == "viewer":
        {"لوحة التحكم": page_dashboard, "الطلاب": page_students,
         "المدرسون": page_teachers}.get(choice, lambda: None)()
        return

    routes = {
        "لوحة التحكم": page_dashboard, "ملف المدير": page_manager_profile,
        "الطلاب": page_students, "المدرسون": page_teachers,
        "دفتر الجلسات": page_sessions, "الحضور والغياب": page_attendance,
        "المستحقات المالية": page_payroll, "إدارة المستخدمين": page_users,
    }
    routes.get(choice, page_dashboard)()


if __name__ == "__main__":
    main()
