# 📚 KJSIT Book Recommendation System

An interactive dashboard for book recommendations specifically designed for KJSIT (K. J. Somaiya Institute of Technology) students. This system provides personalized book recommendations using collaborative filtering, content-based filtering, and hybrid recommendation algorithms.

## 🚀 Features

- **Personalized Recommendations**: Get book suggestions based on your reading history and preferences
- **Advanced Search**: Search books by title, author, or genre with filtering options
- **User Authentication**: Secure login and registration system for KJSIT students
- **Interactive Dashboard**: Modern web interface built with Streamlit
- **Analytics Dashboard**: View statistics about books, ratings, and reading trends
- **Community Features**: Discover trending and popular books among peers
- **Rating System**: Rate books and write reviews to help others
- **Multiple Recommendation Engines**:
  - Collaborative Filtering (user-based)
  - Content-Based Filtering (book similarity)
  - Hybrid Recommendations (combination of both)

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with SQLAlchemy ORM
- **Database**: SQLite (can be easily switched to PostgreSQL/MySQL)
- **Machine Learning**: Scikit-learn for recommendation algorithms
- **Visualization**: Plotly for interactive charts
- **Authentication**: Custom authentication system

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager

## 🔧 Installation

1. **Clone the repository** (if applicable) or download the files to a directory

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Edit the `.env` file and update the following:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   GOOGLE_BOOKS_API_KEY=your-google-books-api-key  # Optional
   ```

5. **Initialize the database and seed sample data**:
   ```bash
   python seed_data.py
   ```

6. **Run the application**:
   ```bash
   streamlit run app.py
   ```

7. **Open your browser** and navigate to `http://localhost:8501`

## 👤 User Guide

### Registration/Login
- Use your KJSIT Student ID as username
- Default password for sample users: `password123`
- Register with your actual details for personalized experience

### Sample User Accounts
- **Student ID**: CS001, **Name**: Rahul Sharma, **Password**: password123
- **Student ID**: CS002, **Name**: Priya Patel, **Password**: password123
- **Student ID**: IT001, **Name**: Amit Kumar, **Password**: password123
- **Student ID**: IT002, **Name**: Sneha Reddy, **Password**: password123

### Navigation
1. **Home**: View personalized book recommendations
2. **Search**: Find books by title, author, or genre
3. **My Books**: View and manage your rated books
4. **Analytics**: Explore reading statistics and trends
5. **Community**: Discover popular books among KJSIT students

## 📊 Sample Data

The system comes pre-loaded with:
- **15 Programming & Technical Books**: Including Clean Code, Design Patterns, Algorithms, etc.
- **4 Sample Users**: KJSIT students from CS and IT departments
- **Sample Ratings**: Realistic rating data for testing recommendations

## 🔍 How Recommendations Work

### 1. Collaborative Filtering
- Finds users with similar reading patterns
- Recommends books liked by similar users
- Uses cosine similarity for user-to-user matching

### 2. Content-Based Filtering
- Analyzes book descriptions, titles, and genres
- Uses TF-IDF vectorization for text similarity
- Recommends books with similar content

### 3. Hybrid Approach
- Combines both collaborative and content-based methods
- Provides more accurate and diverse recommendations
- Weights recommendations based on confidence scores

## 🎯 Features for KJSIT Students

- **Department-Specific**: Books relevant to Computer Science and IT curricula
- **Academic Focus**: Technical books that complement coursework
- **Peer Learning**: See what books your classmates are reading
- **Progress Tracking**: Monitor your reading and rating activity

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: Database connection string (default: SQLite)
- `SECRET_KEY`: For session management
- `DEBUG`: Enable/disable debug mode
- `GOOGLE_BOOKS_API_KEY`: For fetching additional book information

### Database
The system uses SQLAlchemy ORM and can work with:
- SQLite (default)
- PostgreSQL
- MySQL
- Other SQL databases

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Production Deployment
1. Set `DEBUG=False` in `.env`
2. Use a production WSGI server like Gunicorn
3. Set up a production database (PostgreSQL recommended)
4. Configure proper authentication and security

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Create an issue on GitHub
3. Contact the development team

## 🔮 Future Enhancements

- [ ] Integration with Google Books API for more book data
- [ ] Social features (book clubs, reading challenges)
- [ ] Mobile-responsive design improvements
- [ ] Advanced analytics and reporting
- [ ] Integration with library management systems
- [ ] Multi-language support
- [ ] Book availability checking

---

**Built with ❤️ for KJSIT students**

*Empowering learning through intelligent book recommendations*
