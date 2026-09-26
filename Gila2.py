# -*- coding: utf-8 -*-
"""
==========================================================
نظام إدارة مدرسة "التوكل جيلا" - الإصدار الاحترافي 2.0
مدرسة نانوي صناعي — نظام التدريب المزدوج
تم التطوير بواسطة Python + Streamlit
==========================================================
"""

import hashlib
import re
import random
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

# ==========================================================
# إعداد الصفحة
# ==========================================================
st.set_page_config(
    page_title="التوكل جيلا | نظام الإدارة الاحترافي",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# الثوابت
# ==========================================================
GRADES = ["الأول الصناعي", "الثاني الصناعي", "الثالث الصناعي"]
SPECIALTIES = [
    "ميكانيكا عامة",
    "كهرباء وإلكترونيات",
    "لحام وتشكيل معادن",
    "خراطة",
    "نجارة",
    "تبريد وتكييف",
]
PERIODS = [f"الحصة {i}" for i in range(1, 9)]

ROLES = {
    "admin": "مدير المدرسة",
    "teacher": "معلم",
    "accountant": "محاسب",
    "viewer": "مشاهد",
}


# ==========================================================
# CSS احترافي متكامل
# ==========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&family=Tajawal:wght@400;500;700;800&display=swap');

    :root {
        --primary: #6366f1;
        --primary-2: #8b5cf6;
        --accent: #f59e0b;
        --success: #10b981;
        --danger: #ef4444;
        --info: #06b6d4;
        --dark: #0f172a;
        --surface: #ffffff;
        --bg-soft: #f5f7fb;
        --border: #e5e9f2;
        --text: #1e293b;
        --muted: #64748b;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Cairo','Tajawal', sans-serif !important;
        color: var(--text);
    }

    .stApp {
        background:
            radial-gradient(1200px 600px at 100% -10%, #eef2ff 0%, transparent 60%),
            radial-gradient(1000px 500px at -10% 110%, #ecfeff 0%, transparent 60%),
            #f7f9fc !important;
        direction: rtl;
        text-align: right;
    }

    .stApp, .main, section.main, .block-container {
        direction: rtl;
        text-align: right;
    }

    /* ---------- Sidebar to the right ---------- */
    div[data-testid="stAppViewContainer"] { flex-direction: row-reverse; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
        border-left: none;
        border-right: 1px solid rgba(255,255,255,0.06);
        direction: rtl;
        text-align: right;
    }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; text-align: right !important; }
    section[data-testid="stSidebar"] .stRadio > label { display: none; }
    section[data-testid="stSidebar"] .stRadio label {
        display: flex; flex-direction: row-reverse; justify-content: flex-start;
        padding: 10px 12px; margin: 2px 0; border-radius: 10px;
        transition: background .2s; cursor: pointer; font-weight: 600;
    }
    section[data-testid="stSidebar"] .stRadio label:hover { background: rgba(99,102,241,0.22); }
    section[data-testid="stSidebar"] .stRadio input:checked + div { color: #fff !important; }

    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] button {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background: rgba(99,102,241,0.35) !important;
        border-color: rgba(139,92,246,0.6) !important;
    }

    /* ---------- Inputs ---------- */
    input, textarea, select,
    .stTextInput input, .stNumberInput input,
    .stDateInput input, .stTextArea textarea, .stTimeInput input {
        direction: rtl !important; text-align: right !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="input"], div[data-baseweb="textarea"],
    div[data-baseweb="select"] > div {
        direction: rtl !important; text-align: right !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
        direction: rtl; text-align: right;
    }
    label, p, h1, h2, h3, h4, h5, h6, span, div { text-align: right; }

    /* ---------- Buttons ---------- */
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
        direction: rtl; font-family: 'Cairo', sans-serif !important;
        border-radius: 12px !important; font-weight: 800 !important;
        transition: all .2s ease; border: none;
    }
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #fff !important;
        box-shadow: 0 6px 20px rgba(99,102,241,0.35);
    }
    .stButton > button[kind="primary"]:hover { transform: translateY(-1px); }

    /* ---------- Metrics ---------- */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(15,23,42,0.05);
    }
    [data-testid="stMetricLabel"] { text-align: right !important; color: var(--muted) !important; font-weight: 700; }
    [data-testid="stMetricValue"] { text-align: right !important; color: #1e293b !important; font-weight: 900; }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl; gap: 6px; border-bottom: 2px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Cairo', sans-serif !important; font-weight: 700;
        border-radius: 10px 10px 0 0; padding: 10px 18px;
    }
    .stTabs [aria-selected="true"] { color: var(--primary) !important; }

    /* ---------- Expander ---------- */
    .streamlit-expanderHeader {
        font-weight: 800 !important; border-radius: 12px !important;
        background: #f8faff !important;
    }

    /* ---------- Alerts ---------- */
    .stAlert { border-radius: 14px !important; text-align: right; }

    /* ---------- Dataframe ---------- */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        direction: rtl; border-radius: 12px; overflow: hidden;
    }

    /* ---------- Custom classes ---------- */
    .app-hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        border-radius: 24px; padding: 26px 30px; color: #fff !important;
        box-shadow: 0 12px 40px rgba(99,102,241,0.35);
        margin-bottom: 22px; position: relative; overflow: hidden;
    }
    .app-hero::after {
        content: ''; position: absolute; top: -50%; right: -20%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, transparent 60%);
        border-radius: 50%;
    }
    .app-hero h1 { color: #fff !important; margin: 0 0 6px 0; font-weight: 900; font-size: 30px; }
    .app-hero p  { color: rgba(255,255,255,0.92) !important; margin: 0; font-size: 15px; }

    .login-wrap {
        max-width: 460px; margin: 40px auto; padding: 34px 30px;
        background: #fff; border-radius: 24px;
        box-shadow: 0 24px 60px rgba(99,102,241,0.18);
        border: 1px solid #eef2ff;
        position: relative;
    }
    .login-wrap::before {
        content: ''; position: absolute; inset: 0 0 auto 0; height: 6px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        border-radius: 24px 24px 0 0;
    }
    .login-logo {
        width: 70px; height: 70px; margin: 0 auto 14px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 20px; display: flex; align-items: center; justify-content: center;
        font-size: 34px; color: #fff;
        box-shadow: 0 10px 26px rgba(99,102,241,0.4);
    }
    .login-title {
        text-align: center !important; color: #1e293b;
        font-weight: 900; font-size: 24px; margin-bottom: 4px;
    }
    .login-sub {
        text-align: center !important; color: #64748b;
        font-size: 13px; margin-bottom: 22px;
    }
    .user-card {
        background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px; padding: 12px 14px; margin-bottom: 6px;
    }
    .user-card .name { font-weight: 800; color: #fff !important; font-size: 15px; }
    .user-card .role { font-size: 12px; color: #a5b4fc !important; }
    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 12px; font-weight: 800; margin-inline-start: 6px;
    }
    .badge-success { background: #d1fae5; color: #047857; }
    .badge-danger  { background: #fee2e2; color: #b91c1c; }
    .badge-warn    { background: #fef3c7; color: #92400e; }
    .badge-info    { background: #dbeafe; color: #1e40af; }
    .stat-card {
        background: #fff; border: 1px solid var(--border); border-radius: 18px;
        padding: 18px; box-shadow: 0 4px 16px rgba(15,23,42,0.04);
        display: flex; align-items: center; gap: 14px;
    }
    .stat-card .ico {
        width: 52px; height: 52px; border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px; color: #fff; flex-shrink: 0;
    }
    .stat-card .val { font-size: 24px; font-weight: 900; color: #1e293b; }
    .stat-card .lbl { font-size: 13px; color: #64748b; font-weight: 700; }
    .sec-title {
        display: flex; align-items: center; gap: 10px;
        font-size: 22px; font-weight: 900; color: #1e293b;
        margin: 6px 0 16px 0;
    }
    .sec-title .bar {
        width: 6px; height: 26px; border-radius: 3px;
        background: linear-gradient(180deg, #6366f1, #8b5cf6);
    }
    hr { border: none; border-top: 1px solid var(--border); margin: 18px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# دوال مساعدة
# ==========================================================
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def verify_password(pw: str, hashed: str) -> bool:
    return hash_password(pw) == hashed


def split_phones(text: str):
    if not text:
        return []
    parts = re.split(r"[,،;/\n]+", text)
    return [p.strip() for p in parts if p.strip()]


def attendance_totals(student):
    att = student.get("attendance", {})
    present = sum(1 for v in att.values() if v == "حاضر")
    absent = sum(1 for v in att.values() if v == "غائب")
    late = sum(1 for v in att.values() if v == "متأخر")
    return present, absent, late


def build_attendance(seed: int, days: int = 21):
    rnd = random.Random(seed * 7919 + 13)
    result = {}
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=i)
        if d.weekday() == 4:  # الجمعة
            continue
        result[d.isoformat()] = rnd.choices(
            ["حاضر", "غائب", "متأخر"], weights=[80, 10, 10]
        )[0]
    return result


def generate_demo_sessions(teachers):
    """توليد سجل جلسات تعليمية تجريبية لآخر 30 يوماً."""
    rnd = random.Random(2025)
    sessions = []
    sid = 1
    today = date.today()
    for offset in range(0, 30):
        d = today - timedelta(days=offset)
        if d.weekday() == 4:
            continue
        for t in teachers:
            n_sessions = rnd.randint(2, 5)
            for _ in range(n_sessions):
                sessions.append(
                    {
                        "id": sid,
                        "teacher_id": t["id"],
                        "date": d.isoformat(),
                        "grade": rnd.choice(GRADES),
                        "specialty": rnd.choice(SPECIALTIES),
                        "subject": rnd.choice(
                            [
                                "ورشة عملية",
                                "رسم فني",
                                "تكنولوجيا عامة",
                                "حصة نظري",
                                "تدريب ميداني",
                                "مشروع تخرج",
                            ]
                        ),
                        "period": rnd.choice(PERIODS),
                        "duration_minutes": rnd.choice([45, 60, 90]),
                        "notes": "",
                        "logged_by": "demo",
                        "logged_at": datetime.now().isoformat(timespec="seconds"),
                    }
                )
                sid += 1
    return sessions


def month_key(d: date):
    return f"{d.year}-{d.month:02d}"


def count_teacher_sessions(teacher_id, year, month):
    key = f"{year}-{month:02d}"
    return sum(
        1
        for s in st.session_state.sessions
        if s["teacher_id"] == teacher_id and s["date"].startswith(key)
    )


def weekly_teacher_sessions(teacher_id):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    return sum(
        1
        for s in st.session_state.sessions
        if s["teacher_id"] == teacher_id
        and start.isoformat() <= s["date"] <= today.isoformat()
    )


def teacher_by_id(tid):
    return next((t for t in st.session_state.teachers if t["id"] == tid), None)


def user_by_email_or_username(identifier):
    identifier = (identifier or "").strip().lower()
    for u in st.session_state.users:
        if u["email"].lower() == identifier or u.get("username", "").lower() == identifier:
            return u
    return None


def find_user(user_id):
    return next((u for u in st.session_state.users if u["id"] == user_id), None)


def badge_active(active):
    if active:
        return "<span class='badge badge-success'>مفعّل</span>"
    return "<span class='badge badge-danger'>معطّل</span>"


# ==========================================================
# تهيئة البيانات
# ==========================================================
def init_data():
    if st.session_state.get("_init_v2"):
        return
    st.session_state._init_v2 = True

    # ---- Session state basics ----
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = ""
    st.session_state.display_name = ""
    st.session_state.email = ""
    st.session_state.current_teacher_id = None

    # ---- ملف مدير المدرسة ----
    st.session_state.manager = {
        "name": "أ. عبد الرحمن محمد التوكل",
        "national_id": "28001011234567",
        "phone": "01001234567",
        "code": "MGR-001",
        "qualification": "بكالوريوس هندسة صناعية — قسم ميكانيكا",
        "grad_year": "2004",
        "email": "admin@tawakkol.edu",
    }

    # ---- المستخدمون ----
    default_users = [
        {
            "id": 1,
            "name": "أ. عبد الرحمن محمد التوكل",
            "email": "admin@tawakkol.edu",
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "teacher_id": None,
            "active": True,
            "created_at": date.today().isoformat(),
        }
    ]

    # ---- المدرسون ----
    teachers_seed = [
        {
            "name": "أ. خالد سعيد رمضان",
            "national_id": "28501011234567",
            "phone": "01099887766",
            "code": "TCH-001",
            "qualification": "بكالوريوس تربية صناعية",
            "grad_year": "2008",
            "session_price": 75.0,
            "specialty": "ميكانيكا عامة",
        },
        {
            "name": "أ. منى عبد الحميد علي",
            "national_id": "28702021234567",
            "phone": "01088776655",
            "code": "TCH-002",
            "qualification": "بكالوريوس علوم — رياضيات",
            "grad_year": "2010",
            "session_price": 70.0,
            "specialty": "كهرباء وإلكترونيات",
        },
        {
            "name": "أ. مصطفى كامل الجندي",
            "national_id": "28403031234567",
            "phone": "01077665544",
            "code": "TCH-003",
            "qualification": "دبلوم فني صناعي متقدم",
            "grad_year": "2006",
            "session_price": 85.0,
            "specialty": "لحام وتشكيل معادن",
        },
        {
            "name": "أ. هدى إبراهيم شاكر",
            "national_id": "28904041234567",
            "phone": "01066554433",
            "code": "TCH-004",
            "qualification": "ليسانس آداب — لغة إنجليزية",
            "grad_year": "2012",
            "session_price": 65.0,
            "specialty": "خراطة",
        },
        {
            "name": "أ. طارق ياسر عبد الفتاح",
            "national_id": "28305051234567",
            "phone": "01055443322",
            "code": "TCH-005",
            "qualification": "بكالوريوس هندسة ميكاترونكس",
            "grad_year": "2007",
            "session_price": 90.0,
            "specialty": "تبريد وتكييف",
        },
    ]

    teachers = []
    for idx, t in enumerate(teachers_seed, start=1):
        rec = dict(t)
        rec["id"] = idx
        rec["active"] = True
        teachers.append(rec)
        # حساب دخول لكل مدرس
        default_users.append(
            {
                "id": idx + 1,
                "name": t["name"],
                "email": f"teacher{idx}@tawakkol.edu",
                "username": f"teacher{idx}",
                "password_hash": hash_password(f"teach{idx}123"),
                "role": "teacher",
                "teacher_id": idx,
                "active": True,
                "created_at": date.today().isoformat(),
            }
        )

    st.session_state.teachers = teachers
    st.session_state.users = default_users

    # ---- الطلاب ----
    students_seed = [
        {
            "name": "أحمد محمود السيد",
            "code": "STD-001",
            "national_id": "30101011234567",
            "grade": "الأول الصناعي",
            "specialty": "ميكانيكا عامة",
            "phones": ["01011112222", "01011113333"],
            "parent_phones": ["01211112222", "01211113333"],
            "father_job": "نجار",
        },
        {
            "name": "مريم خالد عبد الله",
            "code": "STD-002",
            "national_id": "30201021234567",
            "grade": "الأول الصناعي",
            "specialty": "كهرباء وإلكترونيات",
            "phones": ["01022223333"],
            "parent_phones": ["01222223333"],
            "father_job": "مدرسة لغة عربية",
        },
        {
            "name": "يوسف إبراهيم حسن",
            "code": "STD-003",
            "national_id": "30101031234567",
            "grade": "الثاني الصناعي",
            "specialty": "لحام وتشكيل معادن",
            "phones": ["01033334444", "01133334444"],
            "parent_phones": ["01233334444"],
            "father_job": "حداد",
        },
        {
            "name": "سلمى أحمد فتحي",
            "code": "STD-004",
            "national_id": "30201041234567",
            "grade": "الثاني الصناعي",
            "specialty": "خراطة",
            "phones": ["01044445555"],
            "parent_phones": ["01244445555", "01544445555"],
            "father_job": "تاجر",
        },
        {
            "name": "عمر سامي رشاد",
            "code": "STD-005",
            "national_id": "30101051234567",
            "grade": "الثالث الصناعي",
            "specialty": "تبريد وتكييف",
            "phones": ["01055556666"],
            "parent_phones": ["01255556666"],
            "father_job": "كهربائي",
        },
        {
            "name": "نور الهدى مصطفى",
            "code": "STD-006",
            "national_id": "30201061234567",
            "grade": "الأول الصناعي",
            "specialty": "ميكانيكا عامة",
            "phones": ["01066667777"],
            "parent_phones": ["01266667777"],
            "father_job": "محاسب",
        },
        {
            "name": "محمد عادل شعبان",
            "code": "STD-007",
            "national_id": "30101071234567",
            "grade": "الثاني الصناعي",
            "specialty": "كهرباء وإلكترونيات",
            "phones": ["01077778888"],
            "parent_phones": ["01277778888"],
            "father_job": "سباك",
        },
        {
            "name": "حبيبة وليد أنور",
            "code": "STD-008",
            "national_id": "30201081234567",
            "grade": "الثالث الصناعي",
            "specialty": "لحام وتشكيل معادن",
            "phones": ["01088889999"],
            "parent_phones": ["01288889999"],
            "father_job": "صيدلي",
        },
    ]

    students = []
    for idx, s in enumerate(students_seed, start=1):
        rec = dict(s)
        rec["id"] = idx
        rec["attendance"] = build_attendance(idx)
        if idx % 3 == 0:
            rec["penalties"] = [
                {
                    "date": (date.today() - timedelta(days=3)).isoformat(),
                    "reason": "التأخر عن الطابور الصباحي",
                }
            ]
        else:
            rec["penalties"] = []
        rec["notes"] = (
            "طالب منتظم ومتفاعل في الحصص العملية."
            if idx % 2 == 1
            else "يحتاج متابعة إضافية في الجزء العملي بالورشة."
        )
        students.append(rec)
    st.session_state.students = students

    # ---- الجلسات ----
    st.session_state.sessions = generate_demo_sessions(teachers)


# ==========================================================
# شاشة تسجيل الدخول
# ==========================================================
def login_page():
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown(
            """
            <div class='login-wrap'>
                <div class='login-logo'>🎓</div>
                <div class='login-title'>مدرسة التوكل جيلا</div>
                <div class='login-sub'>نظام الإدارة الاحترافي — تدريب مزدوج صناعي</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            identifier = st.text_input(
                "📧 البريد الإلكتروني أو اسم المستخدم",
                placeholder="admin@tawakkol.edu",
            )
            password = st.text_input(
                "🔑 كلمة المرور", type="password", placeholder="••••••••"
            )
            submitted = st.form_submit_button(
                "🚀 تسجيل الدخول", use_container_width=True, type="primary"
            )

        if submitted:
            identifier = (identifier or "").strip()
            password = (password or "").strip()
            if not identifier or not password:
                st.error("⚠️ من فضلك أدخل بيانات الدخول كاملة.")
            else:
                user = user_by_email_or_username(identifier)
                if user is None or not verify_password(password, user["password_hash"]):
                    st.error("❌ بيانات الدخول غير صحيحة.")
                elif not user.get("active", True):
                    st.error("⛔ هذا الحساب معطّل. تواصل مع مدير النظام.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.role = user["role"]
                    st.session_state.display_name = user["name"]
                    st.session_state.email = user["email"]
                    st.session_state.current_teacher_id = user.get("teacher_id")
                    st.rerun()

        with st.expander("ℹ️ بيانات الدخول الافتراضية"):
            st.markdown(
                """
                - **المدير:** البريد `admin@tawakkol.edu` — اسم المستخدم `admin` — كلمة المرور `admin123`
                - **معلم 1:** `teacher1@tawakkol.edu` — `teacher1` — `teach1123`
                - **معلم 2:** `teacher2@tawakkol.edu` — `teacher2` — `teach2123`
                """
            )


# ==========================================================
# مكونات الواجهة
# ==========================================================
def hero(title, subtitle, icon="🎓"):
    st.markdown(
        f"""
        <div class='app-hero'>
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text, icon="📌"):
    st.markdown(
        f"<div class='sec-title'><span class='bar'></span>{icon} {text}</div>",
        unsafe_allow_html=True,
    )


def stat_card(icon, label, value, color="#6366f1"):
    st.markdown(
        f"""
        <div class='stat-card'>
            <div class='ico' style='background:{color}'>{icon}</div>
            <div>
                <div class='val'>{value}</div>
                <div class='lbl'>{label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# صفحة: لوحة التحكم
# ==========================================================
def page_dashboard():
    hero(
        "لوحة التحكم",
        "نظرة شاملة على أداء المدرسة والطلاب والمدرسين والمستحقات المالية",
        "🏠",
    )

    students = st.session_state.students
    teachers = st.session_state.teachers
    sessions = st.session_state.sessions
    today_str = date.today().isoformat()
    cur_month = month_key(date.today())

    present_today = sum(1 for s in students if s["attendance"].get(today_str) == "حاضر")
    absent_today = sum(1 for s in students if s["attendance"].get(today_str) == "غائب")
    late_today = sum(1 for s in students if s["attendance"].get(today_str) == "متأخر")

    month_sessions = [s for s in sessions if s["date"].startswith(cur_month)]
    total_month_due = 0.0
    for t in teachers:
        cnt = sum(1 for s in month_sessions if s["teacher_id"] == t["id"])
        total_month_due += cnt * t["session_price"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("👨‍🎓", "إجمالي الطلاب", len(students), "#6366f1")
    with c2:
        stat_card("👨‍🏫", "إجمالي المدرسين", len(teachers), "#8b5cf6")
    with c3:
        stat_card("📚", "جلسات هذا الشهر", len(month_sessions), "#06b6d4")
    with c4:
        stat_card("💰", "مستحقات الشهر (ج.م)", f"{total_month_due:,.0f}", "#10b981")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        stat_card("✅", "حضور اليوم", present_today, "#10b981")
    with c6:
        stat_card("❌", "غياب اليوم", absent_today, "#ef4444")
    with c7:
        stat_card("⏰", "تأخير اليوم", late_today, "#f59e0b")
    with c8:
        active_users = sum(1 for u in st.session_state.users if u.get("active", True))
        stat_card("👥", "حسابات نشطة", active_users, "#06b6d4")

    st.markdown("<hr>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        section_title("أكثر المدرسين حصصاً هذا الشهر", "🏆")
        counts = []
        for t in teachers:
            cnt = sum(1 for s in month_sessions if s["teacher_id"] == t["id"])
            counts.append({"المدرس": t["name"], "عدد الحصص": cnt})
        df = pd.DataFrame(counts).sort_values("عدد الحصص", ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with col_r:
        section_title("ملخص حضور الطلاب", "📊")
        rows = []
        for s in students:
            p, a, l = attendance_totals(s)
            rows.append(
                {
                    "الطالب": s["name"],
                    "حضور": p,
                    "غياب": a,
                    "تأخير": l,
                    "جزاءات": len(s["penalties"]),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ==========================================================
# صفحة: ملف المدير
# ==========================================================
def page_manager_profile():
    hero("ملف مدير المدرسة", "بياناتك الشخصية والمهنية داخل النظام", "👤")
    m = st.session_state.manager

    with st.form("manager_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("الاسم بالكامل", value=m["name"])
        national_id = c2.text_input("الرقم القومي", value=m["national_id"])
        phone = c1.text_input("رقم التليفون", value=m["phone"])
        code = c2.text_input("الكود", value=m["code"])
        qualification = c1.text_input("المؤهل الدراسي", value=m["qualification"])
        grad_year = c2.text_input("سنة الحصول على المؤهل", value=m["grad_year"])
        email = c1.text_input("البريد الإلكتروني الشخصي", value=m.get("email", ""))
        save = st.form_submit_button("💾 حفظ البيانات", type="primary", use_container_width=True)

    if save:
        st.session_state.manager = {
            "name": name.strip(),
            "national_id": national_id.strip(),
            "phone": phone.strip(),
            "code": code.strip(),
            "qualification": qualification.strip(),
            "grad_year": grad_year.strip(),
            "email": email.strip(),
        }
        # تحديث بيانات حساب المستخدم أيضاً
        for u in st.session_state.users:
            if u["id"] == st.session_state.user_id:
                u["name"] = name.strip()
                if email.strip():
                    u["email"] = email.strip()
        st.success("✅ تم حفظ بيانات المدير بنجاح.")

    section_title("بطاقة المدير الحالية", "📇")
    mm = st.session_state.manager
    c1, c2, c3 = st.columns(3)
    c1.metric("الاسم", mm["name"])
    c2.metric("الرقم القومي", mm["national_id"])
    c3.metric("الكود", mm["code"])
    c1.metric("التليفون", mm["phone"])
    c2.metric("المؤهل", mm["qualification"])
    c3.metric("سنة التخرج", mm["grad_year"])


# ==========================================================
# صفحة: الطلاب
# ==========================================================
def page_students():
    hero("إدارة الطلاب", "بيانات الطلاب، الملفات الشخصية، الحضور والجزاءات", "🎓")

    tabs = st.tabs(["📋 القائمة", "➕ إضافة طالب", "🗂️ الملف الشخصي"])

    # --- القائمة ---
    with tabs[0]:
        students = st.session_state.students
        if not students:
            st.warning("لا يوجد طلاب مسجلون.")
        else:
            rows = []
            for s in students:
                p, a, l = attendance_totals(s)
                rows.append(
                    {
                        "الكود": s["code"],
                        "الاسم": s["name"],
                        "الصف": s.get("grade", "-"),
                        "التخصص": s.get("specialty", "-"),
                        "تليفون الطالب": " / ".join(s["phones"]) or "-",
                        "ولي الأمر": " / ".join(s["parent_phones"]) or "-",
                        "حضور": p,
                        "غياب": a,
                        "تأخير": l,
                        "جزاءات": len(s["penalties"]),
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            section_title("حذف طالب", "🗑️")
            del_opts = {f"{s['name']} — {s['code']}": s["id"] for s in students}
            sel = st.selectbox("اختر الطالب", list(del_opts.keys()), key="del_student")
            if st.button("🗑️ حذف نهائي", key="del_student_btn"):
                sid = del_opts[sel]
                st.session_state.students = [
                    x for x in st.session_state.students if x["id"] != sid
                ]
                st.success("تم الحذف.")
                st.rerun()

    # --- إضافة ---
    with tabs[1]:
        with st.form("add_student", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم الطالب")
            code = c2.text_input("الكود")
            national_id = c1.text_input("الرقم القومي")
            father_job = c2.text_input("مهنة الأب")
            grade = c1.selectbox("الصف", GRADES)
            specialty = c2.selectbox("التخصص", SPECIALTIES)
            phones = c1.text_input("أرقام تليفون الطالب (افصل بفاصلة)")
            parent_phones = c2.text_input("أرقام تليفون ولي الأمر (افصل بفاصلة)")
            notes = st.text_area("ملاحظات")
            add_btn = st.form_submit_button("➕ إضافة الطالب", type="primary", use_container_width=True)

        if add_btn:
            name = (name or "").strip()
            code = (code or "").strip()
            if not name or not code:
                st.error("⚠️ اسم الطالب والكود مطلوبان.")
            elif any(s["code"] == code for s in st.session_state.students):
                st.error("⚠️ هذا الكود مستخدم بالفعل.")
            else:
                new_id = max([s["id"] for s in st.session_state.students], default=0) + 1
                st.session_state.students.append(
                    {
                        "id": new_id,
                        "name": name,
                        "code": code,
                        "national_id": (national_id or "").strip(),
                        "grade": grade,
                        "specialty": specialty,
                        "phones": split_phones(phones),
                        "parent_phones": split_phones(parent_phones),
                        "father_job": (father_job or "").strip(),
                        "attendance": {},
                        "penalties": [],
                        "notes": notes.strip(),
                    }
                )
                st.success(f"✅ تمت إضافة الطالب {name}.")

    # --- الملف الشخصي ---
    with tabs[2]:
        students = st.session_state.students
        if not students:
            st.info("لا يوجد طلاب.")
            return
        opts = {f"{s['name']} — {s['code']}": s["id"] for s in students}
        sel = st.selectbox("اختر الطالب", list(opts.keys()), key="profile_student")
        sid = opts[sel]
        student = next((s for s in students if s["id"] == sid), None)
        if student is None:
            return

        p, a, l = attendance_totals(student)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("✅ الحضور", p)
        c2.metric("❌ الغياب", a)
        c3.metric("⏰ التأخير", l)
        c4.metric("⚖️ الجزاءات", len(student["penalties"]))

        section_title("البيانات الشخصية", "📇")
        colA, colB = st.columns(2)
        colA.markdown(f"**الاسم:** {student['name']}")
        colB.markdown(f"**الكود:** {student['code']}")
        colA.markdown(f"**الرقم القومي:** {student['national_id'] or '-'}")
        colB.markdown(f"**مهنة الأب:** {student['father_job'] or '-'}")
        colA.markdown(f"**الصف:** {student.get('grade', '-')}")
        colB.markdown(f"**التخصص:** {student.get('specialty', '-')}")
        colA.markdown(
            f"**تليفون الطالب:** {' / '.join(student['phones']) or '-'}"
        )
        colB.markdown(
            f"**تليفون ولي الأمر:** {' / '.join(student['parent_phones']) or '-'}"
        )
        st.markdown(f"**الملاحظات:** {student['notes'] or '-'}")

        section_title("سجل الحضور", "🗓️")
        if student["attendance"]:
            df = pd.DataFrame(
                [
                    {"التاريخ": k, "الحالة": v}
                    for k, v in sorted(student["attendance"].items(), reverse=True)
                ]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("لا يوجد سجل.")

        section_title("الجزاءات", "⚖️")
        if student["penalties"]:
            df = pd.DataFrame(
                [{"التاريخ": x["date"], "السبب": x["reason"]} for x in student["penalties"]]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
        with st.form("add_penalty", clear_on_submit=True):
            c1, c2 = st.columns([3, 1])
            reason = c1.text_input("سبب الجزاء")
            pdate = c2.date_input("التاريخ", value=date.today())
            pen_btn = st.form_submit_button("➕ إضافة جزاء", use_container_width=True)
        if pen_btn and reason.strip():
            student["penalties"].append(
                {"date": pdate.isoformat(), "reason": reason.strip()}
            )
            st.success("✅ تم تسجيل الجزاء.")
            st.rerun()

        section_title("تعديل الملاحظات", "📝")
        new_notes = st.text_area("ملاحظات", value=student.get("notes", ""), key=f"notes_{sid}")
        if st.button("💾 حفظ الملاحظات", key=f"save_notes_{sid}"):
            student["notes"] = new_notes.strip()
            st.success("تم الحفظ.")


# ==========================================================
# صفحة: المدرسين
# ==========================================================
def page_teachers():
    hero("إدارة المدرسين", "بيانات المدرسين والحصص والمستحقات المالية", "👨‍🏫")
    tabs = st.tabs(["📋 القائمة", "➕ إضافة مدرس"])

    with tabs[0]:
        teachers = st.session_state.teachers
        if not teachers:
            st.warning("لا يوجد مدرسون.")
        else:
            rows = []
            for t in teachers:
                month_cnt = count_teacher_sessions(t["id"], date.today().year, date.today().month)
                week_cnt = weekly_teacher_sessions(t["id"])
                due = month_cnt * t["session_price"]
                rows.append(
                    {
                        "الكود": t["code"],
                        "الاسم": t["name"],
                        "التخصص": t.get("specialty", "-"),
                        "التليفون": t["phone"],
                        "حصص/أسبوع": week_cnt,
                        "حصص/شهر": month_cnt,
                        "ثمن الحصة": f"{t['session_price']:,.0f}",
                        "المستحق الشهري": f"{due:,.0f}",
                        "الحالة": "مفعّل ✅" if t.get("active", True) else "معطّل ⛔",
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            section_title("تعديل بيانات مدرس", "✏️")
            edit_opts = {f"{t['name']} — {t['code']}": t["id"] for t in teachers}
            sel = st.selectbox("اختر المدرس", list(edit_opts.keys()), key="edit_teacher")
            tid = edit_opts[sel]
            teacher = teacher_by_id(tid)
            if teacher:
                with st.form("edit_teacher_form"):
                    c1, c2 = st.columns(2)
                    name = c1.text_input("الاسم", value=teacher["name"])
                    national_id = c2.text_input("الرقم القومي", value=teacher["national_id"])
                    phone = c1.text_input("التليفون", value=teacher["phone"])
                    code = c2.text_input("الكود", value=teacher["code"])
                    qualification = c1.text_input("المؤهل", value=teacher["qualification"])
                    grad_year = c2.text_input("سنة التخرج", value=teacher["grad_year"])
                    specialty = c1.selectbox(
                        "التخصص",
                        SPECIALTIES,
                        index=SPECIALTIES.index(teacher.get("specialty", SPECIALTIES[0]))
                        if teacher.get("specialty") in SPECIALTIES else 0,
                    )
                    price = c2.number_input(
                        "ثمن الحصة",
                        min_value=0.0,
                        max_value=100000.0,
                        value=float(teacher["session_price"]),
                        step=5.0,
                    )
                    save = st.form_submit_button(
                        "💾 حفظ التعديلات", type="primary", use_container_width=True
                    )
                if save:
                    teacher.update(
                        {
                            "name": name.strip(),
                            "national_id": national_id.strip(),
                            "phone": phone.strip(),
                            "code": code.strip(),
                            "qualification": qualification.strip(),
                            "grad_year": grad_year.strip(),
                            "specialty": specialty,
                            "session_price": float(price),
                        }
                    )
                    st.success("✅ تم الحفظ.")

    with tabs[1]:
        with st.form("add_teacher", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("الاسم")
            national_id = c2.text_input("الرقم القومي")
            phone = c1.text_input("التليفون")
            code = c2.text_input("الكود")
            qualification = c1.text_input("المؤهل")
            grad_year = c2.text_input("سنة التخرج")
            specialty = c1.selectbox("التخصص", SPECIALTIES)
            price = c2.number_input("ثمن الحصة", min_value=0.0, value=75.0, step=5.0)
            add = st.form_submit_button("➕ إضافة المدرس", type="primary", use_container_width=True)

        if add:
            name = (name or "").strip()
            code = (code or "").strip()
            if not name or not code:
                st.error("⚠️ الاسم والكود مطلوبان.")
            elif any(t["code"] == code for t in st.session_state.teachers):
                st.error("⚠️ الكود مستخدم بالفعل.")
            else:
                new_id = max([t["id"] for t in st.session_state.teachers], default=0) + 1
                st.session_state.teachers.append(
                    {
                        "id": new_id,
                        "name": name,
                        "national_id": (national_id or "").strip(),
                        "phone": (phone or "").strip(),
                        "code": code,
                        "qualification": (qualification or "").strip(),
                        "grad_year": (grad_year or "").strip(),
                        "specialty": specialty,
                        "session_price": float(price),
                        "active": True,
                    }
                )
                st.success(f"✅ تمت إضافة {name}.")


# ==========================================================
# صفحة: دفتر الجلسات (حصص المدرسين)
# ==========================================================
def page_sessions():
    role = st.session_state.role
    is_teacher = role == "teacher"
    my_tid = st.session_state.current_teacher_id

    hero(
        "دفتر الجلسات التعليمية",
        "تسجيل الحصص التي يقوم المدرس بتدريسها فعلياً — أساس حساب المستحقات الشهرية",
        "📚",
    )

    # -------- نموذج تسجيل جلسة جديدة --------
    with st.expander("➕ تسجيل جلسة جديدة", expanded=True):
        with st.form("add_session", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            if is_teacher:
                teacher_opts = {teacher_by_id(my_tid)["name"]: my_tid}
                s_teacher_label = c1.selectbox(
                    "المدرس", list(teacher_opts.keys()), disabled=True
                )
                s_teacher_id = my_tid
            else:
                teacher_opts = {t["name"]: t["id"] for t in st.session_state.teachers}
                s_teacher_label = c1.selectbox("المدرس", list(teacher_opts.keys()))
                s_teacher_id = teacher_opts[s_teacher_label]

            s_date = c2.date_input("التاريخ", value=date.today())
            s_grade = c3.selectbox("الصف", GRADES)
            s_spec = c1.selectbox("التخصص", SPECIALTIES)
            s_subject = c2.text_input("المادة / الوصف", value="ورشة عملية")
            s_period = c3.selectbox("الحصة", PERIODS)
            s_dur = c1.number_input("المدة (دقيقة)", min_value=15, max_value=300, value=90, step=15)
            s_notes = c2.text_input("ملاحظات", value="")
            submit = st.form_submit_button("💾 حفظ الجلسة", type="primary", use_container_width=True)

        if submit:
            new_id = max([s["id"] for s in st.session_state.sessions], default=0) + 1
            st.session_state.sessions.append(
                {
                    "id": new_id,
                    "teacher_id": s_teacher_id,
                    "date": s_date.isoformat(),
                    "grade": s_grade,
                    "specialty": s_spec,
                    "subject": s_subject.strip() or "—",
                    "period": s_period,
                    "duration_minutes": int(s_dur),
                    "notes": s_notes.strip(),
                    "logged_by": st.session_state.display_name,
                    "logged_at": datetime.now().isoformat(timespec="seconds"),
                }
            )
            st.success("✅ تم تسجيل الجلسة بنجاح، وسيتم احتسابها في المستحقات.")
            st.rerun()

    # -------- عرض الجلسات --------
    section_title("سجل الجلسات", "🗂️")

    c1, c2, c3 = st.columns(3)
    if is_teacher:
        teachers_filter = {teacher_by_id(my_tid)["name"]: my_tid}
        sel_teacher = c1.selectbox("المدرس", list(teachers_filter.keys()), disabled=True)
        f_tid = my_tid
    else:
        teachers_filter = {"الكل": None}
        for t in st.session_state.teachers:
            teachers_filter[t["name"]] = t["id"]
        sel_teacher = c1.selectbox("المدرس", list(teachers_filter.keys()))
        f_tid = teachers_filter[sel_teacher]

    cur = date.today()
    f_year = c2.number_input("السنة", min_value=2020, max_value=2100, value=cur.year, step=1)
    f_month = c2.selectbox(
        "الشهر", list(range(1, 13)), index=cur.month - 1
    )
    f_month = f_month if isinstance(f_month, int) else cur.month

    month_prefix = f"{int(f_year)}-{int(f_month):02d}"

    filtered = [
        s for s in st.session_state.sessions
        if s["date"].startswith(month_prefix)
        and (f_tid is None or s["teacher_id"] == f_tid)
    ]
    filtered.sort(key=lambda x: x["date"], reverse=True)

    if not filtered:
        st.info("لا توجد جلسات في هذا الشهر.")
    else:
        rows = []
        for s in filtered:
            t = teacher_by_id(s["teacher_id"])
            rows.append(
                {
                    "التاريخ": s["date"],
                    "المدرس": t["name"] if t else "—",
                    "الصف": s["grade"],
                    "التخصص": s["specialty"],
                    "الوصف": s["subject"],
                    "الحصة": s["period"],
                    "المدة": f"{s['duration_minutes']} د",
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # ملخص
        total = len(filtered)
        total_due = sum(
            (teacher_by_id(s["teacher_id"])["session_price"] if teacher_by_id(s["teacher_id"]) else 0)
            for s in filtered
        )
        cA, cB = st.columns(2)
        cA.metric("إجمالي الجلسات في الشهر", total)
        cB.metric("إجمالي قيمة هذه الجلسات", f"{total_due:,.2f} ج.م")

        # حذف
        section_title("حذف جلسة مسجلة", "🗑️")
        del_opts = {
            f"#{s['id']} — {s['date']} — {teacher_by_id(s['teacher_id'])['name'] if teacher_by_id(s['teacher_id']) else ''}": s["id"]
            for s in filtered
        }
        sel_del = st.selectbox("اختر الجلسة", list(del_opts.keys()), key="del_session")
        if st.button("🗑️ حذف الجلسة", key="del_session_btn"):
            sid = del_opts[sel_del]
            st.session_state.sessions = [
                x for x in st.session_state.sessions if x["id"] != sid
            ]
            st.success("تم الحذف.")
            st.rerun()


# ==========================================================
# صفحة: الحضور والغياب اليومي للطلاب
# ==========================================================
def page_attendance():
    hero("الحضور والغياب اليومي", "تسجيل حضور الطلاب ومتابعة السجلات التراكمية", "✅")

    students = st.session_state.students
    if not students:
        st.warning("لا يوجد طلاب.")
        return

    c1, c2 = st.columns([1, 2])
    sel_date = c1.date_input("📅 التاريخ", value=date.today())
    c2.markdown(
        f"<div class='stat-card' style='margin-top:12px'>"
        f"<div class='ico' style='background:#6366f1'>📅</div>"
        f"<div><div class='val'>{sel_date.isoformat()}</div>"
        f"<div class='lbl'>تاريخ التسجيل</div></div></div>",
        unsafe_allow_html=True,
    )

    dstr = sel_date.isoformat()

    # فلتر حسب الصف
    gr = st.selectbox("الصف", ["الكل"] + GRADES, key="att_grade")
    filtered = students if gr == "الكل" else [s for s in students if s.get("grade") == gr]

    df = pd.DataFrame(
        [
            {
                "الكود": s["code"],
                "الطالب": s["name"],
                "الصف": s.get("grade", "-"),
                "الحالة": s["attendance"].get(dstr, "حاضر"),
            }
            for s in filtered
        ]
    )

    edited = st.data_editor(
        df,
        key=f"att_editor_{dstr}_{gr}",
        hide_index=True,
        use_container_width=True,
        disabled=["الكود", "الطالب", "الصف"],
        column_config={
            "الحالة": st.column_config.SelectboxColumn(
                "الحالة",
                help="اختر حالة الطالب",
                options=["حاضر", "غائب", "متأخر"],
                required=True,
            )
        },
    )

    if st.button("💾 حفظ الحضور", type="primary", use_container_width=True):
        by_code = {s["code"]: s for s in students}
        for _, row in edited.iterrows():
            code = row["الكود"]
            if code in by_code:
                by_code[code]["attendance"][dstr] = row["الحالة"]
        st.success(f"✅ تم حفظ سجل حضور يوم {dstr}.")
        st.rerun()

    section_title("ملخص تراكمي", "📊")
    rows = []
    for s in students:
        p, a, l = attendance_totals(s)
        rows.append(
            {
                "الكود": s["code"],
                "الطالب": s["name"],
                "الصف": s.get("grade", "-"),
                "حضور": p,
                "غياب": a,
                "تأخير": l,
                "جزاءات": len(s["penalties"]),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ==========================================================
# صفحة: المستحقات المالية
# ==========================================================
def page_payroll():
    hero(
        "المستحقات المالية للمدرسين",
        "تُحسب تلقائياً من الجلسات المسجلة فعلياً × ثمن الحصة",
        "💰",
    )

    teachers = st.session_state.teachers
    if not teachers:
        st.warning("لا يوجد مدرسون.")
        return

    c1, c2 = st.columns(2)
    cur = date.today()
    year = c1.number_input("السنة", min_value=2020, max_value=2100, value=cur.year, step=1)
    month = c2.selectbox("الشهر", list(range(1, 13)), index=cur.month - 1)
    month_prefix = f"{int(year)}-{int(month):02d}"

    rows = []
    grand_total = 0.0
    total_sessions = 0

    for t in teachers:
        cnt = sum(
            1
            for s in st.session_state.sessions
            if s["teacher_id"] == t["id"] and s["date"].startswith(month_prefix)
        )
        due = cnt * t["session_price"]
        grand_total += due
        total_sessions += cnt
        rows.append(
            {
                "الكود": t["code"],
                "المدرس": t["name"],
                "التخصص": t.get("specialty", "-"),
                "عدد الحصص": cnt,
                "ثمن الحصة": f"{t['session_price']:,.2f}",
                "المستحق": f"{due:,.2f}",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    cA, cB = st.columns(2)
    cA.metric("إجمالي الحصص في الشهر", total_sessions)
    cB.metric("إجمالي المستحقات", f"{grand_total:,.2f} ج.م")

    # تصدير
    df_export = pd.DataFrame(rows)
    st.download_button(
        "⬇️ تحميل كشف المستحقات (CSV)",
        df_export.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"payroll_{month_prefix}.csv",
        mime="text/csv",
    )

    st.caption("المعادلة: عدد الحصص المسجّلة فعلياً × ثمن الحصة الواحدة.")


# ==========================================================
# صفحة: إدارة المستخدمين
# ==========================================================
def page_users():
    hero("إدارة المستخدمين والصلاحيات", "إضافة مستخدمين جدد وتحديد الأدوار وتعطيل الحسابات", "🔐")

    section_title("المستخدمون الحاليون", "👥")
    users = st.session_state.users
    rows = []
    for u in users:
        rows.append(
            {
                "الاسم": u["name"],
                "البريد الإلكتروني": u["email"],
                "اسم المستخدم": u.get("username", ""),
                "الدور": ROLES.get(u["role"], u["role"]),
                "الحالة": "مفعّل" if u.get("active", True) else "معطّل",
                "تاريخ الإنشاء": u.get("created_at", "-"),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    section_title("إدارة حساب مستخدم", "⚙️")
    if users:
        sel_user = st.selectbox(
            "اختر المستخدم",
            [f"{u['name']} — {u['email']}" for u in users],
            key="mgmt_user",
        )
        idx = [f"{u['name']} — {u['email']}" for u in users].index(sel_user)
        user = users[idx]

        with st.form("edit_user_form"):
            c1, c2 = st.columns(2)
            new_name = c1.text_input("الاسم", value=user["name"])
            new_email = c2.text_input("البريد", value=user["email"])
            new_user = c1.text_input("اسم المستخدم", value=user.get("username", ""))
            new_pass = c2.text_input("كلمة مرور جديدة (اتركها فارغة لعدم التغيير)", value="")
            new_role = c1.selectbox(
                "الدور",
                list(ROLES.keys()),
                format_func=lambda x: ROLES[x],
                index=list(ROLES.keys()).index(user["role"]),
            )
            new_active = c2.checkbox("الحساب مفعّل", value=user.get("active", True))
            save = st.form_submit_button("💾 حفظ التغييرات", type="primary", use_container_width=True)

        if save:
            # التحقق من عدم تكرار البريد/اسم المستخدم
            conflict = any(
                other["id"] != user["id"]
                and (
                    other["email"].lower() == new_email.strip().lower()
                    or (new_user.strip() and other.get("username", "").lower() == new_user.strip().lower())
                )
                for other in users
            )
            if conflict:
                st.error("⚠️ البريد أو اسم المستخدم مستخدم بالفعل.")
            else:
                user["name"] = new_name.strip()
                user["email"] = new_email.strip()
                user["username"] = new_user.strip()
                user["role"] = new_role
                user["active"] = new_active
                if new_pass.strip():
                    user["password_hash"] = hash_password(new_pass.strip())
                st.success("✅ تم التحديث.")
                st.rerun()

        if user["id"] != st.session_state.user_id:
            if st.button("🗑️ حذف المستخدم", key="del_user"):
                st.session_state.users = [u for u in users if u["id"] != user["id"]]
                st.success("تم الحذف.")
                st.rerun()
        else:
            st.caption("لا يمكنك حذف حسابك الحالي أثناء تسجيل الدخول.")

    section_title("إضافة مستخدم جديد", "➕")
    with st.form("add_user", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n_name = c1.text_input("الاسم")
        n_email = c2.text_input("البريد الإلكتروني")
        n_user = c1.text_input("اسم المستخدم")
        n_pass = c2.text_input("كلمة المرور", type="password")
        n_role = c1.selectbox(
            "الدور", list(ROLES.keys()), format_func=lambda x: ROLES[x]
        )
        link_teacher = None
        if n_role == "teacher":
            teacher_opts = {"— بدون ربط —": None}
            for t in st.session_state.teachers:
                teacher_opts[t["name"]] = t["id"]
            sel_t = c2.selectbox("ربط بمدرس", list(teacher_opts.keys()))
            link_teacher = teacher_opts[sel_t]
        add = st.form_submit_button("➕ إضافة المستخدم", type="primary", use_container_width=True)

    if add:
        n_name = (n_name or "").strip()
        n_email = (n_email or "").strip()
        n_user = (n_user or "").strip()
        n_pass = (n_pass or "").strip()
        if not n_name or not n_email or not n_pass:
            st.error("⚠️ الاسم والبريد وكلمة المرور مطلوبة.")
        elif any(u["email"].lower() == n_email.lower() for u in st.session_state.users):
            st.error("⚠️ البريد مستخدم بالفعل.")
        else:
            new_id = max([u["id"] for u in st.session_state.users], default=0) + 1
            st.session_state.users.append(
                {
                    "id": new_id,
                    "name": n_name,
                    "email": n_email,
                    "username": n_user or n_email.split("@")[0],
                    "password_hash": hash_password(n_pass),
                    "role": n_role,
                    "teacher_id": link_teacher,
                    "active": True,
                    "created_at": date.today().isoformat(),
                }
            )
            st.success(f"✅ تم إضافة المستخدم {n_name}.")


# ==========================================================
# Sidebar
# ==========================================================
def render_sidebar():
    role = st.session_state.role

    with st.sidebar:
        st.markdown(
            """
            <div style='text-align:right; padding:6px 4px 0 4px;'>
                <div style='font-size:24px; font-weight:900; color:#fff;'>🎓 التوكل جيلا</div>
                <div style='color:#a5b4fc; font-size:12px;'>مدرسة نانوي صناعي — تدريب مزدوج</div>
            </div>
            <hr style='border-color: rgba(255,255,255,0.1); margin: 12px 0;'>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class='user-card'>
                <div class='name'>👤 {st.session_state.display_name}</div>
                <div class='role'>🔑 {ROLES.get(role, role)}</div>
                <div class='role' style='font-size:11px; margin-top:4px;'>📧 {st.session_state.email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # القوائم حسب الصلاحية
        if role == "admin":
            pages = [
                "🏠 لوحة التحكم",
                "👤 ملف المدير",
                "🎓 الطلاب",
                "👨‍🏫 المدرسين",
                "📚 دفتر الجلسات",
                "✅ الحضور والغياب",
                "💰 المستحقات المالية",
                "🔐 إدارة المستخدمين",
            ]
        elif role == "teacher":
            pages = [
                "📚 دفتر الجلسات",
                "✅ الحضور والغياب",
                "💰 مستحقاتي",
            ]
        elif role == "accountant":
            pages = [
                "🏠 لوحة التحكم",
                "📚 دفتر الجلسات",
                "💰 المستحقات المالية",
            ]
        else:  # viewer
            pages = ["🏠 لوحة التحكم", "🎓 الطلاب", "👨‍🏫 المدرسين"]

        choice = st.radio("القائمة", pages, label_visibility="collapsed")

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            for key in [
                "logged_in", "user_id", "role", "display_name", "email",
                "current_teacher_id",
            ]:
                st.session_state[key] = None if key != "logged_in" else False
            st.session_state.role = ""
            st.session_state.display_name = ""
            st.session_state.email = ""
            st.rerun()

    return choice


# ==========================================================
# الصفحة الخاصة بالمدرس (مستحقاتي)
# ==========================================================
def page_my_payroll():
    tid = st.session_state.current_teacher_id
    t = teacher_by_id(tid)
    if not t:
        st.error("لا يوجد ملف مدرس مرتبط بحسابك.")
        return

    hero("مستحقاتي الشخصية", f"كشف مستحقاتك المالية بناءً على الجلسات المسجلة", "💵")

    cur = date.today()
    c1, c2 = st.columns(2)
    year = c1.number_input("السنة", min_value=2020, max_value=2100, value=cur.year, step=1)
    month = c2.selectbox("الشهر", list(range(1, 13)), index=cur.month - 1)
    prefix = f"{int(year)}-{int(month):02d}"

    my_sessions = [
        s for s in st.session_state.sessions
        if s["teacher_id"] == tid and s["date"].startswith(prefix)
    ]

    cA, cB, cC = st.columns(3)
    cA.metric("عدد الحصص", len(my_sessions))
    cB.metric("ثمن الحصة", f"{t['session_price']:,.0f} ج.م")
    cC.metric("المستحق", f"{len(my_sessions) * t['session_price']:,.0f} ج.م")

    section_title("سجل جلساتي", "📚")
    if my_sessions:
        df = pd.DataFrame(
            [
                {
                    "التاريخ": s["date"],
                    "الصف": s["grade"],
                    "التخصص": s["specialty"],
                    "الوصف": s["subject"],
                    "الحصة": s["period"],
                }
                for s in sorted(my_sessions, key=lambda x: x["date"], reverse=True)
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد جلسات مسجلة في هذا الشهر.")


# ==========================================================
# Main
# ==========================================================
def main():
    init_data()

    if not st.session_state.get("logged_in"):
        login_page()
        return

    choice = render_sidebar()
    role = st.session_state.role

    # توجيه حسب الدور
    if role == "teacher":
        if choice == "📚 دفتر الجلسات":
            page_sessions()
        elif choice == "✅ الحضور والغياب":
            page_attendance()
        elif choice == "💰 مستحقاتي":
            page_my_payroll()
        return

    if role == "accountant":
        if choice == "🏠 لوحة التحكم":
            page_dashboard()
        elif choice == "📚 دفتر الجلسات":
            page_sessions()
        elif choice == "💰 المستحقات المالية":
            page_payroll()
        return

    if role == "viewer":
        if choice == "🏠 لوحة التحكم":
            page_dashboard()
        elif choice == "🎓 الطلاب":
            page_students()
        elif choice == "👨‍🏫 المدرسين":
            page_teachers()
        return

    # admin
    if choice == "🏠 لوحة التحكم":
        page_dashboard()
    elif choice == "👤 ملف المدير":
        page_manager_profile()
    elif choice == "🎓 الطلاب":
        page_students()
    elif choice == "👨‍🏫 المدرسين":
        page_teachers()
    elif choice == "📚 دفتر الجلسات":
        page_sessions()
    elif choice == "✅ الحضور والغياب":
        page_attendance()
    elif choice == "💰 المستحقات المالية":
        page_payroll()
    elif choice == "🔐 إدارة المستخدمين":
        page_users()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()
