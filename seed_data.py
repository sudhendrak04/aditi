import pandas as pd
from models import get_session, Book, User, Rating, Review, create_tables
from recommendation_engine import recommendation_engine
import random
from datetime import datetime, timedelta
import hashlib

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def map_branch_to_department(branch):
    """Map library branch to student department"""
    branch_mapping = {
        'BASIC SCIENCE AND HUMANITIES': 'Computer Science',
        'COMPUTER': 'Computer Science',
        'INFORMATION TECHNOLOGY': 'Information Technology',
        'ELECTRONICS': 'Electronics',
        'ELECTRONICS AND TELECOMMUNICATIONS': 'Electronics and Telecommunications'
    }
    return branch_mapping.get(branch, 'Computer Science')

def generate_isbn(accession_number):
    """Generate a pseudo-ISBN from accession number"""
    # Create a deterministic ISBN-like string from accession number
    base = accession_number.replace('CB', '').zfill(6)
    return f"978-0-{base[:3]}-{base[3:6]}-{base[-1]}"

def seed_kjsit_data():
    """Seed the database with real KJSIT Library Book Bank data"""
    session = get_session()

    try:
        # Create tables
        create_tables()

        print("📚 Loading KJSIT Library Book Bank data...")

        # Load the Excel file
        df = pd.read_excel('KJSIT Library Book Bank data.xlsx', header=1)

        print(f"📊 Loaded {len(df)} books from KJSIT Library")

        # Clean and prepare data
        df = df.dropna(subset=['Title', 'Author'])  # Remove rows without title or author
        df['Title'] = df['Title'].str.strip()
        df['Author'] = df['Author'].str.strip()
        df['Publisher'] = df['Publisher'].str.strip()
        df['Branch'] = df['Branch'].str.strip()

        # NOTE: We're keeping all books including duplicates/editions
        # Each accession number represents a unique copy/edition
        print(f"✅ Loaded data: {len(df)} books (including all editions)")

        # Add ALL books to database (including duplicates/editions)
        # Each accession number represents a unique copy/edition
        books_added = 0
        for _, row in df.iterrows():
            # Generate ISBN from accession number
            isbn = generate_isbn(str(row['Accession number']))

            # Map branch to genre
            branch = str(row['Branch'])
            genre_mapping = {
                'BASIC SCIENCE AND HUMANITIES': 'Engineering Physics',
                'COMPUTER': 'Computer Science',
                'INFORMATION TECHNOLOGY': 'Information Technology',
                'ELECTRONICS': 'Electronics',
                'ELECTRONICS AND TELECOMMUNICATIONS': 'Electronics and Telecommunications'
            }
            genre = genre_mapping.get(branch, 'General')

            # Create book record (we're keeping ALL books now)
            book = Book(
                isbn=isbn,
                accession_number=str(row['Accession number']),
                title=str(row['Title']),
                author=str(row['Author']),
                genre=genre,
                publisher=str(row['Publisher']) if pd.notna(row['Publisher']) else None,
                price=float(row['Price']) if pd.notna(row['Price']) else None,
                description=f"A textbook from KJSIT Library Book Bank - {genre} department.",
                publication_year=None,  # Not available in data
                pages=None,  # Not available in data
                language='English',
                cover_url=None
            )

            session.add(book)
            books_added += 1

        session.commit()
        print(f"✅ Added {books_added} books to database")

        # Create KJSIT student users
        kjsit_users = [
            {
                'student_id': '21CS001',
                'name': 'Arjun Sharma',
                'email': 'arjun.sharma@kjsit.edu.in',
                'department': 'Computer Science',
                'year': 'TE',
                'password_hash': hash_password('password123')
            },
            {
                'student_id': '21CS002',
                'name': 'Priya Patel',
                'email': 'priya.patel@kjsit.edu.in',
                'department': 'Computer Science',
                'year': 'BE',
                'password_hash': hash_password('password123')
            },
            {
                'student_id': '21IT001',
                'name': 'Rohit Kumar',
                'email': 'rohit.kumar@kjsit.edu.in',
                'department': 'Information Technology',
                'year': 'SE',
                'password_hash': hash_password('password123')
            },
            {
                'student_id': '21IT002',
                'name': 'Sneha Reddy',
                'email': 'sneha.reddy@kjsit.edu.in',
                'department': 'Information Technology',
                'year': 'FE',
                'password_hash': hash_password('password123')
            },
            {
                'student_id': '21ET001',
                'name': 'Kavita Singh',
                'email': 'kavita.singh@kjsit.edu.in',
                'department': 'Electronics and Telecommunications',
                'year': 'TE',
                'password_hash': hash_password('password123')
            },
            {
                'student_id': '21ET002',
                'name': 'Vikram Gupta',
                'email': 'vikram.gupta@kjsit.edu.in',
                'department': 'Electronics and Telecommunications',
                'year': 'BE',
                'password_hash': hash_password('password123')
            },
            {
                'student_id': '21EL001',
                'name': 'Anjali Desai',
                'email': 'anjali.desai@kjsit.edu.in',
                'department': 'Electronics',
                'year': 'SE',
                'password_hash': hash_password('password123')
            },
            {
                'student_id': '21BS001',
                'name': 'Rahul Mehta',
                'email': 'rahul.mehta@kjsit.edu.in',
                'department': 'Computer Science',
                'year': 'FE',
                'password_hash': hash_password('password123')
            }
        ]

        # Add users to database
        for user_data in kjsit_users:
            existing_user = session.query(User).filter_by(student_id=user_data['student_id']).first()
            if not existing_user:
                user = User(**user_data)
                session.add(user)

        session.commit()
        print(f"✅ Added {len(kjsit_users)} KJSIT student users")

        # Get all books and users
        books = session.query(Book).all()
        users = session.query(User).all()

        print(f"📈 Total books in database: {len(books)}")
        print(f"👥 Total users in database: {len(users)}")

        # Generate realistic ratings based on department preferences
        ratings_data = []
        for user in users:
            # Each user rates 8-15 books from their department and related departments
            num_ratings = random.randint(8, 15)

            # Get books from user's department
            user_dept_books = [b for b in books if b.genre == user.department]
            other_books = [b for b in books if b.genre != user.department]

            # Mix of department books and other books
            dept_book_count = int(num_ratings * 0.7)  # 70% from own department
            other_book_count = num_ratings - dept_book_count

            rated_books = []

            if user_dept_books:
                rated_books.extend(random.sample(user_dept_books, min(dept_book_count, len(user_dept_books))))

            if other_books and other_book_count > 0:
                rated_books.extend(random.sample(other_books, min(other_book_count, len(other_books))))

            # Generate ratings
            for book in rated_books:
                # Higher ratings for department books
                if book.genre == user.department:
                    rating = round(random.uniform(3.5, 5.0), 1)
                else:
                    rating = round(random.uniform(3.0, 4.5), 1)

                ratings_data.append({
                    'user_id': user.id,
                    'book_id': book.id,
                    'rating': rating
                })

        # Clear existing ratings to keep data idempotent on reseed
        session.query(Rating).delete()

        # Add ratings to database
        for rating_data in ratings_data:
            rating = Rating(**rating_data)
            session.add(rating)

        session.commit()
        print(f"⭐ Generated {len(ratings_data)} realistic ratings")

        # Update book statistics
        for book in books:
            ratings = session.query(Rating).filter_by(book_id=book.id).all()
            if ratings:
                avg_rating = sum(r.rating for r in ratings) / len(ratings)
                book.average_rating = round(avg_rating, 2)
                book.total_ratings = len(ratings)

        session.commit()

        print("\n📊 Database Statistics:")
        print(f"   • Books: {len(books)}")
        print(f"   • Users: {len(users)}")
        print(f"   • Ratings: {len(ratings_data)}")
        print(f"   • Average ratings per book: {len(ratings_data) / len(books):.1f}")

        # Show genre distribution
        genre_counts = {}
        for book in books:
            genre_counts[book.genre] = genre_counts.get(book.genre, 0) + 1

        print("\n📚 Books by Department:")
        for genre, count in sorted(genre_counts.items()):
            print(f"   • {genre}: {count} books")

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

def seed_sample_data():
    """Compatibility wrapper expected by run.py"""
    seed_kjsit_data()

if __name__ == "__main__":
    seed_kjsit_data()
