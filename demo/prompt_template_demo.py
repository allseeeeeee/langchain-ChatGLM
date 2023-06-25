from langchain.prompts import PromptTemplate

from configs.model_config import PROMPT_TEMPLATE

template = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=['context', 'question'])
print(template.format(question="浙江省人民医院朝晖院区的地址在哪？", context="浙江省人民医院相关知识"))
