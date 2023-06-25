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

    vs_path = "/home/dev/team/langchain-ChatGLM/vector_store/YY0000309718060"
    query = "那是民营的？"

    history = [['医院是三甲的吗', '根据已知信息，皖北煤电集团总医院是一家三级甲等医院。'],
               ['医院是公立的吗', '根据已知信息，皖北煤电集团总医院是一家三级甲等医院，但无法确定其是否为公立医院。'],
               ['医院类型是公立的吗', '根据已知信息，皖北煤电集团总医院是一家三级甲等医院，但无法确定其是否为公立。']]

    history_content = "\n".join(["\n".join(item) for item in history])
    SUMMARY_TEMPLATE = f"""
    这是人类与机器人的对话：{history_content}
    为以上对话编写简洁的用户提问摘要，仅生成包含摘要内容，无需解释。
    """
    print(SUMMARY_TEMPLATE)

    for answer_result in local_doc_qa.llm.generatorAnswer(prompt=SUMMARY_TEMPLATE, history=[], streaming=False):
        resp = answer_result.llm_output["answer"]
        print(resp)

    for resp, history in local_doc_qa.get_knowledge_based_answer(
            query=query, vs_path=vs_path, chat_history=[], streaming=False):
        print(resp)

    pass

