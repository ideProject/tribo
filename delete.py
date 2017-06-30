import pandas as pd

ide = pd.read_csv("data/pre_hokan.csv", encoding='shift-jis')

ide2 = ide[ide.before_id != ide.after_id]

ide2.to_csv("data/pre_hokandel_.csv", encoding='shift-jis', index=False)