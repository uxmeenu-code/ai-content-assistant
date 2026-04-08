import os
import json
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext

from authenticated_httpx import create_authenticated_client
from datetime import datetime, timedelta

def get_next_week_dates(n):
    today = datetime.utcnow()
    start = today + timedelta(days=(7 - today.weekday()))
    
    return [
        (start + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(n)
    ]

# --- Callbacks ---
def create_save_output_callback(key: str):
    """Creates a callback to save the agent's final response to session state."""
    def callback(callback_context: CallbackContext, **kwargs) -> None:
        ctx = callback_context
        # Find the last event from this agent that has content
        for event in reversed(ctx.session.events):
            if event.author == ctx.agent_name and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    # Try to parse as JSON if it looks like it, for judge_feedback
                    if key == "judge_feedback" and text.strip().startswith("{"):
                        try:
                            ctx.state[key] = json.loads(text)
                        except json.JSONDecodeError:
                            ctx.state[key] = text
                    else:
                        ctx.state[key] = text
                    print(f"[{ctx.agent_name}] Saved output to state['{key}']")
                    return
    return callback

# --- Remote Agents ---

# TODO: Define connections to remote agents
# Connect to Researcher, Judge, and Content Builder using RemoteA2aAgent.
# Remember to use the environment variables for URLs (or localhost defaults).
# Connect to Content Agent (port 8003)
content_builder_url = os.environ.get(
    "CONTENT_BUILDER_AGENT_CARD_URL",
    "http://localhost:8003/a2a/agent/.well-known/agent-card.json"
)

content_builder = RemoteA2aAgent(
    name="content_builder",
    agent_card=content_builder_url,
    description="Generates high-engagement LinkedIn posts.",
    # Save generated content for next step
    after_agent_callback=create_save_output_callback("generated_post"),
    httpx_client=create_authenticated_client(content_builder_url)
)


# Connect to Judge Agent (port 8002)
judge_url = os.environ.get(
    "JUDGE_AGENT_CARD_URL",
    "http://localhost:8002/a2a/agent/.well-known/agent-card.json"
)

judge = RemoteA2aAgent(
    name="judge",
    agent_card=judge_url,
    description="Evaluates LinkedIn post quality and engagement.",
    after_agent_callback=create_save_output_callback("evaluation_result"),
    httpx_client=create_authenticated_client(judge_url)
)

# --- Escalation Checker ---

# TODO: Define EscalationChecker
# This agent should check the status of the judge's feedback.
# If status is "pass", it should escalate (break the loop).

# --- Orchestration ---

# TODO: Define the Research Loop
# Use LoopAgent to cycle through Researcher -> Judge -> EscalationChecker.

# TODO: Define the Root Agent (Pipeline)
# Use SequentialAgent to run the Research Loop followed by the Content Builder.

orchestrator = SequentialAgent(
    name="orchestrator",
    description="Runs content generation followed by evaluation.",
    sub_agents=[
        content_builder,
        judge
    ]
)

root_agent = orchestrator