# -*- coding: utf-8 -*-
"""
نظام إدارة مدرسة التوكل جيلا
الإصدار: 2.1.0
"""

import hashlib
import re
import random
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

# ==========================================================
# ثوابت عامة
# ==========================================================
APP_NAME = "التوكل جيلا"
APP_TAGLINE = "نظام إدارة المدرسة"
APP_VERSION = "1.1.0"
APP_BUILD = "2026.09"

GRADES = ["الأول الصناعي", "الثاني الصناعي", "الثالث الصناعي"]
SPECIALTIES = [
    "ميكانيكا عامة", "كهرباء وإلكترونيات", "لحام وتشكيل معادن",
    "خراطة", "نجارة", "تبريد وتكييف",
]
PERIODS = [f"الحصة {i}" for i in range(1, 9)]

ROLES = {
    "admin": "مدير المدرسة",
    "teacher": "معلم",
    "accountant": "محاسب",
    "viewer": "مشاهد",
}

# ==========================================================
# إعداد الصفحة
# ==========================================================
st.set_page_config(
    page_title=f"{APP_NAME} | نظام الإدارة",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# الهوية البصرية (CSS)
# ==========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');

    :root {
        --bg: #f6f7fb;
        --bg-elev: #ffffff;
        --surface: #ffffff;
        --surface-2: #f1f3f9;
        --border: #e4e7ef;
        --border-strong: #d4d8e3;
        --text: #0f172a;
        --text-2: #334155;
        --muted: #64748b;
        --faint: #94a3b8;
        --primary: #4f46e5;
        --primary-2: #6366f1;
        --primary-soft: #eef2ff;
        --accent: #0ea5e9;
        --success: #16a34a;
        --success-soft: #dcfce7;
        --danger: #dc2626;
        --danger-soft: #fee2e2;
        --warning: #d97706;
        --warning-soft: #fef3c7;
        --sb-bg: #0b1220;
        --sb-bg-2: #111a2e;
        --sb-text: #e5e9f2;
        --sb-muted: #94a3b8;
        --sb-border: rgba(255,255,255,0.06);
        --sb-hover: rgba(99,102,241,0.18);
        --sb-active: rgba(99,102,241,0.28);
        --shadow-sm: 0 1px 2px rgba(15,23,42,0.05);
        --shadow: 0 4px 16px rgba(15,23,42,0.07);
        --shadow-lg: 0 16px 40px rgba(15,23,42,0.12);
        --r-sm: 8px;
        --r: 12px;
        --r-lg: 16px;
        --r-xl: 20px;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg: #0a0f1c;
            --bg-elev: #111827;
            --surface: #131c31;
            --surface-2: #0f172a;
            --border: #1f2b47;
            --border-strong: #2a3a5f;
            --text: #e8eefc;
            --text-2: #c7d2e6;
            --muted: #94a3b8;
            --faint: #64748b;
            --primary: #818cf8;
            --primary-2: #a5b4fc;
            --primary-soft: rgba(129,140,248,0.14);
            --accent: #38bdf8;
            --success: #4ade80;
            --success-soft: rgba(74,222,128,0.14);
            --danger: #f87171;
            --danger-soft: rgba(248,113,113,0.14);
            --warning: #fbbf24;
            --warning-soft: rgba(251,191,36,0.14);
            --sb-bg: #060a15;
            --sb-bg-2: #0a1224;
            --sb-text: #e8eefc;
            --sb-muted: #8394b4;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.4);
            --shadow: 0 4px 16px rgba(0,0,0,0.4);
            --shadow-lg: 0 16px 40px rgba(0,0,0,0.5);
        }
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Cairo', system-ui, -apple-system, sans-serif !important;
    }

    /* ====== Root app ====== */
    .stApp {
        background: var(--bg) !important;
        color: var(--text);
    }
    .stApp, .stApp * { box-sizing: border-box; }

    /* ====== Layout: sidebar on the RIGHT ====== */
    div[data-testid="stAppViewContainer"] {
        flex-direction: row-reverse !important;
        background: var(--bg);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sb-bg) 0%, var(--sb-bg-2) 100%) !important;
        border-left: 1px solid var(--sb-border) !important;
        border-right: none !important;
        direction: rtl !important;
        text-align: right !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--sb-text) !important;
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div {
        color: var(--sb-text) !important;
    }
    section[data-testid="stSidebar"] .stRadio > label:first-child { display: none !important; }
    section[data-testid="stSidebar"] .stRadio [role="radiogroup"] {
        gap: 4px;
        display: flex;
        flex-direction: column;
    }
    section[data-testid="stSidebar"] .stRadio label {
        display: flex !important;
        flex-direction: row-reverse !important;
        justify-content: flex-start !important;
        align-items: center;
        gap: 10px;
        padding: 10px 14px !important;
        margin: 0 !important;
        border-radius: var(--r) !important;
        transition: background .15s ease;
        font-weight: 600 !important;
        font-size: 14px !important;
        cursor: pointer;
        border: 1px solid transparent;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: var(--sb-hover) !important;
        border-color: rgba(129,140,248,0.25);
    }
    section[data-testid="stSidebar"] .stRadio label p { font-size: 14px !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] .stRadio label > div:first-child { display: none !important; }
    section[data-testid="stSidebar"] .stRadio [aria-checked="true"] { background: var(--sb-active) !important; }

    section[data-testid="stSidebar"] hr {
        border: none; border-top: 1px solid var(--sb-border); margin: 12px 0;
    }

    /* ====== Header ====== */
    header[data-testid="stHeader"] { background: transparent !important; }

    /* ====== Typography ====== */
    h1, h2, h3, h4, h5, h6 { color: var(--text) !important; font-weight: 800 !important; letter-spacing: -0.01em; }
    p, span, div, label { color: var(--text); }
    .stMarkdown p { color: var(--text-2); }
    small, .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }

    /* ====== Inputs ====== */
    input, textarea, select,
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stTimeInput input, .stTextArea textarea {
        direction: rtl !important;
        text-align: right !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
        border-radius: var(--r) !important;
    }
    div[data-baseweb="input"], div[data-baseweb="textarea"],
    div[data-baseweb="select"] > div {
        direction: rtl !important;
        text-align: right !important;
        background: var(--surface) !important;
        border-radius: var(--r) !important;
        border-color: var(--border) !important;
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within,
    div[data-baseweb="select"]:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-soft) !important;
    }
    div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
        direction: rtl !important; text-align: right !important;
        background: var(--surface) !important;
        color: var(--text) !important;
    }
    label, .stMarkdown, .stText, .stCaption { text-align: right; }

    /* ====== Buttons ====== */
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
        direction: rtl !important;
        font-family: 'Cairo', sans-serif !important;
        border-radius: var(--r) !important;
        font-weight: 700 !important;
        border: 1px solid var(--border-strong) !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        padding: 9px 18px !important;
        transition: all .15s ease;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        border-color: var(--primary) !important;
        color: var(--primary) !important;
    }
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: var(--primary) !important;
        color: #ffffff !important;
        border-color: var(--primary) !important;
        box-shadow: 0 2px 8px rgba(79,70,229,0.28);
    }
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {
        background: var(--primary-2) !important;
        color: #fff !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79,70,229,0.35);
    }

    /* ====== Metrics ====== */
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);
        padding: 16px 18px;
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stMetricLabel"] p {
        text-align: right !important;
        color: var(--muted) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    [data-testid="stMetricValue"] {
        text-align: right !important;
        color: var(--text) !important;
        font-weight: 900 !important;
        font-size: 26px !important;
    }

    /* ====== Tabs ====== */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
        gap: 4px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Cairo', sans-serif !important;
        font-weight: 700;
        font-size: 14px;
        padding: 10px 18px;
        color: var(--muted) !important;
        border-bottom: 2px solid transparent;
        border-radius: 0;
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
    }

    /* ====== Expander ====== */
    .streamlit-expanderHeader {
        font-weight: 700 !important;
        font-size: 14px !important;
        background: var(--surface) !important;
        border-radius: var(--r) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        padding: 10px 14px !important;
    }
    details[open] > summary.streamlit-expanderHeader { border-bottom-left-radius: 0 !important; border-bottom-right-radius: 0 !important; }
    [data-testid="stExpander"] { border: none !important; }

    /* ====== Alerts ====== */
    .stAlert {
        border-radius: var(--r) !important;
        border: 1px solid var(--border) !important;
        text-align: right;
    }

    /* ====== Dataframe ====== */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        direction: rtl;
        border-radius: var(--r) !important;
        overflow: hidden;
        border: 1px solid var(--border) !important;
    }

    /* ====== Forms ====== */
    [data-testid="stForm"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--r-lg) !important;
        padding: 20px !important;
        background: var(--surface) !important;
    }

    /* ====== Custom utilities ====== */
    .page-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 4px 0 20px 0;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--border);
    }
    .page-head .titles { display: flex; flex-direction: column; gap: 2px; }
    .page-head .title { font-size: 22px; font-weight: 900; color: var(--text); }
    .page-head .sub { font-size: 13px; color: var(--muted); font-weight: 500; }
    .page-head .badge {
        font-size: 11px;
        font-weight: 700;
        color: var(--primary);
        background: var(--primary-soft);
        padding: 4px 12px;
        border-radius: 999px;
        letter-spacing: .3px;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 15px;
        font-weight: 800;
        color: var(--text);
        margin: 20px 0 10px 0;
    }
    .section-title::before {
        content: '';
        width: 4px; height: 18px;
        border-radius: 2px;
        background: var(--primary);
    }

    .stat {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);
        padding: 16px 18px;
        box-shadow: var(--shadow-sm);
        display: flex;
        align-items: center;
        gap: 14px;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .stat:hover { transform: translateY(-1px); box-shadow: var(--shadow); }
    .stat .icon {
        width: 46px; height: 46px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        background: var(--primary-soft);
        color: var(--primary);
        flex-shrink: 0;
    }
    .stat .icon.success { background: var(--success-soft); color: var(--success); }
    .stat .icon.danger  { background: var(--danger-soft);  color: var(--danger); }
    .stat .icon.warning { background: var(--warning-soft); color: var(--warning); }
    .stat .icon.accent  { background: rgba(14,165,233,.12); color: var(--accent); }
    .stat .val { font-size: 22px; font-weight: 900; color: var(--text); line-height: 1.1; }
    .stat .lbl { font-size: 12.5px; color: var(--muted); font-weight: 600; margin-top: 2px; }

    /* ====== Sidebar internal ====== */
    .sb-brand {
        display: flex; align-items: center; gap: 12px;
        padding: 8px 4px 16px 4px;
        border-bottom: 1px solid var(--sb-border);
        margin-bottom: 12px;
    }
    .sb-brand .logo {
        width: 44px; height: 44px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #fff; font-size: 22px;
        box-shadow: 0 6px 16px rgba(99,102,241,.4);
        flex-shrink: 0;
    }
    .sb-brand .name { font-weight: 900; font-size: 16px; color: var(--sb-text); line-height: 1.1; }
    .sb-brand .tag { font-size: 11px; color: var(--sb-muted); margin-top: 2px; }

    .sb-user {
        background: rgba(255,255,255,0.05);
        border: 1px solid var(--sb-border);
        border-radius: var(--r);
        padding: 12px 14px;
        margin-bottom: 12px;
    }
    .sb-user .n { font-weight: 800; font-size: 14px; color: var(--sb-text); }
    .sb-user .r { font-size: 11.5px; color: #a5b4fc; margin-top: 2px; font-weight: 600; }
    .sb-user .e { font-size: 10.5px; color: var(--sb-muted); margin-top: 4px; direction: ltr; text-align: right; }

    .sb-footer {
        text-align: center;
        font-size: 11px;
        color: var(--sb-muted);
        padding: 12px 0 4px 0;
        border-top: 1px solid var(--sb-border);
        margin-top: 12px;
        line-height: 1.6;
    }
    .sb-footer .ver {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        background: rgba(99,102,241,0.18);
        color: #a5b4fc;
        font-weight: 700;
        font-size: 10.5px;
        letter-spacing: .3px;
    }

    /* ====== Login ====== */
    .login-shell {
        max-width: 420px;
        margin: 6vh auto 0 auto;
        padding: 0;
    }
    .login-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--r-xl);
        padding: 34px 30px 26px 30px;
        box-shadow: var(--shadow-lg);
        position: relative;
    }
    .login-brand {
        text-align: center;
        margin-bottom: 24px;
    }
    .login-brand .mark {
        width: 62px; height: 62px;
        margin: 0 auto 14px auto;
        border-radius: 18px;
        background: linear-gradient(135deg, #4f46e5, #7c3aed 60%, #ec4899);
        display: flex; align-items: center; justify-content: center;
        color: #fff; font-size: 30px;
        box-shadow: 0 12px 28px rgba(79,70,229,.4);
    }
    .login-brand .t1 {
        font-size: 22px; font-weight: 900; color: var(--text);
        letter-spacing: -0.01em;
    }
    .login-brand .t2 {
        font-size: 13px; color: var(--muted); margin-top: 4px; font-weight: 600;
    }
    .login-foot {
        text-align: center;
        font-size: 11px;
        color: var(--faint);
        margin-top: 18px;
    }

    /* ====== Empty states ====== */
    .empty {
        padding: 30px;
        text-align: center;
        color: var(--muted);
        background: var(--surface-2);
        border: 1px dashed var(--border-strong);
        border-radius: var(--r-lg);
        font-size: 14px;
        font-weight: 600;
    }

    /* ====== Chips ====== */
    .chip {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 700;
        margin-inline-start: 6px;
    }
    .chip.ok  { background: var(--success-soft); color: var(--success); }
    .chip.no  { background: var(--danger-soft);  color: var(--danger); }
    .chip.wrn { background: var(--warning-soft); color: var(--warning); }
    .chip.inf { background: var(--primary-soft); color: var(--primary); }

    /* ====== Misc ====== */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--muted); }

    /* Hide Streamlit decoration */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stDecoration"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# دوال مساعدة
# ==========================================================
def hp(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def verify(pw: str, hashed: str) -> bool:
    return hp(pw) == hashed


def split_phones(text: str):
    if not text:
        return []
    parts = re.split(r"[,،;/\n]+", text)
    return [p.strip() for p in parts if p.strip()]


def attendance_totals(student):
    att = student.get("attendance", {})
    p = sum(1 for v in att.values() if v == "حاضر")
    a = sum(1 for v in att.values() if v == "غائب")
    l = sum(1 for v in att.values() if v == "متأخر")
    return p, a, l


def build_attendance(seed: int, days: int = 21):
    rnd = random.Random(seed * 7919 + 13)
    res = {}
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=i)
        if d.weekday() == 4:
            continue
        res[d.isoformat()] = rnd.choices(
            ["حاضر", "غائب", "متأخر"], weights=[80, 10, 10]
        )[0]
    return res


def month_prefix(d: date) -> str:
    return f"{d.year}-{d.month:02d}"


def teacher_by_id(tid):
    return next((t for t in st.session_state.teachers if t["id"] == tid), None)


def user_by_login(identifier):
    identifier = (identifier or "").strip().lower()
    for u in st.session_state.users:
        if u["email"].lower() == identifier:
            return u
        if u.get("username", "").lower() == identifier and u.get("username"):
            return u
    return None


def count_teacher_month(teacher_id, year, month):
    prefix = f"{year}-{month:02d}"
    return sum(
        1 for s in st.session_state.sessions
        if s["teacher_id"] == teacher_id and s["date"].startswith(prefix)
    )


def count_teacher_week(teacher_id):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    return sum(
        1 for s in st.session_state.sessions
        if s["teacher_id"] == teacher_id
        and start.isoformat() <= s["date"] <= today.isoformat()
    )


def gen_demo_sessions(teachers):
    rnd = random.Random(2025)
    out = []
    sid = 1
    today = date.today()
    for off in range(30):
        d = today - timedelta(days=off)
        if d.weekday() == 4:
            continue
        for t in teachers:
            for _ in range(rnd.randint(2, 5)):
                out.append({
                    "id": sid,
                    "teacher_id": t["id"],
                    "date": d.isoformat(),
                    "grade": rnd.choice(GRADES),
                    "specialty": rnd.choice(SPECIALTIES),
                    "subject": rnd.choice([
                        "ورشة عملية", "رسم فني", "تكنولوجيا عامة",
                        "حصة نظري", "تدريب ميداني", "مشروع تخرج",
                    ]),
                    "period": rnd.choice(PERIODS),
                    "duration_minutes": rnd.choice([45, 60, 90]),
                    "notes": "",
                    "logged_by": "demo",
                    "logged_at": datetime.now().isoformat(timespec="seconds"),
                })
                sid += 1
    return out


# ==========================================================
# تهيئة البيانات
# ==========================================================
def init_data():
    if st.session_state.get("_init_v21"):
        return
    st.session_state._init_v21 = True

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
        "qualification": "بكالوريوس هندسة صناعية — ميكانيكا",
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
         "بكالوريوس تربية صناعية", "2008", 75.0, "ميكانيكا عامة"),
        ("أ. منى عبد الحميد علي", "28702021234567", "01088776655", "TCH-002",
         "بكالوريوس علوم — رياضيات", "2010", 70.0, "كهرباء وإلكترونيات"),
        ("أ. مصطفى كامل الجندي", "28403031234567", "01077665544", "TCH-003",
         "دبلوم فني صناعي متقدم", "2006", 85.0, "لحام وتشكيل معادن"),
        ("أ. هدى إبراهيم شاكر", "28904041234567", "01066554433", "TCH-004",
         "ليسانس آداب — إنجليزي", "2012", 65.0, "خراطة"),
        ("أ. طارق ياسر عبد الفتاح", "28305051234567", "01055443322", "TCH-005",
         "بكالوريوس هندسة ميكاترونكس", "2007", 90.0, "تبريد وتكييف"),
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
        ("أحمد محمود السيد", "STD-001", "30101011234567", "الأول الصناعي", "ميكانيكا عامة",
         ["01011112222", "01011113333"], ["01211112222"], "نجار"),
        ("مريم خالد عبد الله", "STD-002", "30201021234567", "الأول الصناعي", "كهرباء وإلكترونيات",
         ["01022223333"], ["01222223333"], "مدرسة"),
        ("يوسف إبراهيم حسن", "STD-003", "30101031234567", "الثاني الصناعي", "لحام وتشكيل معادن",
         ["01033334444"], ["01233334444"], "حداد"),
        ("سلمى أحمد فتحي", "STD-004", "30201041234567", "الثاني الصناعي", "خراطة",
         ["01044445555"], ["01244445555"], "تاجر"),
        ("عمر سامي رشاد", "STD-005", "30101051234567", "الثالث الصناعي", "تبريد وتكييف",
         ["01055556666"], ["01255556666"], "كهربائي"),
        ("نور الهدى مصطفى", "STD-006", "30201061234567", "الأول الصناعي", "ميكانيكا عامة",
         ["01066667777"], ["01266667777"], "محاسب"),
        ("محمد عادل شعبان", "STD-007", "30101071234567", "الثاني الصناعي", "كهرباء وإلكترونيات",
         ["01077778888"], ["01277778888"], "سباك"),
        ("حبيبة وليد أنور", "STD-008", "30201081234567", "الثالث الصناعي", "لحام وتشكيل معادن",
         ["01088889999"], ["01288889999"], "صيدلي"),
    ]

    students = []
    for idx, s in enumerate(students_seed, start=1):
        students.append({
            "id": idx, "name": s[0], "code": s[1], "national_id": s[2],
            "grade": s[3], "specialty": s[4],
            "phones": s[5], "parent_phones": s[6], "father_job": s[7],
            "attendance": build_attendance(idx),
            "penalties": (
                [{"date": (date.today() - timedelta(days=3)).isoformat(),
                  "reason": "التأخر عن الطابور الصباحي"}] if idx % 3 == 0 else []
            ),
            "notes": "منتظم ومتفاعل." if idx % 2 == 1 else "يحتاج متابعة إضافية بالورشة.",
        })
    st.session_state.students = students
    st.session_state.sessions = gen_demo_sessions(teachers)


# ==========================================================
# مكونات واجهة موحدة
# ==========================================================
def page_head(title, subtitle="", badge=""):
    badge_html = f"<span class='badge'>{badge}</span>" if badge else ""
    sub_html = f"<span class='sub'>{subtitle}</span>" if subtitle else ""
    st.markdown(
        f"""
        <div class='page-head'>
            <div class='titles'>
                <span class='title'>{title}</span>
                {sub_html}
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)


def stat(icon, label, value, tone=""):
    cls = f"icon {tone}".strip()
    st.markdown(
        f"""
        <div class='stat'>
            <div class='{cls}'>{icon}</div>
            <div>
                <div class='val'>{value}</div>
                <div class='lbl'>{label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(text):
    st.markdown(f"<div class='empty'>{text}</div>", unsafe_allow_html=True)


# ==========================================================
# صفحة تسجيل الدخول
# ==========================================================
def login_page():
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.15, 1])
    with c2:
        st.markdown(
            f"""
            <div class='login-shell'>
                <div class='login-card'>
                    <div class='login-brand'>
                        <div class='mark'>🎓</div>
                        <div class='t1'>{APP_NAME}</div>
                        <div class='t2'>{APP_TAGLINE}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form", clear_on_submit=False):
            identifier = st.text_input("اسم المستخدم أو البريد الإلكتروني")
            password = st.text_input("كلمة المرور", type="password")
            ok = st.form_submit_button(
                "تسجيل الدخول", use_container_width=True, type="primary"
            )
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
# الشريط الجانبي
# ==========================================================
def render_sidebar():
    role = st.session_state.role
    with st.sidebar:
        st.markdown(
            f"""
            <div class='sb-brand'>
                <div class='logo'>🎓</div>
                <div>
                    <div class='name'>{APP_NAME}</div>
                    <div class='tag'>{APP_TAGLINE}</div>
                </div>
            </div>
            <div class='sb-user'>
                <div class='n'>👤 {st.session_state.display_name}</div>
                <div class='r'>{ROLES.get(role, role)}</div>
                <div class='e'>{st.session_state.email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if role == "admin":
            pages = [
                "لوحة التحكم",
                "ملف المدير",
                "الطلاب",
                "المدرسون",
                "دفتر الجلسات",
                "الحضور والغياب",
                "المستحقات المالية",
                "إدارة المستخدمين",
            ]
        elif role == "teacher":
            pages = ["دفتر الجلسات", "الحضور والغياب", "مستحقاتي"]
        elif role == "accountant":
            pages = ["لوحة التحكم", "دفتر الجلسات", "المستحقات المالية"]
        else:
            pages = ["لوحة التحكم", "الطلاب", "المدرسون"]

        icons = {
            "لوحة التحكم": "🏠", "ملف المدير": "👤", "الطلاب": "🎓",
            "المدرسون": "👨‍🏫", "دفتر الجلسات": "📚", "الحضور والغياب": "✅",
            "المستحقات المالية": "💰", "إدارة المستخدمين": "🔐", "مستحقاتي": "💵",
        }
        labels = [f"{icons.get(p, '•')}  {p}" for p in pages]
        choice_label = st.radio("nav", labels, label_visibility="collapsed")
        choice = pages[labels.index(choice_label)]

        st.markdown(
            f"""
            <div class='sb-footer'>
                <span class='ver'>v {APP_VERSION}</span>
                <div style='margin-top:6px;'>التوكل جيلا © {date.today().year}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("تسجيل الخروج", use_container_width=True, key="logout"):
            for k in ["logged_in", "user_id", "role", "display_name", "email", "current_teacher_id"]:
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

    p_today = sum(1 for s in students if s["attendance"].get(today_str) == "حاضر")
    a_today = sum(1 for s in students if s["attendance"].get(today_str) == "غائب")
    l_today = sum(1 for s in students if s["attendance"].get(today_str) == "متأخر")

    month_sessions = [s for s in sessions if s["date"].startswith(cur_prefix)]
    due = 0.0
    for t in teachers:
        c = sum(1 for s in month_sessions if s["teacher_id"] == t["id"])
        due += c * t["session_price"]

    c1, c2, c3, c4 = st.columns(4)
    with c1: stat("🎓", "إجمالي الطلاب", len(students))
    with c2: stat("👨‍🏫", "إجمالي المدرسين", len(teachers), "accent")
    with c3: stat("📚", "جلسات الشهر", len(month_sessions), "warning")
    with c4: stat("💰", "مستحقات الشهر", f"{due:,.0f} ج.م", "success")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5: stat("✅", "حضور اليوم", p_today, "success")
    with c6: stat("❌", "غياب اليوم", a_today, "danger")
    with c7: stat("⏰", "تأخير اليوم", l_today, "warning")
    with c8: stat("👥", "حسابات نشطة",
                  sum(1 for u in st.session_state.users if u.get("active", True)),
                  "accent")

    section("ترتيب المدرسين حسب الحصص هذا الشهر")
    rows = []
    for t in teachers:
        c = sum(1 for s in month_sessions if s["teacher_id"] == t["id"])
        rows.append({"المدرس": t["name"], "التخصص": t["specialty"], "عدد الحصص": c})
    df = pd.DataFrame(rows).sort_values("عدد الحصص", ascending=False).reset_index(drop=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


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
                if email.strip():
                    u["email"] = email.strip()
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
            q = c1.text_input("بحث بالاسم أو الكود", placeholder="").strip().lower()
            gr = c2.selectbox("الصف", ["الكل"] + GRADES)

            filtered = [
                s for s in students
                if (not q or q in s["name"].lower() or q in s["code"].lower())
                and (gr == "الكل" or s.get("grade") == gr)
            ]

            if not filtered:
                empty_state("لا توجد نتائج مطابقة.")
            else:
                rows = []
                for s in filtered:
                    p, a, l = attendance_totals(s)
                    rows.append({
                        "الكود": s["code"], "الاسم": s["name"],
                        "الصف": s.get("grade", "-"), "التخصص": s.get("specialty", "-"),
                        "حضور": p, "غياب": a, "تأخير": l,
                        "جزاءات": len(s["penalties"]),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

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
            name = (name or "").strip()
            code = (code or "").strip()
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
            df = pd.DataFrame(
                [{"التاريخ": k, "الحالة": v}
                 for k, v in sorted(s["attendance"].items(), reverse=True)]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            empty_state("لا يوجد سجل.")

        section("الجزاءات")
        if s["penalties"]:
            df = pd.DataFrame([{"التاريخ": x["date"], "السبب": x["reason"]} for x in s["penalties"]])
            st.dataframe(df, use_container_width=True, hide_index=True)
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
        nn = st.text_area("ملاحظات", value=s.get("notes", ""), key=f"n_{s['id']}", height=80)
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
                rows.append({
                    "الكود": t["code"], "الاسم": t["name"], "التخصص": t["specialty"],
                    "التليفون": t["phone"], "حصص/أسبوع": w_c, "حصص/شهر": m_c,
                    "ثمن الحصة": f"{t['session_price']:,.0f}",
                    "المستحق": f"{m_c * t['session_price']:,.0f}",
                    "الحالة": "مفعّل" if t.get("active", True) else "معطّل",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

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
                        index=SPECIALTIES.index(t["specialty"]) if t["specialty"] in SPECIALTIES else 0,
                    )
                    pr = c2.number_input(
                        "ثمن الحصة", min_value=0.0, value=float(t["session_price"]),
                        step=5.0, format="%.2f",
                    )
                    ac = st.checkbox("الحساب مفعّل", value=t.get("active", True))
                    sv = st.form_submit_button("حفظ", type="primary", use_container_width=True)
                if sv:
                    t.update({
                        "name": nm.strip(), "national_id": nid.strip(),
                        "phone": ph.strip(), "code": cd.strip(),
                        "qualification": ql.strip(), "grad_year": gy.strip(),
                        "specialty": sp, "session_price": float(pr), "active": ac,
                    })
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
            nm = (nm or "").strip()
            cd = (cd or "").strip()
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
                sel_t = c1.selectbox("المدرس", list(t_opts.keys()))
                s_tid = t_opts[sel_t]

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
        sel_t = c1.selectbox("المدرس", list(t_opts.keys()), key="f_t")
        f_tid = t_opts[sel_t]

    cur = date.today()
    f_year = c2.number_input("السنة", 2020, 2100, cur.year, 1)
    f_month = c3.selectbox("الشهر", list(range(1, 13)), index=cur.month - 1)
    prefix = f"{int(f_year)}-{int(f_month):02d}"

    rows_all = [
        s for s in st.session_state.sessions
        if s["date"].startswith(prefix) and (f_tid is None or s["teacher_id"] == f_tid)
    ]
    rows_all.sort(key=lambda x: x["date"], reverse=True)

    if not rows_all:
        empty_state("لا توجد جلسات في هذه الفترة.")
    else:
        data = []
        for s in rows_all:
            t = teacher_by_id(s["teacher_id"])
            data.append({
                "التاريخ": s["date"],
                "المدرس": t["name"] if t else "—",
                "الصف": s["grade"], "التخصص": s["specialty"],
                "الوصف": s["subject"], "الحصة": s["period"],
                "المدة": f"{s['duration_minutes']} د",
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

        total = len(rows_all)
        due = sum(
            (teacher_by_id(s["teacher_id"])["session_price"]
             if teacher_by_id(s["teacher_id"]) else 0)
            for s in rows_all
        )
        cA, cB = st.columns(2)
        cA.metric("عدد الجلسات", total)
        cB.metric("القيمة", f"{due:,.2f} ج.م")


# ==========================================================
# الحضور والغياب
# ==========================================================
def page_attendance():
    page_head("الحضور والغياب", "تسجيل الحضور اليومي للطلاب")
    students = st.session_state.students
    if not students:
        empty_state("لا يوجد طلاب.")
        return

    c1, c2, c3 = st.columns([1, 1, 2])
    sel_date = c1.date_input("التاريخ", value=date.today())
    gr = c2.selectbox("الصف", ["الكل"] + GRADES, key="att_gr")
    dstr = sel_date.isoformat()
    filtered = students if gr == "الكل" else [s for s in students if s.get("grade") == gr]

    section("تسجيل الحضور")
    mark_all = st.radio(
        "إجراء سريع", ["بدون", "تعليم الكل حاضر", "تعليم الكل غائب"],
        horizontal=True, label_visibility="collapsed",
    )

    default_status = "حاضر"
    df = pd.DataFrame([{
        "الكود": s["code"], "الطالب": s["name"],
        "الصف": s.get("grade", "-"),
        "الحالة": s["attendance"].get(dstr, default_status),
    } for s in filtered])

    edited = st.data_editor(
        df, key=f"att_{dstr}_{gr}_{mark_all}",
        hide_index=True, use_container_width=True,
        disabled=["الكود", "الطالب", "الصف"],
        column_config={
            "الحالة": st.column_config.SelectboxColumn(
                "الحالة", options=["حاضر", "غائب", "متأخر"], required=True,
            )
        },
    )

    if st.button("حفظ سجل الحضور", type="primary", use_container_width=True):
        target_status = {"بدون": None, "تعليم الكل حاضر": "حاضر", "تعليم الكل غائب": "غائب"}[mark_all]
        by_code = {s["code"]: s for s in students}
        for _, row in edited.iterrows():
            code = row["الكود"]
            if code in by_code:
                by_code[code]["attendance"][dstr] = target_status or row["الحالة"]
        st.success(f"تم حفظ حضور {dstr}.")
        st.rerun()

    section("ملخص تراكمي")
    rows = []
    for s in students:
        p, a, l = attendance_totals(s)
        rows.append({
            "الكود": s["code"], "الطالب": s["name"],
            "الصف": s.get("grade", "-"),
            "حضور": p, "غياب": a, "تأخير": l,
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ==========================================================
# المستحقات المالية
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
        c = sum(
            1 for s in st.session_state.sessions
            if s["teacher_id"] == t["id"] and s["date"].startswith(prefix)
        )
        due = c * t["session_price"]
        grand += due
        total += c
        rows.append({
            "الكود": t["code"], "المدرس": t["name"], "التخصص": t["specialty"],
            "عدد الحصص": c, "ثمن الحصة": f"{t['session_price']:,.2f}",
            "المستحق": f"{due:,.2f}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    cA, cB = st.columns(2)
    cA.metric("إجمالي الحصص", total)
    cB.metric("إجمالي المستحقات", f"{grand:,.2f} ج.م")

    st.download_button(
        "تحميل الكشف (CSV)",
        pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig"),
        file_name=f"payroll_{prefix}.csv",
        mime="text/csv",
    )


# ==========================================================
# صفحة مستحقات المعلم الشخصية
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

    mine = [
        s for s in st.session_state.sessions
        if s["teacher_id"] == tid and s["date"].startswith(prefix)
    ]

    cA, cB, cC = st.columns(3)
    cA.metric("عدد الحصص", len(mine))
    cB.metric("ثمن الحصة", f"{t['session_price']:,.0f} ج.م")
    cC.metric("المستحق", f"{len(mine) * t['session_price']:,.0f} ج.م")

    section("سجل جلساتي")
    if mine:
        df = pd.DataFrame([{
            "التاريخ": s["date"], "الصف": s["grade"],
            "التخصص": s["specialty"], "الوصف": s["subject"], "الحصة": s["period"],
        } for s in sorted(mine, key=lambda x: x["date"], reverse=True)])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        empty_state("لا توجد جلسات في هذا الشهر.")


# ==========================================================
# إدارة المستخدمين
# ==========================================================
def page_users():
    page_head("إدارة المستخدمين", "الصلاحيات والحسابات")
    users = st.session_state.users

    section("المستخدمون")
    rows = [{
        "الاسم": u["name"], "البريد": u["email"],
        "اسم المستخدم": u.get("username", ""),
        "الدور": ROLES.get(u["role"], u["role"]),
        "الحالة": "مفعّل" if u.get("active", True) else "معطّل",
    } for u in users]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    section("تعديل مستخدم")
    sel = st.selectbox(
        "اختر المستخدم",
        [f"{u['name']} — {u['email']}" for u in users],
        key="mg_u",
    )
    u = users[[f"{x['name']} — {x['email']}" for x in users].index(sel)]

    with st.form("edit_user_form"):
        c1, c2 = st.columns(2)
        nm = c1.text_input("الاسم", value=u["name"])
        em = c2.text_input("البريد", value=u["email"])
        un = c1.text_input("اسم المستخدم", value=u.get("username", ""))
        pw = c2.text_input("كلمة مرور جديدة (اتركها فارغة لعدم التغيير)", value="", type="password")
        rl = c1.selectbox("الدور", list(ROLES.keys()),
                          format_func=lambda x: ROLES[x],
                          index=list(ROLES.keys()).index(u["role"]))
        ac = c2.checkbox("مفعّل", value=u.get("active", True))
        sv = st.form_submit_button("حفظ", type="primary", use_container_width=True)

    if sv:
        conflict = any(
            x["id"] != u["id"] and (
                x["email"].lower() == em.strip().lower()
                or (un.strip() and x.get("username", "").lower() == un.strip().lower())
            )
            for x in users
        )
        if conflict:
            st.error("البريد أو اسم المستخدم مستخدم مسبقاً.")
        else:
            u["name"] = nm.strip()
            u["email"] = em.strip()
            u["username"] = un.strip()
            u["role"] = rl
            u["active"] = ac
            if pw.strip():
                u["password_hash"] = hp(pw.strip())
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
        n_nm = (n_nm or "").strip()
        n_em = (n_em or "").strip()
        n_pw = (n_pw or "").strip()
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
        if choice == "دفتر الجلسات":
            page_sessions()
        elif choice == "الحضور والغياب":
            page_attendance()
        elif choice == "مستحقاتي":
            page_my_payroll()
        return

    if role == "accountant":
        if choice == "لوحة التحكم":
            page_dashboard()
        elif choice == "دفتر الجلسات":
            page_sessions()
        elif choice == "المستحقات المالية":
            page_payroll()
        return

    if role == "viewer":
        if choice == "لوحة التحكم":
            page_dashboard()
        elif choice == "الطلاب":
            page_students()
        elif choice == "المدرسون":
            page_teachers()
        return

    # admin
    routes = {
        "لوحة التحكم": page_dashboard,
        "ملف المدير": page_manager_profile,
        "الطلاب": page_students,
        "المدرسون": page_teachers,
        "دفتر الجلسات": page_sessions,
        "الحضور والغياب": page_attendance,
        "المستحقات المالية": page_payroll,
        "إدارة المستخدمين": page_users,
    }
    routes.get(choice, page_dashboard)()


if __name__ == "__main__":
    main()
