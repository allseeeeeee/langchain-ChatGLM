import torch

from chains.local_doc_qa import LocalDocQA
from models.loader import LoaderCheckPoint
import models.shared as shared
from models.loader.args import parser

# LLM input history length
LLM_HISTORY_LEN = 3

if __name__ == '__main__':
    args = parser.parse_args()
    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()
    llm_model_ins.set_history_len(LLM_HISTORY_LEN)

    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(llm_model=llm_model_ins)

    vs_path = "/home/dev/team/langchain-ChatGLM/vector_store/医院知识库"
    query = "浙江省人民医院的具体地址？"

    for resp, history in local_doc_qa.get_knowledge_based_answer(
            query=query, vs_path=vs_path, chat_history=[], streaming=False):
        print(resp)

    pass

