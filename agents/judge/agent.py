from typing import Literal
from google.adk.agents import Agent
from google.adk.apps.app import App
from pydantic import BaseModel, Field


MODEL = "gemini-2.5-pro"

# TODO: Define the JudgeFeedback schema
# It should extend BaseModel and define 'status' ("pass" or "fail") and 'feedback'.
class JudgeFeedback(BaseModel):
    """Structured feedback for LinkedIn post evaluation."""
    
    score: float = Field(
        description="Overall quality score from 1 to 10 based on engagement potential."
    )
    
    feedback: List[str] = Field(
        description="List of 2-3 specific, actionable improvements."
    )

# TODO: Define the Judge Agent
# The judge should accept research findings, evaluate them, and output the JudgeFeedback schema.

judge = Agent(
    name="judge",
    model=MODEL,
    description="Evaluates LinkedIn post quality and engagement potential.",
    instruction="""
    You are a strict LinkedIn content evaluator.

    Evaluate the given LinkedIn post based on:

    - Hook strength (first line must grab attention)
    - Readability (short lines, clean formatting)
    - Value (insight, usefulness, or perspective)
    - Engagement potential (likelihood of likes/comments)
    - Hashtag quality (relevant and optimized)

    Scoring rules:
    - 9-10: Excellent, highly engaging
    - 7-8: Good but can improve
    - 5-6: Average, lacks strong engagement
    - Below 5: Weak content

    Output:
    - A score between 1 and 10
    - 2-3 specific improvements

    Be strict. Do not give high scores easily.
    """,
    output_schema=JudgeFeedback,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)
