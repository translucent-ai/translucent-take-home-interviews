import pandas as pd

denials = pd.read_csv('data/denials.csv')

reason_counts = denials[denials['department'] == 'Cardiology'][['department', 'denial_reason']].groupby(
    ['department', 'denial_reason']).value_counts().sort_values(ascending=False)

print(reason_counts.to_string())
