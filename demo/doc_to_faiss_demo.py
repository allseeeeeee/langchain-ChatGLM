from pprint import pprint
import torch
from langchain import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from configs import model_config

device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
embeddings = HuggingFaceEmbeddings(model_name="/home/dev/team/langchain-ChatGLM/text2vec-large-chinese",
                                   model_kwargs={'device': device})
doc_path = '/home/dev/team/langchain-ChatGLM/demo/data/hsp_hospital.txt'
vs_path = '/home/dev/team/langchain-ChatGLM/demo/data/vector_store'

docs = []
with open(doc_path) as f:
    line = f.read()
    docs = line.split('\n')
print(docs)

documents = [Document(page_content=text, metadata={"source": doc_path}) for text in docs]

try:
    vector_store = FAISS.load_local(vs_path, embeddings)
except Exception as e:
    print(e)
    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local(vs_path)


query = "浙江省人民医院的具体地址在哪？"
related_docs_with_score = vector_store.similarity_search_with_score(query, k=5)
pprint(related_docs_with_score)

