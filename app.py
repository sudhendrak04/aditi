import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from models import get_session, User, Book, Rating, Review, create_tables
from sqlalchemy import func
from recommendation_engine import recommendation_engine
import hashlib

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="KJSIT Book Recommendation System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS adapted to Streamlit theme variables for good contrast
st.markdown("""
<style>
    :root {
        /* Fallbacks if theme variables are missing */
        --primary-color: var(--primary-color, #1f77b4);
        --text-color: var(--text-color, #262730);
        --bg-color: var(--background-color, #ffffff);
        --secondary-bg: var(--secondary-background-color, #f6f6f6);
    }

    /* Ensure base text uses theme text color for readability */
    html, body, [class^="css"], .stMarkdown p, .stMarkdown li, .stTextInput label,
    .stSelectbox label, .stSlider label, .stMetric, .stRadio label, .stButton button {
        color: var(--text-color) !important;
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--text-color) !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    .book-card {
        background-color: var(--secondary-bg);
        color: var(--text-color);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid var(--primary-color);
    }
    .rating-stars {
        color: #ffd700;
        font-size: 1.2rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--text-color) !important;
        margin-bottom: 1rem;
    }

    /* Tabs and nav accents */
    .stTabs [data-baseweb="tab-list"] button {
        color: var(--text-color) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary-color) !important;
    }

    /* Info/success messages better contrast */
    .stAlert > div {
        color: var(--text-color) !important;
    }

    /* Improve readability under dark mode */
    @media (prefers-color-scheme: dark) {
        html, body, [class^="css"], .stMarkdown p, .stMarkdown li, .stTextInput label,
        .stSelectbox label, .stSlider label, .stMetric, .stRadio label, .stButton button,
        h1, h2, h3, h4, h5, h6, label, p, span, div, li, a, strong, em {
            color: #f5f5f5 !important;
        }

        .main-header { color: #f5f5f5 !important; }
        .book-card { background-color: #1f2937; color: #f5f5f5; border-left-color: #60a5fa; }
        .sidebar-header { color: #f5f5f5 !important; }
        .stTabs [data-baseweb="tab-list"] button { color: #e5e7eb !important; }
        .stTabs [data-baseweb="tab"]:hover { color: #93c5fd !important; }
        .stAlert > div { color: #f5f5f5 !important; }
    }

    /* Chatbot Styles */
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
    }
    
    .chatbot-icon {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        animation: pulse 2s infinite;
    }
    
    .chatbot-icon:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .chatbot-icon svg {
        width: 30px;
        height: 30px;
        fill: white;
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        50% {
            box-shadow: 0 4px 25px rgba(102, 126, 234, 0.7);
        }
    }
    
    .chatbot-window {
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        z-index: 9998;
    }
    
    .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chatbot-close {
        cursor: pointer;
        font-size: 20px;
        font-weight: bold;
        opacity: 0.8;
        transition: opacity 0.2s;
    }
    
    .chatbot-close:hover {
        opacity: 1;
    }
    
    .chatbot-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background: #f8f9fa;
    }
    
    .chatbot-message {
        margin-bottom: 15px;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .bot-message {
        background: white;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 5px;
        max-width: 80%;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 5px 15px;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .chatbot-options {
        padding: 15px;
        background: white;
        border-top: 1px solid #e0e0e0;
    }
    
    .chatbot-option-btn {
        display: block;
        width: 100%;
        padding: 10px;
        margin-bottom: 8px;
        background: #f0f0f0;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
        font-size: 14px;
    }
    
    .chatbot-option-btn:hover {
        background: #667eea;
        color: white;
        transform: translateX(5px);
    }
    
    @media (prefers-color-scheme: dark) {
        .chatbot-window {
            background: #1e293b;
        }
        .chatbot-messages {
            background: #0f172a;
        }
        .bot-message {
            background: #1e293b;
            color: #f1f5f9;
        }
        .chatbot-options {
            background: #1e293b;
            border-top-color: #334155;
        }
        .chatbot-option-btn {
            background: #334155;
            color: #f1f5f9;
        }
    }
</style>
""", unsafe_allow_html=True)

def init_database():
    """Initialize database tables"""
    try:
        create_tables()
        st.success("Database initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing database: {e}")


def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user"""
    session = get_session()
    try:
        user = session.query(User).filter_by(student_id=username).first()
        if user and user.password_hash == hash_password(password):
            return user
        return None
    finally:
        session.close()

def register_user(student_id, name, email, department, year, password):
    """Register new user"""
    session = get_session()
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(
            (User.student_id == student_id) | (User.email == email)
        ).first()

        if existing_user:
            return False, "User already exists with this Student ID or Email"

        # Create new user
        new_user = User(
            student_id=student_id,
            name=name,
            email=email,
            department=department,
            year=year,
            password_hash=hash_password(password)
        )

        session.add(new_user)
        session.commit()
        return True, "User registered successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Error registering user: {e}"
    finally:
        session.close()

def get_user_stats(user_id):
    """Get user statistics"""
    session = get_session()
    try:
        ratings_count = session.query(Rating).filter_by(user_id=user_id).count()
        avg_rating = session.query(Rating.rating).filter_by(user_id=user_id).first()
        avg_rating = avg_rating[0] if avg_rating else 0

        return {
            'total_ratings': ratings_count,
            'average_rating': round(avg_rating, 2)
        }
    finally:
        session.close()

def main():
    # Initialize database
    init_database()

    # Sidebar
    st.sidebar.markdown('<div class="sidebar-header">📚 KJSIT Book Recommender</div>',
                       unsafe_allow_html=True)

    # Authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.current_user = None

    if not st.session_state.authenticated:
        auth_mode = st.sidebar.radio("Choose mode:", ["Login", "Register"])

        if auth_mode == "Login":
            st.sidebar.subheader("Login")
            username = st.sidebar.text_input("Student ID")
            password = st.sidebar.text_input("Password", type="password")

            if st.sidebar.button("Login"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.current_user = user
                    st.success(f"Welcome back, {user.name}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        else:  # Register
            st.sidebar.subheader("Register")
            with st.sidebar.form("registration_form"):
                student_id = st.text_input("Student ID")
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                department = st.selectbox("Department", [
                    "Computer", "Information Technology", "Electronics & Telecommunication",
                     "AIDS"
                ])
                year = st.selectbox("Year", ["FY", "SY", "TY", "LY"])
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")

                submitted = st.form_submit_button("Register")

                if submitted:
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        success, message = register_user(
                            student_id, name, email, department, year, password
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

        return

    # Main content for authenticated users
    st.markdown('<div class="main-header">📚 KJSIT Book Recommendation System</div>',
                unsafe_allow_html=True)

    # User info in sidebar
    user = st.session_state.current_user
    st.sidebar.write(f"**User:** {user.name}")
    st.sidebar.write(f"**Department:** {user.department}")
    st.sidebar.write(f"**Year:** {user.year}")

    user_stats = get_user_stats(user.id)
    st.sidebar.write(f"**Books Rated:** {user_stats['total_ratings']}")
    st.sidebar.write(f"**Avg Rating:** {user_stats['average_rating']} ⭐")

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.rerun()

    # Main navigation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Home", "🔍 Search", "📖 My Books", "📊 Analytics", "👥 Community", "📝 Journals", "📓 Blackbooks"
    ])

    with tab1:
        show_home_page()

    with tab2:
        show_search_page()

    with tab3:
        show_my_books_page(user.id)

    with tab4:
        show_analytics_page()

    with tab5:
        show_community_page()


def show_home_page():
    st.subheader("🎯 Personalized Recommendations")

    user = st.session_state.current_user

    # Get hybrid recommendations
    recommendations = recommendation_engine.get_hybrid_recommendations(user.id, 6)

    if recommendations:
        cols = st.columns(2)
        for i, book in enumerate(recommendations):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"""
                    <div class="book-card">
                        <h4>{book['title']}</h4>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Genre:</strong> {book['genre'] or 'N/A'}</p>
                        <p><strong>Accession:</strong> {book['accession_number'] or 'N/A'}</p>
                        <p><strong>Price:</strong> ₹{book['price'] if book['price'] else 'N/A'}</p>
                        <p><strong>Avg Rating:</strong> {book['average_rating']:.1f} ⭐</p>
                        <p><strong>Total Ratings:</strong> {book['total_ratings']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Check if book has external URL
                    external_url = get_book_external_url(book['title'], book['author'])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"View Details", key=f"rec_{book['book_id']}"):
                            show_book_details(book['book_id'])
                    with col2:
                        if external_url:
                            st.markdown(f"[🌐 External Link]({external_url})")
    else:
        st.info("Rate some books to get personalized recommendations!")

        # Show popular books instead
        st.subheader("🔥 Popular Books")
        popular_books = recommendation_engine.get_popular_books(6)

        if popular_books:
            cols = st.columns(2)
            for i, book in enumerate(popular_books):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="book-card">
                        <h4>{book['title']}</h4>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Genre:</strong> {book['genre'] or 'N/A'}</p>
                        <p><strong>Accession:</strong> {book['accession_number'] or 'N/A'}</p>
                        <p><strong>Price:</strong> ₹{book['price'] if book['price'] else 'N/A'}</p>
                        <p><strong>Avg Rating:</strong> {book['average_rating']:.1f} ⭐</p>
                        <p><strong>Total Ratings:</strong> {book['total_ratings']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Check if book has external URL
                    external_url = get_book_external_url(book['title'], book['author'])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"View Details", key=f"popular_{book['book_id']}"):
                            show_book_details(book['book_id'])
                    with col2:
                        if external_url:
                            st.markdown(f"[🌐 External Link]({external_url})")
        else:
            st.info("No books found matching your search.")

def show_search_page():
    st.subheader("🔍 Search Books")

    search_query = st.text_input("Search by title, author, or genre:")

    if search_query:
        results = recommendation_engine.search_books(search_query, 20)

        if results:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                genre_filter = st.selectbox("Filter by Genre",
                    ["All"] + list(set([r['genre'] for r in results if r['genre']])))
            with col2:
                min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.0)
            with col3:
                sort_by = st.selectbox("Sort by", ["Rating", "Title", "Author", "Price (Low to High)", "Price (High to Low)"])

            # Apply filters
            filtered_results = results
            if genre_filter != "All":
                filtered_results = [r for r in results if r['genre'] == genre_filter]
            filtered_results = [r for r in filtered_results if r['average_rating'] >= min_rating]

            # Sort results
            if sort_by == "Rating":
                filtered_results.sort(key=lambda x: x['average_rating'], reverse=True)
            elif sort_by == "Title":
                filtered_results.sort(key=lambda x: x['title'])
            elif sort_by == "Author":
                filtered_results.sort(key=lambda x: x['author'])
            elif sort_by == "Price (Low to High)":
                # Sort by price, handling None values
                filtered_results.sort(key=lambda x: x.get('price', 0) or 0)
            elif sort_by == "Price (High to Low)":
                # Sort by price descending, handling None values
                filtered_results.sort(key=lambda x: x.get('price', 0) or 0, reverse=True)

            # Display results
            for book in filtered_results:
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="book-card">
                            <h4>{book['title']}</h4>
                            <p><strong>Author:</strong> {book['author']}</p>
                            <p><strong>Genre:</strong> {book['genre'] or 'N/A'}</p>
                            <p><strong>Accession:</strong> {book['accession_number'] or 'N/A'}</p>
                            <p><strong>Price:</strong> ₹{book['price'] if book['price'] else 'N/A'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.write(f"**Rating:** {book['average_rating']:.1f} ⭐")
                        st.write(f"**Total:** {book['total_ratings']} ratings")
                    with col3:
                        # Check if book has external URL
                        external_url = get_book_external_url(book['title'], book['author'])
                        if st.button("View Details", key=f"search_{book['book_id']}"):
                            show_book_details(book['book_id'])
                        if external_url:
                            st.markdown(f"[🌐 External]({external_url})")
        else:
            st.info("No books found matching your search.")

def show_my_books_page(user_id):
    st.subheader("📖 My Books")

    # Get user's ratings
    session = get_session()
    try:
        user_ratings = session.query(Rating, Book).join(Book).filter(
            Rating.user_id == user_id
        ).all()

        if user_ratings:
            for rating, book in user_ratings:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="book-card">
                            <h4>{book.title}</h4>
                            <p><strong>Author:</strong> {book.author}</p>
                            <p><strong>Genre:</strong> {book.genre or 'N/A'}</p>
                            <p><strong>Accession:</strong> {book.accession_number or 'N/A'}</p>
                            <p><strong>Price:</strong> ₹{book.price if book.price else 'N/A'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.write(f"**Your Rating:** {rating.rating:.1f} ⭐")
                    with col3:
                        st.write(f"**Avg Rating:** {book.average_rating:.1f} ⭐")
                    with col4:
                        # Check if book has external URL
                        external_url = get_book_external_url(book.title, book.author)
                        if st.button("Update Rating", key=f"update_{book.id}"):
                            new_rating = st.number_input(
                                f"New rating for {book.title}",
                                min_value=1.0, max_value=5.0, step=0.5,
                                key=f"rating_{book.id}"
                            )
                            if st.button("Save", key=f"save_{book.id}"):
                                # Update rating logic here
                                st.success("Rating updated!")
                        if external_url:
                            st.markdown(f"[🌐 External]({external_url})")
        else:
            st.info("You haven't rated any books yet. Start exploring and rate some books!")

    finally:
        session.close()

def show_analytics_page():
    st.subheader("📊 Analytics Dashboard")

    # Get overall statistics
    session = get_session()
    try:
        total_books = session.query(Book).count()
        total_users = session.query(User).count()
        total_ratings = session.query(Rating).count()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", total_books)
        with col2:
            st.metric("Total Users", total_users)
        with col3:
            st.metric("Total Ratings", total_ratings)

        # Show some sample books
        st.subheader("📚 Sample Books from Collection")
        sample_books = session.query(Book).limit(10).all()
        for book in sample_books:
            price_info = f"₹{book.price:.2f}" if book.price else "Price not available"
            accession_info = f"Accession: {book.accession_number}" if book.accession_number else "Accession: N/A"
            st.markdown(f"**{book.title}** by {book.author} ({book.genre}) - {accession_info} - {price_info}")

        # Genre distribution
        st.subheader("📈 Genre Distribution")
        genre_data = session.query(Book.genre, func.count(Book.id)).filter(
            Book.genre.isnot(None)
        ).group_by(Book.genre).all()
        
        st.write(f"Found {len(genre_data)} genres")
        
        if genre_data:
            genres, counts = zip(*genre_data)
            # Debug information
            st.write("Genre data:", dict(zip(genres, counts)))
            try:
                fig = px.pie(values=counts, names=genres, title="Books by Genre")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating genre chart: {e}")
        else:
            st.warning("No genre data available")

        # Top authors
        st.subheader("👥 Top Authors by Book Count")
        author_data = session.query(Book.author, func.count(Book.id)).group_by(Book.author).order_by(func.count(Book.id).desc()).limit(10).all()
        if author_data:
            authors, counts = zip(*author_data)
            fig = px.bar(x=counts, y=authors, orientation='h', title="Top Authors")
            fig.update_layout(xaxis_title="Number of Books", yaxis_title="Author")
            st.plotly_chart(fig, use_container_width=True)
        
        # Rating distribution
        st.subheader("⭐ Rating Distribution")
        rating_data = session.query(Rating.rating, func.count(Rating.id)).group_by(
            Rating.rating
        ).all()
        
        st.write(f"Found {len(rating_data)} rating values")

        if rating_data:
            ratings, counts = zip(*rating_data)
            # Debug information
            st.write("Rating data:", dict(zip(ratings, counts)))
            try:
                fig = px.bar(x=ratings, y=counts, title="Rating Distribution")
                fig.update_layout(xaxis_title="Rating", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating rating chart: {e}")
        else:
            st.warning("No rating data available")

    except Exception as e:
        st.error(f"Error in analytics page: {e}")
        import traceback
        st.text(traceback.format_exc())
    finally:
        session.close()

def show_community_page():
    st.subheader("👥 Community")

    # Popular books this week
    st.subheader("🔥 Trending This Week")
    popular_books = recommendation_engine.get_popular_books(5)

    for book in popular_books:
        with st.container():
            st.markdown(f"""
            <div class="book-card">
                <h4>{book['title']}</h4>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Genre:</strong> {book['genre'] or 'N/A'}</p>
                <p><strong>Accession:</strong> {book['accession_number'] or 'N/A'}</p>
                <p><strong>Price:</strong> ₹{book['price'] if book['price'] else 'N/A'}</p>
                <p><strong>Avg Rating:</strong> {book['average_rating']:.1f} ⭐ ({book['total_ratings']} ratings)</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check if book has external URL
            external_url = get_book_external_url(book['title'], book['author'])
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"View Details", key=f"community_{book['book_id']}"):
                    show_book_details(book['book_id'])
            with col2:
                if external_url:
                    st.markdown(f"[🌐 External Link]({external_url})")

def get_book_external_url(book_title, book_author):
    """Get external URL for a book if available"""
    # Sample mapping of books to external URLs (for demonstration)
    book_urls = {
        "ENGINEERING PHYSICS": "https://www.amazon.com/s?k=engineering+physics",
        "DATABASE MANAGEMENT SYSTEMS": "https://www.amazon.com/s?k=database+management+systems",
        "COMPUTER NETWORKS": "https://www.amazon.com/s?k=computer+networks",
        "OPERATING SYSTEMS": "https://www.amazon.com/s?k=operating+systems",
        "DATA STRUCTURES": "https://www.amazon.com/s?k=data+structures"
    }
    
    # Check for exact match
    if book_title in book_urls:
        return book_urls[book_title]
    
    # Check for partial matches
    for title, url in book_urls.items():
        if title in book_title.upper():
            return url
    
    return None

def show_book_details(book_id):
    """Show detailed view of a book"""
    book_details = recommendation_engine.get_book_details(book_id)

    if not book_details:
        st.error("Book not found")
        return

    st.subheader(f"📖 {book_details['title']}")
    st.write(f"**Author:** {book_details['author']}")
    st.write(f"**Genre:** {book_details['genre'] or 'N/A'}")
    st.write(f"**Accession Number:** {book_details['accession_number'] or 'N/A'}")
    st.write(f"**Price:** ₹{book_details['price'] if book_details['price'] else 'N/A'}")
    st.write(f"**Average Rating:** {book_details['average_rating']:.1f} ⭐")
    st.write(f"**Total Ratings:** {book_details['total_ratings']}")

    if book_details.get('description'):
        st.write(f"**Description:** {book_details['description']}")
    
    # Check if book has external URL
    external_url = get_book_external_url(book_details['title'], book_details['author'])
    if external_url:
        st.markdown(f"**[🌐 View on External Website]({external_url})**")

    # Rating section
    st.subheader("⭐ Rate this book")
    rating = st.slider("Your rating", 1.0, 5.0, 3.0, 0.5)
    review_text = st.text_area("Write a review (optional)")

    if st.button("Submit Rating"):
        # Save rating logic here
        st.success("Rating submitted successfully!")

    # Similar books
    st.subheader("📚 Similar Books")
    similar_books = recommendation_engine.get_content_based_recommendations(book_id, 5)

    if similar_books:
        for book in similar_books:
            st.write(f"• {book['title']} by {book['author']} (Similarity: {book['similarity_score']:.2f})")

if __name__ == "__main__":
    main()
    # Inject chatbot into parent document so it stays fixed and visible without scrolling
    components.html("""
    <script>
    (function() {
        try {
            const doc = (window.parent && window.parent.document) ? window.parent.document : document;

            // Inject styles once
            if (!doc.getElementById('chatbotStylesInjected')) {
                const style = doc.createElement('style');
                style.id = 'chatbotStylesInjected';
                style.textContent = `
                .chatbot-floating-container {
                    position: fixed !important;
                    bottom: 20px !important;
                    right: 20px !important;
                    z-index: 999999 !important;
                    pointer-events: none !important;
                }
                .chatbot-floating-container * { pointer-events: auto !important; }
                .chatbot-fab { width: 60px; height: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display:flex; align-items:center; justify-content:center; cursor:pointer; box-shadow: 0 4px 15px rgba(102,126,234,0.4); transition: all .3s ease; animation: chatbot-pulse 2s infinite; }
                @keyframes chatbot-pulse { 0%,100%{ box-shadow:0 4px 15px rgba(102,126,234,.4);} 50%{ box-shadow:0 4px 25px rgba(102,126,234,.7);} }
                .chatbot-fab:hover { transform: scale(1.1); box-shadow: 0 6px 20px rgba(102,126,234,.6); }
                .chatbot-fab svg { width:30px; height:30px; }
                .chatbot-popup { position: fixed; bottom: 90px; right: 20px; width: 350px; height: 500px; background: white; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,.3); display: none; flex-direction: column; overflow: hidden; z-index: 999998; }
                .chatbot-popup.active { display: flex; }
                .chatbot-header { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white; padding:15px 20px; font-weight:bold; display:flex; justify-content: space-between; align-items:center; }
                .chatbot-close-btn { cursor:pointer; font-size:20px; opacity:.8; background:none; border:none; color:white; padding:0; line-height:1; }
                .chatbot-close-btn:hover { opacity:1; }
                .chatbot-body { flex:1; overflow-y:auto; padding:20px; background:#f8f9fa; }
                .chat-msg { margin-bottom:15px; animation: slide-up .3s ease; }
                @keyframes slide-up { from{ opacity:0; transform: translateY(10px);} to{ opacity:1; transform: translateY(0);} }
                .msg-bot { background:white; padding:10px 15px; border-radius:15px 15px 15px 5px; max-width:80%; box-shadow:0 2px 5px rgba(0,0,0,.1); font-size:14px; line-height:1.4; color:#333; }
                .msg-user { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white; padding:10px 15px; border-radius:15px 15px 5px 15px; max-width:80%; margin-left:auto; box-shadow:0 2px 5px rgba(0,0,0,.1); font-size:14px; line-height:1.4; }
                .chatbot-actions { padding:15px; background:white; border-top:1px solid #e0e0e0; max-height:200px; overflow-y:auto; }
                .chat-action-btn { display:block; width:100%; padding:10px; margin-bottom:8px; background:#f0f0f0; border:none; border-radius:8px; cursor:pointer; text-align:left; font-size:14px; color:#333; transition: all .2s; }
                .chat-action-btn:hover { background:#667eea; color:white; transform: translateX(5px); }
                @media (prefers-color-scheme: dark) {
                    .chatbot-popup { background:#1e293b; }
                    .chatbot-body { background:#0f172a; }
                    .msg-bot { background:#1e293b; color:#f1f5f9; }
                    .chatbot-actions { background:#1e293b; border-top-color:#334155; }
                    .chat-action-btn { background:#334155; color:#f1f5f9; }
                }
                `;
                doc.head.appendChild(style);
            }

            // Render floating button
            if (!doc.getElementById('chatbotContainer')) {
                const container = doc.createElement('div');
                container.id = 'chatbotContainer';
                container.className = 'chatbot-floating-container';
                container.innerHTML = `
                    <div class="chatbot-fab" onclick="toggleChatbot()">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="white">
                            <path d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 3 .97 4.29L2 22l5.71-.97C9 21.64 10.46 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.38 0-2.68-.31-3.85-.85l-.28-.14-2.85.48.48-2.85-.14-.28C4.31 14.68 4 13.38 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z"/>
                            <circle cx="9" cy="12" r="1.5"/>
                            <circle cx="15" cy="12" r="1.5"/>
                        </svg>
                    </div>
                `;
                doc.body.appendChild(container);
            }

            // Render popup
            if (!doc.getElementById('chatbotPopup')) {
                const popup = doc.createElement('div');
                popup.id = 'chatbotPopup';
                popup.className = 'chatbot-popup';
                popup.innerHTML = `
                    <div class="chatbot-header">
                        <span>📚 KJSIT Library Assistant</span>
                        <button class="chatbot-close-btn" onclick="closeChatbot()">✕</button>
                    </div>
                    <div class="chatbot-body" id="chatbotMessages">
                        <div class="chat-msg"><div class="msg-bot">👋 Hi! I'm your KJSIT Library Assistant. How can I help you today?</div></div>
                    </div>
                    <div class="chatbot-actions">
                        <button class="chat-action-btn" onclick="askQuestion('search')">🔍 How do I search for books?</button>
                        <button class="chat-action-btn" onclick="askQuestion('rate')">⭐ How do I rate a book?</button>
                        <button class="chat-action-btn" onclick="askQuestion('recommend')">🎯 How do recommendations work?</button>
                        <button class="chat-action-btn" onclick="askQuestion('mybooks')">📖 Where are my rated books?</button>
                        <button class="chat-action-btn" onclick="askQuestion('trending')">🔥 What's trending?</button>
                        <button class="chat-action-btn" onclick="askQuestion('stats')">📊 Can I see statistics?</button>
                        <button class="chat-action-btn" onclick="askQuestion('availability')">📚 Check book availability</button>
                        <button class="chat-action-btn" onclick="askQuestion('support')">💬 Contact support</button>
                    </div>
                `;
                doc.body.appendChild(popup);
            }

            // Handlers and responses in parent scope
            const responses = {
                search:{q:"How do I search for books?",a:"You can search for books by going to the '🔍 Search' tab. Simply enter the book title, author name, or genre in the search box. You can also filter results by genre and minimum rating!"},
                rate:{q:"How do I rate a book?",a:"To rate a book, click on 'View Details' button on any book card. You'll see a rating slider where you can give a rating from 1 to 5 stars. You can also write a review!"},
                recommend:{q:"How do recommendations work?",a:"Our system uses hybrid recommendations combining collaborative filtering (based on similar users' preferences) and content-based filtering (based on book similarity). Rate more books to get better personalized recommendations!"},
                mybooks:{q:"Where can I see my rated books?",a:"Go to the '📖 My Books' tab to see all the books you've rated. You can also update your ratings from there!"},
                trending:{q:"What are the trending books?",a:"Check out the '👥 Community' tab to see the most popular and trending books among KJSIT students this week!"},
                stats:{q:"Can I see statistics?",a:"Yes! Visit the '📊 Analytics' tab to see interesting statistics about books, genres, authors, and rating distributions in our library."},
                support:{q:"How do I contact support?",a:"For any issues or suggestions, please reach out to the KJSIT Library administration or your department coordinator. You can also report issues through your student portal."},
                availability:{q:"How do I check book availability?",a:"Each book shows its accession number which you can use to check availability at the KJSIT Library. You can also see external links for some books to purchase or read online."}
            };

            doc.defaultView.toggleChatbot = function() {
                const popup = doc.getElementById('chatbotPopup');
                if (popup) popup.classList.toggle('active');
            };
            doc.defaultView.closeChatbot = function() {
                const popup = doc.getElementById('chatbotPopup');
                if (popup) popup.classList.remove('active');
            };
            doc.defaultView.askQuestion = function(key) {
                const response = responses[key];
                const container = doc.getElementById('chatbotMessages');
                if (!response || !container) return;
                container.innerHTML += '<div class="chat-msg"><div class="msg-user">' + response.q + '</div></div>';
                container.scrollTop = container.scrollHeight;
                setTimeout(() => {
                    container.innerHTML += '<div class="chat-msg"><div class="msg-bot">' + response.a + '</div></div>';
                    container.scrollTop = container.scrollHeight;
                }, 400);
            };
        } catch (e) {
            console.error('Chatbot injection error:', e);
        }
    })();
    </script>
    """, height=0, scrolling=False)
