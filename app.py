import base64
from datetime import datetime
import io
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# הגדרת עיצוב עמוד
st.set_page_config(
    page_title="מבחן בקיאות באבטחת מידע", page_icon="🔒", layout="centered"
)

# הגדרת השאלות והתשובות הנכונות לפי המסמך
QUESTIONS = [
    {
        "id": 1,
        "title": "העברת מידע חסוי/חסוי ביותר",
        "options": [
            (
                "ניתן ומומלץ להעביר מידע חסוי/חסוי ביותר למחשב האישי של העובד על"
                " מנת להמשיך ולעבוד בבית."
            ),
            (
                "חל איסור להעברת ולשמירת מידע חסוי/חסוי ביותר על המחשב האישי של"
                " העובד."
            ),
            (
                "רק במקרה בו אישר המנהל הישיר של העובד את הפעולה ניתן להעביר מידע"
                " חסוי/חסוי ביותר למחשב האישי של העובד."
            ),
            (
                "יש להפעיל שיקול דעת בהעברת מידע חסוי/חסוי ביותר למחשב האישי של"
                " העובד. במידה והעובד מצא לנכון כי יש צורך לבצע את הפעולה, ניתן"
                " לבצעה בהתאם לנהלי אבטחת המידע של משרד הבריאות."
            ),
        ],
        "correct": 1,  # תשובה שנייה
    },
    {
        "id": 2,
        "title": "הוצאת מידע מבית החולים",
        "options": [
            (
                "ניתן לשלוח מידע חסוי ביותר באמצעות דואר אלקטרוני במקרים בהם יש צורך"
                " קליני בפעולה."
            ),
            (
                "ניתן לשלוח מידע חסוי ביותר באמצעות דואר אלקטרוני רק במקרים שאושרו"
                ' ע"י המנהל הישיר.'
            ),
            "חל איסור לשלוח מידע חסוי ביותר באמצעות דואר אלקטרוני.",
            (
                "במקרים של שליחת מידע חסוי ביותר באמצעות דואר אלקטרוני יש לעשות"
                " שימוש בנוהל שליחת דואר אלקטרוני של משרד הבריאות- לשלוח מייל מקדים,"
                " לשלוח את המידע לאותה כתובת ובסיום השליחה לוודא כי הדואר האלקטרוני"
                " אכן הגיע ליעדו."
            ),
        ],
        "correct": 2,
    },
    {
        "id": 3,
        "title": "התקנת תוכנות",
        "options": [
            (
                "כל תוכנה תותקן על המחשב ע\"י מחלקת מידע ומחשוב בלבד ולאחר שאושרה"
                " בהיבטי מחשוב ואבטחת מידע."
            ),
            "ניתן להתקין תוכנות רק במקרה של צורך קליני.",
            "ניתן להתקין תוכנות רק לאחר קבלת אישור מהמנהל הישיר.",
            "אף תשובה איננה נכונה.",
        ],
        "correct": 0,
    },
    {
        "id": 4,
        "title": "שם משתמש וסיסמא",
        "options": [
            (
                "שם המשתמש הוא אישי ונועד לשימושו של המשתמש בלבד ולצורך ביצוע"
                " עבודתו."
            ),
            (
                "ניתן להעביר את הסיסמה ושם המשתמש, רק במקרים בהם מכירים את העובד"
                " באופן אישי."
            ),
            (
                "מומלץ לרשום את שם המשתמש והסיסמה באזור העבודה בכדי למנוע העברתו"
                " לעובדים אחרים."
            ),
            "אף תשובה איננה נכונה.",
        ],
        "correct": 0,
    },
    {
        "id": 5,
        "title": "גריסת נייר",
        "options": [
            "יש לגרוס כל נייר משרדי שאין בו עוד צורך.",
            "רק ניירת המכילה מידע מסווג תיגרס.",
            (
                "יש לפנות לממונה על אבטחת המידע בבית החולים בכל מקרה שבו יש צורך"
                " לגרוס ניירת משרדית."
            ),
            "גריסת נייר נתונה לשיקול דעתו האישי של העובד.",
        ],
        "correct": 0,
    },
    {
        "id": 6,
        "title": "שימוש נאות בציוד המשרד",
        "options": [
            "ניתן להפסיק את פעולת המערכות לאבטחת מידע כגון אנטי וירוס.",
            (
                "ניתן להפסיק את פעולת המערכות לאבטחת מידע כגון אנטי וירוס במקרה של"
                " צורך קליני."
            ),
            (
                "ניתן להפסיק את פעולת המערכות לאבטחת מידע כגון אנטי וירוס במקרה של"
                " צורך קליני ורק לאחר קבלת אישורו המנהל הישיר."
            ),
            "חל איסור להפסיק את פעולת המערכות לאבטחת מידע כגון אנטי וירוס.",
        ],
        "correct": 3,
    },
    {
        "id": 7,
        "title": "אירועי אבטחת מידע",
        "options": [
            (
                "אין צורך לדווח על אירוע אבטחת מידע, אך יש חובה לנסות למזער את"
                " הנזקים באופן מידי"
            ),
            (
                "יש לדווח לממונה הישיר ולממונה על אבטחת מידע בבית החולים אודות כל"
                " אירוע ו/או חשד לאירוע אבטחת מידע."
            ),
            (
                "יש להפעיל שיקול דעת לפני דיווח על אירוע ו/או חשד לאירוע אבטחת"
                " מידע למנהל הישיר ולממונה על אבטחת מידע בבית החולים."
            ),
            "אף תשובה אינה נכונה.",
        ],
        "correct": 1,
    },
    {
        "id": 8,
        "title": 'איזה מהמשפטים הבאים הוא דוגמא למתקפת "פישינג"?',
        "options": [
            (
                "שליחת אימייל המכיל קישור זדוני המוסווה כדי להיראות כמו אימייל"
                " ממישהו שהאדם מכיר."
            ),
            (
                "יצירת אתר מזויף הנראה כמעט זהה לאתר האמיתי על מנת להערים על"
                " משתמשים להזין את פרטי ההתחברות שלהם."
            ),
            (
                "שליחת הודעת טקסט למישהו המכילה קישור זדוני שמוסווה כדי להיראות"
                " כמו הודעה אמיתית (בנק, דואר וכו')."
            ),
            "כל התשובות נכונות.",
        ],
        "correct": 3,
    },
    {
        "id": 9,
        "title": "מהו מתקפת כופרה",
        "options": [
            (
                "תוכנה המדביקה רשתות מחשבים והתקנים ניידים, כדי להחזיק את"
                " הנתונים שלך כבני ערובה עד העברת התשלום לתוקפים ."
            ),
            (
                "גניבת ציוד מחשבים שהפושעים לוקחים, ומחזירים רק כאשר תשלם להם."
            ),
            (
                "תוכנה המשמשת להגנה על המחשב או המכשיר הנייד שלך מפני וירוסים"
                " מזיקים."
            ),
            "סוג של מטבע קריפטוגרפי.",
        ],
        "correct": 0,
    },
    {
        "id": 10,
        "title": (
            "אילו מהמשפטים מתאר בצורה הטובה ביותר כיצד פושעים מתחילים"
            " בהתקפות של תוכנות כופר?"
        ),
        "options": [
            (
                "שליחת אימייל הונאה עם קישורים או קבצים מצורפים המסכנים את"
                " הנתונים והרשת שלך."
            ),
            (
                "כניסה לשרתי הארגון דרך נקודות תורפה והתקנת תוכנות זדוניות."
            ),
            (
                "שימוש באתרי אינטרנט נגועים שמורידים אוטומטית תוכנה זדונית למחשב"
                " או למכשיר הנייד שלך."
            ),
            "כל התשובות נכונות",
        ],
        "correct": 3,
    },
]

# אתחול מצב באפליקציה
if "step" not in st.session_state:
  st.session_state.step = 0  # 0: פרטים אישיים, 1-10: שאלות, 11: תוצאה
if "user_data" not in st.session_state:
  st.session_state.user_data = {}
if "answers" not in st.session_state:
  st.session_state.answers = {}

# כותרת ראשית
st.title("🔒 מבחן בקיאות - אבטחת מידע")
st.markdown("---")

# שלב 0: קליטת פרטים אישיים
if st.session_state.step == 0:
  st.subheader("נא להזין את פרטיך האישיים לפני תחילת המבחן:")

  with st.form("user_form"):
    first_name_he = st.text_input("שם פרטי (עברית)")
    last_name_he = st.text_input("שם משפחה (עברית)")
    first_name_en = st.text_input("שם פרטי (אנגלית)")
    last_name_en = st.text_input("שם משפחה (אנגלית)")

    submitted = st.form_submit_button("התחל מבחן 🚀")
    if submitted:
      if (
          not first_name_he
          or not last_name_he
          or not first_name_en
          or not last_name_en
      ):
        st.error("נא למלא את כל שדות החובה!")
      else:
        st.session_state.user_data = {
            "first_name_he": first_name_he,
            "last_name_he": last_name_he,
            "first_name_en": first_name_en,
            "last_name_en": last_name_en,
        }
        st.session_state.step = 1
        st.rerun()

# שלבי השאלות (1 עד 10)
elif 1 <= st.session_state.step <= len(QUESTIONS):
  q_index = st.session_state.step - 1
  q = QUESTIONS[q_index]

  st.markdown(f"### שאלה {q['id']} מתוך {len(QUESTIONS)}")
  st.write(f"**{q['title']}**")

  # הצגת אפשרויות בחירה
  current_answer = st.session_state.answers.get(q_index, None)
  selected_option = st.radio(
      "בחר את התשובה הנכונה:",
      options=range(len(q["options"])),
      format_func=lambda x: q["options"][x],
      index=current_answer if current_answer is not None else 0,
      key=f"q_{q_index}",
  )

  st.session_state.answers[q_index] = selected_option

  col1, col2 = st.columns(2)
  with col1:
    if st.session_state.step > 1:
      if st.button("⬅️ שאלה קודמת"):
        st.session_state.step -= 1
        st.rerun()

  with col2:
    if st.session_state.step < len(QUESTIONS):
      if st.button("שאלה הבאה ➡️"):
        st.session_state.step += 1
        st.rerun()
    else:
      if st.button("סיים והגש מבחן ✅"):
        st.session_state.step = 11
        st.rerun()

# שלב 11: סיכום, ציון והפקת PDF
elif st.session_state.step == 11:
  st.subheader("🎉 סיימת את המבחן בהצלחה!")

  # חישוב ציון
  score = 0
  for idx, q in enumerate(QUESTIONS):
    if st.session_state.answers.get(idx) == q["correct"]:
      score += 10  # 10 נקודות לשאלה (סה"כ 100)

  ud = st.session_state.user_data
  st.success(f"הציון הסופי שלך הוא: **{score} / 100**")
  st.write(
      f"**שם העובד:** {ud['first_name_he']} {ud['last_name_he']} ("
      f"{ud['first_name_en']} {ud['last_name_en']})"
  )


  # פונקציית יצירת PDF
  def create_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 750, "Security Test Results")

    p.setFont("Helvetica", 12)
    p.drawString(
        50,
        710,
        f"Name (HE): {ud['first_name_he']} {ud['last_name_he']}",
    )
    p.drawString(
        50,
        690,
        f"Name (EN): {ud['first_name_en']} {ud['last_name_en']}",
    )
    p.drawString(
        50, 670, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    p.drawString(50, 630, f"Final Score: {score} / 100")

    p.save()
    buffer.seek(0)
    return buffer


  pdf_data = create_pdf()

  st.download_button(
      label="📄 הורד תוצאות כקובץ PDF למחשב/טאבלט",
      data=pdf_data,
      file_name=(
          f"security_test_{ud['first_name_en']}_{ud['last_name_en']}.pdf"
      ),
      mime="application/pdf",
  )

  if st.button("🔄 התחל מבחן חדש לעובד הבא"):
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.user_data = {}
    st.rerun()