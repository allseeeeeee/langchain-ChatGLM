import numpy as np
import gensim

# 预处理好的文本数据集路径
corpus_path = "data/corpus.txt"

# 加载文本数据集
corpus_file = open(corpus_path, "r", encoding="utf-8")
corpus = []
for line in corpus_file:
    corpus.append(line.split())

# 训练词向量模型
model = gensim.models.Word2Vec(corpus, vector_size=100, window=5, min_count=5, workers=4)

# 保存词向量模型
model.wv.save("data/word_vectors.bin")

# 使用gensim找最相近的词
most_similar = model.wv.most_similar(positive="癌症", topn=10)
print(most_similar)

# 加载词向量模型
model_wv = gensim.models.KeyedVectors.load("data/word_vectors.bin", mmap="r")

# 使用gensim找最相近的词
most_similar = model_wv.most_similar("癌症", topn=10)
print(most_similar)

# 获取所有向量
word_embedding = model_wv.vectors
np.save("data/word_vectors.npy", word_embedding)

weight_numpy = np.load(file="data/word_vectors.npy")
print(weight_numpy)