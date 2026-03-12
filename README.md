# Drag'n'Scroll - Chinese Learning App
A modern Chinese language learning application with a TikTok-style interface and Spaced Repetition System (SRS).

## 🎯 Features
- **TikTok-Style Interface**: Vertical swipe navigation for an immersive learning experience
- **SuperMemo SM-2 Algorithm**: Proven spaced repetition system for effective vocabulary retention
- **Multi-language Support**: Learn with Russian or Kazakh translations
- **Progress Tracking**: XP system, streaks, and detailed statistics
- **HSK-aligned Content**: Structured courses for HSK 1-6 levels
- **Gamification**: Earn XP, maintain streaks, and track your learning journey

## 🏗️ Architecture

### Backend (Django REST Framework)
- Python 3.9+
- Django 4.2
- PostgreSQL database
- JWT authentication (SimpleJWT)
- SuperMemo SM-2 algorithm implementation

### Frontend (Vue 3)
- TypeScript
- Vite build system
- Pinia state management
- Vue Router
- Axios for API  communication

## 📁 Project Structure
Drag'n'Scroll/
├── backend/                 # Django REST API
│   ├── config/             # Django settings
│   ├── core/               # User & Profile models
│   ├── course/             # Course structure
│   ├── vocab/              # Vocabulary & Grammar
│   ├── learning            # Sessions & SRS
│   ├── manage.py
│   └── requirement.txt
├── frontend/               # Vue 3 Application
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # Vue components
│   │   ├── stores/        # Pinia stores
│   │   ├── views/         # Page views
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Populate with realistic sample data (RECOMMENDED!)
python manage.py populate_chats
python manage.py populate_videos

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
```


Backend API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start dev server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 📚 Sample Data

The project includes management commands to populate the database with realistic sample data:

### Chat Data
```bash
python manage.py populate_chats
```
Creates:
- **6 users** with learning profiles
- **7 chat rooms** (DMs + group chats)
- **75+ messages** with realistic Chinese learning conversations
- **6 stories** with views and reactions

### Video Data
```bash
python manage.py populate_videos
```

Creates:
- **5 content creators**
- **7 video categories** (Vocabulary, Grammar, Culture, etc.)
- **18 educational videos** with realistic interactions
- **61 hashtags** for content discovery
- **User interactions** (views, likes, comments, bookmarks)

**For detailed information, see [backend/POPULATE_DATA.md](backend/POPULATE_DATA.md)**

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/refresh/` - Refresh JWT token

### Learning
- `GET /api/learning/current-session/` - Get current lesson
- `POST /api/learning/submit-step/` - Submit step answer
- `POST /api/learning/finish-session/` - Complete session

### Vocabulary
- `GET /api/vocab/words/` - List all words
- `GET /api/vocab/my-words/` - Get user's vocabulary
- `GET /api/vocab/grammar/` - List grammar rules

### SRS (Spaced Repetition)
- GET /api/learning/srs/review-batch/` - Get words for review
- POST /api/learning/srs/submit-review/` - Submit review results
- GET /api/learning/srs/stats/` - Get SRS statistics

See [backend/README.md](./backend/README.md) for complete API documentation.

## 🧠 SRS Algorithm

The app implements the SuperMemo SM-2 algorithm with quality ratings:

- **5**: Perfect response (< 3 sec)
- **4**: Correct response (3-10 sec)
- **3**: Correct response (> 10 sec or with difficulty)
- **2**: Incorrect but remembered with hint
- **1**: Incorrect but recognized correct answer
- **0**: Complete failure

Intervals increase based on performance and ease factor.

## 🎨 UI/UX Features

### TikTok-Style Navigation
- **Swipe Up**: Next card/step
- **Swipe Down**: Previous card/step
- **Tap**: Reveal answer (flashcards)
- **Keyboard**: Arrow keys for navigation

### Card Types
1. **Vocabulary Intro**: Learn new words
2. **Vocabulary Recognize**: Multiple choice quiz
3. **Grammar Introduction**: Rules with examples
4. **Build Phrase**: Drag-and-drop sentence building
5. **SRS Review**: Spaced repetition flashcards

## 📊 Data Models

### User & Progress
- Custom User model with profile
- Learning language preference (RU/KZ)
- Course progress tracking
- XP and streak system

### Course Structure
- Course (HSK 1-6)
- Course Days (30+ days per course)
- Lessons (Vocabulary/Grammar/Mixed)
- Lesson Steps (Interactive exercises)

### Vocabulary
- Words with hanzi, pinyin, translations
- Audio pronunciation
- HSK level and frequency ranking
- Grammar rules with examples

### SRS Data
- Word progress with SM-2 parameters
- Review history for analytics
- Dynamic review scheduling

## 🔒 Security

- JWT-based authentication
- Token refresh mechanism
- CORS configuration
- Protected API endpoints
- Password validation

## 📱 Responsive Design

- Mobile-first approach
- Touch gestures for mobile
- Keyboard shortcuts for desktop
- Adaptive layouts for all screen sizes

## 🧪 Development

### Backend Testing
```bash
cd backend
python manage.py test
```

### Frontend Development
```bash
cd frontend
npm run type-check  # TypeScript checking
npm run lint        # ESLint
```

### Database Management
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 📦 Deployment

### Backend (Production)
1. Set `DEBUG=False` in `.env`
2. Configure production database
3. Set up static file serving
4. Use Gunicorn + Nginx
5. Configure HTTPS

### Frontend (Production)
1. Build: `npm run build`
2. Deploy `dist/` to static hosting
3. Configure environment variables
4. Set up proper CORS

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

##  Acknowledgments

- SuperMemo SM-2 algorithm
- HSK standardized curriculum
- TikTok for UI inspiration
- Django REST Framework
- Vue.js team

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ for Chinese language learners
