import pandas as pd

# 读取Excel文件
filename = r"/home/dev/team/langchain-ChatChat/knowledge_base/幼儿信息/content/1711012368266.xlsx"
data = pd.read_excel(filename)
# 解析用户提问并提取关键信息
target_position = "保教主任"

# 数据筛选
filtered_data = data[data['岗位'] == target_position]

# 输出结果
print(filtered_data[['姓名', '手机号']])