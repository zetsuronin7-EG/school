# -*- coding: utf-8 -*-
"""
نظام إدارة مدرسة التوكل جيلا
مدرسة نانوي صناعي تدريب مزدوج
تطبيق ويب مبني بلغة Python ومكتبة Streamlit
"""

import streamlit as st
import pandas as pd
import random
import string
from datetime import date

# =====================================================================================
# 1) إعدادات الصفحة الأساسية
# =====================================================================================
st.set_page_config(
    page_title="مدرسة التوكل جيلا - نظام الإدارة",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================================
# 2) تنسيق CSS لجعل الواجهة بالكامل من اليمين إلى اليسار (RTL)
# =====================================================================================
RTL_CSS = """
<style>
    /* اتجاه الصفحة بالكامل */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        direction: rtl;
    }

    /* هذا السطر هو ما يجعل القائمة الجانبية تنتقل فعلياً إلى اليمين */
    [data-testid="stAppViewContainer"] {
        direction: rtl;
    }

    .main .block-container {
        direction: rtl;
        text-align: right;
    }

    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stSidebar"] * {
        text-align: right;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        text-align: right;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {
        text-align: right;
        direction: rtl;
    }

    div[data-baseweb="select"] {
        direction: rtl;
        text-align: right;
    }
    div[data-baseweb="popover"] {
        direction: rtl;
        text-align: right;
    }

    div[role="radiogroup"] {
        direction: rtl;
    }
    div[role="radiogroup"] > label {
        flex-direction: row-reverse;
    }

    [data-testid="stMetric"] {
        text-align: right;
    }

    thead tr th, tbody tr td {
        text-align: right !important;
    }

    [data-testid="stForm"] {
        direction: rtl;
    }
</style>
"""

# =====================================================================================
# 3) تهيئة البيانات الافتراضية (لمنع ظهور شاشات فارغة عند أول تشغيل)
# =====================================================================================
def init_state():
    ss = st.session_state

    if "logged_in" not in ss:
        ss.logged_in = False
    if "username" not in ss:
        ss.username = ""
    if "role" not in ss:
        ss.role = ""
    if "teacher_code" not in ss:
        ss.teacher_code = ""

    # حساب المدير الافتراضي لتسجيل الدخول
    if "admin_login" not in ss:
        ss.admin_login = {"admin": "admin123"}

    # بيانات مدير المدرسة (البروفايل الشخصي)
    if "school_info" not in ss:
        ss.school_info = {
            "الاسم": "أ. كريم عبد الفتاح أحمد",
            "الرقم القومي": "28001011234567",
            "رقم التليفون": "01001234567",
            "الكود": "MGR-001",
            "المؤهل الدراسي": "بكالوريوس تربية صناعية",
            "سنة الحصول على المؤهل": 2004,
        }

    # بيانات الطلاب التجريبية
    if "students" not in ss:
        ss.students = [
            {
                "الكود": "STU-001",
                "الاسم": "أحمد محمود سيد",
                "الرقم القومي": "31001011234561",
                "أرقام هاتف الطالب": ["01111111111"],
                "أرقام هاتف ولي الأمر": ["01222222222", "01000111222"],
                "مهنة الأب": "سباك",
            },
            {
                "الكود": "STU-002",
                "الاسم": "محمد سيد إبراهيم",
                "الرقم القومي": "31002021234562",
                "أرقام هاتف الطالب": ["01133333333"],
                "أرقام هاتف ولي الأمر": ["01244444444"],
                "مهنة الأب": "نجار",
            },
            {
                "الكود": "STU-003",
                "الاسم": "يوسف كمال حسن",
                "الرقم القومي": "31003031234563",
                "أرقام هاتف الطالب": ["01155555555", "01099999999"],
                "أرقام هاتف ولي الأمر": ["01266666666"],
                "مهنة الأب": "حداد",
            },
        ]

    # بيانات المدرسين التجريبية
    if "teachers" not in ss:
        ss.teachers = [
            {
                "الكود": "TCH-001",
                "الاسم": "أ. سامي فتحي محمود",
                "الرقم القومي": "27505051234561",
                "رقم التليفون": "01077777777",
                "المؤهل الدراسي": "بكالوريوس هندسة إنتاج",
                "سنة الحصول على المؤهل": 2010,
                "عدد الحصص الأسبوعية": 12,
                "ثمن الحصة الواحدة": 50.0,
            },
            {
                "الكود": "TCH-002",
                "الاسم": "أ. هالة محمد عبد الله",
                "الرقم القومي": "28709091234562",
                "رقم التليفون": "01088888888",
                "المؤهل الدراسي": "بكالوريوس تربية فنية",
                "سنة الحصول على المؤهل": 2013,
                "عدد الحصص الأسبوعية": 10,
                "ثمن الحصة الواحدة": 60.0,
            },
        ]

    # حسابات دخول المعلمين (تُدار من لوحة المدير)
    if "teacher_accounts" not in ss:
        ss.teacher_accounts = {
            "sami.tch001": {
                "password": "teach123",
                "الكود": "TCH-001",
                "مفعل": True,
            },
            "hala.tch002": {
                "password": "teach123",
                "الكود": "TCH-002",
                "مفعل": True,
            },
        }

    # سجل الحضور والغياب التجريبي
    if "attendance" not in ss:
        ss.attendance = [
            {"كود الطالب": "STU-001", "التاريخ": "2026-09-20", "الحالة": "حاضر", "جزاء": "", "ملاحظات": ""},
            {"كود الطالب": "STU-001", "التاريخ": "2026-09-21", "الحالة": "متأخر", "جزاء": "تنبيه شفهي", "ملاحظات": "تأخر 15 دقيقة"},
            {"كود الطالب": "STU-002", "التاريخ": "2026-09-20", "الحالة": "غائب", "جزاء": "خصم نصف يوم", "ملاحظات": "بدون عذر"},
            {"كود الطالب": "STU-002", "التاريخ": "2026-09-21", "الحالة": "حاضر", "جزاء": "", "ملاحظات": ""},
            {"كود الطالب": "STU-003", "التاريخ": "2026-09-20", "الحالة": "حاضر", "جزاء": "", "ملاحظات": ""},
            {"كود الطالب": "STU-003", "التاريخ": "2026-09-21", "الحالة": "حاضر", "جزاء": "", "ملاحظات": ""},
        ]


# =====================================================================================
# 4) دوال مساعدة
# =====================================================================================
def parse_multi_values(text):
    """يحول نص يحتوي على عدة أرقام مفصولة بفاصلة أو سطر جديد إلى قائمة"""
    if not text:
        return []
    cleaned = text.replace("،", ",").replace("\n", ",")
    return [v.strip() for v in cleaned.split(",") if v.strip()]


def format_multi_values(values):
    """يحول قائمة أرقام إلى نص واحد للعرض"""
    return "، ".join(values) if values else "—"


def next_code(prefix, items):
    """يولد كوداً تسلسلياً جديداً مثل STU-004 أو TCH-003"""
    numbers = []
    for item in items:
        code = item.get("الكود", "")
        if code.startswith(prefix + "-"):
            try:
                numbers.append(int(code.split("-")[1]))
            except ValueError:
                pass
    n = max(numbers) + 1 if numbers else 1
    return f"{prefix}-{n:03d}"


def get_student(code):
    for s in st.session_state.students:
        if s["الكود"] == code:
            return s
    return None


def get_teacher(code):
    for t in st.session_state.teachers:
        if t["الكود"] == code:
            return t
    return None


def student_summary(code):
    """يحسب إجمالي الحضور والغياب والتأخير والجزاءات لطالب معين"""
    records = [r for r in st.session_state.attendance if r["كود الطالب"] == code]
    present = sum(1 for r in records if r["الحالة"] == "حاضر")
    absent = sum(1 for r in records if r["الحالة"] == "غائب")
    late = sum(1 for r in records if r["الحالة"] == "متأخر")
    penalties = [r["جزاء"] for r in records if r["جزاء"]]
    notes = [r["ملاحظات"] for r in records if r["ملاحظات"]]
    return {
        "عدد أيام الحضور": present,
        "عدد أيام الغياب": absent,
        "عدد مرات التأخير": late,
        "عدد الجزاءات": len(penalties),
        "الجزاءات": penalties,
        "الملاحظات": notes,
        "السجل": records,
    }


def teacher_financials(teacher):
    """يحسب إجمالي الحصص الأسبوعية والشهرية والمستحقات المالية الشهرية للمدرس"""
    weekly = teacher["عدد الحصص الأسبوعية"]
    monthly_classes = weekly * 4
    monthly_due = monthly_classes * teacher["ثمن الحصة الواحدة"]
    return weekly, monthly_classes, monthly_due


def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


# =====================================================================================
# 5) شاشة تسجيل الدخول
# =====================================================================================
def login_page():
    st.markdown("<h1 style='text-align:center;'>🎓 مدرسة التوكل جيلا</h1>", unsafe_allow_html=True)
    st.markdown(
        "<h4 style='text-align:center; color:gray;'>مدرسة نانوي صناعي تدريب مزدوج</h4>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("تسجيل الدخول")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        login_btn = st.button("دخول", use_container_width=True)

        if login_btn:
            admin_login = st.session_state.admin_login
            teacher_accounts = st.session_state.teacher_accounts

            if username in admin_login and admin_login[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = "admin"
                st.rerun()

            elif username in teacher_accounts:
                account = teacher_accounts[username]
                if not account["مفعل"]:
                    st.error("هذا الحساب معطل حالياً. برجاء التواصل مع إدارة المدرسة.")
                elif account["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "teacher"
                    st.session_state.teacher_code = account["الكود"]
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

        st.info("بيانات الدخول الافتراضية للمدير: admin / admin123")


# =====================================================================================
# 6) القائمة الجانبية وتسجيل الخروج
# =====================================================================================
def sidebar_menu():
    with st.sidebar:
        if st.session_state.role == "admin":
            display_name = "مدير النظام"
        else:
            teacher = get_teacher(st.session_state.teacher_code)
            display_name = teacher["الاسم"] if teacher else st.session_state.username

        st.markdown(f"### 👋 أهلاً، {display_name}")
        st.caption("صلاحية: مدير" if st.session_state.role == "admin" else "صلاحية: معلم")
        st.markdown("---")

        if st.session_state.role == "admin":
            page = st.radio(
                "القائمة الرئيسية",
                [
                    "لوحة التحكم",
                    "بيانات مدير المدرسة",
                    "بيانات الطلاب",
                    "بيانات المدرسين",
                    "الحضور والغياب",
                    "حسابات المعلمين",
                ],
            )
        else:
            page = "تسجيل الحضور والغياب"
            st.write("📋 تسجيل الحضور والغياب اليومي للطلاب")

        st.markdown("---")
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            for key in ["logged_in", "username", "role", "teacher_code"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    return page


# =====================================================================================
# 7) لوحة التحكم الرئيسية (للمدير)
# =====================================================================================
def page_dashboard():
    st.title("📊 لوحة التحكم الرئيسية")

    students = st.session_state.students
    teachers = st.session_state.teachers
    attendance = st.session_state.attendance

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("عدد الطلاب", len(students))
    c2.metric("عدد المدرسين", len(teachers))
    c3.metric("سجلات الحضور", len(attendance))
    total_monthly_due = sum(teacher_financials(t)[2] for t in teachers)
    c4.metric("مستحقات المدرسين شهرياً", f"{total_monthly_due:,.0f} جنيه")

    st.markdown("---")
    st.subheader("نظرة عامة على الحضور")
    if attendance:
        df = pd.DataFrame(attendance)
        status_counts = df["الحالة"].value_counts()
        st.bar_chart(status_counts)
    else:
        st.info("لا يوجد سجلات حضور بعد")


# =====================================================================================
# 8) بيانات مدير المدرسة
# =====================================================================================
def page_school_info():
    st.title("🏫 بيانات مدير المدرسة")
    info = st.session_state.school_info

    with st.form("school_info_form"):
        name = st.text_input("الاسم", value=info["الاسم"])
        national_id = st.text_input("الرقم القومي", value=info["الرقم القومي"])
        phone = st.text_input("رقم التليفون", value=info["رقم التليفون"])
        code = st.text_input("الكود", value=info["الكود"])
        qualification = st.text_input("المؤهل الدراسي", value=info["المؤهل الدراسي"])
        qualification_year = st.number_input(
            "سنة الحصول على المؤهل",
            min_value=1950,
            max_value=2100,
            value=int(info["سنة الحصول على المؤهل"]),
            step=1,
        )
        submitted = st.form_submit_button("💾 حفظ التعديلات")
        if submitted:
            st.session_state.school_info = {
                "الاسم": name.strip(),
                "الرقم القومي": national_id.strip(),
                "رقم التليفون": phone.strip(),
                "الكود": code.strip(),
                "المؤهل الدراسي": qualification.strip(),
                "سنة الحصول على المؤهل": qualification_year,
            }
            st.success("تم حفظ البيانات بنجاح")


# =====================================================================================
# 9) بيانات الطلاب
# =====================================================================================
def page_students():
    st.title("👨‍🎓 بيانات الطلاب")
    tab1, tab2, tab3 = st.tabs(["عرض الطلاب والملف الشخصي", "➕ إضافة طالب جديد", "✏️ تعديل / حذف طالب"])

    # ---------------- عرض الطلاب والملف الشخصي ----------------
    with tab1:
        students = st.session_state.students
        if not students:
            st.info("لا يوجد طلاب مسجلين")
        else:
            names = {s["الكود"]: f'{s["الاسم"]} ({s["الكود"]})' for s in students}
            selected_code = st.selectbox(
                "اختر طالباً لعرض ملفه الشخصي",
                options=list(names.keys()),
                format_func=lambda c: names[c],
            )
            student = get_student(selected_code)
            if student:
                st.markdown("### 🗂️ الملف الشخصي")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**الاسم:** {student['الاسم']}")
                    st.write(f"**الكود:** {student['الكود']}")
                    st.write(f"**الرقم القومي:** {student['الرقم القومي']}")
                    st.write(f"**مهنة الأب:** {student['مهنة الأب']}")
                with c2:
                    st.write(f"**أرقام هاتف الطالب:** {format_multi_values(student['أرقام هاتف الطالب'])}")
                    st.write(f"**أرقام هاتف ولي الأمر:** {format_multi_values(student['أرقام هاتف ولي الأمر'])}")

                st.markdown("### 📅 سجل الحضور والغياب التراكمي")
                summary = student_summary(selected_code)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("أيام الحضور", summary["عدد أيام الحضور"])
                m2.metric("أيام الغياب", summary["عدد أيام الغياب"])
                m3.metric("مرات التأخير", summary["عدد مرات التأخير"])
                m4.metric("عدد الجزاءات", summary["عدد الجزاءات"])

                if summary["السجل"]:
                    st.dataframe(pd.DataFrame(summary["السجل"]), use_container_width=True, hide_index=True)
                else:
                    st.info("لا يوجد سجل حضور لهذا الطالب بعد")

            st.markdown("---")
            st.markdown("### 📋 جميع الطلاب")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "الكود": s["الكود"],
                            "الاسم": s["الاسم"],
                            "الرقم القومي": s["الرقم القومي"],
                            "هاتف الطالب": format_multi_values(s["أرقام هاتف الطالب"]),
                            "هاتف ولي الأمر": format_multi_values(s["أرقام هاتف ولي الأمر"]),
                            "مهنة الأب": s["مهنة الأب"],
                        }
                        for s in students
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )

    # ---------------- إضافة طالب جديد ----------------
    with tab2:
        st.markdown("### إضافة طالب جديد")
        with st.form("add_student_form", clear_on_submit=True):
            name = st.text_input("اسم الطالب")
            national_id = st.text_input("الرقم القومي")
            student_phones = st.text_area("أرقام هاتف الطالب (افصل بين الأرقام بفاصلة)")
            guardian_phones = st.text_area("أرقام هاتف ولي الأمر (افصل بين الأرقام بفاصلة)")
            father_job = st.text_input("مهنة الأب")
            submitted = st.form_submit_button("➕ إضافة الطالب")
            if submitted:
                if not name.strip():
                    st.error("يجب إدخال اسم الطالب")
                else:
                    new_code = next_code("STU", st.session_state.students)
                    st.session_state.students.append(
                        {
                            "الكود": new_code,
                            "الاسم": name.strip(),
                            "الرقم القومي": national_id.strip(),
                            "أرقام هاتف الطالب": parse_multi_values(student_phones),
                            "أرقام هاتف ولي الأمر": parse_multi_values(guardian_phones),
                            "مهنة الأب": father_job.strip(),
                        }
                    )
                    st.success(f"تم إضافة الطالب بنجاح — الكود: {new_code}")
                    st.rerun()

    # ---------------- تعديل / حذف طالب ----------------
    with tab3:
        students = st.session_state.students
        if not students:
            st.info("لا يوجد طلاب لتعديلهم")
        else:
            names = {s["الكود"]: f'{s["الاسم"]} ({s["الكود"]})' for s in students}
            selected_code = st.selectbox(
                "اختر طالباً للتعديل أو الحذف",
                options=list(names.keys()),
                format_func=lambda c: names[c],
                key="edit_student_select",
            )
            student = get_student(selected_code)
            if student:
                with st.form("edit_student_form"):
                    name = st.text_input("اسم الطالب", value=student["الاسم"])
                    national_id = st.text_input("الرقم القومي", value=student["الرقم القومي"])
                    student_phones = st.text_area(
                        "أرقام هاتف الطالب", value=format_multi_values(student["أرقام هاتف الطالب"]).replace("—", "")
                    )
                    guardian_phones = st.text_area(
                        "أرقام هاتف ولي الأمر",
                        value=format_multi_values(student["أرقام هاتف ولي الأمر"]).replace("—", ""),
                    )
                    father_job = st.text_input("مهنة الأب", value=student["مهنة الأب"])
                    save_btn = st.form_submit_button("💾 حفظ التعديلات")
                    if save_btn:
                        student["الاسم"] = name.strip()
                        student["الرقم القومي"] = national_id.strip()
                        student["أرقام هاتف الطالب"] = parse_multi_values(student_phones)
                        student["أرقام هاتف ولي الأمر"] = parse_multi_values(guardian_phones)
                        student["مهنة الأب"] = father_job.strip()
                        st.success("تم حفظ التعديلات بنجاح")
                        st.rerun()

                st.markdown("---")
                if st.button("🗑️ حذف هذا الطالب نهائياً", type="primary"):
                    st.session_state.students = [
                        s for s in st.session_state.students if s["الكود"] != selected_code
                    ]
                    st.session_state.attendance = [
                        r for r in st.session_state.attendance if r["كود الطالب"] != selected_code
                    ]
                    st.success("تم حذف الطالب وجميع سجلاته")
                    st.rerun()


# =====================================================================================
# 10) بيانات المدرسين
# =====================================================================================
def page_teachers():
    st.title("👨‍🏫 بيانات المدرسين")
    tab1, tab2, tab3 = st.tabs(["عرض المدرسين والحسابات المالية", "➕ إضافة مدرس جديد", "✏️ تعديل / حذف مدرس"])

    # ---------------- عرض المدرسين والحسابات المالية ----------------
    with tab1:
        teachers = st.session_state.teachers
        if not teachers:
            st.info("لا يوجد مدرسين مسجلين")
        else:
            rows = []
            for t in teachers:
                weekly, monthly_classes, monthly_due = teacher_financials(t)
                rows.append(
                    {
                        "الكود": t["الكود"],
                        "الاسم": t["الاسم"],
                        "الرقم القومي": t["الرقم القومي"],
                        "رقم التليفون": t["رقم التليفون"],
                        "المؤهل الدراسي": t["المؤهل الدراسي"],
                        "سنة الحصول عليه": t["سنة الحصول على المؤهل"],
                        "الحصص الأسبوعية": weekly,
                        "الحصص الشهرية": monthly_classes,
                        "ثمن الحصة": t["ثمن الحصة الواحدة"],
                        "المستحقات الشهرية": monthly_due,
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            total_due = sum(r["المستحقات الشهرية"] for r in rows)
            st.metric("إجمالي مستحقات المدرسين هذا الشهر", f"{total_due:,.0f} جنيه")

    # ---------------- إضافة مدرس جديد ----------------
    with tab2:
        st.markdown("### إضافة مدرس جديد")
        with st.form("add_teacher_form", clear_on_submit=True):
            name = st.text_input("اسم المدرس")
            national_id = st.text_input("الرقم القومي")
            phone = st.text_input("رقم التليفون")
            qualification = st.text_input("المؤهل الدراسي")
            qualification_year = st.number_input(
                "سنة الحصول على المؤهل", min_value=1950, max_value=2100, value=2015, step=1
            )
            weekly_classes = st.number_input("عدد الحصص الأسبوعية", min_value=0, value=10, step=1)
            price_per_class = st.number_input("ثمن الحصة الواحدة (جنيه)", min_value=0.0, value=50.0, step=5.0)
            submitted = st.form_submit_button("➕ إضافة المدرس")
            if submitted:
                if not name.strip():
                    st.error("يجب إدخال اسم المدرس")
                else:
                    new_code = next_code("TCH", st.session_state.teachers)
                    st.session_state.teachers.append(
                        {
                            "الكود": new_code,
                            "الاسم": name.strip(),
                            "الرقم القومي": national_id.strip(),
                            "رقم التليفون": phone.strip(),
                            "المؤهل الدراسي": qualification.strip(),
                            "سنة الحصول على المؤهل": qualification_year,
                            "عدد الحصص الأسبوعية": weekly_classes,
                            "ثمن الحصة الواحدة": price_per_class,
                        }
                    )
                    st.success(f"تم إضافة المدرس بنجاح — الكود: {new_code}")
                    st.rerun()

    # ---------------- تعديل / حذف مدرس ----------------
    with tab3:
        teachers = st.session_state.teachers
        if not teachers:
            st.info("لا يوجد مدرسين لتعديلهم")
        else:
            names = {t["الكود"]: f'{t["الاسم"]} ({t["الكود"]})' for t in teachers}
            selected_code = st.selectbox(
                "اختر مدرساً للتعديل أو الحذف",
                options=list(names.keys()),
                format_func=lambda c: names[c],
                key="edit_teacher_select",
            )
            teacher = get_teacher(selected_code)
            if teacher:
                with st.form("edit_teacher_form"):
                    name = st.text_input("اسم المدرس", value=teacher["الاسم"])
                    national_id = st.text_input("الرقم القومي", value=teacher["الرقم القومي"])
                    phone = st.text_input("رقم التليفون", value=teacher["رقم التليفون"])
                    qualification = st.text_input("المؤهل الدراسي", value=teacher["المؤهل الدراسي"])
                    qualification_year = st.number_input(
                        "سنة الحصول على المؤهل",
                        min_value=1950,
                        max_value=2100,
                        value=int(teacher["سنة الحصول على المؤهل"]),
                        step=1,
                    )
                    weekly_classes = st.number_input(
                        "عدد الحصص الأسبوعية", min_value=0, value=int(teacher["عدد الحصص الأسبوعية"]), step=1
                    )
                    price_per_class = st.number_input(
                        "ثمن الحصة الواحدة (جنيه)",
                        min_value=0.0,
                        value=float(teacher["ثمن الحصة الواحدة"]),
                        step=5.0,
                    )
                    save_btn = st.form_submit_button("💾 حفظ التعديلات")
                    if save_btn:
                        teacher["الاسم"] = name.strip()
                        teacher["الرقم القومي"] = national_id.strip()
                        teacher["رقم التليفون"] = phone.strip()
                        teacher["المؤهل الدراسي"] = qualification.strip()
                        teacher["سنة الحصول على المؤهل"] = qualification_year
                        teacher["عدد الحصص الأسبوعية"] = weekly_classes
                        teacher["ثمن الحصة الواحدة"] = price_per_class
                        st.success("تم حفظ التعديلات بنجاح")
                        st.rerun()

                st.markdown("---")
                if st.button("🗑️ حذف هذا المدرس نهائياً", type="primary"):
                    st.session_state.teachers = [
                        t for t in st.session_state.teachers if t["الكود"] != selected_code
                    ]
                    st.session_state.teacher_accounts = {
                        u: acc for u, acc in st.session_state.teacher_accounts.items() if acc["الكود"] != selected_code
                    }
                    st.success("تم حذف المدرس وحسابه المرتبط به")
                    st.rerun()


# =====================================================================================
# 11) نموذج تسجيل الحضور (يُستخدم من صفحة المدير وصفحة المعلم معاً)
# =====================================================================================
def record_attendance_form():
    students = st.session_state.students
    if not students:
        st.info("لا يوجد طلاب لتسجيل حضورهم")
        return

    names = {s["الكود"]: f'{s["الاسم"]} ({s["الكود"]})' for s in students}
    with st.form("attendance_form", clear_on_submit=True):
        student_code = st.selectbox("اختر الطالب", options=list(names.keys()), format_func=lambda c: names[c])
        attendance_date = st.date_input("التاريخ", value=date.today())
        status = st.radio("الحالة", ["حاضر", "غائب", "متأخر"], horizontal=True)
        penalty = st.text_input("الجزاء (اختياري)")
        note = st.text_area("ملاحظات (اختياري)")
        submitted = st.form_submit_button("✅ تسجيل")
        if submitted:
            st.session_state.attendance.append(
                {
                    "كود الطالب": student_code,
                    "التاريخ": str(attendance_date),
                    "الحالة": status,
                    "جزاء": penalty.strip(),
                    "ملاحظات": note.strip(),
                }
            )
            st.success("تم تسجيل الحضور بنجاح")
            st.rerun()


# =====================================================================================
# 12) صفحة الحضور والغياب (للمدير)
# =====================================================================================
def page_attendance_admin():
    st.title("🗓️ الحضور والغياب")
    tab1, tab2 = st.tabs(["تسجيل حضور جديد", "📖 سجل الحضور الكامل"])

    with tab1:
        record_attendance_form()

    with tab2:
        attendance = st.session_state.attendance
        if not attendance:
            st.info("لا يوجد سجلات حضور بعد")
        else:
            df = pd.DataFrame(attendance)
            students_map = {s["الكود"]: s["الاسم"] for s in st.session_state.students}
            df["اسم الطالب"] = df["كود الطالب"].map(students_map)
            df = df[["التاريخ", "كود الطالب", "اسم الطالب", "الحالة", "جزاء", "ملاحظات"]]
            df = df.sort_values("التاريخ", ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)


# =====================================================================================
# 13) صفحة الحضور والغياب (للمعلم فقط)
# =====================================================================================
def page_teacher_attendance():
    st.title("📋 تسجيل الحضور والغياب اليومي")
    record_attendance_form()

    st.markdown("---")
    st.markdown("### آخر السجلات المضافة")
    attendance = st.session_state.attendance
    if attendance:
        df = pd.DataFrame(attendance[-10:])
        students_map = {s["الكود"]: s["الاسم"] for s in st.session_state.students}
        df["اسم الطالب"] = df["كود الطالب"].map(students_map)
        df = df[["التاريخ", "كود الطالب", "اسم الطالب", "الحالة", "جزاء", "ملاحظات"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("لا يوجد سجلات حضور بعد")


# =====================================================================================
# 14) إدارة حسابات المعلمين (للمدير فقط)
# =====================================================================================
def page_teacher_accounts():
    st.title("🔐 إدارة حسابات المعلمين")

    teachers = st.session_state.teachers
    accounts = st.session_state.teacher_accounts

    st.markdown("### الحسابات الحالية")
    if accounts:
        rows = []
        for username, acc in accounts.items():
            teacher = get_teacher(acc["الكود"])
            rows.append(
                {
                    "اسم المستخدم": username,
                    "اسم المدرس": teacher["الاسم"] if teacher else "—",
                    "كود المدرس": acc["الكود"],
                    "الحالة": "مفعل ✅" if acc["مفعل"] else "معطل 🚫",
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("### تفعيل / تعطيل حساب")
        selected_username = st.selectbox("اختر حساباً", options=list(accounts.keys()))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚫 تعطيل الحساب", use_container_width=True):
                accounts[selected_username]["مفعل"] = False
                st.success("تم تعطيل الحساب")
                st.rerun()
        with col2:
            if st.button("✅ إعادة تفعيل الحساب", use_container_width=True):
                accounts[selected_username]["مفعل"] = True
                st.success("تم تفعيل الحساب")
                st.rerun()
    else:
        st.info("لا يوجد حسابات معلمين بعد")

    st.markdown("---")
    st.markdown("### إنشاء حساب جديد لمعلم")

    teachers_without_account = [
        t for t in teachers if t["الكود"] not in [a["الكود"] for a in accounts.values()]
    ]
    if not teachers_without_account:
        st.info("جميع المدرسين لديهم حسابات بالفعل")
    else:
        names = {t["الكود"]: f'{t["الاسم"]} ({t["الكود"]})' for t in teachers_without_account}
        with st.form("add_teacher_account_form"):
            teacher_code = st.selectbox(
                "اختر المدرس", options=list(names.keys()), format_func=lambda c: names[c]
            )
            auto_generate = st.checkbox("توليد اسم مستخدم وكلمة مرور تلقائياً", value=True)
            manual_username = ""
            manual_password = ""
            if not auto_generate:
                manual_username = st.text_input("اسم المستخدم")
                manual_password = st.text_input("كلمة المرور")
            submitted = st.form_submit_button("🔑 إنشاء الحساب")

            if submitted:
                if auto_generate:
                    username = teacher_code.lower().replace("-", "")
                    password = generate_password()
                else:
                    username = manual_username.strip()
                    password = manual_password.strip()

                if not username:
                    st.error("يجب إدخال اسم مستخدم")
                elif username in accounts:
                    st.error("اسم المستخدم مستخدم بالفعل")
                elif not password:
                    st.error("يجب إدخال كلمة مرور")
                else:
                    accounts[username] = {
                        "password": password,
                        "الكود": teacher_code,
                        "مفعل": True,
                    }
                    st.success(f"تم إنشاء الحساب بنجاح — اسم المستخدم: {username} | كلمة المرور: {password}")
                    st.rerun()


# =====================================================================================
# 15) الدالة الرئيسية وربط كل الصفحات
# =====================================================================================
def main():
    st.markdown(RTL_CSS, unsafe_allow_html=True)
    init_state()

    if not st.session_state.logged_in:
        login_page()
        return

    page = sidebar_menu()

    if st.session_state.role == "admin":
        if page == "لوحة التحكم":
            page_dashboard()
        elif page == "بيانات مدير المدرسة":
            page_school_info()
        elif page == "بيانات الطلاب":
            page_students()
        elif page == "بيانات المدرسين":
            page_teachers()
        elif page == "الحضور والغياب":
            page_attendance_admin()
        elif page == "حسابات المعلمين":
            page_teacher_accounts()
    else:
        page_teacher_attendance()


if __name__ == "__main__":
    main()
