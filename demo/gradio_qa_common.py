import copy
import json
import os

import pymongo
import gradio as gr
import requests
import subprocess

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


def copy_to_clipboard(question, prompt, source_docs):
    try:
        info = prompt.replace("{question}", question) if question and len(question) > 0 else prompt
        info = info.replace("{context}", source_docs) if source_docs and len(source_docs) > 0 else info
        print(info)
        p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
        p.communicate(input=info.encode())
        return "问题复制成功"
    except Exception as e:
        print('复制出错啦', e)
        return "复制出错啦"


def submit_qa(choice_hsp=None, question=None, prompt=None, resp=None, cate1=None, cate2=None, cate3=None, cate4=None,
              source_docs=None, *args, **kwargs):
    # source_docs = kwargs.get('source_label')
    # print(args[5])
    if choice_hsp and 'common' != choice_hsp:
        json_data = {
            "knowledge_base_id": choice_hsp,
            "question": question,
            "prompt_template": prompt
        }
        resp = requests.post("http://localhost:7861/local_doc_qa/local_doc_chat", json=json_data).json()
        print(choice_hsp, resp)
        return resp['response'], resp['source_documents'], "提交问答成功"
    else:
        prompt = prompt.replace("{context}", source_docs) if source_docs and len(source_docs) > 0 else prompt
        json_data = {
            "streaming": False,
            "question": question,
            "prompt_template": prompt
        }
        resp = requests.post("http://localhost:7861/chat", json=json_data).json()
    print(choice_hsp, resp)
    return resp['response'], source_docs, "提交问答成功"


def load_qa(choice_hsp, qa_skip):
    global qa_idx, qa_total, qa, qa_filters
    qa_total = table.count_documents(qa_filters)
    qa_skip = 0 if qa_skip < 0 else qa_skip
    qa_skip = max(qa_total - 1, 0) if qa_skip >= qa_total - 1 else qa_skip
    print(qa_filters, qa_skip, qa_total)
    try:
        qa = table.find(qa_filters).skip(qa_skip).limit(1)[0]
        qa_idx = qa_skip
        print(qa)
        return qa['prompt_template'] if 'prompt_template' in qa else '', \
            qa['question'] if 'question' in qa else '', \
            qa['response'] if 'response' in qa else '', \
            qa['cate1'] if 'cate1' in qa else '', \
            qa['cate2'] if 'cate2' in qa else '', \
            qa['cate3'] if 'cate3' in qa else '', \
            qa['mark0'] if 'mark0' in qa else '', \
            qa['mark4'] if 'mark4' in qa else '', \
            qa['mark_6b0'] if 'mark_6b0' in qa else '', \
            qa['mark_6b1'] if 'mark_6b1' in qa else '', \
            qa['mark_6b11'] if 'mark_6b11' in qa else '', \
            qa['mark_6b12'] if 'mark_6b12' in qa else '', \
            qa['mark_6b13'] if 'mark_6b13' in qa else '', \
            qa['source_documents'] if 'source_documents' in qa else '', \
            f"总数：{qa_total}", qa_idx+1, '', f"加载成功", \
            qa['before_response_1'] if 'before_response_1' in qa else '', \
            qa['6b_resp0'] if '6b_resp0' in qa else '', \
            qa['6b_resp1'] if '6b_resp1' in qa else '', \
            qa['6b_resp_11'] if '6b_resp_11' in qa else '', \
            qa['6b_resp_12'] if '6b_resp_12' in qa else '', \
            qa['6b_resp_13'] if '6b_resp_13' in qa else '', \
            qa['after_response_1'] if 'after_response_1' in qa else ''
    except Exception as e:
        print('ERROR: >>>>> ', e)
        return "prompt_template", "question", "response", \
            "cate1", "cate2", "cate3", "mark0", "mark4", "mark-6b0", "mark-6b1", "mark-6b11", "mark-6b12", "mark-6b13",\
            "source_documents", f"总数：{qa_total}", qa_idx+1, '', f"无数据", \
            '', '', '', '', '', '', ''


def refresh_qa(choice_hsp, *args, **kwargs):
    global qa_idx
    return load_qa(choice_hsp, qa_idx)


def filter_change(filter_info, *args, **kwargs):
    try:
        filter_json = json.loads(filter_info)
    except Exception as e:
        filter_json = {}

    global qa_filters
    qa_filters = filter_json
    return "筛选条件已更新"


def load_qa_jump(jump_to, choice_hsp, *args, **kwargs):
    print('jump_to >> ', jump_to)
    return load_qa(choice_hsp, int(jump_to)-1)


def load_qa_prev(choice_hsp, *args, **kwargs):
    global qa_idx
    return load_qa(choice_hsp, qa_idx - 1)


def load_qa_next(choice_hsp, *args, **kwargs):
    global qa_idx
    return load_qa(choice_hsp, qa_idx + 1)


def modify_qa(choice_hsp=None, question=None, prompt=None, answer=None, cate1=None, cate2=None, cate3=None,
              mark0=None, mark1=None, mark2=None, mark3=None, mark4=None, mark5=None, mark6=None,
              source=None, *args, **kwargs):
    print(f"医院：{choice_hsp}")
    global qa
    result = table.find_one_and_update({"_id": qa['_id']},
                                       {"$set": {'question': question, 'response': answer,
                                                 'cate1': cate1, 'cate2': cate2, 'cate3': cate3, 'mark0': mark0,
                                                 'mark4': mark1, 'mark_6b0': mark2, 'mark_6b1': mark3, 'mark_6b11': mark4,
                                                 'mark_6b12': mark5, 'mark_6b13': mark6,
                                                 'prompt_template': prompt,
                                                 'source_documents': source}},
                                       return_document=pymongo.ReturnDocument.AFTER
                                       )
    print(result)
    qa = result
    return f"修改成功"


def save_new_qa(choice_hsp=None, question=None, prompt=None, answer=None, cate1=None, cate2=None, cate3=None,
                mark0=None, mark1=None, mark2=None, mark3=None, mark4=None, mark5=None, mark6=None,
                source=None, *args, **kwargs):
    print(f"医院：{choice_hsp}\n提示：{prompt}\n问题：{question}\n回答：{answer}")
    global qa, qa_idx, qa_total
    qa_new = copy.deepcopy(qa)
    if "_id" in qa_new:
        del qa_new['_id']
    qa_new['question'] = question
    qa_new['response'] = answer
    qa_new['prompt_template'] = prompt
    qa_new['cate1'] = cate1
    qa_new['cate2'] = cate2
    qa_new['cate3'] = cate3
    qa_new['mark0'] = mark0
    qa_new['mark4'] = mark1
    qa_new['mark_6b0'] = mark2
    qa_new['mark_6b1'] = mark3
    qa_new['mark_6b11'] = mark4
    qa_new['mark_6b12'] = mark5
    qa_new['mark_6b13'] = mark6
    qa_new['source_documents'] = source

    result = table.insert_one(qa_new)
    if result.inserted_id:
        qa_total += 1
    return refresh_qa(choice_hsp, qa_idx)


def delete_qa(choice_hsp=None, question=None, prompt=None, answer=None, *args, **kwargs):
    print(f"医院：{choice_hsp}\n提示：{prompt}\n问题：{question}\n回答：{answer}")
    global qa, qa_idx, qa_total
    table.delete_one({"_id": qa['_id']})
    qa_total -= 1
    return refresh_qa(choice_hsp, qa_idx)


if __name__ == '__main__':
    with gr.Blocks() as app:
        qa = table.find_one(qa_filters)
        qa_total = table.count_documents(qa_filters)
        print(qa)

        if qa is None:
            qa = {}

        with gr.Row():
            with gr.Column(scale=5):
                filter_box = gr.Textbox(label="筛选", value="{}", lines=1)
                with gr.Row():
                    guide = gr.Markdown(f"总数：{qa_total}")
                    qa_idx_tbox = gr.Number(value=qa_idx + 1, label='当前问答')
                    prev_btn = gr.Button(" < 前一个")
                    next_btn = gr.Button("下一个 > ")
                with gr.Row():
                    cate1_tbox = gr.Textbox(value=qa['cate1'] if 'cate1' in qa else '', label='cate1')  # cate1
                    mark0_tbox = gr.Textbox(value=qa['mark0'] if 'mark0' in qa else '', label='Mark0')  # mark0
                    mark1_tbox = gr.Textbox(value=qa['mark1'] if 'mark4' in qa else '', label='Mark1')  # mark4
                    mark2_tbox = gr.Textbox(value=qa['mark_6b0'] if 'mark_6b0' in qa else '', label='Mark 6B0')  # mark_6b0
                    mark3_tbox = gr.Textbox(value=qa['mark_6b1'] if 'mark_6b1' in qa else '', label='Mark 6B1')  # mark_6b1
                with gr.Row():
                    cate2_tbox = gr.Textbox(value=qa['cate2'] if 'cate2' in qa else '', label='cate2')  # cate2
                    cate3_tbox = gr.Textbox(value=qa['cate3'] if 'cate3' in qa else '', label='cate3')  # cate3
                    mark4_tbox = gr.Textbox(value=qa['mark_6b11'] if 'mark_6b11' in qa else '', label='Mark 6B11')  # mark_6b11
                    mark5_tbox = gr.Textbox(value=qa['mark_6b12'] if 'mark_6b12' in qa else '', label='Mark 6B12')  # mark_6b12
                    mark6_tbox = gr.Textbox(value=qa['mark_6b13'] if 'mark_6b13' in qa else '', label='Mark 6B13')  # mark_6b13

                with gr.Row():
                    refresh_btn = gr.Button("刷新问答")
                    modify_qa_btn = gr.Button("更新原问答", variant="primary")
                    save_new_qa_btn = gr.Button(" + 保存新问答 ", variant='secondary')
                    delete_qa_btn = gr.Button(" - 删除问答 ", variant='stop')
                question_textbox = gr.TextArea(label="问题", lines=1, value=qa['question'] if 'question' in qa else '')
                resp1_textbox = gr.TextArea(label="微调前回答2-6B", lines=1,
                                            value=qa['6b_resp0'] if '6b_resp0' in qa else '')
                resp2_textbox = gr.TextArea(label="微调后回答2-6BFB", lines=1,
                                            value=qa['6b_resp1'] if '6b_resp1' in qa else '')
                resp3_textbox = gr.TextArea(label="微调后回答2-6B11", lines=1,
                                            value=qa['6b_resp_11'] if '6b_resp_11' in qa else '')
                resp4_textbox = gr.TextArea(label="微调后回答2-6B12", lines=1,
                                            value=qa['6b_resp_12'] if '6b_resp_12' in qa else '')
                resp5_textbox = gr.TextArea(label="微调后回答2-6B13", lines=1,
                                            value=qa['6b_resp_13'] if '6b_resp_13' in qa else '')
                resp6_textbox = gr.TextArea(label="微调后回答int4", lines=1,
                                            value=qa['after_response_1'] if 'after_response_1' in qa else '')

            with gr.Column(scale=3):
                prompt_label = gr.TextArea(label="提示模板", lines=2,
                                           value=qa['prompt_template'] if 'prompt_template' in qa else '')
                source_label = gr.TextArea(label="参考信息", lines=4,
                                           value=qa['source_documents'] if 'source_documents' in qa else '')
                answer_textbox = gr.TextArea(label="标准回答", lines=1,
                                             value=qa['response'] if 'response' in qa else '')
                answer1_textbox = gr.TextArea(label="微调前回答", lines=1,
                                              value=qa['before_response_1'] if 'before_response_1' in qa else '')

                with gr.Row():
                    copy_btn = gr.Button("复制问题")
                    qa_btn = gr.Button("AI问答")
                choice_hsp_dropdown = gr.Textbox(label="当前知识库", value="common")
                ai_answer_textbox = gr.Textbox(label="AI问答", lines=1)
        gr.Markdown("**医院知识问答数据集编辑💰**: 医院通用知识. ")
        output_textbot = gr.Markdown("")
        inputs = [choice_hsp_dropdown, question_textbox, prompt_label, answer_textbox,
                  cate1_tbox, cate2_tbox, cate3_tbox, mark0_tbox, mark1_tbox, mark2_tbox, mark3_tbox,
                  mark4_tbox, mark5_tbox, mark6_tbox, source_label]
        outputs = [prompt_label, question_textbox, answer_textbox, cate1_tbox, cate2_tbox, cate3_tbox,
                   mark0_tbox, mark1_tbox, mark2_tbox, mark3_tbox, mark4_tbox, mark5_tbox, mark6_tbox,
                   source_label, guide, qa_idx_tbox, ai_answer_textbox, output_textbot, answer1_textbox,
                   resp4_textbox, resp5_textbox, resp6_textbox,
                   resp1_textbox, resp2_textbox, resp3_textbox]

        qa_btn.click(fn=submit_qa, inputs=inputs, outputs=[ai_answer_textbox, source_label, output_textbot])
        copy_btn.click(fn=copy_to_clipboard, inputs=[question_textbox, prompt_label, source_label],
                       outputs=output_textbot)
        filter_box.change(fn=filter_change, inputs=[filter_box] + inputs, outputs=output_textbot)
        refresh_btn.click(fn=refresh_qa, inputs=inputs, outputs=outputs)
        qa_idx_tbox.change(fn=load_qa_jump, inputs=[qa_idx_tbox] + inputs, outputs=outputs)
        prev_btn.click(fn=load_qa_prev, inputs=inputs, outputs=outputs)
        next_btn.click(fn=load_qa_next, inputs=inputs, outputs=outputs)

        modify_qa_btn.click(fn=modify_qa, inputs=inputs, outputs=output_textbot)
        save_new_qa_btn.click(fn=save_new_qa, inputs=inputs, outputs=outputs)
        delete_qa_btn.click(fn=delete_qa, inputs=inputs, outputs=outputs)

    app.launch(server_name="0.0.0.0")

