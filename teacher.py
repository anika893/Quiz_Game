"""
Teacher Module for Quiz Pool App
Handles teacher-related functionality including quiz creation and management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import DatabaseManager
import re

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')
db_manager = DatabaseManager()

# Teacher password for authentication
TEACHER_PASSWORD = "1234"


@teacher_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Teacher login page"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('teacher/login.html')
        
        # Try to authenticate with registered teachers first
        teacher_data = db_manager.authenticate_teacher(email, password)
        if teacher_data:
            session['teacher_logged_in'] = True
            session['teacher_data'] = teacher_data
            flash(f'Welcome back, {teacher_data["name"]}!', 'success')
            return redirect(url_for('teacher.dashboard'))
        
        # Fallback to old password system for backward compatibility
        if password == TEACHER_PASSWORD:
            session['teacher_logged_in'] = True
            session['teacher_data'] = {'name': 'Admin Teacher', 'teacher_id': 1}
            flash('Logged in with admin access.', 'info')
            return redirect(url_for('teacher.dashboard'))
        
        flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('teacher/login.html')


@teacher_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Teacher registration page"""
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not all([teacher_id, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('teacher/register.html', teachers=db_manager.get_all_teachers())
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('teacher/register.html', teachers=db_manager.get_all_teachers())
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('teacher/register.html', teachers=db_manager.get_all_teachers())
        
        # Check if teacher is already registered
        if db_manager.is_teacher_registered(email):
            flash('This email is already registered. Please use a different email or try logging in.', 'error')
            return render_template('teacher/register.html', teachers=db_manager.get_all_teachers())
        
        # Validate teacher email
        if not db_manager.validate_teacher_email(int(teacher_id), email):
            flash('Email does not match the selected teacher\'s email in our records.', 'error')
            return render_template('teacher/register.html', teachers=db_manager.get_all_teachers())
        
        # Get teacher name
        teachers = db_manager.get_all_teachers()
        teacher_name = next((t['name'] for t in teachers if t['id'] == int(teacher_id)), None)
        
        if not teacher_name:
            flash('Invalid teacher selection.', 'error')
            return render_template('teacher/register.html', teachers=teachers)
        
        # Register the teacher
        if db_manager.register_teacher(int(teacher_id), teacher_name, email, password):
            # Create teacher folder
            db_manager.create_teacher_folder(int(teacher_id), teacher_name)
            
            flash(f'Registration successful! Welcome, {teacher_name}!', 'success')
            return redirect(url_for('teacher.login'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    teachers = db_manager.get_all_teachers()
    return render_template('teacher/register.html', teachers=teachers)


@teacher_bp.route('/dashboard')
def dashboard():
    """Teacher dashboard showing available options"""
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher.login'))
    
    teacher_data = session.get('teacher_data', {})
    teacher_name = teacher_data.get('name', 'Teacher')
    
    return render_template('teacher/dashboard.html', teacher_name=teacher_name)


@teacher_bp.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    """Create a new quiz - SIMPLIFIED APPROACH"""
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher.login'))
    
    teacher_data = session.get('teacher_data', {})
    teacher_name = teacher_data.get('name', 'Admin Teacher')
    
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        timer_minutes = int(request.form.get('timer_minutes', 0))
        
        if not subject:
            flash('Please enter a quiz subject.', 'error')
            return render_template('teacher/create_quiz.html')
        
        # Use the new simplified quiz creation
        if db_manager.create_simple_quiz(subject, timer_minutes, teacher_name):
            flash(f'Quiz "{subject}" created successfully! You can now add questions to it.', 'success')
            return redirect(url_for('teacher.manage_quizzes'))
        else:
            flash('Failed to create quiz. Please try again.', 'error')
    
    return render_template('teacher/create_quiz.html')


@teacher_bp.route('/manage_quizzes')
def manage_quizzes():
    """Manage existing quizzes - SIMPLIFIED APPROACH"""
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher.login'))
    
    teacher_data = session.get('teacher_data', {})
    teacher_name = teacher_data.get('name', 'Admin Teacher')
    
    # Use the new simplified quiz retrieval
    quizzes = db_manager.get_simple_quizzes(teacher_name)
    
    return render_template('teacher/manage_quizzes.html', quizzes=quizzes, teacher_name=teacher_name)


@teacher_bp.route('/edit_quiz/<table_name>')
def edit_quiz(table_name):
    """Edit quiz questions"""
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher.login'))
    
    subject = request.args.get('subject', table_name.replace('_', ' ').title())
    questions = db_manager.get_all_questions(table_name)
    
    # Convert questions to a more manageable format
    formatted_questions = []
    for idx, (q_text, options, correct) in enumerate(questions):
        formatted_questions.append({
            'id': idx + 1,
            'question': q_text,
            'options': options,
            'correct': correct
        })
    
    return render_template('teacher/edit_quiz.html', 
                         subject=subject, 
                         table_name=table_name, 
                         questions=formatted_questions)


@teacher_bp.route('/add_question/<table_name>', methods=['GET', 'POST'])
def add_question(table_name):
    """Add a new question to a quiz"""
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher.login'))
    
    subject = request.args.get('subject', table_name.replace('_', ' ').title())
    
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        options = [
            request.form.get('option1', '').strip(),
            request.form.get('option2', '').strip(),
            request.form.get('option3', '').strip(),
            request.form.get('option4', '').strip()
        ]
        correct_answer = int(request.form.get('correct_answer', 1))
        
        # Validation
        if not question:
            flash('Question cannot be empty.', 'error')
            return render_template('teacher/add_question.html', subject=subject, table_name=table_name)
        
        if any(not opt for opt in options):
            flash('All options must be filled.', 'error')
            return render_template('teacher/add_question.html', subject=subject, table_name=table_name)
        
        if len(set(options)) != len(options):
            flash('Options must be unique.', 'error')
            return render_template('teacher/add_question.html', subject=subject, table_name=table_name)
        
        # Insert question into database
        if db_manager.insert_question(table_name, question, options[0], options[1], options[2], options[3], correct_answer):
            flash('Question added successfully!', 'success')
            return redirect(url_for('teacher.edit_quiz', table_name=table_name, subject=subject))
        else:
            flash('Failed to add question to database.', 'error')
    
    return render_template('teacher/add_question.html', subject=subject, table_name=table_name)


@teacher_bp.route('/edit_question/<table_name>/<int:question_id>', methods=['GET', 'POST'])
def edit_question(table_name, question_id):
    """Edit an existing question"""
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher.login'))
    
    subject = request.args.get('subject', table_name.replace('_', ' ').title())
    
    # Get current question data
    question_data = db_manager.get_question_by_id(table_name, question_id)
    if not question_data:
        flash('Question not found.', 'error')
        return redirect(url_for('teacher.edit_quiz', table_name=table_name, subject=subject))
    
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        options = [
            request.form.get('option1', '').strip(),
            request.form.get('option2', '').strip(),
            request.form.get('option3', '').strip(),
            request.form.get('option4', '').strip()
        ]
        correct_answer = int(request.form.get('correct_answer', 1))
        
        # Validation
        if not question:
            flash('Question cannot be empty.', 'error')
            return render_template('teacher/edit_question.html', 
                                 subject=subject, 
                                 table_name=table_name, 
                                 question_data=question_data)
        
        if any(not opt for opt in options):
            flash('All options must be filled.', 'error')
            return render_template('teacher/edit_question.html', 
                                 subject=subject, 
                                 table_name=table_name, 
                                 question_data=question_data)
        
        if len(set(options)) != len(options):
            flash('Options must be unique.', 'error')
            return render_template('teacher/edit_question.html', 
                                 subject=subject, 
                                 table_name=table_name, 
                                 question_data=question_data)
        
        # Update question in database
        if db_manager.update_question(table_name, question_id, question, options[0], options[1], options[2], options[3], correct_answer):
            flash('Question updated successfully!', 'success')
            return redirect(url_for('teacher.edit_quiz', table_name=table_name, subject=subject))
        else:
            flash('Failed to update question in database.', 'error')
    
    return render_template('teacher/edit_question.html', 
                         subject=subject, 
                         table_name=table_name, 
                         question_data=question_data)


@teacher_bp.route('/delete_question/<table_name>/<int:question_id>')
def delete_question(table_name, question_id):
    """Delete a question"""
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher.login'))
    
    subject = request.args.get('subject', table_name.replace('_', ' ').title())
    
    if db_manager.delete_question(table_name, question_id):
        flash('Question deleted successfully!', 'success')
    else:
        flash('Failed to delete question from database.', 'error')
    
    return redirect(url_for('teacher.edit_quiz', table_name=table_name, subject=subject))


@teacher_bp.route('/delete_quiz/<table_name>')
def delete_quiz(table_name):
    """Delete an entire quiz"""
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher.login'))
    
    display_name = table_name.replace('_', ' ').title()
    
    if db_manager.drop_table(table_name):
        flash(f'Quiz "{display_name}" deleted successfully!', 'success')
    else:
        flash('Failed to delete quiz from database.', 'error')
    
    return redirect(url_for('teacher.manage_quizzes'))


@teacher_bp.route('/logout')
def logout():
    """Teacher logout"""
    session.pop('teacher_logged_in', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))
