# Happy Scissors Salon Management System

## 📋 Project Overview

Happy Scissors Salon Management System is a comprehensive digital solution designed to streamline operations for Happy Scissors Hair Salon. The system addresses current manual process challenges by providing an efficient appointment management platform that reduces scheduling conflicts, improves staff productivity, and enhances customer experience.

### Key Features
- **Online Appointment Booking** - Clients can book services 24/7
- **Staff Scheduling** - Optimized staff allocation and calendar management
- **Client Database** - Secure storage of client preferences and history
- **Business Analytics** - Reporting and insights for data-driven decisions
- **Walk-in Management** - Queue system for non-appointment clients

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL
- Git

### Installation

#### Backend Setup (Django)
```bash
# Clone the repository
git clone [repository-url]
cd happy-scissors-salon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials and settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

#### Frontend Setup (React)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.2+
- **API**: Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Django Allauth
- **Deployment**: Vercel

### Frontend
- **Framework**: React 18+
- **Routing**: React Router
- **HTTP Client**: Axios
- **UI Components**: Material-UI (optional)

## 📁 Project Structure

```
happy-scissors-salon/
├── backend/                 # Django project
│   ├── api/                # REST API app
│   ├── users/              # Authentication app
│   ├── appointments/        # Booking management
│   ├── services/           # Service catalog
│   └── manage.py
├── frontend/               # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.js
│   └── package.json
├── docs/                   # Documentation
└── README.md
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory with:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://user:password@localhost/happy_scissors
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Setup
1. Install PostgreSQL
2. Create database: `createdb happy_scissors`
3. Update DATABASE_URL in your .env file

## 🎯 Development Workflow

1. **Setup Development Environment**
   - Install required software
   - Set up virtual environment
   - Configure database

2. **Run Development Servers**
   ```bash
   # Terminal 1 - Backend
   python manage.py runserver

   # Terminal 2 - Frontend  
   cd frontend && npm start
   ```

3. **Access Applications**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - Admin Panel: http://localhost:8000/admin

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request


---

**Happy Coding!** 🎉
