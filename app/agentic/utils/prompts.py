from langchain_core.prompts import ChatPromptTemplate

TECHNICAL_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """

            """
        )
    ]
)

SENTIMENT_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """

            """
        )
    ]
)

VALUATION_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """

            """
        )
    ]
)

REPORT_WRITING_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """

            """
        ),
        ("placeholder", "{messages}")
    ]
)