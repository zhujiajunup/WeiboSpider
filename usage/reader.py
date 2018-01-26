import pandas as pd

user = pd.read_excel('C:\\workspace\\zju\\graduate\\weibo_user_small.xlsx', header=None)

for index, row in user.iterrows():
    for col_name in user.columns:
        print(row[col_name])
