import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

async def main():
    client = MultiServerMCPClient(  
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": ["./math_server.py"],
            },
            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:31000/mcp",
            }
        }
    )

    tools = await client.get_tools()  
    agent = ChatOllama(
        model="llama3.1:8b",
        tools=tools,
        validate_model_on_init=True,
        temperature=0,
    )

    math_response = await agent.ainvoke([
        HumanMessage(content="what's (3 + 5) x 12?")
    ])
    print("Math result:", math_response.content)

    weather_response = await agent.ainvoke([
        HumanMessage(content="what is the weather in nyc?")
    ])
    print("Weather result:", weather_response.content)

if __name__ == "__main__":
    asyncio.run(main())