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
        tmp_files = os.path.join(doc_path, 'tmp_files')
        if os.path.exists(tmp_files):
            shutil.rmtree(tmp_files)
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
    if os.path.exists(vs_path):
        shutil.rmtree(vs_path)
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
    local_doc_qa.init_cfg(llm_model=None, embedding_model_path='/home/dev/team/text2vec-large-chinese')

    all_hsp = ["5C6CC2CB199E0500010412CB", 'YY0000337418065', 'YY0000322318065', '5D8495D05FBB69000130CD92',
               "5DBF8442B1379F0001C5E0C1", '607807F375FEA05011100CA7', '5DD42D5F4683AF0001688224',
               "YY0000316118065", "YY0000318718065", "YY0000333818065", "YY0000327418065", "YY0000320218065",
               "YY0000345918065", "61933992553DC843DCE256BC", "5D01B04538E4E30001B36A4D",
               "5C9DBFC9CC6A00000178C70B", "5DA6C2AD832802000159B247"
               ]

    for hsp in all_hsp:
        result_data = db.get_collection("hsp_hospital").find_one({'organization_code': hsp})
        # result_data = db.get_collection("hsp_hospital").find({'organization_code': "YY0000309218060"})
        print(result_data)
        init_knowledge_base(local_doc_qa, result_data)

    pass
