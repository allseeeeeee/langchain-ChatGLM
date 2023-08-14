import json

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


if __name__ == '__main__':
    print_qa()
    pass
