import torch
from transformers import BertTokenizer, BertForSequenceClassification

model_name = '/home/dev/team/text2vec-large-chinese'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)  # 2 表示二分类任务

# 设置 GPU 设备（如果可用）
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

