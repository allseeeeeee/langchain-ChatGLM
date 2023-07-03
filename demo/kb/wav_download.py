import os.path
import time

import pandas as pd
import requests
from tqdm import tqdm

if __name__ == '__main__':
    path = '/home/dev/chat_online/qiyu/'
    excelpath = os.path.join(path, "call_records_excel/2023-06.xlsx")
    data = pd.read_excel(excelpath)
    # filter_data = data.head(10)
    filtered_data = data[(data['服务录音'].str.contains('http'))]
    folder = excelpath.split('/')[-1].split(".")[0]
    progress_bar = tqdm(total=len(filtered_data), ncols=80)
    call_records_path = os.path.join(path, "call_records", folder)
    for index, row in filtered_data.iterrows():
        wav_url = row['服务录音'].strip()
        filename = wav_url.split('/')[-1]
        filepath = os.path.join(call_records_path, filename)
        if os.path.exists(filepath):
            progress_bar.write(f"  跳过已下载文件 {filename}", end="\033[F")
        else:
            progress_bar.write(f"  正在下载文件 {filename} ...", end="\033[F")
            response = requests.get(wav_url)
            if response.status_code == 200:
                with open(filepath, 'wb') as file:
                    file.write(response.content)
                progress_bar.write(f"  已成功下载文件: {filename}", end="\033[F")
            else:
                progress_bar.write(f"  下载文件失败: {wav_url}", end="\033[F")
        progress_bar.update(1)
        time.sleep(2)

    progress_bar.close()
    pass
