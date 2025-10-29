import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_and_clean_data(file_path):
    """
    Load and clean the library book dataset from Excel.
    Preserves all editions by using accession number as unique identifier.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pd.DataFrame: Cleaned dataset with all editions
    """
    print("📚 Loading and cleaning dataset...")
    
    # Read the Excel file, using header=1 as first row is metadata
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=1)
    
    # Rename columns for clarity
    df.columns = ['Accession_Number', 'Title', 'Author', 'Publisher', 'Price', 'Branch']
    
    # Fill missing values with empty strings
    df = df.fillna('')
    
    # Drop rows with empty titles
    df = df[df['Title'] != '']
    
    print(f"✅ Dataset loaded with {len(df)} books (all editions preserved)")
    print(f"   Unique titles: {df['Title'].nunique()}")
    return df

def create_book_profiles(df):
    """
    Combine text features into a single profile for each book.
    
    Args:
        df (pd.DataFrame): Cleaned dataset
        
    Returns:
        pd.DataFrame: Dataset with added Profile column
    """
    print("🔧 Creating book profiles...")
    
    # Combine text features into a single profile
    df['Profile'] = (
        df['Title'] + ' ' + 
        df['Author'] + ' ' + 
        df['Publisher'] + ' ' + 
        df['Branch']
    )
    
    print("✅ Book profiles created")
    return df

def build_model(df):
    """
    Build TF-IDF vectorizer and compute cosine similarity matrix.
    
    Args:
        df (pd.DataFrame): Dataset with Profile column
        
    Returns:
        tuple: (tfidf_vectorizer, cosine_sim_matrix)
    """
    print("🧠 Building recommendation model...")
    
    # Initialize TF-IDF Vectorizer with English stopwords
    tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    
    # Fit and transform the Profile column
    tfidf_matrix = tfidf.fit_transform(df['Profile'])
    
    # Compute cosine similarity matrix
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    print("✅ Model built successfully")
    return tfidf, cosine_sim

def recommend_books(title, df, cosine_sim, tfidf, top_n=5, branch=None, author=None):
    """
    Recommend books based on content similarity.
    Preserves all editions by treating each accession number as unique.
    
    Args:
        title (str): Title of the book to find recommendations for
        df (pd.DataFrame): Dataset with book information
        cosine_sim (np.ndarray): Cosine similarity matrix
        tfidf: TF-IDF vectorizer
        top_n (int): Number of recommendations to return
        branch (str, optional): Filter by branch/subject area
        author (str, optional): Filter by author
        
    Returns:
        pd.DataFrame: Recommended books
    """
    print(f"🔍 Searching for books similar to '{title}'...")
    
    # Check if the book exists in the dataset
    matching_books = df[df['Title'].str.contains(title, case=False, na=False)]
    if matching_books.empty:
        print(f"❌ No books found matching '{title}' in the dataset")
        return pd.DataFrame()
    elif len(matching_books) == 1:
        # Exact match or single match
        book_row = matching_books.iloc[0]
        print(f"📎 Found book: '{book_row['Title']}' (Accession: {book_row['Accession_Number']})")
    else:
        # Multiple matches - show options
        print(f"📎 Found {len(matching_books)} books matching '{title}':")
        for i, (idx, book) in enumerate(matching_books.head(5).iterrows()):
            print(f"   {i+1}. '{book['Title']}' (Accession: {book['Accession_Number']}) by {book['Author']}")
        # Use the first match for recommendations
        book_row = matching_books.iloc[0]
        print(f"Using first match: '{book_row['Title']}' (Accession: {book_row['Accession_Number']})")
    
    # Get the index of the book
    idx = matching_books.index[0]
    
    # Get similarity scores for all books
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort books based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get indices of top similar books (excluding the book itself)
    sim_scores = sim_scores[1:top_n*3]  # Get more candidates for filtering
    book_indices = [i[0] for i in sim_scores]
    
    # Get the recommended books
    recommendations = df.iloc[book_indices].copy()
    
    # Apply filters if provided
    if branch:
        print(f"📎 Filtering by branch: {branch}")
        recommendations = recommendations[recommendations['Branch'].str.contains(branch, case=False, na=False)]
    
    if author:
        print(f"👤 Filtering by author: {author}")
        # Apply author filter to candidate books
        candidate_books = df.iloc[book_indices]
        recommendations = candidate_books[candidate_books['Author'].str.contains(author, case=False, na=False)]
        
        # If no recommendations found, try partial matching
        if recommendations.empty:
            # Split author name and try matching each part
            author_parts = author.split()
            for part in author_parts:
                partial_matches = candidate_books[candidate_books['Author'].str.contains(part, case=False, na=False)]
                if not partial_matches.empty:
                    recommendations = partial_matches
                    break
    
    # Limit to top_n results
    recommendations = recommendations.head(top_n)
    
    # If no recommendations found after filtering
    if recommendations.empty:
        print("⚠️ No recommendations found with the given filters")
        return recommendations
    
    print(f"✅ Found {len(recommendations)} recommendations:")
    return recommendations[['Title', 'Author', 'Publisher', 'Branch', 'Accession_Number']]

def get_book_details(accession_number, df):
    """
    Get detailed information about a specific book by accession number.
    
    Args:
        accession_number (str): Accession number of the book
        df (pd.DataFrame): Dataset with book information
        
    Returns:
        pd.Series: Book details or None if not found
    """
    book = df[df['Accession_Number'] == accession_number]
    return book.iloc[0] if not book.empty else None

def main():
    """
    Main function to demonstrate the book recommendation system.
    """
    # Load and clean data
    file_path = "KJSIT Library Book Bank data.xlsx"
    
    try:
        df = load_and_clean_data(file_path)
    except FileNotFoundError:
        print(f"❌ File '{file_path}' not found. Please check the file path.")
        return
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Create book profiles
    df = create_book_profiles(df)
    
    # Build recommendation model
    tfidf, cosine_sim = build_model(df)
    
    print("\n" + "="*60)
    print("BOOK RECOMMENDATION SYSTEM (All Editions Preserved)")
    print("="*60)
    
    # Example 1: Basic recommendations
    print("\n📝 Example 1: Basic recommendations for 'ENGINEERING PHYSICS'")
    print("-" * 60)
    rec1 = recommend_books("ENGINEERING PHYSICS", df, cosine_sim, tfidf)
    if not rec1.empty:
        print(rec1.to_string(index=False))
    
    # Example 2: Recommendations filtered by branch
    print("\n📝 Example 2: Recommendations for 'ENGINEERING PHYSICS' in 'BASIC SCIENCE AND HUMANITIES'")
    print("-" * 60)
    rec2 = recommend_books("ENGINEERING PHYSICS", df, cosine_sim, tfidf, 
                          branch="BASIC SCIENCE AND HUMANITIES")
    if not rec2.empty:
        print(rec2.to_string(index=False))
    
    # Example 3: Recommendations filtered by author
    print("\n📝 Example 3: Recommendations for 'ENGINEERING PHYSICS' by author 'GAUR'")
    print("-" * 60)
    rec3 = recommend_books("ENGINEERING PHYSICS", df, cosine_sim, tfidf, 
                          author="GAUR")
    if not rec3.empty:
        print(rec3.to_string(index=False))
    
    # Example 4: Show different editions are preserved
    print("\n📝 Example 4: Showing different editions are preserved")
    print("-" * 60)
    print("Different editions of 'ENGINEERING PHYSICS':")
    ep_books = df[df['Title'].str.contains('ENGINEERING PHYSICS', case=False, na=False)]
    print(ep_books[['Title', 'Accession_Number', 'Publisher']].head(10).to_string(index=False))

# OPTIONAL FUTURE EXTENSIONS (commented out):
"""
1. Streamlit UI Implementation:
   - Add dropdowns for Title, Branch, and Author
   - Use st.selectbox for title selection from df['Title'].unique()
   - Add st.text_input for custom filters
   - Display results in a nice table format

2. Dynamic Dataset Upload:
   - Add file uploader: st.file_uploader("Upload Excel file", type=['xlsx'])
   - Process uploaded file instead of hardcoded path

3. Export Recommendations:
   - Add button to save recommendations as CSV
   - Use: recommendations.to_csv('recommendations.csv', index=False)

Example Streamlit code structure:
import streamlit as st

st.title("📚 College Library Book Recommendation System")
title = st.selectbox("Select a book", df['Title'].unique())
branch = st.selectbox("Filter by Branch", ["All"] + list(df['Branch'].unique()))
author = st.text_input("Filter by Author")
top_n = st.slider("Number of recommendations", 1, 20, 5)

if st.button("Get Recommendations"):
    rec = recommend_books(title, df, cosine_sim, tfidf, top_n, 
                         branch if branch != "All" else None, author if author else None)
    st.dataframe(rec)
"""

if __name__ == "__main__":
    main()