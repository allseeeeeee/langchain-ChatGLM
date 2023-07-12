
from similarities import Similarity

doc_path = '/home/dev/team/langchain-ChatGLM/demo/data/hsp_hospital.txt'
vs_path = '/home/dev/team/langchain-ChatGLM/demo/data/vector_store'

docs = []
with open(doc_path) as f:
    line = f.read()
    docs = line.split('\n')

# dicts = {str(i): doc for i, doc in enumerate(docs)}

m = Similarity(model_name_or_path="/home/dev/team/text2vec-large-chinese",
               corpus=docs)

queries = ['我要去体检，请问省人民朝晖的地址在哪里？', '省人民朝晖的报告多久出？', '我约了省人民朝晖的体检，现在去还来得及吗？',
           '请问：浙江省人民医院朝晖院区的体检中心在几号楼几层？',
           '请问：浙江省人民医院有入职体检吗？', '请问：浙江省人民医院有入职体检吗？用户预约了浙江省人民医院朝晖院区2023-06-07的健康体检',
           '请问浙江省人民医院周末可以体检吗？', '请问浙江省人民医院周末可以体检吗？用户预约了浙江省人民医院朝晖院区2023-06-07的健康体检',
           "支持报告邮寄吗？用户预约了浙江省人民医院朝晖院区2023-06-07的健康体检",
           "周末要去哪里玩", "如何更换花呗绑定银行卡"]
for query in queries:
    print(f"\n{query}")
    # for sentence in sentences:
    r = m.most_similar(query, topn=5)
    for key in r[0]:
        print(f"{query} > {docs[key]} similarity : {r[0][key]}")

# 策略：
# 有相似度高于0.5的匹配，直接采信 TOP 1
# 无相似度高于0.5的匹配，取TOP 5，由用户进一步确认


