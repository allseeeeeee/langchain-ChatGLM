import jieba
import numpy as np
import faiss

# 定义实体列表
entity_list = ["浙江省人民医院朝晖院区", "浙江省人民医院望江山院区",
               "浙江省人民医院（朝晖院区）", "省人民医院", "省人民朝晖",
               "安徽省人民医院", "安徽省第二人民医院"]


# 对实体进行分词并生成词向量
def get_entity_vectors(entity_list):
    # 加载预训练词向量模型
    word_vectors = np.load("word_vectors.npy", allow_pickle=True).item()
    # 初始化分词器
    jieba.initialize()
    # 分词并计算平均词向量
    vectors = []
    for entity in entity_list:
        words = jieba.lcut(entity)
        vector = np.zeros(300)
        for word in words:
            if word in word_vectors:
                vector += word_vectors[word]
        vector /= len(words)
        vectors.append(vector)
    # 转换为faiss向量格式
    vectors = np.array(vectors).astype('float32')
    return vectors


# 构建索引并存储向量
def store_entity_vectors(entity_vectors):
    dim = entity_vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(entity_vectors)
    faiss.write_index(index, "entity.index")


# 加载索引并检索相似实体
def search_entities(query, k):
    # 加载索引
    index = faiss.read_index("entity.index")
    # 加载预训练词向量模型
    word_vectors = np.load("word_vectors.npy", allow_pickle=True).item()
    # 计算查询向量
    words = jieba.lcut(query)
    vector = np.zeros(300)
    for word in words:
        if word in word_vectors:
            vector += word_vectors[word]
    vector /= len(words)
    query_vector = np.expand_dims(vector, axis=0)
    query_vector = np.array(query_vector).astype('float32')
    # 检索相似实体
    D, I = index.search(query_vector, k)
    results = []
    for i in range(k):
        results.append(entity_list[I[0][i]])
    return results


# 存储实体向量索引
entity_vectors = get_entity_vectors(entity_list)
store_entity_vectors(entity_vectors)

# 查询相似实体并输出结果
query = "杭州省人民医院在哪"
k = 5
results = search_entities(query, k)
print("查询结果：")
for i, result in enumerate(results):
    print("{}. {}".format(i + 1, result))