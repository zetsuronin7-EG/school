# -*- coding: utf-8 -*-
"""
نظام إدارة مدرسة "التوكل جيلا"
مدرسة نانوي صناعي - تدريب مزدوج
تم البناء باستخدام Python + Streamlit
"""

import re
import random
from datetime import date, timedelta

import pandas as pd
import streamlit as st

# ==========================================================
# إعداد الصفحة
# ==========================================================
st.set_page_config(
    page_title="مدرسة التوكل جيلا - نظام إدارة المدرسة",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# التنسيق العام واتجاه RTL + نقل القائمة الجانبية لليمين
# ==========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Cairo', sans-serif !important;
    }

    .stApp {
        direction: rtl;
        text-align: right;
    }

    /* ---------- نقل القائمة الجانبية إلى اليمين ---------- */
    div[data-testid="stAppViewContainer"] {
        flex-direction: row-reverse;
    }
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
        order: 2;
        right: 0;
        left: auto;
        border-left: 2px solid #0d6efd;
        border-right: none;
    }
    section[data-testid="stSidebar"] * {
        text-align: right !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        display: flex;
        justify-content: flex-start;
        flex-direction: row-reverse;
    }
    [data-testid="stSidebarNav"] {
        direction: rtl;
    }

    /* ---------- الحقول والنصوص ---------- */
    input, textarea, select,
    .stTextInput input, .stNumberInput input,
    .stDateInput input, .stTextArea textarea {
        direction: rtl !important;
        text-align: right !important;
    }
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        direction: rtl;
    }
    div[data-baseweb="select"] > div {
        direction: rtl;
        text-align: right;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"] {
        direction: rtl;
        text-align: right;
    }
    label, p, h1, h2, h3, h4, h5, h6, span, div {
        text-align: right;
    }
    .stMarkdown, .stText, .stCaption {
        text-align: right;
    }

    /* ---------- الأزرار ---------- */
    .stButton > button,
    .stFormSubmitButton > button,
    .stDownloadButton > button {
        direction: rtl;
        font-family: 'Cairo', sans-serif !important;
        border-radius: 12px;
        font-weight: 700;
        width: 100%;
    }

    /* ---------- الكروت والمؤشرات ---------- */
    [data-testid="stMetric"] {
        direction: rtl;
        text-align: right;
        background: linear-gradient(135deg, #f8fbff 0%, #e6f0ff 100%);
        border: 1px solid #cfe2ff;
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(13, 110, 253, 0.08);
    }
    [data-testid="stMetricLabel"] {
        text-align: right !important;
        font-weight: 700;
    }
    [data-testid="stMetricValue"] {
        text-align: right !important;
        color: #0d6efd;
        font-weight: 900;
    }

    /* ---------- الجداول ---------- */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        direction: rtl;
    }

    /* ---------- التبويبات ---------- */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Cairo', sans-serif !important;
        font-weight: 700;
        border-radius: 10px 10px 0 0;
    }

    /* ---------- صندوق تسجيل الدخول ---------- */
    .login-box {
        background: linear-gradient(135deg, #ffffff 0%, #eef5ff 100%);
        border: 2px solid #0d6efd;
        border-radius: 20px;
        padding: 26px 22px;
        box-shadow: 0 6px 22px rgba(13, 110, 253, 0.15);
    }
    .app-title {
        text-align: center !important;
        color: #0d6efd;
        font-weight: 900;
        font-size: 34px;
        margin-bottom: 4px;
    }
    .app-sub {
        text-align: center !important;
        color: #495057;
        font-weight: 600;
        font-size: 16px;
        margin-bottom: 10px;
    }
    .card {
        background: #ffffff;
        border: 1px solid #dbe7ff;
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# الدوال المساعدة
# ==========================================================
def split_phones(text: str):
    """تقسيم الأرقام المدخلة إلى قائمة، مع دعم الفاصلة العربية والإنجليزية."""
    if not text:
        return []
    parts = re.split(r"[,،;/\n]+", text)
    return [p.strip() for p in parts if p.strip()]


def build_attendance(seed: int, days: int = 14):
    """توليد سجل حضور تجريبي لآخر عدد من الأيام (باستثناء أيام الجمعة)."""
    rnd = random.Random(seed * 7919 + 13)
    result = {}
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=i)
        if d.weekday() == 4:  # الجمعة
            continue
        result[d.isoformat()] = rnd.choices(
            ["حاضر", "غائب", "متأخر"], weights=[78, 12, 10]
        )[0]
    return result


def attendance_totals(student):
    """إرجاع (أيام الحضور، أيام الغياب، أيام التأخير)."""
    att = student.get("attendance", {})
    present = sum(1 for v in att.values() if v == "حاضر")
    absent = sum(1 for v in att.values() if v == "غائب")
    late = sum(1 for v in att.values() if v == "متأخر")
    return present, absent, late


def find_teacher_by_credentials(username, password):
    for t in st.session_state.teachers:
        if (
            t.get("username")
            and t.get("password")
            and t["username"] == username
            and t["password"] == password
        ):
            return t
    return None


# ==========================================================
# تهيئة البيانات الافتراضية داخل session_state
# ==========================================================
def init_data():
    if st.session_state.get("_initialized"):
        return
    st.session_state._initialized = True

    # ---------- حالة الدخول ----------
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.display_name = ""
    st.session_state.role = ""
    st.session_state.current_teacher_id = None

    # ---------- بيانات مدير المدرسة ----------
    st.session_state.manager = {
        "name": "أ. عبد الرحمن محمد التوكل",
        "national_id": "28001011234567",
        "phone": "01001234567",
        "code": "MGR-001",
        "qualification": "بكالوريوس هندسة صناعية - قسم ميكانيكا",
        "grad_year": "2004",
    }

    # ---------- بيانات الطلاب ----------
    students_seed = [
        {
            "name": "أحمد محمود السيد",
            "code": "STD-001",
            "national_id": "30101011234567",
            "phones": ["01011112222", "01011113333"],
            "parent_phones": ["01211112222", "01211113333"],
            "father_job": "نجار",
        },
        {
            "name": "مريم خالد عبد الله",
            "code": "STD-002",
            "national_id": "30201021234567",
            "phones": ["01022223333"],
            "parent_phones": ["01222223333"],
            "father_job": "مدرسة لغة عربية",
        },
        {
            "name": "يوسف إبراهيم حسن",
            "code": "STD-003",
            "national_id": "30101031234567",
            "phones": ["01033334444", "01133334444"],
            "parent_phones": ["01233334444"],
            "father_job": "حداد",
        },
        {
            "name": "سلمى أحمد فتحي",
            "code": "STD-004",
            "national_id": "30201041234567",
            "phones": ["01044445555"],
            "parent_phones": ["01244445555", "01544445555"],
            "father_job": "تاجر",
        },
        {
            "name": "عمر سامي رشاد",
            "code": "STD-005",
            "national_id": "30101051234567",
            "phones": ["01055556666"],
            "parent_phones": ["01255556666"],
            "father_job": "كهربائي",
        },
        {
            "name": "نور الهدى مصطفى",
            "code": "STD-006",
            "national_id": "30201061234567",
            "phones": ["01066667777"],
            "parent_phones": ["01266667777"],
            "father_job": "محاسب",
        },
        {
            "name": "محمد عادل شعبان",
            "code": "STD-007",
            "national_id": "30101071234567",
            "phones": ["01077778888"],
            "parent_phones": ["01277778888"],
            "father_job": "سباك",
        },
        {
            "name": "حبيبة وليد أنور",
            "code": "STD-008",
            "national_id": "30201081234567",
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

    # ---------- بيانات المدرسين ----------
    teachers_seed = [
        {
            "name": "أ. خالد سعيد رمضان",
            "national_id": "28501011234567",
            "phone": "01099887766",
            "code": "TCH-001",
            "qualification": "بكالوريوس تربية صناعية",
            "grad_year": "2008",
            "weekly_sessions": 18,
            "session_price": 75.0,
            "username": "khaled",
            "password": "khaled123",
            "active": True,
        },
        {
            "name": "أ. منى عبد الحميد علي",
            "national_id": "28702021234567",
            "phone": "01088776655",
            "code": "TCH-002",
            "qualification": "بكالوريوس علوم - قسم رياضيات",
            "grad_year": "2010",
            "weekly_sessions": 22,
            "session_price": 70.0,
            "username": "mona",
            "password": "mona123",
            "active": True,
        },
        {
            "name": "أ. مصطفى كامل الجندي",
            "national_id": "28403031234567",
            "phone": "01077665544",
            "code": "TCH-003",
            "qualification": "دبلوم فني صناعي متقدم",
            "grad_year": "2006",
            "weekly_sessions": 16,
            "session_price": 85.0,
            "username": "mostafa",
            "password": "mostafa123",
            "active": True,
        },
        {
            "name": "أ. هدى إبراهيم شاكر",
            "national_id": "28904041234567",
            "phone": "01066554433",
            "code": "TCH-004",
            "qualification": "ليسانس آداب - قسم لغة إنجليزية",
            "grad_year": "2012",
            "weekly_sessions": 20,
            "session_price": 65.0,
            "username": "hoda",
            "password": "hoda123",
            "active": False,
        },
        {
            "name": "أ. طارق ياسر عبد الفتاح",
            "national_id": "28305051234567",
            "phone": "01055443322",
            "code": "TCH-005",
            "qualification": "بكالوريوس هندسة ميكاترونكس",
            "grad_year": "2007",
            "weekly_sessions": 24,
            "session_price": 90.0,
            "username": "tarek",
            "password": "tarek123",
            "active": True,
        },
    ]

    teachers = []
    for idx, t in enumerate(teachers_seed, start=1):
        rec = dict(t)
        rec["id"] = idx
        teachers.append(rec)

    st.session_state.teachers = teachers


# ==========================================================
# شاشة تسجيل الدخول
# ==========================================================
def login_page():
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        st.markdown(
            "<div class='login-box'>"
            "<div class='app-title'>🏫 مدرسة التوكل جيلا</div>"
            "<div class='app-sub'>مدرسة نانوي صناعي — نظام تدريب مزدوج</div>"
            "<hr style='border:1px solid #dbe7ff'>"
            "</div>",
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 اسم المستخدم", placeholder="اكتب اسم المستخدم")
            password = st.text_input(
                "🔑 كلمة المرور", type="password", placeholder="اكتب كلمة المرور"
            )
            submitted = st.form_submit_button("🔓 تسجيل الدخول", use_container_width=True)

        if submitted:
            username = (username or "").strip()
            password = (password or "").strip()

            if not username or not password:
                st.error("⚠️ من فضلك أدخل اسم المستخدم وكلمة المرور.")
            elif username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.username = "admin"
                st.session_state.display_name = "مدير المدرسة"
                st.session_state.role = "admin"
                st.session_state.current_teacher_id = None
                st.rerun()
            else:
                teacher = find_teacher_by_credentials(username, password)
                if teacher is None:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
                elif not teacher.get("active", True):
                    st.error("⛔ هذا الحساب معطّل، برجاء التواصل مع مدير المدرسة.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = teacher["username"]
                    st.session_state.display_name = teacher["name"]
                    st.session_state.role = "teacher"
                    st.session_state.current_teacher_id = teacher["id"]
                    st.rerun()

        st.caption("الحساب الافتراضي للمدير: admin / admin123")


# ==========================================================
# صفحة: لوحة التحكم الرئيسية
# ==========================================================
def page_dashboard():
    st.markdown("## 🏠 لوحة التحكم الرئيسية")
    st.markdown("---")

    students = st.session_state.students
    teachers = st.session_state.teachers
    today_str = date.today().isoformat()

    present_today = sum(
        1 for s in students if s["attendance"].get(today_str) == "حاضر"
    )
    absent_today = sum(
        1 for s in students if s["attendance"].get(today_str) == "غائب"
    )
    late_today = sum(
        1 for s in students if s["attendance"].get(today_str) == "متأخر"
    )

    total_monthly = sum(
        t["weekly_sessions"] * 4 * t["session_price"] for t in teachers
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👨‍🎓 عدد الطلاب", len(students))
    c2.metric("👨‍🏫 عدد المدرسين", len(teachers))
    c3.metric("✅ حضور اليوم", present_today)
    c4.metric("❌ غياب اليوم", absent_today)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("⏰ تأخير اليوم", late_today)
    c6.metric("🔐 حسابات معطلة", sum(1 for t in teachers if not t.get("active", True)))
    c7.metric("📚 إجمالي الحصص الأسبوعية", sum(t["weekly_sessions"] for t in teachers))
    c8.metric("💰 مستحقات الشهر", f"{total_monthly:,.0f} ج.م")

    st.markdown("---")
    st.markdown("### 📊 ملخص حضور الطلاب")

    rows = []
    for s in students:
        p, a, l = attendance_totals(s)
        rows.append(
            {
                "الكود": s["code"],
                "اسم الطالب": s["name"],
                "أيام الحضور": p,
                "أيام الغياب": a,
                "أيام التأخير": l,
                "عدد الجزاءات": len(s["penalties"]),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 👨‍🏫 ملخص المدرسين")
    trows = []
    for t in teachers:
        trows.append(
            {
                "الكود": t["code"],
                "اسم المدرس": t["name"],
                "الحصص الأسبوعية": t["weekly_sessions"],
                "حصص الشهر": t["weekly_sessions"] * 4,
                "ثمن الحصة": f"{t['session_price']:,.0f} ج.م",
                "المستحق الشهري": f"{t['weekly_sessions'] * 4 * t['session_price']:,.0f} ج.م",
                "الحالة": "مفعّل ✅" if t.get("active", True) else "معطّل ⛔",
            }
        )
    st.dataframe(pd.DataFrame(trows), use_container_width=True, hide_index=True)


# ==========================================================
# صفحة: بيانات مدير المدرسة
# ==========================================================
def page_manager():
    st.markdown("## 👤 بيانات مدير المدرسة")
    st.markdown("---")

    m = st.session_state.manager

    with st.form("manager_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("الاسم بالكامل", value=m["name"])
        national_id = c2.text_input("الرقم القومي", value=m["national_id"])
        phone = c1.text_input("رقم التليفون", value=m["phone"])
        code = c2.text_input("الكود", value=m["code"])
        qualification = c1.text_input("المؤهل الدراسي", value=m["qualification"])
        grad_year = c2.text_input("سنة الحصول على المؤهل", value=m["grad_year"])

        saved = st.form_submit_button("💾 حفظ بيانات المدير", use_container_width=True)

    if saved:
        st.session_state.manager = {
            "name": name.strip(),
            "national_id": national_id.strip(),
            "phone": phone.strip(),
            "code": code.strip(),
            "qualification": qualification.strip(),
            "grad_year": grad_year.strip(),
        }
        st.success("✅ تم حفظ بيانات مدير المدرسة بنجاح.")

    st.markdown("---")
    st.markdown("### 📇 بطاقة المدير الحالية")
    mm = st.session_state.manager
    st.markdown(
        f"""
        <div class='card'>
        <b>الاسم:</b> {mm['name']}<br>
        <b>الرقم القومي:</b> {mm['national_id']}<br>
        <b>رقم التليفون:</b> {mm['phone']}<br>
        <b>الكود:</b> {mm['code']}<br>
        <b>المؤهل الدراسي:</b> {mm['qualification']}<br>
        <b>سنة الحصول عليه:</b> {mm['grad_year']}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# صفحة: الطلاب
# ==========================================================
def page_students():
    st.markdown("## 🎓 إدارة الطلاب")
    st.markdown("---")

    tab_list, tab_add, tab_profile = st.tabs(
        ["📋 قائمة الطلاب", "➕ إضافة طالب جديد", "🗂️ الملف الشخصي للطالب"]
    )

    # ---------- قائمة الطلاب ----------
    with tab_list:
        students = st.session_state.students
        if not students:
            st.warning("لا يوجد طلاب مسجلون حتى الآن.")
        else:
            rows = []
            for s in students:
                p, a, l = attendance_totals(s)
                rows.append(
                    {
                        "الكود": s["code"],
                        "الاسم": s["name"],
                        "الرقم القومي": s["national_id"],
                        "تليفون الطالب": " / ".join(s["phones"]) if s["phones"] else "-",
                        "تليفون ولي الأمر": " / ".join(s["parent_phones"])
                        if s["parent_phones"]
                        else "-",
                        "مهنة الأب": s["father_job"],
                        "الحضور": p,
                        "الغياب": a,
                        "التأخير": l,
                        "الجزاءات": len(s["penalties"]),
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.markdown("### 🗑️ حذف طالب")
            delete_options = {f"{s['name']} - {s['code']}": s["id"] for s in students}
            sel_del = st.selectbox(
                "اختر الطالب المراد حذفه", list(delete_options.keys()), key="del_student_sel"
            )
            if st.button("🗑️ حذف الطالب نهائياً", key="del_student_btn"):
                sid = delete_options[sel_del]
                st.session_state.students = [
                    s for s in st.session_state.students if s["id"] != sid
                ]
                st.success("تم حذف الطالب بنجاح.")
                st.rerun()

    # ---------- إضافة طالب ----------
    with tab_add:
        with st.form("add_student_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم الطالب")
            code = c2.text_input("الكود")
            national_id = c1.text_input("الرقم القومي")
            father_job = c2.text_input("مهنة الأب")
            phones_txt = c1.text_input(
                "أرقام تليفون الطالب (افصل بينها بفاصلة ,)",
                placeholder="01011112222, 01011113333",
            )
            parent_phones_txt = c2.text_input(
                "أرقام تليفون ولي الأمر (افصل بينها بفاصلة ,)",
                placeholder="01211112222, 01211113333",
            )
            notes = st.text_area("ملاحظات", value="")

            add_btn = st.form_submit_button("➕ إضافة الطالب", use_container_width=True)

        if add_btn:
            name = (name or "").strip()
            code = (code or "").strip()
            if not name or not code:
                st.error("⚠️ اسم الطالب والكود مطلوبان.")
            elif any(s["code"] == code for s in st.session_state.students):
                st.error("⚠️ هذا الكود مستخدم بالفعل لطالب آخر.")
            else:
                new_id = (
                    max([s["id"] for s in st.session_state.students], default=0) + 1
                )
                st.session_state.students.append(
                    {
                        "id": new_id,
                        "name": name,
                        "code": code,
                        "national_id": (national_id or "").strip(),
                        "phones": split_phones(phones_txt),
                        "parent_phones": split_phones(parent_phones_txt),
                        "father_job": (father_job or "").strip(),
                        "attendance": {},
                        "penalties": [],
                        "notes": notes.strip(),
                    }
                )
                st.success(f"✅ تمت إضافة الطالب {name} بنجاح.")

    # ---------- الملف الشخصي ----------
    with tab_profile:
        students = st.session_state.students
        if not students:
            st.warning("لا يوجد طلاب مسجلون حتى الآن.")
            return

        options = {f"{s['name']} - {s['code']}": s["id"] for s in students}
        sel = st.selectbox("اختر الطالب", list(options.keys()), key="profile_select")
        sid = options[sel]
        student = next((s for s in students if s["id"] == sid), None)

        if student is None:
            st.error("لم يتم العثور على الطالب.")
            return

        p, a, l = attendance_totals(student)

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("✅ أيام الحضور", p)
        m2.metric("❌ أيام الغياب", a)
        m3.metric("⏰ أيام التأخير", l)
        m4.metric("⚖️ عدد الجزاءات", len(student["penalties"]))

        st.markdown("### 📌 البيانات الشخصية")
        st.markdown(
            f"""
            <div class='card'>
            <b>الاسم:</b> {student['name']}<br>
            <b>الكود:</b> {student['code']}<br>
            <b>الرقم القومي:</b> {student['national_id'] or '-'}<br>
            <b>مهنة الأب:</b> {student['father_job'] or '-'}<br>
            <b>أرقام تليفون الطالب:</b> {' / '.join(student['phones']) if student['phones'] else '-'}<br>
            <b>أرقام تليفون ولي الأمر:</b> {' / '.join(student['parent_phones']) if student['parent_phones'] else '-'}<br>
            <b>الملاحظات:</b> {student['notes'] or '-'}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🗓️ سجل الحضور والغياب")
        if student["attendance"]:
            att_rows = [
                {"التاريخ": k, "الحالة": v}
                for k, v in sorted(student["attendance"].items(), reverse=True)
            ]
            st.dataframe(
                pd.DataFrame(att_rows), use_container_width=True, hide_index=True
            )
        else:
            st.info("لا يوجد سجل حضور لهذا الطالب حتى الآن.")

        st.markdown("### ⚖️ الجزاءات")
        if student["penalties"]:
            pen_rows = [
                {"التاريخ": x.get("date", "-"), "السبب": x.get("reason", "-")}
                for x in student["penalties"]
            ]
            st.dataframe(
                pd.DataFrame(pen_rows), use_container_width=True, hide_index=True
            )
        else:
            st.info("لا توجد جزاءات على هذا الطالب.")

        with st.form("add_penalty_form", clear_on_submit=True):
            c1, c2 = st.columns([2, 1])
            reason = c1.text_input("سبب الجزاء")
            pdate = c2.date_input("تاريخ الجزاء", value=date.today())
            pen_btn = st.form_submit_button("➕ إضافة جزاء", use_container_width=True)

        if pen_btn:
            reason = (reason or "").strip()
            if not reason:
                st.error("⚠️ من فضلك اكتب سبب الجزاء.")
            else:
                student["penalties"].append(
                    {"date": pdate.isoformat(), "reason": reason}
                )
                st.success("✅ تم إضافة الجزاء بنجاح.")
                st.rerun()

        st.markdown("### 📝 تعديل الملاحظات")
        new_notes = st.text_area(
            "الملاحظات", value=student.get("notes", ""), key=f"notes_{student['id']}"
        )
        if st.button("💾 حفظ الملاحظات", key=f"save_notes_{student['id']}"):
            student["notes"] = new_notes.strip()
            st.success("✅ تم حفظ الملاحظات.")


# ==========================================================
# صفحة: المدرسين
# ==========================================================
def page_teachers():
    st.markdown("## 👨‍🏫 إدارة المدرسين")
    st.markdown("---")

    tab_list, tab_add = st.tabs(["📋 قائمة المدرسين", "➕ إضافة مدرس جديد"])

    with tab_list:
        teachers = st.session_state.teachers
        if not teachers:
            st.warning("لا يوجد مدرسون مسجلون حتى الآن.")
        else:
            rows = []
            for t in teachers:
                weekly = t["weekly_sessions"]
                monthly = weekly * 4
                due = monthly * t["session_price"]
                rows.append(
                    {
                        "الكود": t["code"],
                        "الاسم": t["name"],
                        "الرقم القومي": t["national_id"],
                        "التليفون": t["phone"],
                        "المؤهل": t["qualification"],
                        "سنة التخرج": t["grad_year"],
                        "حصص/أسبوع": weekly,
                        "ثمن الحصة": f"{t['session_price']:,.0f}",
                        "حصص/شهر": monthly,
                        "المستحق الشهري": f"{due:,.0f}",
                        "الحالة": "مفعّل ✅" if t.get("active", True) else "معطّل ⛔",
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.markdown("### ✏️ تعديل بيانات مدرس")
            edit_options = {f"{t['name']} - {t['code']}": t["id"] for t in teachers}
            sel_edit = st.selectbox(
                "اختر المدرس", list(edit_options.keys()), key="edit_teacher_sel"
            )
            tid = edit_options[sel_edit]
            teacher = next((t for t in teachers if t["id"] == tid), None)

            if teacher is not None:
                with st.form("edit_teacher_form"):
                    c1, c2 = st.columns(2)
                    name = c1.text_input("الاسم", value=teacher["name"])
                    national_id = c2.text_input(
                        "الرقم القومي", value=teacher["national_id"]
                    )
                    phone = c1.text_input("رقم التليفون", value=teacher["phone"])
                    code = c2.text_input("الكود", value=teacher["code"])
                    qualification = c1.text_input(
                        "المؤهل الدراسي", value=teacher["qualification"]
                    )
                    grad_year = c2.text_input(
                        "سنة الحصول على المؤهل", value=teacher["grad_year"]
                    )
                    weekly_sessions = c1.number_input(
                        "عدد الحصص الأسبوعية",
                        min_value=0,
                        max_value=200,
                        value=int(teacher["weekly_sessions"]),
                        step=1,
                    )
                    session_price = c2.number_input(
                        "ثمن الحصة الواحدة",
                        min_value=0.0,
                        max_value=100000.0,
                        value=float(teacher["session_price"]),
                        step=5.0,
                    )
                    save_btn = st.form_submit_button(
                        "💾 حفظ التعديلات", use_container_width=True
                    )

                if save_btn:
                    teacher["name"] = name.strip()
                    teacher["national_id"] = national_id.strip()
                    teacher["phone"] = phone.strip()
                    teacher["code"] = code.strip()
                    teacher["qualification"] = qualification.strip()
                    teacher["grad_year"] = grad_year.strip()
                    teacher["weekly_sessions"] = int(weekly_sessions)
                    teacher["session_price"] = float(session_price)
                    st.success("✅ تم حفظ تعديلات المدرس بنجاح.")

    with tab_add:
        with st.form("add_teacher_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم المدرس")
            national_id = c2.text_input("الرقم القومي")
            phone = c1.text_input("رقم التليفون")
            code = c2.text_input("الكود")
            qualification = c1.text_input("المؤهل الدراسي")
            grad_year = c2.text_input("سنة الحصول على المؤهل")
            weekly_sessions = c1.number_input(
                "عدد الحصص الأسبوعية", min_value=0, max_value=200, value=12, step=1
            )
            session_price = c2.number_input(
                "ثمن الحصة الواحدة", min_value=0.0, max_value=100000.0, value=70.0, step=5.0
            )
            add_btn = st.form_submit_button("➕ إضافة المدرس", use_container_width=True)

        if add_btn:
            name = (name or "").strip()
            code = (code or "").strip()
            if not name or not code:
                st.error("⚠️ اسم المدرس والكود مطلوبان.")
            elif any(t["code"] == code for t in st.session_state.teachers):
                st.error("⚠️ هذا الكود مستخدم بالفعل لمدرس آخر.")
            else:
                new_id = (
                    max([t["id"] for t in st.session_state.teachers], default=0) + 1
                )
                st.session_state.teachers.append(
                    {
                        "id": new_id,
                        "name": name,
                        "national_id": (national_id or "").strip(),
                        "phone": (phone or "").strip(),
                        "code": code,
                        "qualification": (qualification or "").strip(),
                        "grad_year": (grad_year or "").strip(),
                        "weekly_sessions": int(weekly_sessions),
                        "session_price": float(session_price),
                        "username": "",
                        "password": "",
                        "active": True,
                    }
                )
                st.success(f"✅ تمت إضافة المدرس {name} بنجاح.")


# ==========================================================
# صفحة: الحضور والغياب
# ==========================================================
def page_attendance():
    st.markdown("## ✅ الحضور والغياب اليومي")
    st.markdown("---")

    students = st.session_state.students
    if not students:
        st.warning("لا يوجد طلاب مسجلون حتى الآن.")
        return

    c1, c2 = st.columns([1, 2])
    selected_date = c1.date_input("📅 اختر التاريخ", value=date.today())
    dstr = selected_date.isoformat()
    c2.markdown(
        f"<div class='card' style='margin-top:26px'>"
        f"جارٍ تسجيل حضور يوم: <b>{dstr}</b></div>",
        unsafe_allow_html=True,
    )

    df = pd.DataFrame(
        [
            {
                "الكود": s["code"],
                "الطالب": s["name"],
                "الحالة": s["attendance"].get(dstr, "حاضر"),
            }
            for s in students
        ]
    )

    edited = st.data_editor(
        df,
        key=f"att_editor_{dstr}",
        hide_index=True,
        use_container_width=True,
        disabled=["الكود", "الطالب"],
        column_config={
            "الحالة": st.column_config.SelectboxColumn(
                "الحالة",
                help="اختر حالة الطالب",
                options=["حاضر", "غائب", "متأخر"],
                required=True,
            )
        },
    )

    if st.button("💾 حفظ سجل الحضور", type="primary", use_container_width=True):
        by_code = {s["code"]: s for s in students}
        for _, row in edited.iterrows():
            code = row["الكود"]
            if code in by_code:
                by_code[code]["attendance"][dstr] = row["الحالة"]
        st.success(f"✅ تم حفظ سجل حضور يوم {dstr} بنجاح.")

    st.markdown("---")
    st.markdown("### 📊 ملخص الحضور التراكمي")

    rows = []
    for s in students:
        p, a, l = attendance_totals(s)
        rows.append(
            {
                "الكود": s["code"],
                "الطالب": s["name"],
                "أيام الحضور": p,
                "أيام الغياب": a,
                "أيام التأخير": l,
                "عدد الجزاءات": len(s["penalties"]),
                "ملاحظات": s.get("notes", ""),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ==========================================================
# صفحة: المستحقات المالية
# ==========================================================
def page_finance():
    st.markdown("## 💰 المستحقات المالية للمدرسين")
    st.markdown("---")

    teachers = st.session_state.teachers
    if not teachers:
        st.warning("لا يوجد مدرسون مسجلون حتى الآن.")
        return

    rows = []
    total_weekly = 0
    total_monthly = 0
    total_due = 0.0

    for t in teachers:
        weekly = int(t["weekly_sessions"])
        monthly = weekly * 4
        price = float(t["session_price"])
        due = monthly * price

        total_weekly += weekly
        total_monthly += monthly
        total_due += due

        rows.append(
            {
                "الكود": t["code"],
                "اسم المدرس": t["name"],
                "الحصص الأسبوعية": weekly,
                "الحصص الشهرية": monthly,
                "ثمن الحصة": f"{price:,.2f} ج.م",
                "المستحق الشهري": f"{due:,.2f} ج.م",
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("📚 إجمالي الحصص الأسبوعية", total_weekly)
    c2.metric("🗓️ إجمالي الحصص الشهرية", total_monthly)
    c3.metric("💵 إجمالي المستحقات الشهرية", f"{total_due:,.2f} ج.م")

    st.caption(
        "المعادلة المستخدمة: (عدد الحصص الأسبوعية × 4 أسابيع) × ثمن الحصة الواحدة."
    )


# ==========================================================
# صفحة: إدارة حسابات المعلمين
# ==========================================================
def page_accounts():
    st.markdown("## 🔐 إدارة حسابات المعلمين")
    st.markdown("---")
    st.info(
        "يمكنك من هنا إنشاء اسم مستخدم وكلمة مرور لكل مدرس، وكذلك تعطيل أو تفعيل حسابه في أي وقت."
    )

    teachers = st.session_state.teachers
    if not teachers:
        st.warning("لا يوجد مدرسون مسجلون حتى الآن.")
        return

    for t in teachers:
        status_text = "مفعّل ✅" if t.get("active", True) else "معطّل ⛔"
        with st.expander(f"👨‍🏫 {t['name']} — {t['code']} — الحالة: {status_text}"):
            c1, c2 = st.columns(2)
            new_user = c1.text_input(
                "اسم المستخدم", value=t.get("username", ""), key=f"acc_user_{t['id']}"
            )
            new_pass = c2.text_input(
                "كلمة المرور", value=t.get("password", ""), key=f"acc_pass_{t['id']}"
            )

            b1, b2 = st.columns(2)
            if b1.button("💾 حفظ بيانات الدخول", key=f"acc_save_{t['id']}"):
                new_user = (new_user or "").strip()
                new_pass = (new_pass or "").strip()
                if not new_user or not new_pass:
                    st.error("⚠️ اسم المستخدم وكلمة المرور مطلوبان.")
                else:
                    duplicate = any(
                        other["id"] != t["id"]
                        and other.get("username") == new_user
                        for other in st.session_state.teachers
                    )
                    if duplicate or new_user == "admin":
                        st.error("⚠️ اسم المستخدم هذا مستخدم بالفعل.")
                    else:
                        t["username"] = new_user
                        t["password"] = new_pass
                        st.success("✅ تم حفظ بيانات الدخول بنجاح.")
                        st.rerun()

            toggle_label = (
                "⛔ تعطيل الحساب" if t.get("active", True) else "✅ إعادة تفعيل الحساب"
            )
            if b2.button(toggle_label, key=f"acc_toggle_{t['id']}"):
                t["active"] = not t.get("active", True)
                st.rerun()

            st.caption(
                f"الحالة الحالية: {status_text} — "
                f"اسم المستخدم: {t.get('username') or 'لم يتم إنشاؤه بعد'}"
            )


# ==========================================================
# البرنامج الرئيسي
# ==========================================================
def main():
    init_data()

    if not st.session_state.get("logged_in"):
        login_page()
        return

    role = st.session_state.get("role", "")

    with st.sidebar:
        st.markdown(
            f"<div style='text-align:right'>"
            f"<h3 style='color:#0d6efd;margin-bottom:2px'>🏫 التوكل جيلا</h3>"
            f"<small>مدرسة نانوي صناعي — تدريب مزدوج</small>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            f"**👋 مرحباً:** {st.session_state.get('display_name', '')}"
        )
        st.markdown(
            f"**🔑 الصلاحية:** {'مدير المدرسة' if role == 'admin' else 'معلم'}"
        )
        st.markdown("---")

        if role == "admin":
            pages = [
                "🏠 لوحة التحكم",
                "👤 بيانات مدير المدرسة",
                "🎓 الطلاب",
                "👨‍🏫 المدرسين",
                "✅ الحضور والغياب",
                "💰 المستحقات المالية",
                "🔐 حسابات المعلمين",
            ]
        else:
            pages = ["✅ الحضور والغياب"]

        choice = st.radio("القائمة الرئيسية", pages, label_visibility="collapsed")

        st.markdown("---")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.display_name = ""
            st.session_state.role = ""
            st.session_state.current_teacher_id = None
            st.rerun()

    # ---------- توجيه الصفحات ----------
    if role == "teacher":
        page_attendance()
        return

    if choice == "🏠 لوحة التحكم":
        page_dashboard()
    elif choice == "👤 بيانات مدير المدرسة":
        page_manager()
    elif choice == "🎓 الطلاب":
        page_students()
    elif choice == "👨‍🏫 المدرسين":
        page_teachers()
    elif choice == "✅ الحضور والغياب":
        page_attendance()
    elif choice == "💰 المستحقات المالية":
        page_finance()
    elif choice == "🔐 حسابات المعلمين":
        page_accounts()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()
