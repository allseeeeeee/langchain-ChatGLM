import os.path
import time
from datetime import datetime

from bson.objectid import ObjectId
import pymongo
import requests
from pprint import pprint

path = 'data'
file = f"{path}/QA-{time.strftime('%Y%m%d')}.txt"
parent_dir = os.path.dirname(file)
if not os.path.exists(parent_dir):
    os.makedirs(parent_dir)

PROMPT_TEMPLATE = """已知信息：
{context} 

根据上述已知信息，简洁和专业的来回答用户的问题，无需解释，无需总结，无需添加与问题无关的答复，并自行检查答复与用户提问是否存在冲突。
如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，不允许在答案中添加编造成分。 
问题是：{question}"""

client = pymongo.MongoClient(f"mongodb://{os.environ.get('usr+pwd')}@192.168.0.9:27017")
db = client.get_database("hplus_platform")
table = db.get_collection("00_chat_qa")

if __name__ == '__main__':
    with open(file, "a+", encoding="utf-8") as f:
        f.write(f"\n---------------------------------------------\n"
                f"模板：{PROMPT_TEMPLATE}"
                f"\n---------------------------------------------\n")
        f.flush()

        questions_file = os.path.join(path, 'questions.txt')
        all_hsp = ["5C6CC2CB199E0500010412CB", 'YY0000337418065', 'YY0000322318065', '5D8495D05FBB69000130CD92',
                   "5DBF8442B1379F0001C5E0C1", '607807F375FEA05011100CA7', '5DD42D5F4683AF0001688224',
                   "YY0000316118065", "YY0000318718065", "YY0000333818065", "YY0000327418065", "YY0000320218065",
                   "YY0000345918065", "61933992553DC843DCE256BC", "5D01B04538E4E30001B36A4D",
                   "5C9DBFC9CC6A00000178C70B", "5DA6C2AD832802000159B247"
                   ]

        # 为避免频繁切换向量知识库，依次对每家医院对所有问题做一轮问答
        for hsp in all_hsp:
            with open(questions_file, 'r', encoding='utf-8') as q:
                for query in q:
                    json_data = {
                        "question": query,
                        "knowledge_base_id": hsp,
                        "prompt_template": PROMPT_TEMPLATE
                    }
                    created_at = datetime.now()
                    resp = requests.post("http://localhost:7861/local_doc_qa/local_doc_chat", json=json_data).json()
                    del resp['history']
                    print(resp)
                    row = {
                        "_id": ObjectId(),
                        "question": query,
                        "response": resp['response'],
                        "hsp_code": hsp,
                        "duration": int((datetime.now() - created_at).total_seconds() * 1000),
                        "created_at": created_at,
                        "prompt_template": PROMPT_TEMPLATE,
                        "source_documents": resp['source_documents'],
                    }
                    print(row)
                    table.insert_one(row)

                    f.write(f"问题：{query}")
                    f.write(f"回答：{resp['response']}\n")
                    f.write(f"参考：{resp['source_documents']}\n\n")
                    f.flush()

    pass
