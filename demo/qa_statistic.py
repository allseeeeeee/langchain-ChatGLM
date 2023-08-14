# -*-coding: utf-8 -*-
# @Time    : 2023-02-15
# @Author  : 罗景田
# 此py主要说明：

from demo import *


def mark_count():
    for cate in all_cate:
        print("{}|{}, {}|{},{},{}, {}|{},{},{}, {}|{},{},{}".format(
            cate,
            table.count_documents({"cate2": cate}),
            "mark0",
            table.count_documents({"cate2": cate, "mark0": "OK"}),
            table.count_documents({"cate2": cate, "mark0": "MI"}),
            table.count_documents({"cate2": cate, "mark0": "NO"}),
            "mark1",
            table.count_documents({"cate2": cate, "mark1": "OK"}),
            table.count_documents({"cate2": cate, "mark1": "MI"}),
            table.count_documents({"cate2": cate, "mark1": "NO"}),
            "mark4",
            table.count_documents({"cate2": cate, "mark4": "OK"}),
            table.count_documents({"cate2": cate, "mark4": "MI"}),
            table.count_documents({"cate2": cate, "mark4": "NO"}),
        ))


def distinct_question():
    for cate in all_cate:
        print(f"\n====={cate}=====\n")
        results = table.distinct("question", {"cate2": cate})
        for result in results:
            print(result)


if __name__ == '__main__':
    distinct_question()
    pass
