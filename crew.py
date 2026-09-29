
import asyncio

from crewai import LLM, Agent, Task, Crew, Process

from agents.requirement_checker import create_requirement_checker
from agents.eligibility_evaluator import create_eligibility_evaluator
from agents.program_recommender import create_program_recommender


def get_llm(api_key):
    """Create the Groq LLM shared by all agents."""

    return LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=api_key,
        temperature=0.2,
        max_tokens=4096,
    )


def create_single_agent_crew(agent, task):
    """Create a simple one-agent CrewAI crew."""

    return Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
        cache=False,
    )


def create_admission_crews(
    student_profile,
    university_info,
    api_key,
):
    """Build three independent crews."""

    llm = get_llm(api_key)

    # -----------------------------
    # Agent 1: Requirements Checker
    # -----------------------------

    requirement_checker = create_requirement_checker(llm)

    requirements_task = Task(
        description="""
        Review the following student profile and
        university admission information.

        STUDENT PROFILE:
        {student_profile}

        UNIVERSITY INFORMATION:
        {university_info}

        Identify:
        1. Required degree and academic background.
        2. Minimum GPA or marks.
        3. English language requirements.
        4. Standardized tests, if mentioned.
        5. Work experience requirements.
        6. Required documents.
        7. Application deadlines, if supplied.
        8. Tuition and scholarship requirements,
           if supplied.

        Clearly separate confirmed information
        from missing or unverified information.

        Do not invent any admission requirement.
        """,

        expected_output=(
            "A clear list of admission requirements, "
            "supporting information, and missing facts."
        ),

        agent=requirement_checker,
    )

    requirements_crew = create_single_agent_crew(
        requirement_checker,
        requirements_task,
    )

    # -----------------------------
    # Agent 2: Eligibility Evaluator
    # -----------------------------

    eligibility_evaluator = create_eligibility_evaluator(llm)

    eligibility_task = Task(
        description="""
        Independently evaluate the student's
        admission eligibility.

        STUDENT PROFILE:
        {student_profile}

        UNIVERSITY ADMISSION CRITERIA:
        {university_info}

        Compare the student's qualifications against
        the supplied criteria.

        Evaluate:
        1. Degree and academic background.
        2. CGPA or percentage.
        3. English proficiency.
        4. Work experience.
        5. Documents and other conditions.

        For each requirement, provide:
        - Requirement
        - Student's qualification
        - Status: Meets, Does not meet,
          or Needs verification
        - Explanation

        End with one preliminary status:
        Potentially eligible,
        Not eligible based on supplied evidence,
        or Insufficient information.

        Do not assume missing requirements are met.
        Do not claim an official admission decision.
        """,

        expected_output=(
            "An independent eligibility assessment "
            "with requirement-level statuses, "
            "explanations, and an overall preliminary "
            "eligibility status."
        ),

        agent=eligibility_evaluator,
    )

    eligibility_crew = create_single_agent_crew(
        eligibility_evaluator,
        eligibility_task,
    )

    # -----------------------------
    # Agent 3: Program Recommender
    # -----------------------------

    program_recommender = create_program_recommender(llm)

    recommendation_task = Task(
        description="""
        Recommend relevant university programs
        for the student.

        STUDENT PROFILE:
        {student_profile}

        AVAILABLE UNIVERSITY INFORMATION:
        {university_info}

        Consider:
        1. Academic background.
        2. Preferred degree level.
        3. Research and subject interests.
        4. Preferred countries.
        5. Budget and funding needs.
        6. Career goals.

        For each recommended program, provide:
        - University name
        - Program name
        - Why it matches the student
        - Known eligibility requirements
        - Missing or unverified information

        Recommend only programs supported by
        the supplied information.

        Do not invent universities, program names,
        fees, scholarships, deadlines, or URLs.

        If the information is insufficient,
        explain what additional information
        is needed to recommend programs reliably.
        """,

        expected_output=(
            "A list of relevant programs, reasons "
            "for the recommendations, and eligibility "
            "or information limitations."
        ),

        agent=program_recommender,
    )

    recommendation_crew = create_single_agent_crew(
        program_recommender,
        recommendation_task,
    )

    return (
        requirements_crew,
        eligibility_crew,
        recommendation_crew,
    )


async def run_parallel_assessment(
    student_profile,
    university_info,
    api_key,
):
    """
    Execute all three independent CrewAI crews
    concurrently and return their separate results.
    """

    (
        requirements_crew,
        eligibility_crew,
        recommendation_crew,
    ) = create_admission_crews(
        student_profile=student_profile,
        university_info=university_info,
        api_key=api_key,
    )

    inputs = {
        "student_profile": student_profile,
        "university_info": university_info,
    }

    # All three crews start concurrently.
    results = await asyncio.gather(
        requirements_crew.kickoff_async(inputs=inputs),
        eligibility_crew.kickoff_async(inputs=inputs),
        recommendation_crew.kickoff_async(inputs=inputs),
        return_exceptions=True,
    )

    output = {}

    names = [
        "requirements",
        "eligibility",
        "recommendations",
    ]

    for name, result in zip(names, results):

        if isinstance(result, Exception):
            output[name] = (
                "This agent encountered an error: "
                + str(result)
            )
        else:
            output[name] = str(result)

    return output
