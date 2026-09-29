
from crewai import Agent


def create_requirement_checker(llm):
    """Create the Admission Requirements Checker agent."""

    return Agent(
        role="University Admission Requirements Checker",

        goal=(
            "Identify and organize admission requirements "
            "from the university information supplied by "
            "the student."
        ),

        backstory=(
            "You specialize in university admission rules. "
            "You carefully examine official admission "
            "information supplied by the student. "
            "Identify degree requirements, GPA, language "
            "tests, experience, documents, deadlines, "
            "and other conditions. "
            "Never invent requirements, deadlines, fees, "
            "scholarships, or university policies. "
            "Clearly identify missing or unverified facts."
        ),

        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=3,
    )
