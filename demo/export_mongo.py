# -*-coding: utf-8 -*-
# @Time    : 2023-02-15
# @Author  : 罗景田
# 此py主要说明：
import os
import re
import random

import pymongo as pymongo
import jsonlines

client = pymongo.MongoClient(f"mongodb://{os.environ.get('usr+pwd')}@192.168.0.9:27017")
db = client.get_database("hplus_platform")

def export_hospital_name():
    """导出医院数据"""
    # 简单排除以下测试医院
    ignores = ['6-30-1.0', '6-30-2.0', '成都630', '成都', '大瓜瓜', '愚人节2.0', '见素222', '西安中美111', '狂欢节1.0',
               'AA', '预约派单（请勿下单和修改数据）', 'YT医院', '势成一键康', '见素科技', '见素杭州', '其他', '叶茂青']
    filter_hsp = lambda hsp_name: hsp_name not in ignores and '测试' not in hsp_name and '自动化' not in hsp_name \
                                  and '11' not in hsp_name and '22' not in hsp_name and hsp_name not in ignores
    result_data = db.get_collection("hsp_hospital").find({'is_disable': False, 'is_off_line': False})

    hsp_names = "data/hsp_hospital.txt"
    idx = 0
    with open(hsp_names, 'w', encoding='utf-8') as file_object:
        for line in result_data:
            hsp_name = line['name']
            if filter_hsp(hsp_name):
                line_data = f"{hsp_name}"
                print(idx, line_data)
                if idx != 0:
                    file_object.write("\n")
                file_object.write(line_data)
                idx += 1
    pass


def item(hsp, key, title):
    return f"{title}: {hsp[key]}" if key in hsp else ""


def export_hsp_set_meals(hsp_code: str = None, path: str = 'data'):
    assert hsp_code is not None, "医院编码不能为空"
    file_seetmeals = f'{path}/{hsp_code}_setmeals.txt' if path is None else path
    with open(file_seetmeals, 'w', encoding='utf-8') as file_object:
        setmeals = db.get_collection("hsp_set_meal").find({"hsp_code": hsp_code, "state": 0})
        for setmeal in setmeals:
            # print(setmeal)
            sections = db.get_collection('hsp_section').find({"code": {"$in": setmeal['hsp_section_code_list']}})
            section_names = "#".join([section['section_name'] for section in sections])
            # print(section_names)
            print("..........")
            setmeal_info = f"""
套餐编码：{setmeal['code']} 套餐名称：{setmeal['name']} 套餐别名：{setmeal['alias']} 套餐价格：{setmeal['hsp_price']} 
  适用性别：{setmeal['gender']} 适用婚姻状态：{setmeal['marriage']} 适用年龄：{setmeal['fit_age']}
  包含项目：{section_names} 
"""
            file_object.write(setmeal_info)
            file_object.write("\n")
            print(setmeal_info)


def doc_hsp(hsp):
    return f"""
医院名称：{hsp['name']}
医院类型：{hsp['hospital_type']}{hsp['primary_hsp_level']}{hsp['secondary_hsp_level']}
医院地址：{hsp['province']}{hsp['city']}{hsp['district']}{hsp['address']}
体检工作日：{hsp['work_day']}
{item(hsp, 'desc_of_work_time', '体检工作时间')} {item(hsp, 'reception_deadline_per_day', '最晚到院时间')}
{item(hsp, 'reserve_notice', '体检须知')}
{item(hsp, 'examination_notice_html', '体检注意事项')}
{item(hsp, 'report_obtain_desc', '报告领取')}
{item(hsp, 'days_of_generate_report', '报告出具天数')}
电子报告：{hsp['days_of_generate_digital_report'] + hsp['view_digital_report_url'] if hsp['have_digital_report'] else '不提供' }
{item(hsp, 'intro', '医院简介')}
"""


def export_hsp_info(hsp_code: str = None, path: str = 'data'):
    result_data = db.get_collection("hsp_hospital").find_one({'organization_code': hsp_code})
    print(doc_hsp(result_data))
    file = f'{path}/{hsp_code}_info.txt'
    with open(file, 'w', encoding='utf-8') as file_object:
        file_object.write(doc_hsp(result_data))
    pass


def split_qa_prompt():
    qa_table = db.get_collection("00_chat_qa_common")
    datasets = qa_table.find({"source_documents": {"$ne": ""}})
    # pattern = r"(已知信息：\n)([\s\S]*?)\n(问题是：{question}|请使用中文回答[\s\S]*?问题是：{question})"
    for data in datasets:
        # prompts = data['prompt_template']
        # if "请使用中文回答。问题是：{question}" == prompts\
        #         or "请用中文进行简洁和专业的回答用户的问题。\n问题是：{question}" == prompts:
        #     continue
        #
        # known_info = re.findall(pattern, prompts)
        # if len(known_info) > 0:
        #     context = re.sub(pattern, r"\1{context}\n\n\3", prompts)
        #     update = {
        #         "source_documents": known_info[0][1],
        #         "prompt_template": context
        #     }
        #     print(context)
        #     print(update)
        #     qa_table.update_one({"_id": data['_id']}, update={"$set": update})
        # else:
        #     print(data)
        #     print(prompts)
        print(data['source_documents'])
        print("------------------------------")
    pass


def export_train():
    result_data = db.get_collection("00_chat_qa_common").find({})
    data = list(result_data)
    validation_size = int(0.1 * len(data))
    validation_data = random.sample(data, validation_size)
    for line_item in validation_data:
        data.remove(line_item)

    prompt = """问题是：{question}
根据已知信息回答：
{context}
"""

    with jsonlines.open("data/train_ho.json", 'w') as f:
        for line in data:
            question = line['question'] if 'question' in line else ''
            source_documents = line['source_documents'] if 'source_documents' in line else ''
            # prompt = line['prompt_template'] if 'prompt_template' in line else ''
            response = line['response'] if 'response' in line else ''
            line_item = {
                'content': prompt.replace('{context}', source_documents).replace('{question}', question),
                'summary': response
            }
            f.write(line_item)

    with jsonlines.open("data/validation_ho.json", 'w') as f:
        for line in validation_data:
            question = line['question'] if 'question' in line else ''
            source_documents = line['source_documents'] if 'source_documents' in line else ''
            # prompt = line['prompt_template'] if 'prompt_template' in line else ''
            response = line['response'] if 'response' in line else ''
            line_item = {
                'content': prompt.replace('{context}', source_documents).replace('{question}', question),
                'summary': response
            }
            f.write(line_item)
    pass


def max_qa_len():
    data = db.get_collection("00_chat_qa_common").find({})
    max_q_len = 0
    max_a_len = 0
    summary_q = {}
    summary_a = {}

    prompt = """问题是：{question}
    根据已知信息回答：
    {context}
    """

    for line in data:
        question = line['question'] if 'question' in line else ''
        source_documents = line['source_documents'] if 'source_documents' in line else ''
        # prompt = line['prompt_template'] if 'prompt_template' in line else ''
        final_a = line['response'] if 'response' in line else ''
        final_q = prompt.replace('{context}', source_documents).replace('{question}', question)

        q_len = len(final_q)
        a_len = len(final_a)

        if str(q_len) in summary_q:
            summary_q[str(q_len)] = summary_q[str(q_len)] + 1
        else:
            summary_q[str(q_len)] = 1

        if str(a_len) in summary_a:
            summary_a[str(a_len)] = summary_a[str(a_len)] + 1
        else:
            summary_a[str(a_len)] = 1

        if q_len > max_q_len:
            max_q_len = q_len
        if a_len > max_a_len:
            max_a_len = a_len

    print("最大问题长度:", max_q_len)
    print("最大回答长度:", max_a_len)
    print("summary_q:", summary_q)
    print("summary_a:", summary_a)

    # 最大问题长度: 2744
    # 最大回答长度: 1338

    pass


if __name__ == '__main__':
    # sys_tag = db.get_collection("hsp_hospital")
    # print(sys_tag.find_one({"organization_code": "5C6CC2CB199E0500010412CB"}))
    # export_hospital_name()
    # export_hsp_info("5C6CC2CB199E0500010412CB")
    # export_hsp_set_meals("5C6CC2CB199E0500010412CB")
    # split_qa_prompt()

    # pattern = r"(已知信息：\n)([\s\S]*?)\n(问题是：{question}|根据上述已知信息[\s\S]*?问题是：{question})"
    # prompt = "已知信息：\n医院名称：浙江省人民医院朝晖院区 \n不支持报告邮寄\n根据上述已知信息，简洁专业。用户问题是：{question}"
    # known_info = re.findall(pattern, prompt)
    # print(known_info[0][1])
    # context = re.sub(pattern, r"\1{context}\n\n\3", prompt)
    # print(context)
    export_train()
    # max_qa_len()
    pass
