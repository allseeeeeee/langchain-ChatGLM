import pymongo
from similarities import Similarity

vs_path = '/home/dev/team/langchain-ChatGLM/demo/data/vector_store'

client = pymongo.MongoClient("mongodb://root:password123@192.168.0.9:27017")
db = client.get_database("hplus_platform")

# 简单排除以下测试医院
ignores = ['6-30-1.0', '6-30-2.0', '成都630', '成都', '大瓜瓜', '愚人节2.0', '见素222', '西安中美111', '狂欢节1.0',
           'AA', '预约派单（请勿下单和修改数据）', 'YT医院', '势成一键康', '见素科技', '见素杭州', '其他', '叶茂青']
filter_hsp = lambda hsp_name: hsp_name not in ignores and '测试' not in hsp_name and '自动化' not in hsp_name \
              and '11' not in hsp_name and '22' not in hsp_name and hsp_name not in ignores
result_data = db.get_collection("hsp_hospital").find({'is_disable': False, 'is_off_line': False})

dicts = {line['name']: line['organization_code'] for line in result_data if filter_hsp(line['name'])}

# 增加关键字映射
dicts['浙江省人民医院'] = '5C6CC2CB199E0500010412CB'
docs = [line for line in dicts.keys()]

m = Similarity(model_name_or_path="/home/dev/team/text2vec-large-chinese", corpus=docs)

queries = ['我要去体检，请问省人民朝晖的地址在哪里？', '省人民朝晖的报告多久出？',
           '我约了省人民朝晖的体检，现在去还来得及吗？',
           '请问：浙江省人民医院朝晖院区的体检中心在几号楼几层？',
           '请问：省人民朝晖有入职体检吗？', '请问：浙江省人民医院有入职体检吗？用户在浙江省杭州市',
           '请问：浙江省人民医院有入职体检吗？用户预约了浙江省人民医院朝晖院区2023-06-07的健康体检',
           '请问浙江省人民医院周末可以体检吗？用户预约了浙江省人民医院朝晖院区2023-06-07的健康体检',
           "支持报告邮寄吗？用户预约了浙江省人民医院朝晖院区2023-06-07的健康体检",
           '请问浙江省人民医院周末可以体检吗？', '请问：浙江省人民医院有入职体检吗？',
           '请问：省人民医院有入职体检吗？', '请问：省人民医院有入职体检吗？用户在望江山',
           "周末要去哪里玩", "如何更换花呗绑定银行卡"]

for query in queries:
    print(f"\n{query}")
    # 用户提问简单排除自定义停用词，这些词过于普遍，移除不影响向量化匹配，不移除反而影响
    r = m.most_similar(query.replace("医院", "").replace("体检", "").replace("健康", ""), topn=5)
    # print(r)
    for key in r[0]:
        print(f"{docs[key]} > {dicts[docs[key]]} similarity : {r[0][key]}")

# 策略：
# 有相似度高于0.5的匹配，直接采信 TOP1
# 无相似度高于0.5的匹配，a. 直接采用默认知识库进行回答，并记录问题场景后续优化 ; b. 取TOP5 由用户进一步确认，并记录问题场景后续优化

# 分词影响向量化结果
# 1. 映射词典增加别名映射，提升命中率【 OK 】
# 2. 向量化前需定制分词逻辑, 自定义词典, 停用词（如：医院，体检，健康，检验，实验，查体）【 OK 】
