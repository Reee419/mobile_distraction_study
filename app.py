import streamlit as st
import time
import pandas as pd
import os
import matplotlib.pyplot as plt

# ========================
# Data setup
# ========================
DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["time", "mode"]).to_csv(DATA_FILE, index=False)

# ========================
# Title
# ========================
st.title("تأثير استخدام الجوال على الإنتاجية")

# ========================
# View mode (Presentation / Participant)
# ========================
view_mode = st.sidebar.radio(
    "وضع العرض:",
    ["صفحة المشاركة", "عرض النتائج (للبروجكتور)"]
)

# ========================
# ========================
# PARTICIPANT PAGE
# ========================
# ========================
if view_mode == "صفحة المشاركة":

    st.markdown("""
    تعليمات التجربة:
    - اختر نوع التجربة
    - اضغط (ابدأ) ليبدأ الوقت
    - تتكون التجربة من 3 أسئلة
    - إذا كانت الإجابة خاطئة سيعاد نفس السؤال
    - الوقت يتوقف فقط بعد آخر إجابة صحيحة
    """)

    mode = st.radio("نوع التجربة:", ["بدون إزعاج", "مع إزعاج"])

    questions = [
        ("كم ناتج 7 × 8 ؟", ["40", "54", "56", "64"], "56"),
        ("كم ناتج 9 × 6 ؟", ["42", "48", "54", "56"], "54"),
        ("كم ناتج 5 × 7 ؟", ["30", "35", "40", "45"], "35")
    ]

    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0

    if st.session_state.start_time is None:
        if st.button("ابدأ"):
            st.session_state.start_time = time.time()
            st.session_state.q_index = 0
    else:
        st.info("⏱️ الوقت يعمل")
        
        # 🔊 Distraction (sound only)
        if mode == "مع إزعاج":
            st.audio("notification.mp3")
            time.sleep(0.4)

        q_text, options, correct = questions[st.session_state.q_index]

        answer = st.radio(
            f"السؤال {st.session_state.q_index + 1}: {q_text}",
            options,
            key=st.session_state.q_index
        )

        if st.button("إرسال"):
            if answer != correct:
                st.error("❌ إجابة غير صحيحة، حاولي مرة أخرى")
            else:
                st.success("✅ إجابة صحيحة")
                st.session_state.q_index += 1

                if st.session_state.q_index == len(questions):
                    duration = round(time.time() - st.session_state.start_time, 2)

                    df = pd.read_csv(DATA_FILE)
                    df.loc[len(df)] = [duration, mode]
                    df.to_csv(DATA_FILE, index=False)

                    st.success(f"✅ انتهت التجربة خلال {duration} ثانية")

                    st.session_state.start_time = None
                    st.session_state.q_index = 0
                    st.rerun()

# ========================
# ========================
# PROJECTOR VIEW (CHART ONLY)
# ========================
# ========================
if view_mode == "عرض النتائج (للبروجكتور)":

    st.subheader("📊 Live Results")

    df = pd.read_csv(DATA_FILE)

    if not df.empty:
        bins = [5, 10, 15, 20, 30]

        fig, ax = plt.subplots()

        for label, color in [
            ("بدون إزعاج", "green"),
            ("مع إزعاج", "red")
        ]:
            subset = df[df["mode"] == label]["time"]
            if not subset.empty:
                ax.hist(
                    subset,
                    bins=bins,
                    alpha=0.65,
                    label=label,
                    color=color
                )

        # English labels (ONLY for chart)
        ax.set_xlabel("Completion Time (seconds)")
        ax.set_ylabel("Number of Participants")
        ax.set_title("Time Distribution: With vs Without Distraction")
        ax.legend()

        st.pyplot(fig)

    else:
        st.info("Waiting for participants...")


# زر تشغيل الصوت (تفاعل مباشر)
if mode == "مع إزعاج":
    st.markdown("### تشغيل الإزعاج")
    play_sound = st.button("🔊 تشغيل الإشعار")

    if play_sound:
        st.audio("notification.mp3")
