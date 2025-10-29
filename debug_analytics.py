import streamlit as st
import pandas as pd
import plotly.express as px
from models import get_session, User, Book, Rating
from sqlalchemy import func

def debug_analytics_page():
    st.subheader("📊 Analytics Dashboard - Debug Version")

    # Get overall statistics
    session = get_session()
    try:
        total_books = session.query(Book).count()
        total_users = session.query(User).count()
        total_ratings = session.query(Rating).count()

        st.write(f"**Database Statistics:**")
        st.write(f"- Total Books: {total_books}")
        st.write(f"- Total Users: {total_users}")
        st.write(f"- Total Ratings: {total_ratings}")

        # Genre distribution
        st.subheader("📈 Genre Distribution")
        genre_data = session.query(Book.genre, func.count(Book.id)).filter(
            Book.genre.isnot(None)
        ).group_by(Book.genre).all()
        
        st.write(f"Found {len(genre_data)} genres in database")
        
        if genre_data:
            genres, counts = zip(*genre_data)
            st.write("Genre data:", dict(zip(genres, counts)))
            
            # Create DataFrame for better handling
            genre_df = pd.DataFrame({'Genre': genres, 'Count': counts})
            st.write("Genre DataFrame:")
            st.dataframe(genre_df)
            
            try:
                fig = px.pie(genre_df, values='Count', names='Genre', title="Books by Genre")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating pie chart: {e}")
        else:
            st.warning("No genre data found")

        # Rating distribution
        st.subheader("⭐ Rating Distribution")
        rating_data = session.query(Rating.rating, func.count(Rating.id)).group_by(
            Rating.rating
        ).all()
        
        st.write(f"Found {len(rating_data)} rating values in database")
        
        if rating_data:
            ratings, counts = zip(*rating_data)
            st.write("Rating data:", dict(zip(ratings, counts)))
            
            # Create DataFrame for better handling
            rating_df = pd.DataFrame({'Rating': ratings, 'Count': counts})
            st.write("Rating DataFrame:")
            st.dataframe(rating_df)
            
            try:
                fig = px.bar(rating_df, x='Rating', y='Count', title="Rating Distribution")
                fig.update_layout(xaxis_title="Rating", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating bar chart: {e}")
        else:
            st.warning("No rating data found")

    except Exception as e:
        st.error(f"Error in analytics: {e}")
        import traceback
        st.text(traceback.format_exc())
    finally:
        session.close()

if __name__ == "__main__":
    debug_analytics_page()