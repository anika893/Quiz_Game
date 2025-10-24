"""
Main Application Module for Quiz Pool App
Entry point that coordinates all modules and provides the main interface
"""

from flask import Flask, render_template, redirect, url_for, flash, session
from database import DatabaseManager
from teacher import teacher_bp
from student import student_bp
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Register blueprints
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)

# Initialize database manager
db_manager = DatabaseManager()

# Test database connection on startup
if not db_manager.connect():
    print("WARNING: Could not connect to database. Please check your SQL Server connection.")
else:
    print("Database connection established successfully.")


@app.route('/')
def index():
    """Main page with role selection"""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        os.makedirs('static/css')
        os.makedirs('static/js')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
