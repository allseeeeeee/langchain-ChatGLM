# -*-coding: utf-8 -*-
# @Time    : 2023-02-15
# @Author  : 罗景田
# 此py主要说明：
import time
import pymongo as pymongo

client = pymongo.MongoClient("mongodb://root:password123@192.168.0.9:27017")
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
  套餐标签：{setmeal['set_meal_cate_list']} 
  包含项目：{section_names} 
  套餐介绍：{setmeal['description'] if 'description' in setmeal else '无'}
"""
            file_object.write(setmeal_info)
            file_object.write("\n")
            print(setmeal_info)


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
    电子报告：{hsp['days_of_generate_digital_report'] + hsp['view_digital_report_url'] if hsp['have_digital_report'] else '不提供' }
    {item(hsp, 'intro', '简介')}
    """


def export_hsp_info(hsp_code: str = None, path: str = 'data'):
    result_data = db.get_collection("hsp_hospital").find_one({'organization_code': hsp_code})
    file = f'{path}/{hsp_code}_info.txt'
    with open(file, 'w', encoding='utf-8') as file_object:
        file_object.write(doc_hsp(result_data))
    pass


if __name__ == '__main__':
    sys_tag = db.get_collection("hsp_hospital")
    print(sys_tag.find_one({"organization_code": "5C6CC2CB199E0500010412CB"}))
    # export_hospital_name()
    export_hsp_info("5C6CC2CB199E0500010412CB")
    export_hsp_set_meals("5C6CC2CB199E0500010412CB")

    pass
