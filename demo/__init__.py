import os
import pymongo as pymongo
import re

auth = os.environ.get('usr+pwd')
if auth is None or len(auth) == 0:
    raise EnvironmentError("Please setup env params: [usr+pwd].  e.g: \nusr+pws=username:password")

client = pymongo.MongoClient(f"mongodb://{auth}@192.168.0.9:27017")
db = client.get_database("hplus_platform")
table = db.get_collection("00_chat_qa_common")

all_cate: list[str] = ["医院", "体检", "体检人群", "体检项目", "空腹", "发票",
                       "类型", "地址", "环境", "工作日", "工作时间", "最晚到院", "T规则", "体检时长", "二次预约",
                       "体检流程", "注意事项", "医保", "早餐", "体检售后",
                       "报告获取", "报告时长", "电子报告", "报告邮寄", "报告解读",
                       "套餐推荐", "套餐", "套餐加项"]