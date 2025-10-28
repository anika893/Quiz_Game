# Quiz Pool App - Web Version

A modern, interactive quiz application built with Flask and beautiful HTML interfaces. This application allows teachers to create and manage quizzes while students can take quizzes and receive instant feedback.

## Features

### For Teachers
- **Create Quizzes**: Create unlimited quizzes with custom questions and answers
- **Manage Questions**: Add, edit, and delete questions from existing quizzes
- **Student Tracking**: Monitor student performance and results
- **PDF Reports**: Generate detailed PDF reports for quiz results

### For Students
- **Interactive Quizzes**: Take quizzes with a modern, responsive interface
- **Instant Feedback**: Get immediate score feedback after completing quizzes
- **Answer Review**: Review incorrect answers to learn from mistakes
- **PDF Downloads**: Download detailed result reports as PDF files

## Project Structure

```
Quiz_Game/
├── main.py                 # Main Flask application
├── database.py            # Database operations module
├── teacher.py             # Teacher functionality module
├── student.py             # Student functionality module
├── pdf_generator.py       # PDF report generation module
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── about.html        # About page
│   ├── 404.html          # Error page
│   ├── 500.html          # Server error page
│   ├── teacher/          # Teacher templates
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   └── create_quiz.html
│   └── student/          # Student templates
│       ├── details.html
│       ├── dashboard.html
│       ├── take_quiz.html
│       └── results.html
└── static/               # Static files
    ├── css/
    │   └── style.css     # Custom CSS
    └── js/
        └── main.js       # Custom JavaScript
```

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   - Ensure SQL Server is running
   - Update database connection details in `database.py` if needed
   - The app will automatically create tables as needed

3. **Run the Application**:
   ```bash
   python main.py
   ```

4. **Access the Application**:
   - Open your web browser
   - Navigate to `http://localhost:5000`

## Usage

### Teacher Login
- Default password: `1234`
- Navigate to Teacher Login from the home page
- Create new quizzes or manage existing ones

### Student Portal
- Click "Student Portal" from the home page
- Enter your student details
- Select and take available quizzes

## Key Improvements

### Modular Architecture
- **Separation of Concerns**: Each feature is in its own module
- **Maintainability**: Easy to modify and extend individual features
- **Scalability**: Add new features without affecting existing code

### Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Bootstrap 5**: Modern, professional UI components
- **Font Awesome**: Beautiful icons throughout the interface
- **Custom CSS**: Enhanced styling and animations

### Enhanced User Experience
- **Real-time Timer**: Track time during quizzes
- **Progress Indicators**: Visual feedback for quiz progress
- **Flash Messages**: Clear success/error notifications
- **Smooth Animations**: Hover effects and transitions

### Technical Features
- **Flask Blueprints**: Organized routing and functionality
- **Session Management**: Secure user sessions
- **Form Validation**: Client and server-side validation
- **Error Handling**: Graceful error pages and messages

## Dependencies

- **Flask**: Web framework
- **pyodbc**: Database connectivity
- **reportlab**: PDF generation
- **Bootstrap 5**: CSS framework
- **Font Awesome**: Icon library

## Security Notes

- Change the secret key in `main.py` for production use
- Implement proper authentication for production
- Use HTTPS in production environments
- Validate all user inputs

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.