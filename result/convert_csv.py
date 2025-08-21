import pandas as pd
import json

with open('Multi-Agent_Embodied_Intelligence_Challenge/result/answer_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
df = pd.json_normalize(data)
df.to_csv('answer_data.csv', index=False, encoding='utf-8-sig')
