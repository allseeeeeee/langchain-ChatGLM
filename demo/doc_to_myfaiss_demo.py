from pprint import pprint
import torch
from langchain import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from chains import local_doc_qa
from configs import model_config
from vectorstores import MyFAISS

device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
embeddings = HuggingFaceEmbeddings(model_name="/home/dev/team/langchain-ChatGLM/text2vec-large-chinese",
                                   model_kwargs={'device': device})
doc_path = '/home/dev/team/langchain-ChatGLM/demo/data/hsp_hospital.txt'
vs_path = '/home/dev/team/langchain-ChatGLM/demo/data/vector_store'

# docs = local_doc_qa.load_file(doc_path)
# try:
#     vector_store = local_doc_qa.load_vector_store(vs_path, embeddings)
# except Exception as e:
#     print(e)
#     vector_store = MyFAISS.from_documents(docs, embeddings)
#     vector_store.add_documents(docs)
#     vector_store.save_local(vs_path)

vector_store = local_doc_qa.load_vector_store(vs_path, embeddings)

vector_store.chunk_size = model_config.CHUNK_SIZE
vector_store.chunk_conent = True
vector_store.score_threshold = 500

query = "浙江省人民医院的具体地址在哪？"
related_docs_with_score = vector_store.similarity_search_with_score_by_vector(embeddings.embed_query(query), k=5)
pprint(related_docs_with_score)

