import pandas as pd

# Load the dataset to examine its structure
df = pd.read_excel('KJSIT Library Book Bank data.xlsx', sheet_name='Sheet1', header=1)

print("=== DATASET OVERVIEW ===")
print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print()

print("=== FIRST 5 ROWS ===")
print(df.head())
print()

print("=== DATA CLEANING PROCESS ===")
print(f"Rows before cleaning: {len(df)}")

# Check for missing titles
missing_titles = df['Title'].isna().sum()
print(f"Rows with missing titles: {missing_titles}")

# Check for empty titles
empty_titles = (df['Title'] == '').sum() if 'Title' in df.columns else 0
print(f"Rows with empty titles: {empty_titles}")

# Check for duplicate titles
duplicate_titles = df.duplicated(subset=['Title']).sum()
print(f"Rows with duplicate titles: {duplicate_titles}")

# After cleaning (as done in our main script)
df_cleaned = df.drop_duplicates(subset=['Title']).fillna('')
df_cleaned = df_cleaned[df_cleaned['Title'] != '']

print(f"Rows after cleaning: {len(df_cleaned)}")
print()

print("=== BRANCH DISTRIBUTION ===")
print(df_cleaned['Branch'].value_counts())
print()

print("=== SAMPLE OF CLEANED DATA ===")
print(df_cleaned[['Title', 'Author', 'Branch']].head(10))