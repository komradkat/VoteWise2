# VoteWise v0.1

A modern, secure election management system built with Django. VoteWise provides a comprehensive platform for conducting online elections with real-time results tracking, user authentication, and a beautiful, responsive interface.

![VoteWise](static/img/logo.png)

## Features

### Core Functionality
- **User Authentication**: Secure login/logout system with profile management
- **Election Management**: Create and manage elections with multiple candidates
- **Real-time Results**: Live election results with dynamic vote counting
- **Responsive Design**: Mobile-first design that works on all devices
- **Modern UI**: Clean, professional interface with the "Modern Civic" design system

### User Features
- Student/voter registration and authentication
- Cast votes in active elections
- View live election results
- User profile management
- Secure session handling

### Admin Features
- Election creation and management
- Candidate management
- Results monitoring
- User administration

## Tech Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite (development)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with CSS Variables
- **Icons**: Font Awesome 6.0
- **Fonts**: Inter (Google Fonts)

## Design System

VoteWise uses the **Modern Civic** color palette for a trustworthy, modern aesthetic:

- **Primary Colors**: Navy (#0f172a), Deep Blue (#172554), Royal Blue (#2563eb)
- **Accent Colors**: Red (#e74c3c), Green (#10b981), Gold (#f59e0b)
- **Neutrals**: Slate shades for backgrounds and text

## Project Structure

```
VoteWise2/
├── apps/
│   ├── accounts/          # User authentication and profiles
│   ├── administration/    # Admin panel and management
│   ├── core/             # Core functionality and home page
│   └── elections/        # Election and voting logic
├── project_config/       # Django settings and configuration
├── static/              # Global static files (CSS, JS, images)
│   ├── css/
│   │   ├── base.css
│   │   └── includes/    # Header, footer styles
│   ├── js/
│   │   └── main.js      # Global JavaScript
│   └── img/
├── templates/           # Global templates
│   ├── base.html
│   └── includes/        # Header, footer templates
└── media/              # User-uploaded content
```

## Installation

### Prerequisites
- Python 3.10+
- pip
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd VoteWise2
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set:
   - `SECRET_KEY`: Your Django secret key
   - `DEBUG`: Set to `True` for development

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files** (if needed)
   ```bash
   python manage.py collectstatic
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Usage

### For Voters
1. Navigate to the home page
2. Click "Cast Your Vote" to log in
3. Enter your student ID/email and password
4. View active elections and cast your vote
5. Check live results on the Results page

### For Administrators
1. Access the admin panel at `/admin`
2. Create elections and add candidates
3. Monitor voting progress
4. View detailed results and analytics

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Comment complex logic
- Keep functions focused and single-purpose

### CSS Architecture
- Global styles in `static/css/base.css`
- Component styles in respective app directories
- Use CSS variables for colors and common values
- Follow BEM naming convention where applicable

## Recent Updates

### Design System Implementation
- Applied "Modern Civic" color palette across the application
- Standardized typography using Inter font
- Created consistent button and form styles
- Implemented responsive header with two-row layout

### UI/UX Improvements
- Redesigned login page with modern aesthetics
- Fixed header contrast and button sizing issues
- Added mobile menu toggle functionality
- Improved footer spacing and layout

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Security

- All passwords are hashed using Django's built-in authentication
- CSRF protection enabled on all forms
- Session security with secure cookies (in production)
- SQL injection protection via Django ORM

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## Roadmap

- [ ] Email verification for new users
- [ ] Two-factor authentication
- [ ] Advanced analytics dashboard
- [ ] Export results to PDF/CSV
- [ ] Multi-language support
- [ ] Blockchain-based vote verification

---

**VoteWise** - Making democracy accessible, secure, and transparent.
