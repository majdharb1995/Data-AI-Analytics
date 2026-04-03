import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from fpdf import FPDF
from deep_translator import GoogleTranslator

# --- ⚙️ إعدادات Gemini API (بديل n8n Workflow) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB_8RqR1GTg2pbATVqjmsmzKwQenhngz1Q")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

def call_gemini_api(stats_summary: dict, language: str = "ar") -> str:
    """
    دالة تحاكي منطق n8n Workflow: إرسال البيانات لـ Gemini وتحليلها
    وفق معايير التدقيق الحسابي البنكي الدولي (ISA)
    """
    prompt_text = (
        f"حلل هذه البيانات الإحصائية لملف إكسل حسب المعايير العالمية "
        f"لتدقيق الحسابات البنكية ISA باللغة {('العربية' if language == 'ar' else 'الإنجليزية')}: " + 
        str(stats_summary)
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    
    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.RequestException as e:
        return f"⚠️ خطأ في الاتصال بـ Gemini API: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"⚠️ خطأ في معالجة الاستجابة: {str(e)}"

# --- 1. إعدادات اللغة والترجمة ---
languages = {
    "English": {
        "dir": "ltr", "title": "Data Dashboard Pro", "designed_by": "Designed & Developed by: **Majd Harb**",
        "footer": "© 2026 All Rights Reserved | Majd Harb", "sidebar_title": "Control Panel",
        "uploader": "📂 Upload Data File", "info_msg": "Upload a file to start analysis.",
        "welcome": "Welcome to Smart Data Analyzer 🚀", "welcome_sub": "Please upload an Excel or CSV file from the sidebar to start.",
        "metrics": ["Total Rows", "Columns", "Missing Values", "Numeric Cols"],
        "tabs": ["📑 Data & Filters", "📊 Statistics", "📈 Charts", "🤖 Smart AI"],
        "filter_text": "Search & Filter Data", "stats_title": "Descriptive Statistics",
        "count_if_title": "Count If (Conditional Tool)", "select_col": "Select Column:",
        "select_cond": "Condition:", "input_val": "Value:", "result_text": "Result:",
        "viz_title": "Visual Representation", "ai_btn": "🚀 Start Smart Analysis",
        "copy_info": "↗️ Use the icon at the top right of the box to copy",
        "pdf_btn": "Download PDF", "trans_btn": "Translate Report",
        "error_file": "⚠️ Error processing file:", "report_header": "📊 AI Analysis Report",
        "ai_loading": "🤖 Analyzing data with Gemini AI (ISA Standards)..."
    },
    "العربية": {
        "dir": "rtl", "title": "لوحة بيانات احترافية", "designed_by": "تصميم وتطوير: **مجد حرب**",
        "footer": "© 2026 جميع الحقوق محفوظة | مجد حرب", "sidebar_title": "لوحة التحكم",
        "uploader": "📂 ارفع ملف البيانات", "info_msg": "قم برفع الملف للبدء في تحليل البيانات.",
        "welcome": "مرحباً بك في محلل البيانات الذكي 🚀", "welcome_sub": "الرجاء رفع ملف Excel أو CSV من القائمة الجانبية للبدء.",
        "metrics": ["إجمالي الأسطر", "عدد الأعمدة", "قيم مفقودة", "الأعمدة الرقمية"],
        "tabs": ["📑 البيانات والفلترة", "📊 الإحصائيات التحليلية", "📈 الرسوم البيانية", "🤖 التحليل الذكي"],
        "filter_text": "البحث وتصفية البيانات", "stats_title": "الإحصاء الوصفي الدقيق",
        "count_if_title": "أداة العد الشرطي (Count If)", "select_col": "اختر العمود:",
        "select_cond": "الشرط:", "input_val": "القيمة:", "result_text": "النتيجة:",
        "viz_title": "التمثيل البصري الاحترافي", "ai_btn": "🚀 بدء التحليل الذكي الآن",
        "copy_info": "↗️ استخدم الأيقونة في أعلى يمين الصندوق للنسخ",
        "pdf_btn": "تحميل PDF", "trans_btn": "ترجمة التقرير",
        "error_file": "⚠️ خطأ في معالجة الملف:", "report_header": "📊 تقرير التحليل الذكي",
        "ai_loading": "🤖 جاري تحليل البيانات عبر ذكاء جوجل الاصطناعي (معايير ISA)..."
    }
}

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="Data Pro Dashboard - Majd Harb", layout="wide")
lang_choice = st.sidebar.selectbox("🌐 Language / اللغة", ["English", "العربية"])
txt = languages[lang_choice]
lang_code = "ar" if lang_choice == "العربية" else "en"

direction = "RTL" if txt["dir"] == "rtl" else "LTR"
align = "right" if direction == "RTL" else "left"

st.markdown(f"""
    <style>
    html, body, [data-testid="stSidebar"], .main {{ direction: {direction}; text-align: {align}; }}
    .designer-text {{ color: #666; font-size: 0.9rem; margin-top: -15px; margin-bottom: 20px; }}
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f1f1f1; color: #555; text-align: center; padding: 10px; font-size: 0.8rem; border-top: 1px solid #ddd; z-index: 100; }}
    .report-box {{
        background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); direction: {direction}; text-align: {align};
        white-space: pre-wrap; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6;
    }}
    </style>
    """, unsafe_allow_html=True)

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. الشريط الجانبي ---
with st.sidebar:
    st.title(txt["sidebar_title"])
    uploaded_file = st.file_uploader(txt["uploader"], type=['xlsx', 'csv'])
    st.divider()
    st.info(txt["info_msg"])
    # ⚠️ تلميح أمني
    st.caption("🔐 API Key: Load from .env for production")

st.title(f"📊 {txt['title']}")
st.markdown(f'<p class="designer-text">{txt["designed_by"]}</p>', unsafe_allow_html=True)

# --- 4. معالجة البيانات ---
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(txt["metrics"][0], f"{len(df):,}")
        m2.metric(txt["metrics"][1], len(df.columns))
        m3.metric(txt["metrics"][2], df.isnull().sum().sum())
        m4.metric(txt["metrics"][3], len(df.select_dtypes(include=['number']).columns))

        st.divider()
        tab1, tab2, tab3, tab4 = st.tabs(txt["tabs"])

        with tab1:
            st.subheader(txt["filter_text"])
            search_query = st.text_input("🔍 Search / بحث", "")
            filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)] if search_query else df
            st.dataframe(filtered_df, use_container_width=True)

        with tab2:
            st.subheader(txt["stats_title"])
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                st.table(numeric_df.describe().T[['mean', 'std', 'min', '50%', 'max']].rename(columns={'50%': 'median'}))
            
            st.divider()
            st.subheader(txt["count_if_title"])
            col_a, col_b, col_c = st.columns(3)
            with col_a: selected_col = st.selectbox(txt["select_col"], df.columns, key="count_col")
            with col_b: condition = st.selectbox(txt["select_cond"], ["==", ">", "<", "Contains"], key="cond")
            with col_c: val = st.text_input(txt["input_val"], "")
            if val:
                try:
                    if condition == "==": count_res = len(df[df[selected_col].astype(str) == val])
                    elif condition == ">": count_res = len(df[df[selected_col] > float(val)])
                    elif condition == "<": count_res = len(df[df[selected_col] < float(val)])
                    elif condition == "Contains": count_res = len(df[df[selected_col].astype(str).str.contains(val, case=False)])
                    st.info(f"{txt['result_text']} {count_res}")
                except: st.error("Error")

        with tab3:
            st.subheader(txt["viz_title"])
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                x_axis = st.selectbox("X-Axis", df.columns, key="x_viz")
                y_axis = st.selectbox("Y-Axis (Numeric)", numeric_cols, key="y_viz")
                fig = px.bar(df, x=x_axis, y=y_axis, template="plotly_white", color=y_axis)
                st.plotly_chart(fig, use_container_width=True)

        # --- Tab 4: التحليل الذكي (مدمج مع Gemini API مباشرة) ---
        with tab4:
            st.subheader(txt["tabs"][3])
            if st.button(txt["ai_btn"]):
                stats_summary = df.describe(include='all').astype(str).to_dict()
                
                with st.spinner(txt["ai_loading"]):
                    # ✅ استدعاء مباشر لـ Gemini بدلاً من Webhook خارجي
                    ai_report = call_gemini_api(stats_summary, language=lang_code)
                    st.session_state['report'] = ai_report
                    st.success("✅ Analysis Complete")

            if 'report' in st.session_state:
                report_content = st.session_state['report']
                
                st.markdown(f"### {txt['report_header']}")
                st.markdown(f'<div class="report-box">{report_content}</div>', unsafe_allow_html=True)
                
                st.divider()
                c1, c2, c3 = st.columns(3)
                with c1: st.caption(txt["copy_info"])
                with c2:
                    if st.button(txt["trans_btn"]):
                        target = 'en' if lang_choice == "العربية" else 'ar'
                        st.session_state['report'] = GoogleTranslator(source='auto', target=target).translate(report_content)
                        st.rerun()
                with c3:
                    pdf_bytes = create_pdf(st.session_state['report'])
                    st.download_button(label=txt["pdf_btn"], data=pdf_bytes, file_name="AI_Analysis_Report_Majd.pdf", mime="application/pdf")

    except Exception as e:
        st.error(f"{txt['error_file']} {e}")
else:
    st.title(txt["welcome"])
    st.markdown(txt["welcome_sub"])

st.markdown(f'<div class="footer">{txt["footer"]}</div>', unsafe_allow_html=True)