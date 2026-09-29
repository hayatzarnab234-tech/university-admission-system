
import asyncio
import os

import streamlit as st

from crew import run_parallel_assessment


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="University Admission Assistant",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 University Admission Assistant")

st.write(
    "Three independent AI agents help you check "
    "university requirements, evaluate eligibility, "
    "and discover relevant degree programs."
)

st.info(
    "This application provides preliminary guidance "
    "only. It does not make official university "
    "admission decisions. Always verify requirements "
    "with the university."
)


# -----------------------------
# Groq API key
# -----------------------------

def get_api_key():
    """Read the API key from Streamlit Secrets."""

    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    return key or os.environ.get("GROQ_API_KEY", "")


# -----------------------------
# Student information form
# -----------------------------

st.header("1. Student Profile")

with st.form("student_form"):

    col1, col2 = st.columns(2)

    with col1:

        degree = st.text_input(
            "Current or completed degree",
            placeholder="BS International Relations",
        )

        university = st.text_input(
            "Previous university",
            placeholder="University name",
        )

        cgpa = st.text_input(
            "CGPA or percentage",
            placeholder="3.51/4.00",
        )

        graduation_year = st.text_input(
            "Graduation year",
            placeholder="2025",
        )

    with col2:

        target_degree = st.selectbox(
            "Degree you want to pursue",
            [
                "Master's",
                "MPhil",
                "Bachelor's",
                "PhD",
                "Other",
            ],
        )

        interests = st.text_area(
            "Academic interests",
            placeholder=(
                "International Relations, "
                "Security Studies, Public Policy"
            ),
        )

        countries = st.text_input(
            "Preferred countries",
            placeholder="UK, USA, Germany",
        )

        budget = st.text_input(
            "Budget or funding preference",
            placeholder="Fully funded scholarships",
        )

    english = st.text_input(
        "English language proficiency",
        placeholder="MOI available, IELTS not taken",
    )

    experience = st.text_area(
        "Work experience or internships",
        placeholder="Describe experience or write None",
    )

    extra = st.text_area(
        "Additional information",
        placeholder=(
            "Research interests, career goals, "
            "documents, or other relevant details"
        ),
    )

    # -----------------------------
    # University information
    # -----------------------------

    st.header("2. University Information")

    university_info = st.text_area(
        "Paste admission requirements or program details",
        height=250,
        placeholder=(
            "Paste official university information here. "
            "You may include university names, program "
            "descriptions, GPA requirements, English "
            "tests, fees, scholarships, deadlines, "
            "and official website URLs."
        ),
        help=(
            "The agents use the information you provide. "
            "They do not automatically search university "
            "websites in this version."
        ),
    )

    submitted = st.form_submit_button(
        "Run All Three Agents",
        type="primary",
        use_container_width=True,
    )


# -----------------------------
# Run the three agents
# -----------------------------

if submitted:

    if not degree.strip():
        st.error("Please enter your current or completed degree.")

    elif not interests.strip():
        st.error("Please enter your academic interests.")

    elif not university_info.strip():
        st.error(
            "Please paste university admission "
            "requirements or program information."
        )

    else:

        api_key = get_api_key()

        if not api_key:
            st.error(
                "GROQ_API_KEY is missing. Please add "
                "your Groq API key in Streamlit Cloud Secrets."
            )

        else:

            student_profile = f"""
            Current or completed degree: {degree}
            Previous university: {university or 'Not provided'}
            CGPA or percentage: {cgpa or 'Not provided'}
            Graduation year: {graduation_year or 'Not provided'}
            Target degree: {target_degree}
            Academic interests: {interests}
            Preferred countries: {countries or 'Not specified'}
            Budget: {budget or 'Not specified'}
            English proficiency: {english or 'Not provided'}
            Work experience: {experience or 'Not provided'}
            Additional information: {extra or 'None'}
            """

            with st.spinner(
                "All three agents are working in parallel..."
            ):

                try:

                    results = asyncio.run(
                        run_parallel_assessment(
                            student_profile=student_profile,
                            university_info=university_info,
                            api_key=api_key,
                        )
                    )

                    st.session_state["results"] = results

                except Exception as e:

                    st.error(
                        "The assessment failed. Check your "
                        "Groq API key, model access, and "
                        "Streamlit deployment logs."
                    )

                    with st.expander("Technical details"):
                        st.code(str(e))


# -----------------------------
# Display independent results
# -----------------------------

if "results" in st.session_state:

    results = st.session_state["results"]

    st.divider()

    st.header("3. Results from the Three Agents")

    st.caption(
        "Each section contains the independent output "
        "of one agent. The agents do not depend on "
        "one another's results."
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Requirements Checker",
            "Eligibility Evaluator",
            "Program Recommender",
        ]
    )

    with tab1:

        st.subheader("Admission Requirements")

        st.markdown(
            results["requirements"]
        )

    with tab2:

        st.subheader("Eligibility Assessment")

        st.markdown(
            results["eligibility"]
        )

    with tab3:

        st.subheader("Program Recommendations")

        st.markdown(
            results["recommendations"]
        )

    # Download individual results.
    st.divider()

    st.subheader("Download Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "Download Requirements",
            data=results["requirements"],
            file_name="admission_requirements.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "Download Eligibility",
            data=results["eligibility"],
            file_name="eligibility_assessment.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col3:
        st.download_button(
            "Download Recommendations",
            data=results["recommendations"],
            file_name="program_recommendations.md",
            mime="text/markdown",
            use_container_width=True,
        )
