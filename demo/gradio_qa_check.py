import copy
import json
import os

import pymongo
import gradio as gr
import requests

from api import get_file_path

client = pymongo.MongoClient(f"mongodb://{os.environ.get('usr+pwd')}@192.168.0.9:27017")
db = client.get_database("hplus_platform")
table = db.get_collection("00_chat_qa")

all_hsp = ["5C6CC2CB199E0500010412CB", 'YY0000337418065', 'YY0000322318065', '5D8495D05FBB69000130CD92',
           "5DBF8442B1379F0001C5E0C1", '607807F375FEA05011100CA7', '5DD42D5F4683AF0001688224',
           "YY0000316118065", "YY0000318718065", "YY0000333818065", "YY0000327418065", "YY0000320218065",
           "YY0000345918065", "61933992553DC843DCE256BC", "5D01B04538E4E30001B36A4D",
           "5C9DBFC9CC6A00000178C70B", "5DA6C2AD832802000159B247"
           ]
qa_idx = 0
qa_total = 0
qa = None


def read_file(path):
    with open(path, 'r', encoding="utf-8") as f:
        file_content = f.read()
    return file_content


def save_file(path, content):
    with open(path, 'w', encoding="utf-8") as f:
        f.write(content)


def save_hsp_file(choice_hsp, hsp_info):
    doc_file = get_file_path(choice_hsp, '医院信息.txt')
    save_file(doc_file, hsp_info)
    return f"保存成功：{doc_file}"


def save_pkg_file(choice_hsp, pkg_info):
    doc_file = get_file_path(choice_hsp, '套餐信息.txt')
    save_file(doc_file, pkg_info)
    return f"保存成功：{doc_file}"


def save_kb(choice_hsp):
    resp = requests.post("http://localhost:7861/local_doc_qa/reinit_kb",
                         params={"knowledge_base_id": choice_hsp}).json()
    print(choice_hsp, resp)
    return resp


def ref_kb(choice_hsp, question, *args, **kwargs):
    print(f"医院：{choice_hsp}\n问题：{question}")
    resp = requests.post("http://localhost:7861/local_doc_qa/ref_kb",
                         json={"knowledge_base_id": choice_hsp, "query": question}).json()
    print(choice_hsp, resp)
    return resp['msg'], "修改成功"


def submit_qa(choice_hsp=None, question=None, prompt=None, *args, **kwargs):
    json_data = {
        "knowledge_base_id": choice_hsp,
        "question": question,
        "prompt_template": prompt
    }
    resp = requests.post("http://localhost:7861/local_doc_qa/local_doc_chat", json=json_data).json()
    print(choice_hsp, resp)
    return resp['response'], "\n\n".join(resp['source_documents']), '提交问答成功'


def hsp_change(choice_hsp, *args, **kwargs):
    print(f"切换医院：{choice_hsp}")
    global qa_idx, qa_total, qa
    qa_idx = 0
    qa_total = table.count_documents({"hsp_code": choice_hsp})
    qa = table.find({"hsp_code": choice_hsp}).skip(qa_idx).limit(1)[0]
    print(qa)

    return qa['prompt_template'], qa['question'], qa['response'], "\n\n".join(qa['source_documents']), \
        f"总数：{qa_total}", qa_idx + 1, f"切换医院{choice_hsp}成功", \
        read_file(get_file_path(choice_hsp, '医院信息.txt')), \
        read_file(get_file_path(choice_hsp, '套餐信息.txt'))


def load_qa(choice_hsp, qa_skip):
    global qa_idx, qa_total, qa
    qa_total = table.count_documents({"hsp_code": choice_hsp})
    qa_idx = qa_idx if qa_skip >= 0 else 0
    qa_idx = qa_total-1 if qa_skip >= qa_total-1 else qa_skip

    qa = table.find({"hsp_code": choice_hsp}).skip(qa_idx).limit(1)[0]
    print(qa)

    return qa['prompt_template'], qa['question'], qa['response'], "\n\n".join(qa['source_documents']), \
        f"总数：{qa_total}", qa_idx + 1, f"加载成功"


def refresh_qa(choice_hsp, *args, **kwargs):
    global qa_idx
    return load_qa(choice_hsp, qa_idx)


def load_qa_jump(jump_to, choice_hsp, *args, **kwargs):
    print('jump_to >> ', jump_to)
    global qa_idx
    qa_idx = int(jump_to)-1
    return load_qa(choice_hsp, qa_idx)


def load_qa_prev(choice_hsp, *args, **kwargs):
    global qa_idx
    return load_qa(choice_hsp, qa_idx-1)


def load_qa_next(choice_hsp, *args, **kwargs):
    global qa_idx
    return load_qa(choice_hsp, qa_idx + 1)


def modify_qa(choice_hsp=None, question=None, prompt=None, answer=None, *args, **kwargs):
    print(f"医院：{choice_hsp}\n提示：{prompt}\n问题：{question}\n回答：{answer}")
    global qa
    result = table.update_one({"_id": qa['_id']}, {"$set": {'response': answer}})
    if result.matched_count > 0:
        qa['response'] = answer
    return "修改成功"


def save_new_qa(choice_hsp=None, question=None, prompt=None, answer=None, *args, **kwargs):
    print(f"医院：{choice_hsp}\n提示：{prompt}\n问题：{question}\n回答：{answer}")
    global qa, qa_total
    qa_new = copy.deepcopy(qa)
    if "_id" in qa_new:
        del qa_new['_id']
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
        hsp = all_hsp[0]
        qa = table.find_one({"hsp_code": hsp})
        qa_total = table.count_documents({"hsp_code": hsp})
        print(qa)

        gr.Markdown("**医院知识问答数据集编辑💰**: 选择医院，并根据问题进行答复的人工核对，点击提交进行保存. ")

        with gr.Row():
            with gr.Column():
                choice_hsp_dropdown = gr.Dropdown(label="当前知识库（医院）", choices=all_hsp, value=hsp)
                prompt_label = gr.Textbox(label="提示模板", value=qa['prompt_template'])
                question_textbox = gr.Textbox(label="问题", value=qa['question'], placeholder='请输入问题', lines=2)
                answer_textbox = gr.Textbox(label="回答", value=qa['response'], placeholder='AI回答', lines=2)
                with gr.Row():
                    guide = gr.Markdown(f"总数：{qa_total}")
                    qa_idx_tbox = gr.Number(value=qa_idx + 1, label='当前问答')
                    prev_btn = gr.Button(" < 前一个")
                    next_btn = gr.Button("下一个 > ")

                with gr.Row():
                    refresh_btn = gr.Button("刷新问答")
                    qa_btn = gr.Button("AI问答")
                    modify_qa_btn = gr.Button("更新原问答", variant="primary")
                    save_new_qa_btn = gr.Button(" + 保存新问答 ")
                    delete_qa_btn = gr.Button(" - 删除问答 ")
                output_textbot = gr.TextArea(label="结果")
            with gr.Column():
                with gr.Tab("医院信息", elem_id="hsp") as hsp_tab:
                    hsp_info_box = gr.TextArea(value=read_file(get_file_path(hsp, '医院信息.txt')),
                                               show_label=False, max_lines=10)
                    save_hsp_btn = gr.Button("保存医院信息")
                with gr.Tab("套餐信息", elem_id="pkg") as pkg_tab:
                    pkg_info_box = gr.TextArea(value=read_file(get_file_path(hsp, '套餐信息.txt')),
                                               show_label=False, max_lines=10)
                    save_pkg_btn = gr.Button("保存套餐信息")
                with gr.Row():
                    save_kb_btn = gr.Button("更新知识库")
                    ref_kb_btn = gr.Button("知识匹配")
                source_label = gr.Textbox(label="参考信息", value="\n\n".join(qa['source_documents']))

        inputs = [
            choice_hsp_dropdown, question_textbox, prompt_label, answer_textbox, hsp_info_box, pkg_info_box
        ]
        outputs = [prompt_label, question_textbox, answer_textbox, source_label, guide, qa_idx_tbox, output_textbot]

        choice_hsp_dropdown.change(fn=hsp_change, inputs=inputs, outputs=outputs + [hsp_info_box, pkg_info_box])

        qa_btn.click(fn=submit_qa, inputs=inputs, outputs=[answer_textbox, source_label, output_textbot])
        refresh_btn.click(fn=refresh_qa, inputs=inputs, outputs=outputs)
        qa_idx_tbox.change(fn=load_qa_jump, inputs=[qa_idx_tbox] + inputs, outputs=outputs)
        prev_btn.click(fn=load_qa_prev, inputs=inputs, outputs=outputs)
        next_btn.click(fn=load_qa_next, inputs=inputs, outputs=outputs)

        modify_qa_btn.click(fn=modify_qa, inputs=inputs, outputs=output_textbot)
        save_new_qa_btn.click(fn=save_new_qa, inputs=inputs, outputs=outputs)

        save_hsp_btn.click(fn=save_hsp_file, inputs=[choice_hsp_dropdown, hsp_info_box], outputs=output_textbot)
        save_pkg_btn.click(fn=save_pkg_file, inputs=[choice_hsp_dropdown, pkg_info_box], outputs=output_textbot)
        save_kb_btn.click(fn=save_kb, inputs=[choice_hsp_dropdown], outputs=output_textbot)
        ref_kb_btn.click(fn=ref_kb, inputs=inputs, outputs=[source_label, output_textbot])

    app.launch()
    pass
