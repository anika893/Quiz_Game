"""
Student Module for Quiz Pool App
Handles student-related functionality including taking quizzes and viewing results
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from database import DatabaseManager
from pdf_generator import PDFGenerator
import time
import os
import tempfile

student_bp = Blueprint('student', __name__, url_prefix='/student')
db_manager = DatabaseManager()
pdf_generator = PDFGenerator()


@student_bp.route('/details', methods=['GET', 'POST'])
def details():
    """Student details entry page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        student_id = request.form.get('student_id', '').strip()
        section = request.form.get('section', '').strip()
        intake = request.form.get('intake', '').strip()
        university = request.form.get('university', '').strip()
        
        if not all([name, student_id, section, intake, university]):
            flash('All fields must be filled.', 'error')
            return render_template('student/details.html', teachers=db_manager.get_all_registered_teachers())
        
        # Store student details in session
        session['student_details'] = {
            'name': name,
            'student_id': student_id,
            'section': section,
            'intake': intake,
            'university': university
        }
        
        flash('Student details saved successfully!', 'success')
        return redirect(url_for('student.select_teacher'))
    
    teachers = db_manager.get_all_registered_teachers()
    return render_template('student/details.html', teachers=teachers)


@student_bp.route('/select_teacher', methods=['GET', 'POST'])
def select_teacher():
    """Teacher selection page for students"""
    if 'student_details' not in session:
        return redirect(url_for('student.details'))
    
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        if not teacher_id:
            flash('Please select a teacher.', 'error')
            return render_template('student/select_teacher.html', teachers=db_manager.get_all_registered_teachers())
        
        # Store selected teacher in session
        teachers = db_manager.get_all_registered_teachers()
        selected_teacher = next((t for t in teachers if t['teacher_id'] == int(teacher_id)), None)
        
        if selected_teacher:
            session['selected_teacher'] = selected_teacher
            flash(f'Selected teacher: {selected_teacher["name"]}', 'success')
            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid teacher selection.', 'error')
    
    teachers = db_manager.get_all_registered_teachers()
    return render_template('student/select_teacher.html', teachers=teachers)


@student_bp.route('/dashboard')
def dashboard():
    """Student dashboard showing available quizzes"""
    if 'student_details' not in session:
        return redirect(url_for('student.details'))
    
    if 'selected_teacher' not in session:
        return redirect(url_for('student.select_teacher'))
    
    student_details = session['student_details']
    selected_teacher = session['selected_teacher']
    
    # Get quizzes for the selected teacher using simplified approach
    quizzes = db_manager.get_simple_quizzes(selected_teacher['name'])
    
    return render_template('student/dashboard.html', 
                         student_details=student_details, 
                         selected_teacher=selected_teacher,
                         quizzes=quizzes)


@student_bp.route('/take_quiz/<table_name>')
def take_quiz(table_name):
    """Take a quiz - UPDATED FOR SIMPLIFIED SYSTEM"""
    if 'student_details' not in session or 'selected_teacher' not in session:
        return redirect(url_for('student.details'))
    
    selected_teacher = session['selected_teacher']
    
    # Extract subject name from table name (remove teacher prefix)
    teacher_prefix = selected_teacher['name'].replace(' ', '_').replace('-', '_')
    subject = table_name.replace(f"{teacher_prefix}_", "").replace('_', ' ').title()
    
    questions = db_manager.get_all_questions(table_name)
    
    if not questions:
        flash('No questions available in this quiz.', 'error')
        return redirect(url_for('student.dashboard'))
    
    # Get quiz info (timer and negative marking) from the simplified table
    quiz_info = db_manager.get_quiz_info(table_name)
    
    # Store quiz session data
    session['quiz_session'] = {
        'table_name': table_name,
        'subject': subject,
        'teacher_name': selected_teacher['name'],
        'start_time': time.time(),
        'questions': questions,
        'timer_minutes': quiz_info['timer_minutes'] if quiz_info else 0,
        'negative_marking': quiz_info['negative_marking'] if quiz_info else True
    }
    
    return render_template('student/take_quiz.html', 
                         subject=subject, 
                         teacher_name=selected_teacher['name'],
                         questions=questions,
                         timer_minutes=quiz_info['timer_minutes'] if quiz_info else 0,
                         negative_marking=quiz_info['negative_marking'] if quiz_info else True)


@student_bp.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    """Submit quiz and calculate results - UPDATED FOR SIMPLIFIED SYSTEM"""
    if 'student_details' not in session or 'quiz_session' not in session:
        return redirect(url_for('student.details'))
    
    student_details = session['student_details']
    quiz_session = session['quiz_session']
    
    # Collect student answers
    student_answers = {}
    for i in range(len(quiz_session['questions'])):
        answer = request.form.get(f'question_{i}', 0)
        student_answers[i] = int(answer) if answer else 0
    
    # Calculate score with negative marking
    score_result = db_manager.calculate_quiz_score(
        quiz_session['table_name'], 
        student_answers, 
        quiz_session['negative_marking']
    )
    
    # Calculate time taken
    end_time = time.time()
    elapsed = round(end_time - quiz_session['start_time'])
    
    # Store results in session with all new fields
    session['quiz_results'] = {
        'score': score_result['score'],
        'total': score_result['total'],
        'percentage': score_result['percentage'],
        'elapsed': elapsed,
        'details': score_result['details'],
        'subject': quiz_session['subject'],
        'teacher_name': quiz_session['teacher_name'],
        'negative_marking': quiz_session['negative_marking'],
        'timer_minutes': quiz_session['timer_minutes'],
        'auto_submitted': elapsed > (quiz_session['timer_minutes'] * 60) if quiz_session['timer_minutes'] > 0 else False,
        # Add the new fields from the updated scoring function
        'correct_answers': score_result.get('correct_answers', 0),
        'wrong_answers': score_result.get('wrong_answers', 0),
        'unanswered': score_result.get('unanswered', 0),
        'negative_marking_applied': score_result.get('negative_marking_applied', True)
    }
    
    # Clear quiz session
    session.pop('quiz_session', None)
    
    return redirect(url_for('student.results'))


@student_bp.route('/results')
def results():
    """Display quiz results"""
    if 'student_details' not in session or 'quiz_results' not in session:
        return redirect(url_for('student.details'))
    
    student_details = session['student_details']
    quiz_results = session['quiz_results']
    
    return render_template('student/results.html', 
                         student_details=student_details, 
                         quiz_results=quiz_results)


@student_bp.route('/download_pdf')
def download_pdf():
    """Download quiz results as PDF"""
    if 'student_details' not in session or 'quiz_results' not in session:
        return redirect(url_for('student.details'))
    
    student_details = session['student_details']
    quiz_results = session['quiz_results']
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    # Filter details to get only incorrect answers for PDF
    incorrect_details = []
    if 'details' in quiz_results:
        for detail in quiz_results['details']:
            if not detail.get('is_correct', True):  # Include wrong answers and unanswered
                incorrect_details.append({
                    'question': detail['question'],
                    'your_answer': detail['student_answer'],
                    'correct_answer': detail['correct_answer']
                })
    
    # Generate PDF
    success = pdf_generator.generate_quiz_result_pdf(
        temp_file.name,
        quiz_results['score'],
        quiz_results['total'],
        quiz_results['elapsed'],
        incorrect_details,
        student_details['name'],
        student_details['student_id'],
        student_details['section'],
        student_details['intake'],
        student_details['university'],
        quiz_results['subject'],
        quiz_results.get('correct_answers', 0),
        quiz_results.get('wrong_answers', 0),
        quiz_results.get('unanswered', 0),
        quiz_results.get('negative_marking_applied', True)
    )
    
    if success:
        filename = f"quiz_result_{student_details['student_id']}_{int(time.time())}.pdf"
        return send_file(temp_file.name, as_attachment=True, download_name=filename)
    else:
        flash('Failed to generate PDF.', 'error')
        return redirect(url_for('student.results'))


@student_bp.route('/logout')
def logout():
    """Student logout"""
    session.pop('student_details', None)
    session.pop('quiz_session', None)
    session.pop('quiz_results', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))
