from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools import PythonREPLTool
from langchain.python import PythonREPL
from langchain.llms.openai import OpenAI
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain_community.llms import Tongyi
# ChatGLM Tongyi Minimax QianfanLLMEndpoint


from configs import model_config

# 默认是 qwen-plus、qwen-turbo 需要付费
agent_executor = create_python_agent(
    llm=Tongyi(model_name="qwen-max", dashscope_api_key=model_config.ONLINE_LLM_MODEL['qwen-api']['api_key']),
    tool=PythonREPLTool(),
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

agent_executor.run("从1连续加到100，和是多少?")
