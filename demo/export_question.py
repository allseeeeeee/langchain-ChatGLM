import json
import re

from demo import *

q_table = db.get_collection("00_qa_questions")


def from_files():
    path = 'data'
    questions_file = os.path.join(path, 'questions.txt')
    questions = []
    qa_files = [f for f in os.listdir(path) if f.startswith('QA-')]
    if len(qa_files) > 0:
        with open(questions_file, 'w', encoding='utf-8') as q:
            for file in qa_files:
                with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('问题：'):
                            question = line[3:]
                            if question not in questions:
                                questions.append(question)
                                q.write(question)
                                q.flush()


def from_db():
    result = table.aggregate([{"$group": {"_id": {"cate1": "$cate1", "cate2": "$cate2", "question": "$question"},
                                         "count": {"$sum": 1}}}])
    for item in result:
        print(type(item["_id"]), item["_id"], item["count"])
        count = q_table.count_documents(item["_id"])
        if count == 0:
            q_table.insert_one({**item["_id"], "count": item["count"], "tag": "QA"})
        else:
            print("skip save: ", item["_id"])
    pass


def print_qa():
    results = q_table.find({})
    for item in results:
        print(item)


def save_new_qa():
    qa = {"cate1": "医院", "cate2": "最晚到院", "question": "体检的最晚到院时间是什么时候？"}
    count = q_table.count_documents(qa)
    if count == 0:
        q_table.insert_one({**qa, "count": 1, "tag": "NEW"})


def create_qa_from_files():
    q_maps = [
        {
            "question": "医院是三甲的吗",
            "file": "data/q/a.txt",
            "hsps": ['浙江省人民医院朝晖院区', '树兰（杭州）医院', '兵器工业五二一医院体检科', '广州新海医院', '金沙医院',
                     '苏州一OO医院', '成都中医大健康管理中心', '武汉华中科技大学同济医学院医院']
        },
        {
            "question": "医院是三级的吗",
            "file": "data/q/b.txt",
            "hsps": ['浙江省人民医院朝晖院区', '兵器工业五二一医院体检科', '金沙医院', '苏州一OO医院']
        },
        {
            "question": "医院是公立三甲的吗",
            "file": "data/q/c.txt",
            "hsps": ['浙江省人民医院朝晖院区', '树兰（杭州）医院', '兵器工业五二一医院体检科', '杭州市第一人民医院',
                     '重庆市巴南区人民医院', '金沙医院', '苏州一OO医院', '成都中医大健康管理中心']
        },
        {
            "question": "医院的级别和等级是怎样的？",
            "file": "data/q/d.txt",
            "hsps": ['深圳市第三人民医院体检科']
        },
        {
            "question": "这家医院是公立医院吗",
            "file": "data/q/e.txt",
            "hsps": ['浙江省人民医院朝晖院区']
        },
        {
            "question": "医院是民营的吗",
            "file": "data/q/f.txt",
            "hsps": ['浙江省人民医院朝晖院区', '广东省第二中医院', '安徽省第二人民医院', '兵器工业五二一医院体检科',
                     '杭州市第一人民医院', '金沙医院', '苏州一OO医院']
        },
        {
            "question": "这家医院是公立的还是民营的？",
            "file": "data/q/g.txt",
            "hsps": ['浙江省人民医院朝晖院区']
        },
        {
            "question": "这家医院的体检报告是否具有权威性？",
            "file": "data/q/h.txt",
            "hsps": ['深圳市第三人民医院体检科']
        },
        {
            "question": "医院地址在哪里？",
            "file": "data/q/i.txt",
            "hsps": ['浙江省人民医院朝晖院区', '上海市东方医院南院', '广东省第二中医院', '深圳市第三人民医院体检科',
                     '兵器工业五二一医院体检科', '武汉华中科技大学同济医学院医院']
        },
        {
            "question": "体检中心的详细地址在哪里？",
            "file": "data/q/j.txt",
            "hsps": ['浙江省人民医院朝晖院区', '上海市东方医院南院', '广东省第二中医院', '深圳市第三人民医院体检科',
                     '安徽省第二人民医院', '兵器工业五二一医院体检科', '苏州一OO医院', '武汉华中科技大学同济医学院医院']
        },
        {
            "question": "我到医院了，体检中心在几栋？",
            "file": "data/q/k.txt",
            "hsps": ['浙江省人民医院朝晖院区', '上海市东方医院南院', '广东省第二中医院', '深圳市第三人民医院体检科',
                     '树兰（杭州）医院', '杭州市第一人民医院', '金沙医院']
        },
        {
            "question": "我到体检中心门口了，该去几楼体检？",
            "file": "data/q/l.txt",
            "hsps": ['浙江省人民医院朝晖院区', '上海市东方医院南院', '南宁市第一人民医院健康体检中心', '树兰（杭州）医院',
                     '广东省第二中医院', '深圳市第三人民医院体检科', '金沙医院']
        },
        {
            "question": "体检中心周几可以做体检？",
            "file": "data/q/m.txt",
            "hsps": ['浙江省人民医院朝晖院区', '上海市东方医院南院', '广东省第二中医院', '深圳市第三人民医院体检科',
                     '南宁市第一人民医院健康体检中心', '重庆市巴南区人民医院', '金沙医院']
        },
        {
            "question": "医院周六周日也可以体检吗",
            "file": "data/q/n.txt",
            "hsps": ['浙江省人民医院朝晖院区', '上海市东方医院南院', '广东省第二中医院', '深圳市第三人民医院体检科',
                     '树兰（杭州）医院', '兵器工业五二一医院体检科', '重庆市巴南区人民医院', '金沙医院']
        },
        {
            "question": "医院周末可以做体检吗？",
            "file": "data/q/o.txt",
            "hsps": ['浙江省人民医院朝晖院区', '上海市东方医院南院', '广东省第二中医院', '深圳市第三人民医院体检科',
                     '安徽省第二人民医院', '南宁市第一人民医院健康体检中心', '重庆市巴南区人民医院']
        },
        {
            "question": "医院体检中心的工作时间是？",
            "file": "data/q/p.txt",
            "hsps": ['浙江省人民医院朝晖院区', '上海市东方医院南院', '广东省第二中医院', '深圳市第三人民医院体检科',
                     '安徽省第二人民医院', '南宁市第一人民医院健康体检中心', '重庆市巴南区人民医院']
        },
        {
            "question": "几点开始体检",
            "file": "data/q/q.txt",
            "hsps": ['浙江省人民医院朝晖院区 ', '上海市东方医院南院', '金沙医院']
        },
        {
            "question": "医院下午可以做体检吗?",
            "file": "data/q/r.txt",
            "hsps": ['浙江省人民医院朝晖院区', '上海市东方医院南院', '广东省第二中医院', '深圳市第三人民医院体检科',
                     '安徽省第二人民医院', '南宁市第一人民医院健康体检中心', '重庆市巴南区人民医院']
        },
        {
            "question": "体检的最晚到院时间",
            "file": "data/q/s.txt",
            "hsps": ['深圳市第三人民医院体检科', '浙江省人民医院朝晖院区', '上海市东方医院南院', '金沙医院',
                     '重庆市巴南区人民医院', '树兰（杭州）医院', '兵器工业五二一医院体检科']
        }
    ]
    total = 0
    tag = "S01-0821"
    for qmap in q_maps:   # 问题映射
        question = qmap['question']
        print(question)
        with open(qmap['file'], 'r') as qa:
            for q in qa:  # 用同一个标准答案回答每一个扩展问题
                q = q.strip()
                for hsp in qmap['hsps']:   # 每个问题挨个医院问
                    print(hsp)
                    results = table.find({"question": question,
                                          "source_documents": re.compile(f".*{hsp}.*", re.IGNORECASE)})
                    results = list(results)
                    if len(results) == 0:
                        raise RuntimeError(f"请先补充样例问答: {question}")

                    for item in results:   # 至少找到标准答案
                        print(item)
                        table.update_one({"_id": item['_id']}, {"$set": {"tag": tag}})
                        to_save = {
                            "cate1": item['cate1'],
                            "cate2": item['cate2'],
                            "prompt_template": item['prompt_template'],
                            "response": item['response'],
                            "source_documents": item['source_documents'],
                            "question": q,
                        }
                        count = table.count_documents(to_save)
                        if count == 0:
                            # print("toSave")
                            inserted_result = table.insert_one({**to_save, "tag": tag}, )
                            print(inserted_result.inserted_id, q)
                        else:
                            print(f"问题已存在: {q}")

                        total += 1
    print(total)

    pass


if __name__ == '__main__':
    create_qa_from_files()
    pass
