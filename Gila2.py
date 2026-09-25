import streamlit as st
import pandas as pd
from datetime import date, datetime
import uuid

# ================== 1. إعدادات الصفحة والتصميم RTL الحقيقي ==================
st.set_page_config(
    page_title="مدرسة التوكل جيلا - نظام الإدارة",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS حقيقي RTL يعالج Sidebar والمدخلات و Streamlit الحديث
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif!important;
    }
   .stApp {
        direction: rtl;
        text-align: right;
    }
    /* معالجة القائمة الجانبية */
    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stSidebar"].stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"].stButton {
        text-align: right!important;
        direction: rtl!important;
    }
    /* معالجة حقول الإدخال */
   .stTextInput input,.stNumberInput input,.stSelectbox div[data-baseweb="select"] {
        direction: rtl!important;
        text-align: right!important;
    }
    /* عناوين */
    h1, h2, h3, h4, h5, h6, p, label,.stMetric {
        direction: rtl!important;
        text-align: right!important;
    }
    /* كروت */
   .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-right: 6px solid #1a73e8;
        margin-bottom: 20px;
    }
   .login-card {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        max-width: 450px;
        margin: 80px auto;
        text-align: center;
        border-top: 6px solid #1a73e8;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. البيانات الافتراضية ومنع الشاشات الفارغة ==================
def init_session_state():
    if 'initialized' not in st.session_state:
        # المستخدمين والصلاحيات
        st.session_state.users = {
            "admin": {"password": "admin123", "role": "admin", "active": True, "teacher_code": None},
        }
        # بيانات مدير المدرسة الافتراضية
        st.session_state.director = {
            "name": "أ. محمد أحمد التوكل",
            "national_id": "27501011201234",
            "phone": "01012345678",
            "code": "DIR-001",
            "qualification": "بكالوريوس إدارة تربوية",
            "qual_year": "2005"
        }
        # بيانات المدرسين الافتراضية
        st.session_state.teachers = [
            {
                "id": str(uuid.uuid4()),
                "name": "أ. أحمد محمود علي",
                "national_id": "28511251234567",
                "phone": "01123456789",
                "code": "TCH-101",
                "qualification": "ليسانس لغة عربية",
                "qual_year": "2010",
                "weekly_sessions": 18,
                "session_price": 60
            },
            {
                "id": str(uuid.uuid4()),
                "name": "م. سارة إبراهيم",
                "national_id": "29005051234567",
                "phone": "01287654321",
                "code": "TCH-102",
                "qualification": "بكالوريوس هندسة صناعية",
                "qual_year": "2015",
                "weekly_sessions": 24,
                "session_price": 75
            }
        ]
        # بيانات الطلاب الافتراضية
        st.session_state.students = [
            {
                "id": str(uuid.uuid4()),
                "name": "عمر خالد محمد",
                "code": "STU-2024-001",
                "national_id": "30801011234567",
                "phones": ["01098765432", "01112345678"],
                "parent_phones": ["01000011122"],
                "father_job": "مهندس",
                "class_name": "الصف الأول - تدريب مزدوج"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "يوسف أحمد سمير",
                "code": "STU-2024-002",
                "national_id": "30805051234568",
                "phones": ["01234567890"],
                "parent_phones": ["01000011133", "01100022244"],
                "father_job": "تاجر",
                "class_name": "الصف الثاني - نانو تكنولوجي"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "مريم عبد الله",
                "code": "STU-2024-003",
                "national_id": "30901011234569",
                "phones": ["01011112222"],
                "parent_phones": ["01022223333"],
                "father_job": "موظف",
                "class_name": "الصف الأول - تدريب مزدوج"
            }
        ]
        # الحضور والغياب - بيانات تجريبية
        today_str = str(date.today())
        st.session_state.attendance = {} # {date: {student_id: {status, penalty, notes}}}
        for student in st.session_state.students:
            if today_str not in st.session_state.attendance:
                st.session_state.attendance[today_str] = {}
            # بيانات تجريبية متنوعة
            st.session_state.attendance[today_str][student['id']] = {
                "status": "حاضر",
                "penalty": "",
                "notes": ""
            }

        # حساب معلم افتراضي للتجربة
        st.session_state.users["teacher1"] = {"password": "123456", "role": "teacher", "active": True, "teacher_code": "TCH-101"}

        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.current_role = None
        st.session_state.initialized = True

init_session_state()

# ================== 3. دوال مساعدة ==================
def calculate_attendance_summary(student_id):
    total_present = 0
    total_absent = 0
    total_late = 0
    penalties = []
    notes_list = []
    for day, records in st.session_state.attendance.items():
        if student_id in records:
            rec = records[student_id]
            if rec['status'] == 'حاضر':
                total_present += 1
            elif rec['status'] == 'غائب':
                total_absent += 1
            elif rec['status'] == 'متأخر':
                total_late += 1
            if rec['penalty']:
                penalties.append(f"{day}: {rec['penalty']}")
            if rec['notes']:
                notes_list.append(f"{day}: {rec['notes']}")
    return total_present, total_absent, total_late, penalties, notes_list

def get_teacher_by_code(code):
    for t in st.session_state.teachers:
        if t['code'] == code:
            return t
    return None

# ================== 4. شاشة تسجيل الدخول المؤمنة ==================
def login_page():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h1>🏫 مدرسة التوكل جيلا</h1><h3>مدرسة نانوي صناعي - تدريب مزدوج</h3><p>نظام إدارة المدرسة المتكامل</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("اسم المستخدم", placeholder="ادخل اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password", placeholder="ادخل كلمة المرور")
        submitted = st.form_submit_button("تسجيل الدخول", use_container_width=True, type="primary")

        if submitted:
            if username in st.session_state.users:
                user = st.session_state.users[username]
                if not user['active']:
                    st.error("هذا الحساب معطل، تواصل مع المدير")
                elif user['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.current_role = user['role']
                    st.success("تم تسجيل الدخول بنجاح")
                    st.rerun()
                else:
                    st.error("كلمة المرور غير صحيحة")
            else:
                st.error("اسم المستخدم غير موجود")

    st.info("الحساب الافتراضي للمدير: admin / admin123 | حساب معلم تجريبي: teacher1 / 123456")
    st.markdown('</div>', unsafe_allow_html=True)

# ================== 5. لوحة التحكم الرئيسية ==================
def main_app():
    role = st.session_state.current_role

    with st.sidebar:
        st.markdown(f"### مرحباً، {st.session_state.current_user}")
        st.markdown(f"**الصلاحية:** {'مدير النظام' if role == 'admin' else 'معلم'}")
        st.divider()

        if role == 'admin':
            menu = st.radio("القائمة الرئيسية",
                ["الرئيسية", "بيانات مدير المدرسة", "إدارة الطلاب", "إدارة المدرسين", "الحضور والغياب", "الحسابات المالية", "إدارة حسابات المعلمين"],
                label_visibility="collapsed")
        else:
            menu = st.radio("القائمة الرئيسية", ["الحضور والغياب"], label_visibility="collapsed")

        st.divider()
        if st.button("تسجيل خروج", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.current_role = None
            st.rerun()

    # ----- الصفحات -----
    if menu == "الرئيسية":
        st.title("لوحة تحكم مدرسة التوكل جيلا")
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الطلاب", len(st.session_state.students))
        c2.metric("إجمالي المدرسين", len(st.session_state.teachers))
        c3.metric("أيام تسجيل الحضور", len(st.session_state.attendance))
        st.markdown("---")
        st.subheader("نظرة سريعة على الطلاب")
        df = pd.DataFrame(st.session_state.students)[["name", "code", "class_name"]]
        df.columns = ["اسم الطالب", "الكود", "الفصل"]
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif menu == "بيانات مدير المدرسة":
        st.title("بيانات مدير المدرسة")
        d = st.session_state.director
        with st.form("director_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("الاسم", value=d['name'])
            national_id = col2.text_input("الرقم القومي", value=d['national_id'])
            phone = col1.text_input("رقم التليفون", value=d['phone'])
            code = col2.text_input("الكود", value=d['code'])
            qualification = col1.text_input("المؤهل الدراسي", value=d['qualification'])
            qual_year = col2.text_input("سنة الحصول عليه", value=d['qual_year'])
            if st.form_submit_button("حفظ التعديلات", type="primary"):
                st.session_state.director.update({
                    "name": name, "national_id": national_id, "phone": phone,
                    "code": code, "qualification": qualification, "qual_year": qual_year
                })
                st.success("تم حفظ بيانات المدير")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"**الاسم:** {d['name']} | **الكود:** {d['code']} | **المؤهل:** {d['qualification']} {d['qual_year']}")
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "إدارة الطلاب":
        st.title("إدارة الطلاب")
        tab1, tab2 = st.tabs(["قائمة الطلاب والملف الشخصي", "إضافة طالب جديد"])

        with tab1:
            if not st.session_state.students:
                st.warning("لا يوجد طلاب")
            else:
                student_options = {f"{s['name']} - {s['code']}": s['id'] for s in st.session_state.students}
                selected_label = st.selectbox("اختر الطالب لعرض ملفه الشخصي", list(student_options.keys()))
                selected_id = student_options[selected_label]
                student = next(s for s in st.session_state.students if s['id'] == selected_id)

                present, absent, late, penalties, notes_list = calculate_attendance_summary(selected_id)

                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader(f"الملف الشخصي للطالب: {student['name']}")
                c1, c2 = st.columns(2)
                c1.write(f"**الكود:** {student['code']}")
                c1.write(f"**الرقم القومي:** {student['national_id']}")
                c1.write(f"**الفصل:** {student['class_name']}")
                c1.write(f"**مهنة الأب:** {student['father_job']}")
                c2.write(f"**أرقام الطالب:** {', '.join(student['phones'])}")
                c2.write(f"**أرقام ولي الأمر:** {', '.join(student['parent_phones'])}")

                st.divider()
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("أيام الحضور", present)
                m2.metric("أيام الغياب", absent)
                m3.metric("مرات التأخر", late)
                m4.metric("إجمالي الجزاءات", len(penalties))

                if penalties:
                    st.warning("الجزاءات: " + " | ".join(penalties))
                if notes_list:
                    st.info("الملاحظات: " + " | ".join(notes_list))
                st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            with st.form("add_student"):
                st.subheader("بيانات الطالب الجديد")
                c1, c2 = st.columns(2)
                name = c1.text_input("الاسم *")
                code = c2.text_input("الكود *")
                national_id = c1.text_input("الرقم القومي *")
                father_job = c2.text_input("مهنة الأب")
                class_name = c1.text_input("الفصل / التخصص", value="الصف الأول - تدريب مزدوج")
                phones_raw = c2.text_area("أرقام تليفون الطالب (افصل بفاصلة,)", placeholder="010..., 011...")
                parent_phones_raw = st.text_area("أرقام تليفون ولي الأمر (افصل بفاصلة,)")
                if st.form_submit_button("إضافة الطالب", type="primary"):
                    if name and code and national_id:
                        new_student = {
                            "id": str(uuid.uuid4()),
                            "name": name,
                            "code": code,
                            "national_id": national_id,
                            "phones": [p.strip() for p in phones_raw.split(",") if p.strip()],
                            "parent_phones": [p.strip() for p in parent_phones_raw.split(",") if p.strip()],
                            "father_job": father_job,
                            "class_name": class_name
                        }
                        st.session_state.students.append(new_student)
                        st.success(f"تمت إضافة الطالب {name}")
                    else:
                        st.error("الحقول المميزة بـ * مطلوبة")

    elif menu == "إدارة المدرسين":
        st.title("إدارة المدرسين")
        tab1, tab2 = st.tabs(["قائمة المدرسين", "إضافة مدرس جديد"])
        with tab1:
            df = pd.DataFrame(st.session_state.teachers)
            if not df.empty:
                df_display = df[["name", "code", "phone", "qualification", "weekly_sessions", "session_price"]].copy()
                df_display.columns = ["الاسم", "الكود", "التليفون", "المؤهل", "حصص/أسبوع", "سعر الحصة"]
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info("لا يوجد مدرسين")

        with tab2:
            with st.form("add_teacher"):
                c1, c2 = st.columns(2)
                name = c1.text_input("الاسم *")
                code = c2.text_input("الكود *")
                national_id = c1.text_input("الرقم القومي *")
                phone = c2.text_input("رقم التليفون *")
                qualification = c1.text_input("المؤهل الدراسي")
                qual_year = c2.text_input("سنة المؤهل")
                weekly = c1.number_input("عدد الحصص الأسبوعية", min_value=0, value=12)
                price = c2.number_input("ثمن الحصة الواحدة (جنيه)", min_value=0, value=50)
                if st.form_submit_button("إضافة المدرس", type="primary"):
                    if name and code and national_id and phone:
                        st.session_state.teachers.append({
                            "id": str(uuid.uuid4()),
                            "name": name, "national_id": national_id, "phone": phone,
                            "code": code, "qualification": qualification, "qual_year": qual_year,
                            "weekly_sessions": weekly, "session_price": price
                        })
                        st.success(f"تمت إضافة المدرس {name}")
                    else:
                        st.error("أكمل الحقول المطلوبة")

    elif menu == "الحضور والغياب":
        st.title("نظام الحضور والغياب اليومي والجزاءات")
        selected_date = st.date_input("اختر تاريخ اليوم", value=date.today())
        date_str = str(selected_date)

        if date_str not in st.session_state.attendance:
            st.session_state.attendance[date_str] = {}

        st.subheader(f"تسجيل حضور يوم: {date_str}")

        # جدول تسجيل سريع
        for student in st.session_state.students:
            sid = student['id']
            existing = st.session_state.attendance[date_str].get(sid, {"status": "حاضر", "penalty": "", "notes": ""})

            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 2])
                c1.write(f"**{student['name']}** ({student['code']})")
                status = c2.selectbox(f"الحالة - {sid}", ["حاضر", "غائب", "متأخر"], index=["حاضر", "غائب", "متأخر"].index(existing['status']), key=f"st_{date_str}_{sid}", label_visibility="collapsed")
                penalty = c3.text_input(f"الجزاء - {sid}", value=existing['penalty'], placeholder="جزاء", key=f"pe_{date_str}_{sid}", label_visibility="collapsed")
                notes = c4.text_input(f"ملاحظات - {sid}", value=existing['notes'], placeholder="ملاحظات", key=f"no_{date_str}_{sid}", label_visibility="collapsed")

                st.session_state.attendance[date_str][sid] = {"status": status, "penalty": penalty, "notes": notes}

        st.success(f"تم حفظ حضور يوم {date_str} تلقائياً في الذاكرة المؤقتة")

        st.divider()
        st.subheader("التقرير التراكمي")
        summary_data = []
        for s in st.session_state.students:
            p, a, l, pen, _ = calculate_attendance_summary(s['id'])
            summary_data.append({"الطالب": s['name'], "الكود": s['code'], "حضور": p, "غياب": a, "تأخر": l, "جزاءات": len(pen)})
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

    elif menu == "الحسابات المالية":
        st.title("الحسابات المالية التلقائية للمدرسين")
        st.info("المعادلة: المستحقات الشهرية = إجمالي الحصص في الشهر × ثمن الحصة | الشهر = 4 أسابيع")

        financial_data = []
        for t in st.session_state.teachers:
            weekly = t['weekly_sessions']
            monthly_sessions = weekly * 4
            monthly_due = monthly_sessions * t['session_price']
            weekly_due = weekly * t['session_price']
            financial_data.append({
                "اسم المدرس": t['name'],
                "الكود": t['code'],
                "حصص/أسبوع": weekly,
                "حصص/شهر": monthly_sessions,
                "سعر الحصة": t['session_price'],
                "مستحق أسبوعي": weekly_due,
                "المستحقات الشهرية": monthly_due
            })
        st.dataframe(pd.DataFrame(financial_data), use_container_width=True, hide_index=True)

        # كروت لكل مدرس
        for row in financial_data:
            st.markdown(f"""<div class="card">
                <h4>{row['اسم المدرس']} - {row['الكود']}</h4>
                <p>إجمالي حصص الأسبوع: {row['حصص/أسبوع']} | إجمالي حصص الشهر: {row['حصص/شهر']} | سعر الحصة: {row['سعر الحصة']} جنيه</p>
                <h3 style="color:#1a73e8;">المستحق الشهري: {row['المستحقات الشهرية']} جنيه</h3>
            </div>""", unsafe_allow_html=True)

    elif menu == "إدارة حسابات المعلمين":
        st.title("إدارة حسابات المعلمين - لوحة المدير")

        tab1, tab2 = st.tabs(["إنشاء حساب معلم", "التحكم في الحسابات"])
        with tab1:
            teacher_codes = [t['code'] for t in st.session_state.teachers]
            with st.form("create_teacher_account"):
                st.subheader("توليد حساب جديد للمعلم")
                selected_code = st.selectbox("اختر كود المدرس", teacher_codes)
                username = st.text_input("اسم المستخدم الجديد للمعلم")
                password = st.text_input("كلمة المرور", value="123456")
                if st.form_submit_button("إنشاء الحساب", type="primary"):
                    if username in st.session_state.users:
                        st.error("اسم المستخدم موجود بالفعل")
                    elif username and password and selected_code:
                        st.session_state.users[username] = {"password": password, "role": "teacher", "active": True, "teacher_code": selected_code}
                        st.success(f"تم إنشاء حساب للمعلم {selected_code} -> المستخدم: {username}")
                    else:
                        st.error("أكمل البيانات")

        with tab2:
            users_df = []
            for uname, udata in st.session_state.users.items():
                if udata['role'] == 'teacher':
                    users_df.append({"اسم المستخدم": uname, "كود المدرس": udata['teacher_code'], "الحالة": "نشط" if udata['active'] else "محظور"})
            st.dataframe(pd.DataFrame(users_df), use_container_width=True, hide_index=True)

            st.subheader("تعطيل / تفعيل حساب")
            teacher_usernames = [u for u, d in st.session_state.users.items() if d['role'] == 'teacher']
            if teacher_usernames:
                selected_user = st.selectbox("اختر حساب المعلم", teacher_usernames)
                col1, col2 = st.columns(2)
                if col1.button("حظر الحساب", use_container_width=True):
                    st.session_state.users[selected_user]['active'] = False
                    st.warning(f"تم حظر حساب {selected_user}")
                    st.rerun()
                if col2.button("إعادة تفعيل الحساب", type="primary", use_container_width=True):
                    st.session_state.users[selected_user]['active'] = True
                    st.success(f"تم تفعيل حساب {selected_user}")
                    st.rerun()

# ================== 6. نقطة التشغيل الرئيسية ==================
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
