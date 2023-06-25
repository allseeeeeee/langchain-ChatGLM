from sentence_transformers import SentenceTransformer, util

# model = SentenceTransformer('GanymedeNil/text2vec-large-chinese')
model = SentenceTransformer('/home/dev/team/text2vec-large-chinese')

# Our sentences we like to encode
sentences = ['省人民医院', '浙江省人民医院', '浙江省人民医院朝晖院区', '浙江省人民医院（朝晖院区）',
             '浙江省人民医院望江山院区', '浙江省人民医院（望江山院区）', '浙江省第二人民医院', '杭州市第二人民医院',
             '安徽省人民医院', '湖南省人民医院', '广东省人民医院', '上海市人民医院', '重庆市人民医院']

# Sentences are encoded by calling model.encode()
embeddings = model.encode(sentences)

# Print the embeddings
# for sentence, embedding in zip(sentences, embeddings):
#     print(f"\nSentence: {sentence}， Embedding: {embedding}", )

# Sentences are encoded by calling model.encode()
query = "报告多久可以出？我预约了浙江省人民医院2023-06-06的体检"
emb1 = model.encode(query)
for sentence, embedding in zip(sentences, embeddings):
    print(f"{sentence} Cosine-Similarity: {util.cos_sim(emb1, embedding)}")

