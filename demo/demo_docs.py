import asyncio
import os
import shutil

import pymongo

from api import get_folder_path, list_docs, get_vs_path, get_file_path
from chains.local_doc_qa import LocalDocQA
from models.loader import LoaderCheckPoint
import models.shared as shared
from models.loader.args import parser

# LLM input history length
LLM_HISTORY_LEN = 3


def list_knowledge_base(knowledge_base_id):
    loop = asyncio.get_event_loop()
    docs = loop.run_until_complete(list_docs(knowledge_base_id))
    loop.close()

    print(docs)


def item(hsp, key, title):
    return f"{title}: {hsp[key]}" if key in hsp else ""


def doc_hsp(hsp):
    return f"""
    类型：{hsp['hospital_type'] + '医院'}
    级别：{hsp['primary_hsp_level']}{hsp['secondary_hsp_level']}
    地址：{hsp['province']}{hsp['city']}{hsp['district']}{hsp['address']}
    工作日：{hsp['work_day']}
    {item(hsp, 'desc_of_work_time', '工作时间')} {item(hsp, 'reception_deadline_per_day', '最晚到院')}
    {item(hsp, 'reserve_notice', '体检须知')}
    {item(hsp, 'examination_notice_html', '体检注意事项')}
    {item(hsp, 'report_obtain_desc', '报告领取')}
    {item(hsp, 'days_of_generate_report', '报告出具天数')}
    {item(hsp, 'examination_notice_html', '体检注意事项')}
    电子报告：{hsp['days_of_generate_digital_report'] + hsp['view_digital_report_url'] if hsp['have_digital_report'] else '不提供' }
    {item(hsp, 'intro', '简介')}
    """


def init_knowledge_base(app, hsp):
    doc_content = doc_hsp(hsp)
    print(doc_content)
    knowledge_base_id = hsp['organization_code']
    doc_path = get_folder_path(knowledge_base_id)
    print('本地知识库目录', doc_path)
    if os.path.exists(doc_path):
        # 先删除主要在于tmp_files/load_files.txt会附加重复信息
        shutil.rmtree(doc_path)
        os.makedirs(doc_path)

    doc_file = get_file_path(knowledge_base_id, '医院信息.txt')
    print('本地知识库文件', doc_file)
    with open(doc_file, 'w') as f:
        f.write(doc_content)

    vs_path = get_vs_path(knowledge_base_id)
    print('本地向量库目录', vs_path)
    if not os.path.exists(vs_path):
        os.makedirs(vs_path)

    app.init_knowledge_vector_store(doc_path, vs_path)


if __name__ == '__main__':
    args = parser.parse_args()
    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()
    llm_model_ins.set_history_len(LLM_HISTORY_LEN)
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(llm_model=llm_model_ins)

    client = pymongo.MongoClient("mongodb://root:password123@192.168.0.9:27017")
    db = client.get_database("hplus_platform")
    result_data = db.get_collection("hsp_hospital").find({'organization_code': "YY0000309718060"})
    # result_data = db.get_collection("hsp_hospital").find({'organization_code': "YY0000309218060"})
    print(result_data[0])
    init_knowledge_base(local_doc_qa, result_data[0])

    pass
