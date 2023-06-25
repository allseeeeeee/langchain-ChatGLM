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


if __name__ == '__main__':
    sys_tag = db.get_collection("hsp_hospital")
    print(sys_tag.find_one({}))

    export_hospital_name()
    pass
