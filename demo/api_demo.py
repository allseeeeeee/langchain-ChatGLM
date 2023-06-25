import requests
if __name__ == '__main__':
    while True:
        query = input("Q: ")
        if 'EXIT' in query:
            break

        json_data = {
            "question": query,
            "knowledge_base_id": "医院知识库"
        }
        resp = requests.post("http://localhost:7861/local_doc_qa/local_doc_chat", json=json_data)
        print(resp.status_code)
        print(resp.text)
    pass
