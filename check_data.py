import pandas as pd
df = pd.read_pickle('data/processed/features.pkl')
print(df['image_id'].tolist())