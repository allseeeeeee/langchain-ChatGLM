import os.path
import time

import requests
from pprint import pprint

path = 'data'
file = f"{path}/QA-{time.strftime('%Y%m%d')}.txt"
parent_dir = os.path.dirname(file)
if not os.path.exists(parent_dir):
    os.makedirs(parent_dir)

PROMPT_TEMPLATE = """已知信息：
{context} 

根据上述已知信息，简洁和专业的来回答用户的问题，无需解释，无需总结，无需添加与问题无关的答复，并自行检查答复是否符合用户的提问。
如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，不允许在答案中添加编造成分。 
问题是：{question}"""


if __name__ == '__main__':
    with open(file, "a+", encoding="utf-8") as f:
        f.write(f"\n---------------------------------------------\n"
                f"模板：{PROMPT_TEMPLATE}"
                f"\n---------------------------------------------\n")
        f.flush()

        questions_file = os.path.join(path, 'questions.txt')
        with open(questions_file, 'r', encoding='utf-8') as q:
            for query in q:
                json_data = {
                    "question": query,
                    "knowledge_base_id": "5C6CC2CB199E0500010412CB",
                    "prompt_template": PROMPT_TEMPLATE
                }
                resp = requests.post("http://localhost:7861/local_doc_qa/local_doc_chat", json=json_data).json()
                del resp['history']
                print(resp)
                f.write(f"问题：{query}")
                f.write(f"回答：{resp['response']}\n")
                f.write(f"参考：{resp['source_documents']}\n\n")
                f.flush()

    pass
