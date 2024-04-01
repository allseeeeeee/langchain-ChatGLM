from langchain.agents import load_tools, initialize_agent
from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools import PythonREPLTool
from langchain.python import PythonREPL
from langchain.llms.openai import OpenAI
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain_community.llms import Tongyi
# ChatGLM Tongyi Minimax QianfanLLMEndpoint
from langchain.tools import BingSearchRun

from configs import model_config

search = BingSearchRun()
llm = Tongyi(model_name="qwen-max", dashscope_api_key=model_config.ONLINE_LLM_MODEL['qwen-api']['api_key'])
tools = load_tools(['bing-search', 'llm-math'], llm=llm)

agent = initialize_agent(
    llm=llm,
    tools=tools,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

resp = search.run("今天北京的温度是多少度")
print(resp)
resp = search.run("今天杭州的温度是多少度")
print(resp)

agent.run("今天北京的温度比杭州的温度低多少度?")