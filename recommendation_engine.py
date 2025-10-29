import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import logging
from typing import List, Dict, Tuple, Optional
import os
from models import Book, Rating, User, get_session
from sqlalchemy.orm import joinedload

class BookRecommendationEngine:
    def __init__(self):
        self.session = get_session()
        self.books_df = None
        self.ratings_matrix = None
        self.user_similarity = None
        self.book_similarity = None
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None
        self.load_data()

    def load_data(self):
        """Load books and ratings data from database"""
        try:
            # Load books with ratings
            books = self.session.query(Book).options(
                joinedload(Book.ratings)
            ).all()

            # Create books dataframe
            books_data = []
            for book in books:
                books_data.append({
                    'book_id': book.id,
                    'accession_number': book.accession_number or '',
                    'title': book.title,
                    'author': book.author,
                    'genre': book.genre or '',
                    'description': book.description or '',
                    'price': book.price,
                    'average_rating': book.average_rating,
                    'total_ratings': book.total_ratings
                })

            self.books_df = pd.DataFrame(books_data)

            # Load ratings
            ratings = self.session.query(Rating).all()
            ratings_data = []
            for rating in ratings:
                ratings_data.append({
                    'user_id': rating.user_id,
                    'book_id': rating.book_id,
                    'rating': rating.rating
                })

            self.ratings_df = pd.DataFrame(ratings_data)

            # Create user-item matrix (handle duplicate user-book pairs)
            if not self.ratings_df.empty:
                self.ratings_matrix = self.ratings_df.pivot_table(
                    index='user_id',
                    columns='book_id',
                    values='rating',
                    aggfunc='mean'
                ).fillna(0)

                # Calculate item similarity matrix
                self.book_similarity = cosine_similarity(self.ratings_matrix.T)
                self.book_similarity_df = pd.DataFrame(
                    self.book_similarity,
                    index=self.ratings_matrix.columns,
                    columns=self.ratings_matrix.columns
                )

            # Setup content-based filtering
            self._setup_content_based_filtering()

        except Exception as e:
            logging.error(f"Error loading data: {e}")
            self.books_df = pd.DataFrame()
            self.ratings_df = pd.DataFrame()

    def _setup_content_based_filtering(self):
        """Setup TF-IDF vectorizer for content-based filtering"""
        if self.books_df.empty:
            return

        # Combine title, author, genre, and description for content similarity
        self.books_df['content'] = (
            self.books_df['title'].fillna('') + ' ' +
            self.books_df['author'].fillna('') + ' ' +
            self.books_df['genre'].fillna('') + ' ' +
            self.books_df['description'].fillna('')
        )

        # Create TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )

        try:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
                self.books_df['content']
            )
        except ValueError:
            # Handle case where content is empty
            self.tfidf_matrix = None

    def get_popular_books(self, limit: int = 10) -> List[Dict]:
        """Get popular books based on ratings"""
        if self.books_df.empty:
            return []

        popular_books = self.books_df[
            self.books_df['total_ratings'] > 0
        ].sort_values('average_rating', ascending=False).head(limit)

        return popular_books.to_dict('records')

    def get_books_by_genre(self, genre: str, limit: int = 10) -> List[Dict]:
        """Get books by specific genre"""
        if self.books_df.empty:
            return []

        genre_books = self.books_df[
            self.books_df['genre'].str.contains(genre, case=False, na=False)
        ].sort_values('average_rating', ascending=False).head(limit)

        return genre_books.to_dict('records')

    def get_collaborative_filtering_recommendations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """Get recommendations using collaborative filtering"""
        if self.ratings_matrix is None or user_id not in self.ratings_matrix.index:
            return []

        # Find similar users
        user_ratings = self.ratings_matrix.loc[user_id]
        user_similarity = cosine_similarity(
            [user_ratings],
            self.ratings_matrix
        )[0]

        # Get weighted ratings from similar users
        similar_users_ratings = self.ratings_matrix.mul(user_similarity, axis=0)
        recommendations = similar_users_ratings.sum(axis=0)

        # Filter out books already rated by user
        user_rated_books = self.ratings_matrix.loc[user_id]
        user_rated_books = user_rated_books[user_rated_books > 0].index

        recommendations = recommendations.drop(user_rated_books)
        recommendations = recommendations.sort_values(ascending=False).head(limit)

        # Get book details
        recommended_books = []
        for book_id in recommendations.index:
            book_data = self.books_df[self.books_df['book_id'] == book_id]
            if not book_data.empty:
                book_dict = book_data.iloc[0].to_dict()
                book_dict['predicted_rating'] = recommendations[book_id]
                recommended_books.append(book_dict)

        return recommended_books

    def get_content_based_recommendations(
        self,
        book_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """Get content-based recommendations"""
        if self.tfidf_matrix is None or book_id not in self.books_df['book_id'].values:
            return []

        # Find the index of the book
        book_idx = self.books_df[self.books_df['book_id'] == book_id].index[0]

        # Calculate cosine similarity
        if self.tfidf_matrix is not None:
            similarity_scores = cosine_similarity(
                self.tfidf_matrix[book_idx:book_idx+1],
                self.tfidf_matrix
            )[0]

            # Get top similar books
            similar_indices = similarity_scores.argsort()[::-1][1:limit+1]

            recommendations = []
            for idx in similar_indices:
                book_data = self.books_df.iloc[idx]
                book_dict = book_data.to_dict()
                book_dict['similarity_score'] = similarity_scores[idx]
                recommendations.append(book_dict)

            return recommendations

        return []

    def get_hybrid_recommendations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """Get hybrid recommendations combining collaborative and content-based"""
        # Return early if no ratings available
        if self.ratings_df is None or self.ratings_df.empty:
            return []

        # Get collaborative filtering recommendations
        cf_recommendations = self.get_collaborative_filtering_recommendations(
            user_id, limit * 2
        )

        # Get content-based recommendations for user's highly rated books
        user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
        high_rated_books = user_ratings[user_ratings['rating'] >= 4.0]['book_id'].tolist()

        content_recommendations = []
        for book_id in high_rated_books[:3]:  # Use top 3 highly rated books
            content_recs = self.get_content_based_recommendations(book_id, limit // 3)
            content_recommendations.extend(content_recs)

        # Combine and deduplicate
        all_recommendations = {}
        for rec in cf_recommendations + content_recommendations:
            book_id = rec['book_id']
            if book_id not in all_recommendations:
                all_recommendations[book_id] = rec

        # Sort by predicted rating/similarity score
        sorted_recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x.get('predicted_rating', 0) or x.get('similarity_score', 0),
            reverse=True
        )

        return sorted_recommendations[:limit]

    def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """Search books by title, author, or genre"""
        if self.books_df.empty:
            return []

        # Simple text search
        mask = (
            self.books_df['title'].str.contains(query, case=False, na=False) |
            self.books_df['author'].str.contains(query, case=False, na=False) |
            self.books_df['genre'].str.contains(query, case=False, na=False)
        )

        results = self.books_df[mask].sort_values('average_rating', ascending=False).head(limit)
        return results.to_dict('records')

    def get_book_details(self, book_id: int) -> Optional[Dict]:
        """Get detailed information about a specific book"""
        book_data = self.books_df[self.books_df['book_id'] == book_id]
        if book_data.empty:
            return None

        book_dict = book_data.iloc[0].to_dict()

        # Add user ratings for this book
        book_ratings = self.ratings_df[self.ratings_df['book_id'] == book_id]
        if not book_ratings.empty:
            book_dict['user_ratings'] = book_ratings.to_dict('records')

        return book_dict

    def refresh_data(self):
        """Refresh data from database"""
        self.load_data()

# Global recommendation engine instance
recommendation_engine = BookRecommendationEngine()
