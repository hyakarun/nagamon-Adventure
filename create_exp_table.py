import csv
import os

# マスターデータディレクトリのパス
masterdata_dir = os.path.join(os.path.dirname(__file__), 'masterdata')
# 出力するCSVファイルのパス
output_csv_path = os.path.join(masterdata_dir, 'exp_table.csv')

# ヘッダー
header = ['level', 'required_exp']

# 経験値テーブルのデータを生成
exp_table_data = []
cumulative_exp = 0
for level in range(1, 100):  # レベル1から99まで
    # 次のレベルに必要な経験値 (単純な例)
    exp_for_next_level = level * 100
    cumulative_exp += exp_for_next_level
    exp_table_data.append([level + 1, cumulative_exp])

# CSVファイルに書き出し
with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    # レベル1のデータ
    writer.writerow([1, 0])
    writer.writerows(exp_table_data)

print(f"'{output_csv_path}' に経験値テーブルを作成しました。")
