import gensim
import numpy as np

# 加载词向量模型
model = gensim.models.KeyedVectors.load("data/word_vectors.bin", mmap="r")

# 获取所有单词向量并保存为 Numpy 数组
word_vectors = {}
for word in model.vocab:
    word_vectors[word] = model[word]
np.save("data/word_vectors.npy", word_vectors)