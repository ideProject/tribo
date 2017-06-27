import pandas as pd

ide = pd.read_csv("data/hokan_ver2.csv", encoding='shift-jis')

ide2 = ide[ide.before_id != ide.after_id]

ide2.to_csv("data/hokandel_ver2.csv", encoding='shift-jis', index=False)