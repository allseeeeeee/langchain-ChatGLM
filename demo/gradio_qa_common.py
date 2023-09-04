import json

import gradio as gr
import requests
from bson import ObjectId

from demo import *


def copy_to_clipboard(question, prompt, source_docs):
    import subprocess
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


def submit_qa(choice_hsp=None, question=None, source_docs=None, prompt=None, *args, **kwargs):
    print("submit_qa", args, kwargs)
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


def load_qa(filter_json, qa_idx):
    print("load_qa", filter_json, qa_idx)
    query = json.loads(filter_json)
    total = table.count_documents(query)
    qa_skip = 0 if qa_idx < 0 else qa_idx
    qa_skip = max(total - 1, 0) if qa_skip >= total - 1 else qa_skip
    qa = table.find(query).skip(qa_skip).limit(1)[0] or {}
    print(qa, qa_skip, total)
    # return 的顺序参考 outputs 的定义
    return (qa['prompt_template'] if 'prompt_template' in qa else '',  # prompt_label
            qa['question'] if 'question' in qa else '',  # question_textbox
            qa['response'] if 'response' in qa else '',  # answer_textbox
            qa['cate1'] if 'cate1' in qa else '',
            qa['cate2'] if 'cate2' in qa else '',
            qa['cate3'] if 'cate3' in qa else '',
            qa['mark_6bi4_0'] if 'mark_6bi4_0' in qa else '',      # mark0
            qa['mark_6bfb_0'] if 'mark_6bfb_0' in qa else '',      # mark1
            qa['mark02_6bfb_4'] if 'mark02_6bfb_4' in qa else '',  # mark2
            qa['mark03_6bfb_1'] if 'mark03_6bfb_1' in qa else '',  # mark3
            qa['mark03_6bfb_2'] if 'mark03_6bfb_2' in qa else '',  # mark4
            qa['mark03_6bfb_3'] if 'mark03_6bfb_3' in qa else '',  # mark5
            qa['mark01_6bfb_1'] if 'mark01_6bfb_1' in qa else '',  # mark6
            qa['mark02_6bfb_1'] if 'mark02_6bfb_1' in qa else '',  # mark7
            qa['mark04_6bi4_1'] if 'mark04_6bi4_1' in qa else '',  # mark8
            qa['mark04_6bi4_2'] if 'mark04_6bi4_2' in qa else '',  # mark9
            qa['mark04_6bi4_3'] if 'mark04_6bi4_3' in qa else '',  # mark10
            qa['source_documents'] if 'source_documents' in qa else '',  # source_label
            gr.Slider.update(value=min(qa_skip+1, total), maximum=total, info=f"问题总数： {total}"),
            gr.Textbox.update(value=str(qa['_id']), interactive=False),  # ObjectId
            'ai_answer_textbox',
            "output_textbox: 加载成功",
            qa['resp_6bi4_0'] if 'resp_6bi4_0' in qa else '',      # resp0_textbox
            qa['resp_6bfb_0'] if 'resp_6bfb_0' in qa else '',      # resp1_textbox
            qa['resp02_6bfb_4'] if 'resp02_6bfb_4' in qa else '',  # resp2_textbox
            qa['resp03_6bfb_1'] if 'resp03_6bfb_1' in qa else '',  # resp3_textbox
            qa['resp03_6bfb_2'] if 'resp03_6bfb_2' in qa else '',  # resp4_textbox
            qa['resp03_6bfb_3'] if 'resp03_6bfb_3' in qa else '',  # resp5_textbox
            qa['resp01_6bfb_1'] if 'resp01_6bfb_1' in qa else '',  # resp6_textbox
            qa['resp02_6bfb_1'] if 'resp02_6bfb_1' in qa else '',  # resp7_textbox
            qa['resp04_6bi4_1'] if 'resp04_6bi4_1' in qa else '',  # resp8_textbox
            qa['resp04_6bi4_2'] if 'resp04_6bi4_2' in qa else '',  # resp9_textbox
            qa['resp04_6bi4_3'] if 'resp04_6bi4_3' in qa else '',  # resp10_textbox
            )


def load_qa_jump(filter_json, qa_idx, *args, **kwargs):
    print("load_qa_jump", args, kwargs)
    print('jump_to >> ', qa_idx)
    return load_qa(filter_json, int(qa_idx)-1)


def load_qa_prev(filter_json, qa_idx, *args, **kwargs):
    print("load_qa_prev", args, kwargs)
    return load_qa(filter_json, int(qa_idx) - 2)


def load_qa_next(filter_json, qa_idx, *args, **kwargs):
    print("load_qa_next", args, kwargs)
    return load_qa(filter_json, int(qa_idx))


def modify_qa(qa_id=None, question=None, source=None, prompt=None, answer=None, cate1=None, cate2=None, cate3=None,
              mark0=None, mark1=None, mark2=None, mark3=None, mark4=None, mark5=None, mark6=None, mark7=None, mark8=None, mark9=None, mark10=None,
              *args, **kwargs):
    # 参数顺序参考 inputs 的定义
    print("modify_qa", qa_id, args, kwargs)
    result = table.find_one_and_update({"_id": ObjectId(qa_id)},
                                       {"$set": {'question': question,
                                                 'source_documents': source,
                                                 'prompt_template': prompt,
                                                 'response': answer,
                                                 'cate1': cate1,
                                                 'cate2': cate2,
                                                 'cate3': cate3,
                                                 'mark_6bi4_0': mark0,
                                                 'mark_6bfb_0': mark1,
                                                 'mark02_6bfb_4': mark2,
                                                 'mark04_6bi4_1': mark8,
                                                 'mark04_6bi4_2': mark9,
                                                 'mark04_6bi4_3': mark10,
                                                 'mark03_6bfb_1': mark3,
                                                 'mark03_6bfb_2': mark4,
                                                 'mark03_6bfb_3': mark5,
                                                 'mark01_6bfb_1': mark6,
                                                 'mark02_6bfb_1': mark7}},
                                       return_document=pymongo.ReturnDocument.AFTER
                                       )
    print(result)
    return f"修改成功"


def save_new_qa(filter_json=None, qa_idx=None, qa_id=None, question=None, source=None, prompt=None, answer=None, cate1=None, cate2=None, *args, **kwargs):
    # 参数顺序参考 inputs 的定义
    print("save_new_qa", qa_id, args, kwargs)
    qa_new = {'question': question, 'source_documents': source, 'prompt_template': prompt, 'response': answer, 'cate1': cate1, 'cate2': cate2}
    result = table.insert_one(qa_new)
    print(result)
    return load_qa(filter_json, qa_idx)


def delete_qa(qa_id=None, filter_json=None, qa_idx=None, *args, **kwargs):
    print("delete_qa", qa_id, args, kwargs)
    if qa_id:
        result = table.find_one_and_delete({"_id": ObjectId(qa_id)})
        print(result)
    return load_qa(filter_json, qa_idx-1)


if __name__ == '__main__':
    marks = ['OK', 'NO', 'MI', '']
    with gr.Blocks() as app:
        qa_filters = {}
        qa = table.find_one(qa_filters) or {}
        qa_total = table.count_documents(qa_filters)
        print(qa)

        with gr.Row():
            with gr.Column(scale=8):
                filter_box = gr.Textbox(label="筛选", value="{}", lines=1)
                qa_idx_tbox = gr.Slider(value=1, label='当前问答', step=1, minimum=1, maximum=qa_total, info=f"问题总数：{qa_total}")
                with gr.Row():
                    with gr.Column(scale=9):
                        question_textbox = gr.TextArea(label="问题", lines=1, value=qa['question'] if 'question' in qa else '', show_copy_button=True)
                    with gr.Column(scale=1):
                        qa_id_tbox = gr.Textbox(value=str(qa['_id']), label='ObjectID', show_copy_button=True)

                with gr.Row():
                    cate1_tbox = gr.Textbox(value=qa['cate1'] if 'cate1' in qa else '', label='cate1')
                    cate2_tbox = gr.Textbox(value=qa['cate2'] if 'cate2' in qa else '', label='cate2')
                    cate3_tbox = gr.Textbox(value=qa['cate3'] if 'cate3' in qa else '', label='cate3')
                    with gr.Column(scale=1):
                        refresh_btn2 = gr.Button("刷新问答")
                        modify_qa_btn = gr.Button("更新原问答", variant="primary")

                with gr.Row():
                    with gr.Column(scale=9):
                        resp1_tbox = gr.TextArea(label="微调前回答 resp_6bfb_0", lines=1, value=qa['resp_6bfb_0'] if 'resp_6bfb_0' in qa else '')
                    with gr.Column(scale=1):
                        mark1_tbox = gr.Radio(choices=marks, value=qa['mark_6bfb_0'] if 'mark_6bfb_0' in qa else '', label='mark_6bfb_0')
                with gr.Row():
                    with gr.Column(scale=8):
                        resp2_tbox = gr.TextArea(label="微调后回答 resp02_6bfb_4", lines=1, value=qa['resp02_6bfb_4'] if 'resp02_6bfb_4' in qa else '')
                    with gr.Column(scale=1):
                        mark2_tbox = gr.Radio(choices=marks, value=qa['mark02_6bfb_4'] if 'mark02_6bfb_4' in qa else '', label='mark02_6bfb_4')
                with gr.Row():
                    with gr.Column(scale=7):
                        resp3_tbox = gr.TextArea(label="微调后回答 resp03_6bfb_1", lines=1, value=qa['resp03_6bfb_1'] if 'resp03_6bfb_1' in qa else '')
                    with gr.Column(scale=1):
                        mark3_tbox = gr.Radio(choices=marks, value=qa['mark03_6bfb_1'] if 'mark03_6bfb_1' in qa else '', label='mark03_6bfb_1')
                with gr.Row():
                    with gr.Column(scale=6):
                        resp4_tbox = gr.TextArea(label="微调后回答 resp03_6bfb_2", lines=1, value=qa['resp03_6bfb_2'] if 'resp03_6bfb_2' in qa else '')
                    with gr.Column(scale=1):
                        mark4_tbox = gr.Radio(choices=marks, value=qa['mark03_6bfb_2'] if 'mark03_6bfb_2' in qa else '', label='mark03_6bfb_2')
                with gr.Row():
                    with gr.Column(scale=5):
                        resp5_tbox = gr.TextArea(label="微调后回答 resp03_6bfb_3", lines=1, value=qa['resp03_6bfb_3'] if 'resp03_6bfb_3' in qa else '')
                    with gr.Column(scale=1):
                        mark5_tbox = gr.Radio(choices=marks, value=qa['mark03_6bfb_3'] if 'mark03_6bfb_3' in qa else '', label='mark03_6bfb_3')
                with gr.Row():
                    with gr.Column(scale=5):
                        resp8_tbox = gr.TextArea(label="微调后回答 resp04_6bi4_1", lines=1, value=qa['resp04_6bi4_1'] if 'resp04_6bi4_1' in qa else '')
                    with gr.Column(scale=1):
                        mark8_tbox = gr.Radio(choices=marks, value=qa['mark04_6bi4_1'] if 'mark04_6bi4_1' in qa else '', label='mark04_6bi4_1')
                with gr.Row():
                    with gr.Column(scale=5):
                        resp9_tbox = gr.TextArea(label="微调后回答 resp04_6bi4_2", lines=1, value=qa['resp04_6bi4_2'] if 'resp04_6bi4_2' in qa else '')
                    with gr.Column(scale=1):
                        mark9_tbox = gr.Radio(choices=marks, value=qa['mark04_6bi4_2'] if 'mark04_6bi4_2' in qa else '', label='mark04_6bi4_2')
                with gr.Row():
                    with gr.Column(scale=5):
                        resp10_tbox = gr.TextArea(label="微调后回答 resp04_6bi4_3", lines=1, value=qa['resp04_6bi4_3'] if 'resp04_6bi4_3' in qa else '')
                    with gr.Column(scale=1):
                        mark10_tbox = gr.Radio(choices=marks, value=qa['mark04_6bi4_3'] if 'mark04_6bi4_3' in qa else '', label='mark04_6bi4_3')

                with gr.Row():
                    with gr.Column(scale=4):
                        resp6_tbox = gr.TextArea(label="微调后回答 resp01_6bfb_1", lines=1, value=qa['resp01_6bfb_1'] if 'resp01_6bfb_1' in qa else '')
                    with gr.Column(scale=1):
                        mark6_tbox = gr.Radio(choices=marks, value=qa['mark01_6bfb_1'] if 'mark01_6bfb_1' in qa else '', label='mark01_6bfb_1')
                with gr.Row():
                    with gr.Column(scale=4):
                        resp7_tbox = gr.TextArea(label="微调后回答 resp02_6bfb_1", lines=1, value=qa['resp02_6bfb_1'] if 'resp02_6bfb_1' in qa else '')
                    with gr.Column(scale=1):
                        mark7_tbox = gr.Radio(choices=marks, value=qa['mark02_6bfb_1'] if 'mark02_6bfb_1' in qa else '', label='mark02_6bfb_1')
                with gr.Row():
                    with gr.Column(scale=4):
                        resp0_tbox = gr.TextArea(label="微调前回答", lines=1, value=qa['resp_6bi4_0'] if 'resp_6bi4_0' in qa else '')
                    with gr.Column(scale=1):
                        mark0_tbox = gr.Radio(choices=marks, value=qa['mark_6bi4_0'] if 'mark_6bi4_0' in qa else '', label='mark_6bi4_0')

                with gr.Row():
                    prev_btn = gr.Button(" < 前一个")
                    next_btn = gr.Button("下一个 > ")
                    refresh_btn = gr.Button("刷新问答")
                    modify_qa_btn2 = gr.Button("更新原问答", variant="primary")

            with gr.Column(scale=2):
                prompt_label = gr.TextArea(label="提示模板", lines=2,
                                           value=qa['prompt_template'] if 'prompt_template' in qa else '')
                source_label = gr.TextArea(label="参考信息", lines=4,
                                           value=qa['source_documents'] if 'source_documents' in qa else '')
                answer_textbox = gr.TextArea(label="标准回答", lines=1,
                                             value=qa['response'] if 'response' in qa else '')
                save_new_qa_btn = gr.Button(" + 保存新问答 ", variant='secondary')

                with gr.Row():
                    copy_btn = gr.Button("复制问题")
                    qa_btn = gr.Button("AI问答")
                choice_hsp_dropdown = gr.Textbox(label="当前知识库", value="common")
                ai_answer_tbox = gr.Textbox(label="AI问答", lines=1)
                delete_qa_btn = gr.Button(" - 删除问答 ", variant='stop')

        gr.Markdown("**医院知识问答数据集编辑💰**: 医院通用知识. ")
        output_tbox = gr.Markdown("")
        inputs = [qa_id_tbox, question_textbox, source_label, prompt_label, answer_textbox,
                  cate1_tbox, cate2_tbox, cate3_tbox, mark0_tbox, mark1_tbox, mark2_tbox, mark3_tbox,
                  mark4_tbox, mark5_tbox, mark6_tbox, mark7_tbox, mark8_tbox, mark9_tbox, mark10_tbox]
        outputs = [prompt_label, question_textbox, answer_textbox, cate1_tbox, cate2_tbox, cate3_tbox,
                   mark0_tbox, mark1_tbox, mark2_tbox, mark3_tbox, mark4_tbox, mark5_tbox, mark6_tbox, mark7_tbox, mark8_tbox, mark9_tbox, mark10_tbox,
                   source_label, qa_idx_tbox, qa_id_tbox, ai_answer_tbox, output_tbox,
                   resp0_tbox, resp1_tbox, resp2_tbox, resp3_tbox, resp4_tbox, resp5_tbox, resp6_tbox, resp7_tbox, resp8_tbox, resp9_tbox, resp10_tbox]

        inputs_refresh = [filter_box, qa_idx_tbox]

        qa_btn.click(fn=submit_qa, inputs=inputs, outputs=[ai_answer_tbox, source_label, output_tbox])
        copy_btn.click(fn=copy_to_clipboard, inputs=[question_textbox, prompt_label, source_label], outputs=output_tbox)
        qa_idx_tbox.change(fn=load_qa_jump, inputs=inputs_refresh, outputs=outputs)
        refresh_btn.click(fn=load_qa_jump, inputs=inputs_refresh, outputs=outputs)
        refresh_btn2.click(fn=load_qa_jump, inputs=inputs_refresh, outputs=outputs)
        prev_btn.click(fn=load_qa_prev, inputs=inputs_refresh, outputs=outputs)
        next_btn.click(fn=load_qa_next, inputs=inputs_refresh, outputs=outputs)

        modify_qa_btn.click(fn=modify_qa, inputs=inputs, outputs=output_tbox)
        modify_qa_btn2.click(fn=modify_qa, inputs=inputs, outputs=output_tbox)
        save_new_qa_btn.click(fn=save_new_qa, inputs=inputs_refresh + inputs, outputs=outputs)
        delete_qa_btn.click(fn=delete_qa, inputs=[qa_id_tbox] + inputs_refresh, outputs=outputs)

    app.launch(server_name="0.0.0.0", server_port=7861)

