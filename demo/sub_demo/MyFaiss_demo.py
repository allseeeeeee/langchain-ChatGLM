from pprint import pprint

import torch
from langchain import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModel

from vectorstores import MyFAISS

PROMPT_TEMPLATE = """已知信息：
{context} 

根据上述已知信息，简洁和专业的来回答用户的问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”，不允许在答案中添加编造成分，答案请使用中文。 问题是：{question}"""


device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
embeddings = HuggingFaceEmbeddings(model_name="/home/dev/team/langchain-ChatGLM/text2vec-large-chinese",
                                   model_kwargs={'device': device})

# 多个医院的知识文档放到一个知识库里，向量化检索时存在医院主体识别不精确的问题
# 解决方案：增加一层LLM调用用于识别主体并用于知识库映射，同时需辅以不同医院知识分知识库存储
# 回答不满意时，切换到默认通用知识库重新回答一次（但需做日志记录，以备后续优化模型）
query = "浙江省人民医院的具体地址在哪？"

vector_store = FAISS.load_local("/home/dev/team/langchain-ChatGLM/vector_store/医院知识库", embeddings)
related_docs_with_score = vector_store.similarity_search_with_score(query, k=5)
pprint(related_docs_with_score)
context = "\n".join([doc.page_content for doc, _ in related_docs_with_score])
prompt = PROMPT_TEMPLATE.replace("{question}", query).replace("{context}", context)
print(prompt)

# tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
# model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).half().cuda()
# model = model.eval()
#
# for answer_result in model.chat(prompt=prompt, history=[], streaming=False):
#     resp = answer_result.llm_output["answer"]
#     pprint(resp)