import pandas as pd
import json

with open('result/inference_data_final_gpt-4o.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
df = pd.json_normalize(data)
df.to_csv('answer_data.csv', index=False, encoding='utf-8-sig')
