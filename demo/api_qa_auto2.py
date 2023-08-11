import os.path
import time
from datetime import datetime

from bson.objectid import ObjectId
import pymongo
import requests

auth = os.environ.get('usr+pwd')
if auth is None or len(auth) == 0:
    print("Please setup env params: [usr+pwd].  e.g: \nusr+pws=username:password")

client = pymongo.MongoClient(f"mongodb://{auth}@192.168.0.9:27017")
db = client.get_database("hplus_platform")
table = db.get_collection("00_chat_qa_common")

path = 'data'
file = f"{path}/QA-{time.strftime('%Y%m%d')}.txt"
parent_dir = os.path.dirname(file)
if not os.path.exists(parent_dir):
    os.makedirs(parent_dir)

if __name__ == '__main__':
    with open(file, "a+", encoding="utf-8") as f:
        total = table.count_documents({})
        print(f"总问答数：{total}")
        index = 0
        resp_prefix = "full_bit_resp"
        while index < total:
            print('=====================================================')
            qa = table.find({}).skip(index).limit(1)[0]
            src_docs = qa['source_documents'] if 'source_documents' in qa and len(qa['source_documents']) > 0 else ''
            print('src_docs\n', src_docs)
            print('question', qa['question'])
            print('response', qa['response'])
            print(f">>>>>>>> {index+1} / {total}  |  {round((index+1) / total * 100, 2)}%")

            f.write(f"\n---------------------------------------------\n"
                    f"提示模板：{qa['prompt_template']}\n\n")
            f.write(f"参考文档：{qa['source_documents']}\n\n")
            f.write(f"用户问题：{qa['question']}\n\n")
            f.write(f"参考回答：{qa['response']}\n\n")
            f.flush()

            prompt = qa['prompt_template'].replace("{context}", src_docs)
            json_data = {"streaming": False, "question": qa['question'], "prompt_template": prompt}
            for i in range(1):
                resp = requests.post("http://localhost:7861/chat", json=json_data).json()
                print(f"""{resp_prefix}{i + 1}：{resp['response']}\n\n""")
                qa[f"{resp_prefix}{i + 1}"] = resp['response']
                f.write(f"{resp_prefix}{i + 1}：{resp['response']}\n\n")
                f.flush()

            result = table.find_one_and_update({"_id": qa['_id']},
                                               {
                                                   "$set": {
                                                       f"{resp_prefix}3": qa[f"{resp_prefix}1"],
                                                   }
                                               },
                                               return_document=pymongo.ReturnDocument.AFTER
                                               )
            print('after', result)
            index += 1

    pass
