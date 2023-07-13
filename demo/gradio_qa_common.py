import copy
import json
import os

import pymongo
import gradio as gr
import requests

auth = os.environ.get('usr+pwd')
if auth is None or len(auth) == 0:
    print("Please setup env params: [usr+pwd].  e.g: \nusr+pws=username:password")

client = pymongo.MongoClient(f"mongodb://{auth}@192.168.0.9:27017")
db = client.get_database("hplus_platform")
table = db.get_collection("00_chat_qa_common")

qa_idx = 0
qa_total = 0
qa = None
qa_filters = {}


def submit_qa(choice_hsp=None, question=None, prompt=None, *args, **kwargs):
    if choice_hsp and 'common' != choice_hsp:
        json_data = {
            "knowledge_base_id": choice_hsp,
            "question": question,
            "prompt_template": prompt
        }
        resp = requests.post("http://localhost:7861/local_doc_qa/local_doc_chat", json=json_data).json()
    else:
        json_data = {
            "streaming": False,
            "question": question,
            "prompt_template": prompt
        }
        resp = requests.post("http://localhost:7861/chat", json=json_data).json()
    print(choice_hsp, resp)
    return resp['response'], "\n\n".join(resp['source_documents']), '提交问答成功'


def load_qa(choice_hsp, qa_skip):
    global qa_idx, qa_total, qa, qa_filters
    qa_total = table.count_documents(qa_filters)
    qa_idx = 0 if qa_skip < 0 else qa_skip
    qa_idx = max(qa_total-1, 0) if qa_idx >= qa_total-1 else qa_idx

    qa = table.find(qa_filters).skip(qa_idx).limit(1)[0]
    print(qa)
    return qa['prompt_template'], qa['question'], qa['response'], "\n\n".join(qa['source_documents']), \
        f"总数：{qa_total}", qa_idx + 1, f"加载成功"


def refresh_qa(choice_hsp, *args, **kwargs):
    global qa_idx
    return load_qa(choice_hsp, qa_idx)


def filter_change(filter_info, *args, **kwargs):
    try:
        filter_json = json.loads(filter_info)
    except Exception as e:
        return "筛选条件格式非法"

    global qa_filters
    qa_filters = filter_json
    return "筛选条件已更新"


def load_qa_jump(jump_to, choice_hsp, *args, **kwargs):
    print('jump_to >> ', jump_to)
    global qa_idx
    qa_idx = int(jump_to)-1
    return load_qa(choice_hsp, qa_idx)


def load_qa_prev(choice_hsp, *args, **kwargs):
    global qa_idx
    return load_qa(choice_hsp, qa_idx - 1)


def load_qa_next(choice_hsp, *args, **kwargs):
    global qa_idx
    return load_qa(choice_hsp, qa_idx + 1)


def modify_qa(choice_hsp=None, question=None, prompt=None, answer=None, source=None, *args, **kwargs):
    print(f"医院：{choice_hsp}\n提示：{prompt}\n问题：{question}\n回答：{answer}")
    global qa
    result = table.update_one({"_id": qa['_id']}, {"$set": {'question': question, 'response': answer,
                                                            'prompt_template': prompt, 'source_documents': source}})
    if result.matched_count > 0:
        qa['question'] = question
        qa['response'] = answer
        qa['prompt_template'] = prompt
        qa['source_documents'] = source
    return "修改成功"


def save_new_qa(choice_hsp=None, question=None, prompt=None, answer=None, source=None, *args, **kwargs):
    print(f"医院：{choice_hsp}\n提示：{prompt}\n问题：{question}\n回答：{answer}")
    global qa, qa_total
    qa_new = copy.deepcopy(qa)
    if "_id" in qa_new:
        del qa_new['_id']
    qa_new['question'] = question
    qa_new['response'] = answer
    qa_new['prompt_template'] = prompt
    qa_new['source_documents'] = source

    result = table.insert_one(qa_new)
    if result.inserted_id:
        qa_total += 1
    return refresh_qa(choice_hsp)


def delete_qa(choice_hsp=None, question=None, prompt=None, answer=None, *args, **kwargs):
    print(f"医院：{choice_hsp}\n提示：{prompt}\n问题：{question}\n回答：{answer}")
    global qa, qa_total
    table.delete_one({"_id": qa['_id']})
    qa_total -= 1
    return refresh_qa(choice_hsp)


if __name__ == '__main__':
    with gr.Blocks() as app:
        qa = table.find_one(qa_filters)
        qa_total = table.count_documents(qa_filters)
        print(qa)

        if qa is None:
            qa = {
                "question": "",
                "response": "",
                "prompt_template": "",
                "source_documents": "",
            }

        gr.Markdown("**医院知识问答数据集编辑💰**: 医院通用知识. ")
        output_textbot = gr.Markdown("")
        with gr.Row():
            with gr.Column(scale=5):
                filter_box = gr.Textbox(label="筛选", value="{}", lines=1)
                question_textbox = gr.Textbox(label="问题", value=qa['question'], placeholder='请输入问题', lines=1)
                answer_textbox = gr.Textbox(label="回答", value=qa['response'], placeholder='回答', lines=1)
                with gr.Row():
                    guide = gr.Markdown(f"总数：{qa_total}")
                    qa_idx_tbox = gr.Number(value=qa_idx+1, label='当前问答')
                    prev_btn = gr.Button(" < 前一个")
                    next_btn = gr.Button("下一个 > ")
                with gr.Row():
                    refresh_btn = gr.Button("刷新问答")
                    modify_qa_btn = gr.Button("更新原问答", variant="primary")
                    save_new_qa_btn = gr.Button(" + 保存新问答 ", variant='secondary')
                    delete_qa_btn = gr.Button(" - 删除问答 ", variant='stop')

                qa_btn = gr.Button("AI问答")
                ai_answer_textbox = gr.Textbox(label="AI问答", lines=1)

            with gr.Column(scale=3):
                prompt_label = gr.Textbox(label="提示模板", value=qa['prompt_template'], lines=12)
                choice_hsp_dropdown = gr.Textbox(label="当前知识库", value="common")
                source_label = gr.Textbox(label="参考信息", value=qa['source_documents'])

        inputs = [choice_hsp_dropdown, question_textbox, prompt_label, answer_textbox, source_label]
        outputs = [prompt_label, question_textbox, answer_textbox, source_label, guide, qa_idx_tbox, output_textbot]

        qa_btn.click(fn=submit_qa, inputs=inputs, outputs=[ai_answer_textbox, source_label, output_textbot])
        refresh_btn.click(fn=refresh_qa, inputs=inputs, outputs=outputs)
        qa_idx_tbox.change(fn=load_qa_jump, inputs=[qa_idx_tbox] + inputs, outputs=outputs)
        filter_box.change(fn=filter_change, inputs=[filter_box] + inputs, outputs=output_textbot)
        prev_btn.click(fn=load_qa_prev, inputs=inputs, outputs=outputs)
        next_btn.click(fn=load_qa_next, inputs=inputs, outputs=outputs)

        modify_qa_btn.click(fn=modify_qa, inputs=inputs, outputs=output_textbot)
        save_new_qa_btn.click(fn=save_new_qa, inputs=inputs, outputs=outputs)
        delete_qa_btn.click(fn=delete_qa, inputs=inputs, outputs=outputs)

    app.launch()
    pass
