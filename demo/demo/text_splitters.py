with open('../data/untitled.txt') as f:
    doc = f.read()

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=100,
    chunk_overlap=20,
    length_function=len,
)

texts = text_splitter.create_documents([doc])
print(texts)

for chunks in text_splitter.split_text(doc):
    print(">>>", chunks, "<<<")

print("====================================")
from textsplitter.chinese_text_splitter import ChineseTextSplitter
text_splitter = ChineseTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=100,
    chunk_overlap=20,
    length_function=len,
)

texts = text_splitter.create_documents([doc])
print(texts)

for chunks in text_splitter.split_text(doc):
    print(">>>", chunks, "<<<")