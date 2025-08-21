"""🗽 Agent with Tools - Your AI News Buddy that can search the web

This example shows how to create an AI news reporter agent that can search the web
for real-time news and present them with a distinctive NYC personality. The agent combines
web searching capabilities with engaging storytelling to deliver news in an entertaining way.

Run `pip install openai duckduckgo-search agno` to install dependencies.
"""
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from tool_birthday import BirthdayTools

# Create a News Reporter Agent with a fun personality
agent = Agent(
    model=OpenAIChat(id="gpt-4.1-mini"),
    instructions=dedent("""\
        Luôn trả lời bằng tiếng việt\
    """),
    tools=[BirthdayTools(api_key = "", base_url= "https://api.dify.ai/v1/workflows/run")],
    show_tool_calls=True,
    markdown=True,
)

# Example usage
agent.print_response(
    "hôm nay có ai sinh nhật.", stream=True
)

# More example prompts to try:
"""
Try these engaging news queries:
1. "What's the latest development in NYC's tech scene?"
2. "Tell me about any upcoming events at Madison Square Garden"
3. "What's the weather impact on NYC today?"
4. "Any updates on the NYC subway system?"
5. "What's the hottest food trend in Manhattan right now?"
"""