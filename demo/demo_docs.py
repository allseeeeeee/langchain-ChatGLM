import asyncio
import os
import shutil

from api import get_folder_path, list_docs, get_vs_path, get_file_path
from chains.local_doc_qa import LocalDocQA
from configs.model_config import LLM_HISTORY_LEN
from models.loader import LoaderCheckPoint
import models.shared as shared
from models.loader.args import parser
from export_mongo import *


def list_knowledge_base(knowledge_base_id):
    loop = asyncio.get_event_loop()
    docs = loop.run_until_complete(list_docs(knowledge_base_id))
    loop.close()

    print(docs)


def init_knowledge_base(app, hsp):

    knowledge_base_id = hsp['organization_code']
    doc_path = get_folder_path(knowledge_base_id)
    print('本地知识库目录', doc_path)
    if os.path.exists(doc_path):
        # 先删除主要在于tmp_files/load_files.txt会附加重复信息
        shutil.rmtree(os.path.join(doc_path, 'tmp_files'))
    else:
        os.makedirs(doc_path)

    doc_file = get_file_path(knowledge_base_id, '医院信息.txt')
    print('本地知识库文件医院信息', doc_file)
    doc_content = doc_hsp(hsp)
    print(doc_content)
    with open(doc_file, 'w') as f:
        f.write(doc_content)

    doc_file = get_file_path(knowledge_base_id, '套餐信息.txt')
    print('本地知识库文件套餐信息', doc_file)
    export_hsp_set_meals(knowledge_base_id, doc_file)

    vs_path = get_vs_path(knowledge_base_id)
    print('本地向量库目录', vs_path)
    if not os.path.exists(vs_path):
        os.makedirs(vs_path)

    app.init_knowledge_vector_store(doc_path, vs_path)


if __name__ == '__main__':
    args = parser.parse_args()
    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM(params=args_dict)
    llm_model_ins.set_history_len(LLM_HISTORY_LEN)
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(llm_model=llm_model_ins, embedding_model_path='/home/dev/team/m3e-base')

    result_data = db.get_collection("hsp_hospital").find_one({'organization_code': "5C6CC2CB199E0500010412CB"})
    # result_data = db.get_collection("hsp_hospital").find({'organization_code': "YY0000309218060"})
    print(result_data)
    init_knowledge_base(local_doc_qa, result_data)

    pass
