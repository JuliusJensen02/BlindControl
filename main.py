from scripts import reset_csv, query_data, convert_csv_to_df, remove_outliers, normalize

#reset_csv()
#query_data()
df = convert_csv_to_df("data.csv")
df = remove_outliers(df)
df = normalize(df)
print(df)
