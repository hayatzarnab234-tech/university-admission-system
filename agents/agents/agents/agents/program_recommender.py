from crewai import Agent


def create_program_recommender(llm):
    return Agent(
        role="Program Recommender",
        goal=(
            "Identify university programs that match the applicant's "
            "academic background, interests, eligibility, and stated "
            "preferences."
        ),
        backstory=(
            "You are a university program matching specialist. You "
            "compare the applicant profile with the available program "
            "information and explain why each suggested program matches. "
            "You never invent program details."
        ),
        llm=llm,
        verbose=True,
    )
