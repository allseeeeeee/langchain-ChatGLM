
on chatglm-6b-int4 config.json:
```
_name_or_path: /home/dev/team/chatglm-6b-int4
```

on text2vec-large-chinese config.json
```
  "_name_or_path": "chinese-lert-large",
```

on chinese-lert-large config.json
```
  "_name_or_path": ".",
```
on model_config.py
```
embedding_model_dict = {
 "text2vec": "/home/dev/team/text2vec-large-chinese",
}

llm_model_dict = {
  "chatglm-6b-int4": {
    "local_model_path": "/home/dev/team/chatglm-6b-int4",
  }
  # if run api mode
  "fastchat-chatglm-6b-int4": {
    "local_model_path": "/home/dev/team/chatglm-6b-int4",
  }
}
```
run webui on command:
```shell
python webui.py --no-remote-model --model chatglm-6b-int4
```

run api on command:
```shell
python api.py --no-remote-model --model chatglm-6b-int4
```
