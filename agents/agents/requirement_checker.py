from crewai import Agent


def create_requirement_checker(llm):
    return Agent(
        role="University Requirement Checker",
        goal=(
            "Check the applicant's information against the stated "
            "admission requirements and identify which requirements "
            "are satisfied, missing, or unclear."
        ),
        backstory=(
            "You are a careful university admissions requirements "
            "specialist. You only use the information provided to you "
            "and never invent requirements or applicant information."
        ),
        llm=llm,
        verbose=True,
    )
