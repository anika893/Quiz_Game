"""
PDF Generator Module for Quiz Pool App
Handles PDF report generation for quiz results
"""

import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, red, green, blue, darkblue, lightgrey
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFGenerator:
    """Handles PDF generation for quiz results"""
    
    def __init__(self):
        self.styles = self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom styles for PDF generation"""
        styles = getSampleStyleSheet()
        
        # Custom style for the main title
        styles.add(ParagraphStyle(name='TitleStyle',
                                  fontName='Helvetica-Bold',
                                  fontSize=28,
                                  leading=32,
                                  alignment=TA_CENTER,
                                  textColor=blue))
        
        # Custom style for subtitles/section headers
        styles.add(ParagraphStyle(name='SubtitleStyle',
                                  fontName='Helvetica-Bold',
                                  fontSize=16,
                                  leading=20,
                                  spaceAfter=10,
                                  textColor=darkblue))
        
        # Style for general text
        styles.add(ParagraphStyle(name='NormalStyle',
                                  fontName='Helvetica',
                                  fontSize=12,
                                  leading=15,
                                  textColor=black))
        
        # Style for incorrect answer question
        styles.add(ParagraphStyle(name='QuestionStyle',
                                  fontName='Helvetica-Bold',
                                  fontSize=11,
                                  leading=14,
                                  spaceBefore=10,
                                  textColor=black))
        
        # Style for student's incorrect answer
        styles.add(ParagraphStyle(name='YourAnswerStyle',
                                  fontName='Helvetica',
                                  fontSize=10,
                                  leading=12,
                                  leftIndent=15,
                                  textColor=red))
        
        # Style for correct answer
        styles.add(ParagraphStyle(name='CorrectAnswerStyle',
                                  fontName='Helvetica',
                                  fontSize=10,
                                  leading=12,
                                  leftIndent=15,
                                  textColor=green))
        
        return styles
    
    def generate_quiz_result_pdf(self, filepath, score, total, elapsed, incorrect_details, 
                                student_name, student_id, student_section, student_intake, 
                                student_university, subject, correct_answers=0, wrong_answers=0, 
                                unanswered=0, negative_marking=False):
        """
        Generates and saves a PDF report of the quiz results
        
        Args:
            filepath: Path where to save the PDF
            score: The student's score
            total: The total number of questions
            elapsed: The time taken to complete the quiz
            incorrect_details: List of dictionaries containing details of incorrect answers
            student_name: The name of the student
            student_id: The ID of the student
            student_section: The section of the student
            student_intake: The intake of the student
            student_university: The university of the student
            subject: The quiz subject
        """
        try:
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            margin_x = 50
            margin_y_top = height - 50
            line_height = 16
            section_spacing = 25

            # --- Page Header (Title Bar) ---
            c.setFillColor(lightgrey)
            c.rect(0, height - 70, width, 70, fill=1)
            c.setFillColor(blue)

            # Using Paragraph for rich text and centering
            title_p = Paragraph("Quiz Result Report", self.styles['TitleStyle'])
            title_p_width, title_p_height = title_p.wrapOn(c, width - 2 * margin_x, height)
            title_p.drawOn(c, (width - title_p_width) / 2, height - 50 - title_p_height/2)

            # --- Student Information Section ---
            y_position = height - 90
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin_x, y_position, "Student Information:")
            y_position -= section_spacing

            c.setFont("Helvetica", 12)
            student_info = [
                f"<b>Name:</b> {student_name}",
                f"<b>ID:</b> {student_id}",
                f"<b>Section:</b> {student_section}",
                f"<b>Intake:</b> {student_intake}",
                f"<b>University:</b> {student_university}"
            ]
            for line in student_info:
                p = Paragraph(line, self.styles['NormalStyle'])
                p.wrapOn(c, width - 2 * margin_x, height)
                p.drawOn(c, margin_x, y_position)
                y_position -= line_height

            # --- Quiz Summary Section ---
            y_position -= section_spacing
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin_x, y_position, "Quiz Summary:")
            y_position -= section_spacing

            c.setFont("Helvetica", 12)
            quiz_summary_info = [
                f"<b>Subject:</b> {subject}",
                f"<b>Final Score:</b> {score}/{total}",
                f"<b>Time Taken:</b> {elapsed} seconds"
            ]
            for line in quiz_summary_info:
                p = Paragraph(line, self.styles['NormalStyle'])
                p.wrapOn(c, width - 2 * margin_x, height)
                p.drawOn(c, margin_x, y_position)
                y_position -= line_height
            
            # Add detailed scoring breakdown
            y_position -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin_x, y_position, "Scoring Breakdown:")
            y_position -= line_height
            
            c.setFont("Helvetica", 11)
            scoring_info = [
                f"<b>Correct Answers:</b> {correct_answers} (+1 point each)",
                f"<b>Wrong Answers:</b> {wrong_answers} ({'-0.25 points each' if negative_marking else '0 points each'})",
                f"<b>Unanswered:</b> {unanswered} (0 points)",
                f"<b>Final Score:</b> {correct_answers} - ({wrong_answers} × 0.25) = {score}" if negative_marking else f"<b>Final Score:</b> {correct_answers} (no negative marking)"
            ]
            for line in scoring_info:
                p = Paragraph(line, self.styles['NormalStyle'])
                p.wrapOn(c, width - 2 * margin_x, height)
                p.drawOn(c, margin_x, y_position)
                y_position -= line_height

            # --- Incorrect Answers Review Section ---
            if incorrect_details:
                y_position -= section_spacing
                c.setFont("Helvetica-Bold", 14)
                c.drawString(margin_x, y_position, "Incorrect Answers Review:")
                y_position -= section_spacing / 2

                for i, detail in enumerate(incorrect_details):
                    required_space = (3 * line_height) + 15
                    if y_position < (margin_x + required_space):
                        c.showPage()
                        y_position = height - 50
                        c.setFont("Helvetica-Bold", 14)
                        c.drawString(margin_x, y_position, "Incorrect Answers Review (Cont.):")
                        y_position -= section_spacing / 2
                        c.setFont("Helvetica", 10)

                    # Question
                    q_p = Paragraph(f"Q: {detail['question']}", self.styles['QuestionStyle'])
                    q_p.wrapOn(c, width - 2 * margin_x - 10, height)
                    q_p.drawOn(c, margin_x + 10, y_position - q_p.height)
                    y_position -= q_p.height + 5

                    # Your Answer
                    your_answer_p = Paragraph(f"Your Answer: {detail['your_answer']}", self.styles['YourAnswerStyle'])
                    your_answer_p.wrapOn(c, width - 2 * margin_x - 20, height)
                    your_answer_p.drawOn(c, margin_x + 20, y_position - your_answer_p.height)
                    y_position -= your_answer_p.height + 3

                    # Correct Answer
                    correct_answer_p = Paragraph(f"Correct Answer: {detail['correct_answer']}", self.styles['CorrectAnswerStyle'])
                    correct_answer_p.wrapOn(c, width - 2 * margin_x - 20, height)
                    correct_answer_p.drawOn(c, margin_x + 20, y_position - correct_answer_p.height)
                    y_position -= correct_answer_p.height + 10

            else:
                y_position -= section_spacing
                c.setFont("Helvetica", 12)
                c.drawString(margin_x, y_position, "Congratulations! All answers were correct.")

            # --- Footer ---
            c.setFont("Helvetica-Oblique", 9)
            c.setFillColor(darkblue)
            c.drawCentredString(width / 2.0, 30, f"Generated by Quiz Pool App on {time.strftime('%Y-%m-%d %H:%M:%S')}")
            c.setFillColor(black)

            c.save()
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
