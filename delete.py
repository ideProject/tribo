import pandas as pd

ide = pd.read_csv("data/hokan.csv", encoding='shift-jis')

ide2 = ide[ide.before_id != ide.after_id]

ide2.to_csv("data/hokandel.csv", encoding='shift-jis', index=False)