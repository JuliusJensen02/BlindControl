#from scripts.data_to_csv import reset_csv, query_data
from scripts.data_processing import convert_csv_to_df, remove_outliers, normalize, smooth
from scripts.greybox_fitting import fitting
from scripts.plot import plot_df

#reset_csv()
#query_data()
df = convert_csv_to_df("data/data.csv")
df = remove_outliers(df)
df = smooth(df)
#df = normalize(df)

#print(df["watt"].iloc[37])

df = fitting(df)
plot_df(df)

#print(df)
