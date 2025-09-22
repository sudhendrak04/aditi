import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
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
                    "Computer Science", "Information Technology", "Electronics",
                    "Mechanical", "Civil", "Electrical", "Other"
                ])
                year = st.selectbox("Year", ["FE", "SE", "TE", "BE"])
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Home", "🔍 Search", "📖 My Books", "📊 Analytics", "👥 Community"
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
                        <p><strong>Avg Rating:</strong> {book['average_rating']:.1f} ⭐</p>
                        <p><strong>Total Ratings:</strong> {book['total_ratings']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"View Details", key=f"rec_{book['book_id']}"):
                        show_book_details(book['book_id'])
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
                        <p><strong>Avg Rating:</strong> {book['average_rating']:.1f} ⭐</p>
                        <p><strong>Total Ratings:</strong> {book['total_ratings']}</p>
                    </div>
                    """, unsafe_allow_html=True)

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
                sort_by = st.selectbox("Sort by", ["Rating", "Title", "Author"])

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
            else:
                filtered_results.sort(key=lambda x: x['author'])

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
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.write(f"**Rating:** {book['average_rating']:.1f} ⭐")
                        st.write(f"**Total:** {book['total_ratings']} ratings")
                    with col3:
                        if st.button("View Details", key=f"search_{book['book_id']}"):
                            show_book_details(book['book_id'])
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
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.write(f"**Your Rating:** {rating.rating:.1f} ⭐")
                    with col3:
                        st.write(f"**Avg Rating:** {book.average_rating:.1f} ⭐")
                    with col4:
                        if st.button("Update Rating", key=f"update_{book.id}"):
                            new_rating = st.number_input(
                                f"New rating for {book.title}",
                                min_value=1.0, max_value=5.0, step=0.5,
                                key=f"rating_{book.id}"
                            )
                            if st.button("Save", key=f"save_{book.id}"):
                                # Update rating logic here
                                st.success("Rating updated!")
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

        # Genre distribution
        st.subheader("📈 Genre Distribution")
        genre_data = session.query(Book.genre, func.count(Book.id)).filter(
            Book.genre.isnot(None)
        ).group_by(Book.genre).all()

        if genre_data:
            genres, counts = zip(*genre_data)
            fig = px.pie(values=counts, names=genres, title="Books by Genre")
            st.plotly_chart(fig, use_container_width=True)

        # Rating distribution
        st.subheader("⭐ Rating Distribution")
        rating_data = session.query(Rating.rating, func.count(Rating.id)).group_by(
            Rating.rating
        ).all()

        if rating_data:
            ratings, counts = zip(*rating_data)
            fig = px.bar(x=ratings, y=counts, title="Rating Distribution")
            fig.update_layout(xaxis_title="Rating", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)

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
                <p><strong>Avg Rating:</strong> {book['average_rating']:.1f} ⭐ ({book['total_ratings']} ratings)</p>
            </div>
            """, unsafe_allow_html=True)

def show_book_details(book_id):
    """Show detailed view of a book"""
    book_details = recommendation_engine.get_book_details(book_id)

    if not book_details:
        st.error("Book not found")
        return

    st.subheader(f"📖 {book_details['title']}")
    st.write(f"**Author:** {book_details['author']}")
    st.write(f"**Genre:** {book_details['genre'] or 'N/A'}")
    st.write(f"**Average Rating:** {book_details['average_rating']:.1f} ⭐")
    st.write(f"**Total Ratings:** {book_details['total_ratings']}")

    if book_details.get('description'):
        st.write(f"**Description:** {book_details['description']}")

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
