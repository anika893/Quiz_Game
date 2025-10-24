import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import time
import json
import os
import pyodbc
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, red, green, blue, darkblue, lightgrey
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class DatabaseManager:
    """Handles all database operations for the Quiz Pool App"""
    
    def __init__(self):
        self.server = "DESKTOP-UI6PRJS\\SQLEXPRESS"
        self.database = "Anika Database"
        self.connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;"
        self.connection = None
    
    def connect(self):
        """Establishes connection to SQL Server database"""
        try:
            self.connection = pyodbc.connect(self.connection_string)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Closes database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_quiz_table(self, table_name):
        """Creates a new table for a quiz subject with the required columns"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            # Create table with 6 columns: Question, Option1, Option2, Option3, Option4, RightAnswer
            create_table_query = f"""
            CREATE TABLE dbo.{table_name} (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                Question NVARCHAR(MAX) NOT NULL,
                Option1 NVARCHAR(MAX) NOT NULL,
                Option2 NVARCHAR(MAX) NOT NULL,
                Option3 NVARCHAR(MAX) NOT NULL,
                Option4 NVARCHAR(MAX) NOT NULL,
                RightAnswer INT NOT NULL CHECK (RightAnswer IN (1, 2, 3, 4))
            )
            """
            
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")
            return False
    
    def table_exists(self, table_name):
        """Checks if a table exists in the database"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = ? AND TABLE_SCHEMA = 'dbo'
            """, table_name)
            
            exists = cursor.fetchone()[0] > 0
            cursor.close()
            return exists
            
        except Exception as e:
            print(f"Error checking table existence: {e}")
            return False
    
    def insert_question(self, table_name, question, option1, option2, option3, option4, right_answer):
        """Inserts a new question into the specified quiz table"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            insert_query = f"""
            INSERT INTO dbo.{table_name} (Question, Option1, Option2, Option3, Option4, RightAnswer)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(insert_query, question, option1, option2, option3, option4, right_answer)
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error inserting question: {e}")
            return False
    
    def get_all_questions(self, table_name):
        """Retrieves all questions from a quiz table"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Question, Option1, Option2, Option3, Option4, RightAnswer FROM dbo.{table_name}")
            
            questions = []
            for row in cursor.fetchall():
                question_text = row[0]
                options = [row[1], row[2], row[3], row[4]]
                correct_answer = row[5]
                questions.append((question_text, options, correct_answer))
            
            cursor.close()
            return questions
            
        except Exception as e:
            print(f"Error retrieving questions: {e}")
            return []
    
    def update_question(self, table_name, question_id, question, option1, option2, option3, option4, right_answer):
        """Updates an existing question in the quiz table"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            update_query = f"""
            UPDATE dbo.{table_name} 
            SET Question = ?, Option1 = ?, Option2 = ?, Option3 = ?, Option4 = ?, RightAnswer = ?
            WHERE ID = ?
            """
            
            cursor.execute(update_query, question, option1, option2, option3, option4, right_answer, question_id)
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error updating question: {e}")
            return False
    
    def delete_question(self, table_name, question_id):
        """Deletes a question from the quiz table"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM dbo.{table_name} WHERE ID = ?", question_id)
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error deleting question: {e}")
            return False
    
    def get_question_by_id(self, table_name, question_id):
        """Gets a specific question by ID"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT ID, Question, Option1, Option2, Option3, Option4, RightAnswer FROM dbo.{table_name} WHERE ID = ?", question_id)
            
            row = cursor.fetchone()
            if row:
                question_data = {
                    'id': row[0],
                    'question': row[1],
                    'options': [row[2], row[3], row[4], row[5]],
                    'correct': row[6]
                }
                cursor.close()
                return question_data
            
            cursor.close()
            return None
            
        except Exception as e:
            print(f"Error getting question by ID: {e}")
            return None
    
    def get_all_quiz_tables(self):
        """Gets all quiz tables (excluding system tables)"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'dbo' 
                AND TABLE_NAME NOT LIKE 'sys%'
                AND TABLE_NAME NOT IN ('dtproperties')
                ORDER BY TABLE_NAME
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
            
        except Exception as e:
            print(f"Error getting quiz tables: {e}")
            return []
    
    def drop_table(self, table_name):
        """Drops a quiz table"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DROP TABLE dbo.{table_name}")
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error dropping table: {e}")
            return False


class QuizPoolApp:
   def __init__(self, root):

       self.root = root
       self.root.title("Quiz Pool App")
       # Set an initial geometry, which can be adjusted by the user or dynamically
       self.root.geometry("500x500")
       self.root.minsize(500, 550)  # Set a minimum size for the window
       # Define fonts for consistent styling
       self.font_title = ("Segoe UI", 20, "bold")
       self.font_subtitle = ("Segoe UI", 16, "bold")
       self.font_label = ("Segoe UI", 12)
       self.font_button = ("Segoe UI", 13, "bold")

       # Define button background and foreground colors for a modern look
       self.btn_bg_teacher = "#007bff"  # Blue for teacher actions
       self.btn_bg_student = "#28a745"  # Green for student actions
       self.btn_bg_danger = "#dc3545"  # Red for destructive actions
       self.btn_bg_neutral = "#6c757d"  # Gray for general actions
       self.btn_fg = "white"  # White text for all buttons
       self.frame_bg_light = "#f5f7fa"  # Light background for content frames
       self.frame_bg_dark = "#1e3c72"  # Dark background for main frames and gradient

       # Initialize database manager
       self.db_manager = DatabaseManager()
       
       # Test database connection
       if not self.db_manager.connect():
           messagebox.showerror("Database Error", "Could not connect to database. Please check your SQL Server connection.", parent=self.root)
           self.root.quit()
           return
       
       self.TEACHER_PASSWORD = "1234"  # Default password for teacher login

       # Initialize student details
       self.student_name = ""
       self.student_id = ""
       self.student_section = ""
       self.student_intake = ""
       self.student_university = ""

       self.main_menu()  # Display the main application menu

   def clear_widgets(self):
       """Destroys all widgets currently in the root window, preparing for a new view."""
       for widget in self.root.winfo_children():
           widget.destroy()

   def styled_button(self, text, command, bg=None, fg=None, width=25, parent=None, ipady=8):
       if parent is None:
           parent = self.root
       btn = tk.Button(
           parent,
           text=text,
           command=command,
           bg=bg if bg else self.btn_bg_neutral,
           fg=fg if fg else self.btn_fg,
           font=self.font_button,
           width=width,
           relief="flat",  # Flat appearance for modern look
           bd=0,  # No border
           activebackground="#555",  # Darker background when pressed
           cursor="hand2",  # Change cursor to hand on hover
       )
       # Apply padding after packing if ipady is used for internal padding
       # We'll handle ipady in pack() or grid() call, not here.
       return btn

   def draw_gradient_background(self, start_color="#1e3c72", end_color="#2a5298"):

       canvas = tk.Canvas(self.root, highlightthickness=0)
       canvas.place(x=0, y=0, relwidth=1, relheight=1)

       self.root.update_idletasks()  # Ensure dimensions are updated

       r1, g1, b1 = self.root.winfo_rgb(start_color)
       r2, g2, b2 = self.root.winfo_rgb(end_color)

       # Convert to 0-255 range
       r1, g1, b1 = r1/256, g1/256, b1/256
       r2, g2, b2 = r2/256, g2/256, b2/256

       height = self.root.winfo_height()
       width = self.root.winfo_width()

       for i in range(height):
           # Calculate interpolated color
           r = int(r1 + (r2 - r1) * (i / height))
           g = int(g1 + (g2 - g1) * (i / height))
           b = int(b1 + (b2 - b1) * (i / height))
           color = f'#{r:02x}{g:02x}{b:02x}'
           canvas.create_line(0, i, width, i, fill=color)

       return canvas

   def create_scrollable_area(self, parent_frame, bg_color=None, padx=20, pady=10):

       if bg_color is None:
           bg_color = self.frame_bg_light

       scroll_container = tk.Frame(parent_frame, bg=bg_color)
       scroll_container.pack(fill="both", expand=True, padx=padx, pady=pady)

       canvas = tk.Canvas(scroll_container, bg=bg_color, highlightthickness=0)
       scrollbar = tk.Scrollbar(
           scroll_container, orient="vertical", command=canvas.yview)
       scrollable_frame = tk.Frame(canvas, bg=bg_color)

       canvas_window_id = canvas.create_window(
           (0, 0), window=scrollable_frame, anchor="nw")

       scrollable_frame.bind(
           "<Configure>",
           lambda e: canvas.configure(
               scrollregion=canvas.bbox("all")
           )
       )

       def _on_canvas_configure(event):
           canvas.itemconfigure(canvas_window_id, width=event.width)
           canvas.configure(scrollregion=canvas.bbox("all"))

       canvas.bind("<Configure>", _on_canvas_configure)

       canvas.configure(yscrollcommand=scrollbar.set)

       scrollbar.pack(side="right", fill="y")
       canvas.pack(side="left", fill="both", expand=True)

       return scrollable_frame

   def main_menu(self):
       """
       Displays the main menu of the application, allowing the user to select their role (Teacher/Student).
       """
       self.clear_widgets()  # Clear previous widgets
       self.draw_gradient_background(
           start_color=self.frame_bg_dark, end_color="#2a5298")  # Draw the background

       # Create a main content frame to hold all UI elements, centered on the screen
       main_content_frame = tk.Frame(self.root, bg="white")
       main_content_frame.place(
           relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.7)

       tk.Label(main_content_frame, text="Quiz Pool App",
                font=self.font_title, bg="white", fg="black").pack(pady=(10, 20))
       tk.Label(main_content_frame, text="Select Role:",
                font=self.font_subtitle, bg="white", fg="black").pack(pady=(0, 20))

       # Buttons for role selection, packed into the main_content_frame
       self.styled_button("Teacher", self.teacher_login, bg=self.btn_bg_teacher,
                          parent=main_content_frame).pack(pady=10, ipady=8)
       self.styled_button("Student", self.prompt_student_details_window, bg=self.btn_bg_student,
                          parent=main_content_frame).pack(pady=10, ipady=8)
       self.styled_button("Exit", self.root.quit, bg=self.btn_bg_danger,
                          parent=main_content_frame).pack(pady=10, ipady=8)

   def teacher_login(self):
       """Handles teacher login by prompting for a password."""
       password = simpledialog.askstring(
           "Teacher Login", "Enter password:", show='*', parent=self.root)
       if password == self.TEACHER_PASSWORD:
           self.teacher_panel()  # If password is correct, go to teacher panel
       elif password is not None:  # User entered something but it was wrong
           messagebox.showerror(
               "Error", "Incorrect password", parent=self.root)

   def teacher_panel(self):
       """
       Displays the teacher's main options, including creating new quizzes and managing existing ones.
       """
       self.clear_widgets()
       self.draw_gradient_background(
           start_color=self.frame_bg_dark, end_color="#2a5298")

       # Main content frame for the teacher panel, filling the window
       main_content_frame = tk.Frame(self.root, bg=self.frame_bg_dark)
       main_content_frame.pack(fill="both", expand=True)

       tk.Label(main_content_frame, text="Teacher Panel", fg="white",
                font=self.font_title, bg=self.frame_bg_dark).pack(pady=20)

       # Create a scrollable area for the buttons in the teacher panel
       scrollable_frame = self.create_scrollable_area(
           main_content_frame, bg_color=self.frame_bg_dark, padx=0, pady=0)

       self.styled_button("Create New Quiz", self.create_quiz_prompt, bg=self.btn_bg_teacher,
                          parent=scrollable_frame).pack(pady=10, ipady=7)
       self.styled_button("Manage Existing Quizzes", self.manage_quizzes_panel,
                          bg=self.btn_bg_student, parent=scrollable_frame).pack(pady=10, ipady=7)
       self.styled_button("Back to Main Menu", self.main_menu, bg=self.btn_bg_neutral,
                          parent=scrollable_frame).pack(pady=20, ipady=7)

   def create_quiz_prompt(self):
       """
       Prompts the teacher to enter a subject for a new quiz.
       Checks for existing quizzes with the same subject and allows overwriting.
       """
       subject = simpledialog.askstring(
           "Create Quiz", "Enter quiz subject:", parent=self.root)
       if not subject:
           return  # User cancelled

       # Clean subject name for table name (remove spaces and special characters)
       table_name = ''.join(c for c in subject if c.isalnum() or c in ('_', '-')).strip()
       if not table_name:
           messagebox.showerror("Error", "Invalid quiz subject name. Please use alphanumeric characters only.", parent=self.root)
           return

       if self.db_manager.table_exists(table_name):
           if not messagebox.askyesno("Overwrite Quiz", f"Quiz '{subject}' already exists. Overwrite it?", parent=self.root):
               return
           else:
               # Drop existing table and create new one
               if self.db_manager.drop_table(table_name):
                   if self.db_manager.create_quiz_table(table_name):
                       messagebox.showinfo(
                           "Success", f"Quiz '{subject}' overwritten. You can now add new questions.", parent=self.root)
                   else:
                       messagebox.showerror("Error", "Failed to recreate quiz table.", parent=self.root)
                       return
               else:
                   messagebox.showerror("Error", "Failed to delete existing quiz.", parent=self.root)
                   return
       else:
           if self.db_manager.create_quiz_table(table_name):
               messagebox.showinfo(
                   "Success", f"Quiz '{subject}' created. Now you can add questions.", parent=self.root)
           else:
               messagebox.showerror("Error", "Failed to create quiz table.", parent=self.root)
               return

       # Immediately go to edit details for the new/overwritten quiz
       self.edit_quiz_details(subject, table_name)

   def manage_quizzes_panel(self):
       """
       Displays a list of existing quizzes, allowing the teacher to select one for editing or deletion.
       The list of quizzes is scrollable.
       """
       self.clear_widgets()
       self.draw_gradient_background(
           start_color=self.frame_bg_dark, end_color="#2a5298")

       main_content_frame = tk.Frame(self.root, bg=self.frame_bg_dark)
       main_content_frame.pack(fill="both", expand=True)

       tk.Label(main_content_frame, text="Manage Quizzes",
                font=self.font_title, bg=self.frame_bg_dark, fg="white").pack(pady=20)

       # Get all quiz tables from database
       quiz_tables = self.db_manager.get_all_quiz_tables()
       
       if not quiz_tables:
           tk.Label(main_content_frame, text="No quizzes available.",
                    font=self.font_label, bg=self.frame_bg_dark, fg="white").pack(pady=30)
       else:
           # Create a scrollable area for the list of quiz subjects
           scrollable_frame = self.create_scrollable_area(
               main_content_frame, bg_color=self.frame_bg_light)

           for table_name in quiz_tables:
               # Convert table name back to display name (replace underscores with spaces)
               display_name = table_name.replace('_', ' ').title()
               
               quiz_item_frame = tk.Frame(
                   scrollable_frame, bg="#e0e0e0", bd=1, relief="solid", padx=5, pady=5)
               quiz_item_frame.pack(fill="x", pady=5)
               tk.Label(quiz_item_frame, text=display_name, font=self.font_label, bg="#e0e0e0").pack(
                   side="left", padx=10, fill="x", expand=True)
               self.styled_button("Edit", lambda t=table_name, d=display_name: self.edit_quiz_details(
                   d, t), bg="#0056b3", width=8, parent=quiz_item_frame, ipady=3).pack(side="left", padx=5)
               self.styled_button("Delete", lambda t=table_name, d=display_name: self.confirm_delete_quiz(
                   d, t), bg="#c82333", width=8, parent=quiz_item_frame, ipady=3).pack(side="left", padx=5)

       self.styled_button("Back to Teacher Panel", self.teacher_panel,
                          bg=self.btn_bg_neutral, parent=main_content_frame).pack(pady=20, ipady=7)

   def edit_quiz_details(self, subject, table_name):
       """
       Displays the questions of a selected quiz and provides options to add, edit, or delete questions.
       The questions and options are displayed within a scrollable area.
       :param subject: The display name of the quiz being edited.
       :param table_name: The database table name for the quiz.
       """
       self.clear_widgets()
       self.draw_gradient_background(
           start_color=self.frame_bg_dark, end_color="#2a5298")

       main_content_frame = tk.Frame(self.root, bg=self.frame_bg_dark)
       main_content_frame.pack(fill="both", expand=True)

       tk.Label(main_content_frame, text=f"Editing Quiz: {subject}",
                fg="white", font=self.font_title, bg=self.frame_bg_dark).pack(pady=20)

       # Create a scrollable area for displaying quiz questions and options
       scrollable_frame = self.create_scrollable_area(
           main_content_frame, bg_color=self.frame_bg_light)

       # Get questions from database
       questions = self.db_manager.get_all_questions(table_name)
       
       if not questions:
           tk.Label(scrollable_frame, text="No questions in this quiz. Add one!",
                    fg="black", font=self.font_label, bg=self.frame_bg_light).pack(pady=30)
       else:
           for idx, (q_text, options, correct) in enumerate(questions):
               question_frame = tk.Frame(
                   scrollable_frame, bg="#e0e0e0", bd=1, relief="solid", padx=5, pady=5)
               question_frame.pack(fill="x", pady=5)

               tk.Label(question_frame, text=f"Q{idx+1}: {q_text}", font=self.font_label,
                        bg="#e0e0e0", wraplength=400, justify="left").pack(anchor="w")
               for i, opt in enumerate(options):
                   indicator = " (Correct)" if (i + 1) == correct else ""
                   tk.Label(question_frame, text=f"   {i+1}. {opt}{indicator}", font=(
                       "Segoe UI", 10), bg="#e0e0e0").pack(anchor="w")

               button_frame = tk.Frame(question_frame, bg="#e0e0e0")
               # Align buttons to the right
               button_frame.pack(pady=5, anchor="e")
               self.styled_button("Edit", lambda t=table_name, i=idx: self.edit_question_prompt(
                   t, i), bg="#0056b3", width=8, parent=button_frame, ipady=3).pack(side="left", padx=5)
               self.styled_button("Delete", lambda t=table_name, i=idx: self.delete_question(
                   t, i), bg="#c82333", width=8, parent=button_frame, ipady=3).pack(side="left", padx=5)

       # Buttons for adding new questions and going back, placed outside the scrollable area
       self.styled_button("Add New Question", lambda: self.add_question_window(
           table_name), bg=self.btn_bg_student, parent=main_content_frame).pack(pady=10, ipady=7)
       self.styled_button("Back to Manage Quizzes", self.manage_quizzes_panel,
                          bg=self.btn_bg_neutral, parent=main_content_frame).pack(pady=20, ipady=7)

   def _cancel_toplevel_and_refresh_quiz_details(self, toplevel_window, subject, table_name):
       """
       Helper method to destroy a Toplevel window and refresh the quiz details view.
       This helps address linter warnings about nested function scope.
       """
       toplevel_window.destroy()
       self.edit_quiz_details(subject, table_name)

   def add_question_window(self, table_name):
       """
       Opens a new Toplevel window to add a question to the specified quiz.
       Provides input fields for question text, options, and a radio button for the correct answer.
       :param table_name: The database table name for the quiz to which the question will be added.
       """
       add_window = tk.Toplevel(self.root)
       add_window.title(f"Add Question to {table_name}")
       add_window.geometry("500x550")
       add_window.transient(self.root)
       add_window.grab_set()

       add_canvas = tk.Canvas(add_window, highlightthickness=0)
       add_canvas.place(x=0, y=0, relwidth=1, relheight=1)
       add_window.update_idletasks()
       toplevel_height = add_window.winfo_height()
       toplevel_width = add_window.winfo_width()

       r1, g1, b1 = self.root.winfo_rgb(self.frame_bg_dark)
       r2, g2, b2 = self.root.winfo_rgb("#2a5298")
       r1, g1, b1 = r1/256, g1/256, b1/256
       r2, g2, b2 = r2/256, g2/256, b2/256

       for i in range(toplevel_height):
           nr = int(r1 + (r2 - r1) * (i / toplevel_height))
           ng = int(g1 + (g2 - g1) * (i / toplevel_height))
           nb = int(b1 + (b2 - b1) * (i / toplevel_height))
           color = f'#{nr:02x}{ng:02x}{nb:02x}'
           add_canvas.create_line(0, i, toplevel_width, i, fill=color)

       content_frame = tk.Frame(
           add_window, bg=self.frame_bg_light, padx=20, pady=20)
       content_frame.place(relx=0.5, rely=0.5,
                           anchor="center", relwidth=0.9, relheight=0.9)

       tk.Label(content_frame, text="Question:", font=self.font_label,
                bg=self.frame_bg_light).pack(pady=5, anchor="w")
       question_entry = tk.Entry(
           content_frame, width=50, font=self.font_label)
       question_entry.pack(pady=5, fill="x")

       option_entries = []
       for i in range(4):
           tk.Label(content_frame, text=f"Option {i+1}:", font=self.font_label,
                    bg=self.frame_bg_light).pack(pady=2, anchor="w")
           opt_entry = tk.Entry(content_frame, width=50, font=self.font_label)
           opt_entry.pack(pady=2, fill="x")
           option_entries.append(opt_entry)

       tk.Label(content_frame, text="Correct Option Number (1-4):",
                font=self.font_label, bg=self.frame_bg_light).pack(pady=5, anchor="w")
       correct_option_var = tk.IntVar()
       correct_option_var.set(1)

       radio_frame = tk.Frame(content_frame, bg=self.frame_bg_light)
       radio_frame.pack(pady=5)
       for i in range(1, 5):
           tk.Radiobutton(radio_frame, text=str(i), variable=correct_option_var,
                          value=i, font=self.font_label, bg=self.frame_bg_light,
                          activebackground=self.frame_bg_light).pack(side="left", padx=10)

       def save_and_close():
           q_text = question_entry.get().strip()
           options = [opt_entry.get().strip() for opt_entry in option_entries]
           correct = correct_option_var.get()

           if not q_text:
               messagebox.showwarning(
                   "Input Error", "Question cannot be empty.", parent=add_window)
               return

           if any(not opt for opt in options):
               messagebox.showwarning(
                   "Input Error", "All options must be filled.", parent=add_window)
               return

           if len(set(options)) != len(options):
               messagebox.showwarning(
                   "Input Error", "Options must be unique.", parent=add_window)
               return

           # Insert question into database
           if self.db_manager.insert_question(table_name, q_text, options[0], options[1], options[2], options[3], correct):
               messagebox.showinfo(
                   "Success", "Question added successfully!", parent=add_window)
               add_window.destroy()
               # Get display name for refresh
               display_name = table_name.replace('_', ' ').title()
               self.edit_quiz_details(display_name, table_name)
           else:
               messagebox.showerror("Error", "Failed to add question to database.", parent=add_window)

       self.styled_button("Add Question", save_and_close, bg=self.btn_bg_student,
                          parent=content_frame).pack(pady=10)
       self.styled_button("Cancel", lambda: self._cancel_toplevel_and_refresh_quiz_details(add_window, table_name.replace('_', ' ').title(), table_name),
                          bg=self.btn_bg_danger, parent=content_frame).pack(pady=5)

       self.root.wait_window(add_window)

   def edit_question_prompt(self, table_name, index):
       """
       Opens a new Toplevel window to edit an existing question.
       Populates fields with current question data and allows modifications.
       :param table_name: The database table name for the quiz containing the question.
       :param index: The index of the question to edit.
       """
       # Get questions from database to find the question at the given index
       questions = self.db_manager.get_all_questions(table_name)
       if index >= len(questions):
           messagebox.showerror("Error", "Question not found.", parent=self.root)
           return
           
       current_question, current_options, current_correct = questions[index]

       edit_window = tk.Toplevel(self.root)
       edit_window.title(f"Edit Question {index+1}")
       edit_window.geometry("500x550")
       edit_window.transient(self.root)
       edit_window.grab_set()

       edit_canvas = tk.Canvas(edit_window, highlightthickness=0)
       edit_canvas.place(x=0, y=0, relwidth=1, relheight=1)
       edit_window.update_idletasks()
       toplevel_height = edit_window.winfo_height()
       toplevel_width = edit_window.winfo_width()

       r1, g1, b1 = self.root.winfo_rgb(self.frame_bg_dark)
       r2, g2, b2 = self.root.winfo_rgb("#2a5298")
       r1, g1, b1 = r1/256, g1/256, b1/256
       r2, g2, b2 = r2/256, g2/256, b2/256

       for i in range(toplevel_height):
           nr = int(r1 + (r2 - r1) * (i / toplevel_height))
           ng = int(g1 + (g2 - g1) * (i / toplevel_height))
           nb = int(b1 + (b2 - b1) * (i / toplevel_height))
           color = f'#{nr:02x}{ng:02x}{nb:02x}'
           edit_canvas.create_line(0, i, toplevel_width, i, fill=color)

       content_frame = tk.Frame(
           edit_window, bg=self.frame_bg_light, padx=20, pady=20)
       content_frame.place(relx=0.5, rely=0.5,
                           anchor="center", relwidth=0.9, relheight=0.9)

       tk.Label(content_frame, text="Question:", font=self.font_label,
                bg=self.frame_bg_light).pack(pady=5, anchor="w")
       question_entry = tk.Entry(
           content_frame, width=50, font=self.font_label)
       question_entry.insert(0, current_question)
       question_entry.pack(pady=5, fill="x")

       option_entries = []
       for i in range(4):
           tk.Label(content_frame, text=f"Option {i+1}:", font=self.font_label,
                    bg=self.frame_bg_light).pack(pady=2, anchor="w")
           opt_entry = tk.Entry(content_frame, width=50, font=self.font_label)
           opt_entry.insert(0, current_options[i])
           opt_entry.pack(pady=2, fill="x")
           option_entries.append(opt_entry)

       tk.Label(content_frame, text="Correct Option Number (1-4):",
                font=self.font_label, bg=self.frame_bg_light).pack(pady=5, anchor="w")
       correct_option_var = tk.IntVar()
       correct_option_var.set(current_correct)

       radio_frame = tk.Frame(content_frame, bg=self.frame_bg_light)
       radio_frame.pack(pady=5)
       for i in range(1, 5):
           tk.Radiobutton(radio_frame, text=str(i), variable=correct_option_var,
                          value=i, font=self.font_label, bg=self.frame_bg_light,
                          activebackground=self.frame_bg_light).pack(side="left", padx=10)

       def save_edit_and_close():
           new_question = question_entry.get().strip()
           new_options = [opt_entry.get().strip()
                          for opt_entry in option_entries]
           new_correct = correct_option_var.get()

           if not new_question:
               messagebox.showwarning(
                   "Input Error", "Question cannot be empty.", parent=edit_window)
               return

           if any(not opt for opt in new_options):
               messagebox.showwarning(
                   "Input Error", "All options must be filled.", parent=edit_window)
               return

           if len(set(new_options)) != len(new_options):
               messagebox.showwarning(
                   "Input Error", "Options must be unique.", parent=edit_window)
               return

           # Get the question ID from database
           questions = self.db_manager.get_all_questions(table_name)
           if index >= len(questions):
               messagebox.showerror("Error", "Question not found.", parent=edit_window)
               return
           
           # We need to get the actual question ID from the database
           # For now, we'll use a workaround by getting all questions and finding the right one
           if self.db_manager.update_question(table_name, index + 1, new_question, new_options[0], new_options[1], new_options[2], new_options[3], new_correct):
               messagebox.showinfo(
                   "Success", "Question updated successfully!", parent=edit_window)
               edit_window.destroy()
               display_name = table_name.replace('_', ' ').title()
               self.edit_quiz_details(display_name, table_name)
           else:
               messagebox.showerror("Error", "Failed to update question in database.", parent=edit_window)

       self.styled_button("Save Changes", save_edit_and_close, bg=self.btn_bg_teacher,
                          parent=content_frame).pack(pady=10)
       self.styled_button("Cancel", lambda: self._cancel_toplevel_and_refresh_quiz_details(edit_window, table_name.replace('_', ' ').title(), table_name),
                          bg=self.btn_bg_danger, parent=content_frame).pack(pady=5)

       self.root.wait_window(edit_window)

   def delete_question(self, table_name, index_to_delete):
       """
       Deletes a question from the specified quiz after confirmation.
       :param table_name: The database table name for the quiz from which the question will be deleted.
       :param index_to_delete: The index of the question to delete.
       """
       if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete question {index_to_delete + 1}?", parent=self.root):
           if self.db_manager.delete_question(table_name, index_to_delete + 1):
               messagebox.showinfo(
                   "Deleted", "Question deleted.", parent=self.root)
               # Refresh the interface after deletion
               display_name = table_name.replace('_', ' ').title()
               self.edit_quiz_details(display_name, table_name)
           else:
               messagebox.showerror("Error", "Failed to delete question from database.", parent=self.root)

   def confirm_delete_quiz(self, display_name, table_name):
       """
       Confirms with the teacher before permanently deleting a selected quiz.
       :param display_name: The display name of the quiz to be deleted.
       :param table_name: The database table name for the quiz to be deleted.
       """
       if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the quiz '{display_name}'? This action cannot be undone.", parent=self.root):
           if self.db_manager.drop_table(table_name):
               messagebox.showinfo(
                   "Deleted", f"Quiz '{display_name}' deleted.", parent=self.root)
               self.manage_quizzes_panel()  # Refresh the panel after deletion
           else:
               messagebox.showerror("Error", "Failed to delete quiz from database.", parent=self.root)

   def prompt_student_details_window(self):
       """
       Opens a new Toplevel window to prompt the student for their name, ID, section, intake, and university.
       """
       details_window = tk.Toplevel(self.root)
       details_window.title("Enter Student Details")
       details_window.geometry("500x550")
       details_window.transient(self.root)
       details_window.grab_set()

       details_canvas = tk.Canvas(details_window, highlightthickness=0)
       details_canvas.place(x=0, y=0, relwidth=1, relheight=1)
       details_window.update_idletasks()
       toplevel_height = details_window.winfo_height()
       toplevel_width = details_window.winfo_width()

       r1, g1, b1 = self.root.winfo_rgb(self.frame_bg_dark)
       r2, g2, b2 = self.root.winfo_rgb("#2a5298")
       r1, g1, b1 = r1/256, g1/256, b1/256
       r2, g2, b2 = r2/256, g2/256, b2/256

       for i in range(toplevel_height):
           nr = int(r1 + (r2 - r1) * (i / toplevel_height))
           ng = int(g1 + (g2 - g1) * (i / toplevel_height))
           nb = int(b1 + (b2 - b1) * (i / toplevel_height))
           color = f'#{nr:02x}{ng:02x}{nb:02x}'
           details_canvas.create_line(0, i, toplevel_width, i, fill=color)

       content_frame = tk.Frame(
           details_window, bg=self.frame_bg_light, padx=20, pady=20)
       content_frame.place(relx=0.5, rely=0.5,
                           anchor="center", relwidth=0.9, relheight=0.9)

       tk.Label(content_frame, text="Name:", font=self.font_label,
                bg=self.frame_bg_light).pack(pady=5, anchor="w")
       name_entry = tk.Entry(content_frame, width=40, font=self.font_label)
       name_entry.insert(0, self.student_name)
       name_entry.pack(pady=2, fill="x")

       tk.Label(content_frame, text="ID:", font=self.font_label,
                bg=self.frame_bg_light).pack(pady=5, anchor="w")
       id_entry = tk.Entry(content_frame, width=40, font=self.font_label)
       id_entry.insert(0, self.student_id)
       id_entry.pack(pady=2, fill="x")

       tk.Label(content_frame, text="Section:", font=self.font_label,
                bg=self.frame_bg_light).pack(pady=5, anchor="w")
       section_entry = tk.Entry(content_frame, width=40, font=self.font_label)
       section_entry.insert(0, self.student_section)
       section_entry.pack(pady=2, fill="x")

       tk.Label(content_frame, text="Intake:", font=self.font_label,
                bg=self.frame_bg_light).pack(pady=5, anchor="w")
       intake_entry = tk.Entry(content_frame, width=40, font=self.font_label)
       intake_entry.insert(0, self.student_intake)
       intake_entry.pack(pady=2, fill="x")

       tk.Label(content_frame, text="University:", font=self.font_label,
                bg=self.frame_bg_light).pack(pady=5, anchor="w")
       university_entry = tk.Entry(
           content_frame, width=40, font=self.font_label)
       university_entry.insert(0, self.student_university)
       university_entry.pack(pady=2, fill="x")

       def save_details_and_proceed():
           name = name_entry.get().strip()
           student_id = id_entry.get().strip()
           section = section_entry.get().strip()
           intake = intake_entry.get().strip()
           university = university_entry.get().strip()

           if not all([name, student_id, section, intake, university]):
               messagebox.showwarning(
                   "Input Error", "All fields must be filled.", parent=details_window)
               return

           self.student_name = name
           self.student_id = student_id
           self.student_section = section
           self.student_intake = intake
           self.student_university = university

           details_window.destroy()
           self.student_panel()

       def cancel_details_and_return():
           details_window.destroy()
           self.main_menu()

       self.styled_button("Proceed", save_details_and_proceed, bg=self.btn_bg_student,
                          parent=content_frame).pack(pady=15)
       self.styled_button("Cancel", cancel_details_and_return, bg=self.btn_bg_danger,
                          parent=content_frame).pack(pady=5)

       self.root.wait_window(details_window)

   def student_panel(self):
       """
       Displays a list of available quiz subjects for students to choose from.
       The list of subjects is scrollable.
       """
       self.clear_widgets()
       self.draw_gradient_background(
           start_color=self.frame_bg_dark, end_color="#2a5298")

       main_content_frame = tk.Frame(self.root, bg=self.frame_bg_dark)
       main_content_frame.pack(fill="both", expand=True)

       tk.Label(main_content_frame, text=f"Welcome, {self.student_name}!",
                font=self.font_subtitle, bg=self.frame_bg_dark, fg="white").pack(pady=(10, 5))
       tk.Label(main_content_frame, text=f"ID: {self.student_id} | Section: {self.student_section} | Intake: {self.student_intake}",
                font=self.font_label, bg=self.frame_bg_dark, fg="white").pack(pady=(0, 5))
       tk.Label(main_content_frame, text=f"University: {self.student_university}",
                font=self.font_label, bg=self.frame_bg_dark, fg="white").pack(pady=(0, 20))
       tk.Label(main_content_frame, text="Select Quiz Subject",
                font=self.font_title, bg=self.frame_bg_dark, fg="white").pack(pady=(0, 20))

       # Get all quiz tables from database
       quiz_tables = self.db_manager.get_all_quiz_tables()
       
       if not quiz_tables:
           tk.Label(main_content_frame, text="No quizzes available.",
                    font=self.font_label, bg=self.frame_bg_dark, fg="white").pack(pady=30)
           self.styled_button("Back", self.main_menu, bg=self.btn_bg_neutral,
                              parent=main_content_frame).pack(pady=20, ipady=7)
           return

       scrollable_frame = self.create_scrollable_area(
           main_content_frame, bg_color=self.frame_bg_light)

       for table_name in quiz_tables:
           # Convert table name back to display name
           display_name = table_name.replace('_', ' ').title()
           self.styled_button(display_name, lambda t=table_name: self.take_quiz(
               t), bg=self.btn_bg_student, parent=scrollable_frame).pack(pady=5, ipady=6)
       self.styled_button("Back", self.main_menu, bg=self.btn_bg_neutral,
                          parent=main_content_frame).pack(pady=20, ipady=7)

   def take_quiz(self, table_name):
       """
       Starts the quiz for the selected subject, displaying questions and options.
       Includes a timer and a submit button. The questions are displayed in a scrollable area.
       :param table_name: The database table name for the quiz to be taken.
       """
       self.clear_widgets()
       self.draw_gradient_background(
           start_color=self.frame_bg_dark, end_color="#2a5298")

       self.current_table_name = table_name
       self.current_subject = table_name.replace('_', ' ').title()
       self.student_answers = []
       self.start_time = time.time()

       main_quiz_frame = tk.Frame(self.root, bg=self.frame_bg_dark)
       main_quiz_frame.pack(fill="both", expand=True)

       self.time_label = tk.Label(main_quiz_frame, text="", font=(
           "Segoe UI", 14), bg=self.frame_bg_dark, fg="white")
       self.time_label.pack(pady=5)
       self.update_timer()

       self.answer_vars = []

       quiz_content_frame = self.create_scrollable_area(
           main_quiz_frame, bg_color=self.frame_bg_light, padx=10, pady=10)

       # Get questions from database
       questions = self.db_manager.get_all_questions(table_name)
       
       for idx, (q, options, correct) in enumerate(questions):
           tk.Label(quiz_content_frame, text=f"Q{idx + 1}: {q}", font=self.font_label,
                    bg=self.frame_bg_light, wraplength=500, justify="left").pack(pady=8, anchor="w")
           var = tk.IntVar()
           self.answer_vars.append(var)
           for i, opt in enumerate(options):
               tk.Radiobutton(quiz_content_frame, text=opt, variable=var, value=i + 1,
                              bg=self.frame_bg_light, anchor="w", justify="left",
                              font=("Segoe UI", 11), activebackground=self.frame_bg_light,
                              cursor="hand2").pack(anchor="w", padx=20)

       self.styled_button("Submit Quiz", self.submit_quiz, bg=self.btn_bg_teacher,
                          parent=quiz_content_frame).pack(pady=15, ipady=8)

   def submit_quiz(self):
       """
       Calculates the student's score, displays the result, and provides an option to download a PDF report.
       Also stops the quiz timer and shows incorrect answers.
       """
       # Get questions from database
       questions = self.db_manager.get_all_questions(self.current_table_name)
       
       score = 0
       total = len(questions)
       incorrect_questions_details = []

       for i, (q, options, correct) in enumerate(questions):
           student_choice = self.answer_vars[i].get()
           if student_choice == correct:
               score += 1
           else:
               selected_option_text = options[student_choice -
                                              1] if student_choice else "No answer selected"
               correct_option_text = options[correct - 1]
               incorrect_questions_details.append({
                   "question": q,
                   "your_answer": selected_option_text,
                   "correct_answer": correct_option_text
               })

       end_time = time.time()
       elapsed = round(end_time - self.start_time)

       if hasattr(self, 'timer_job'):
           self.root.after_cancel(self.timer_job)
           del self.timer_job

       messagebox.showinfo(
           "Quiz Completed", f"Score: {score}/{total}\nTime Taken: {elapsed} seconds", parent=self.root)

       self.clear_widgets()
       self.draw_gradient_background(
           start_color=self.frame_bg_dark, end_color="#2a5298")

       main_result_frame = tk.Frame(self.root, bg=self.frame_bg_dark)
       main_result_frame.pack(fill="both", expand=True)

       tk.Label(main_result_frame, text="Quiz Results",
                font=self.font_title, bg=self.frame_bg_dark, fg="white").pack(pady=20)
       tk.Label(main_result_frame, text=f"Your Score: {score}/{total}",
                font=self.font_subtitle, bg=self.frame_bg_dark, fg="white").pack(pady=5)
       tk.Label(main_result_frame, text=f"Time Taken: {elapsed} seconds",
                font=self.font_subtitle, bg=self.frame_bg_dark, fg="white").pack(pady=5)

       if incorrect_questions_details:
           tk.Label(main_result_frame, text="Review Incorrect Answers:",
                    font=self.font_label, bg=self.frame_bg_dark, fg="white").pack(pady=10)

           incorrect_answers_scroll_frame = self.create_scrollable_area(
               main_result_frame, bg_color=self.frame_bg_light)

           for detail in incorrect_questions_details:
               tk.Label(incorrect_answers_scroll_frame, text=f"Q: {detail['question']}", font=self.font_label,
                        bg=self.frame_bg_light, wraplength=500, justify="left").pack(anchor="w", pady=(5, 0))
               tk.Label(incorrect_answers_scroll_frame, text=f"   Your Answer: {detail['your_answer']}", font=(
                   "Segoe UI", 10), bg=self.frame_bg_light, fg="red").pack(anchor="w")
               tk.Label(incorrect_answers_scroll_frame, text=f"   Correct Answer: {detail['correct_answer']}", font=(
                   "Segoe UI", 10), bg=self.frame_bg_light, fg="green").pack(anchor="w")
               tk.Label(incorrect_answers_scroll_frame, text="---",
                        bg=self.frame_bg_light).pack(pady=(0, 5))
       else:
           tk.Label(main_result_frame, text="Congratulations! All answers were correct.",
                    font=self.font_label, bg=self.frame_bg_dark, fg="white").pack(pady=20)

       self.styled_button("Download Result PDF", lambda: self.download_result_pdf(
           score, total, elapsed, incorrect_questions_details,
           self.student_name, self.student_id, self.student_section, self.student_intake, self.student_university),
           bg=self.btn_bg_teacher, parent=main_result_frame).pack(pady=15, ipady=8)
       self.styled_button("Back to Main Menu", self.main_menu,
                          bg=self.btn_bg_neutral, parent=main_result_frame).pack(pady=10, ipady=8)

   def download_result_pdf(self, score, total, elapsed, incorrect_details, student_name, student_id, student_section, student_intake, student_university):
       """
       Generates and saves a PDF report of the quiz results, including score, time, and incorrect answers.
       Incorporates a more attractive page format using ReportLab features.
       :param score: The student's score.
       :param total: The total number of questions.
       :param elapsed: The time taken to complete the quiz.
       :param incorrect_details: A list of dictionaries containing details of incorrect answers.
       :param student_name: The name of the student.
       :param student_id: The ID of the student.
       :param student_section: The section of the student.
       :param student_intake: The intake of the student.
       :param student_university: The university of the student.
       """
       filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
                                               title="Save Quiz Result PDF", parent=self.root)
       if not filepath:
           return  # User cancelled save dialog

       try:
           c = canvas.Canvas(filepath, pagesize=letter)
           width, height = letter
           margin_x = 50
           margin_y_top = height - 50
           line_height = 16
           section_spacing = 25

           # --- PDF Styles ---
           styles = getSampleStyleSheet()
           # Custom style for the main title
           styles.add(ParagraphStyle(name='TitleStyle',
                                     fontName='Helvetica-Bold',
                                     fontSize=28,
                                     leading=32,
                                     alignment=TA_CENTER,
                                     textColor=blue))  # Changed to a darker blue
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

           # --- Page Header (Title Bar) ---
           c.setFillColor(lightgrey)  # Light gray background for the header
           # Draw a filled rectangle for the header bar
           c.rect(0, height - 70, width, 70, fill=1)
           c.setFillColor(blue)  # Reset fill color for text

           # Using Paragraph for rich text and centering
           title_p = Paragraph("Quiz Result Report", styles['TitleStyle'])
           # Calculate position for centered paragraph
           title_p_width, title_p_height = title_p.wrapOn(
               c, width - 2 * margin_x, height)
           # Centered vertically in bar
           title_p.drawOn(c, (width - title_p_width) / 2,
                          height - 50 - title_p_height/2)

           # --- Student Information Section ---
           y_position = height - 90  # Start below the header bar
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
               p = Paragraph(line, styles['NormalStyle'])
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
               f"<b>Subject:</b> {self.current_subject}",
               f"<b>Score:</b> {score}/{total}",
               f"<b>Time Taken:</b> {elapsed} seconds"
           ]
           for line in quiz_summary_info:
               p = Paragraph(line, styles['NormalStyle'])
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
                   # Check if enough space for the next question block
                   # Q, Your, Correct, plus spacing
                   required_space = (3 * line_height) + 15
                   # Need at least required_space above bottom margin
                   if y_position < (margin_x + required_space):
                       c.showPage()
                       y_position = height - 50  # Reset Y for new page
                       c.setFont("Helvetica-Bold", 14)
                       c.drawString(margin_x, y_position,
                                    "Incorrect Answers Review (Cont.):")
                       y_position -= section_spacing / 2
                       c.setFont("Helvetica", 10)

                   # Question
                   q_p = Paragraph(
                       f"Q: {detail['question']}", styles['QuestionStyle'])
                   # Slightly less width for wrap to avoid overlap
                   q_p.wrapOn(c, width - 2 * margin_x - 10, height)
                   q_p.drawOn(c, margin_x + 10, y_position - q_p.height)
                   y_position -= q_p.height + 5

                   # Your Answer
                   your_answer_p = Paragraph(
                       f"Your Answer: {detail['your_answer']}", styles['YourAnswerStyle'])
                   your_answer_p.wrapOn(c, width - 2 * margin_x - 20, height)
                   your_answer_p.drawOn(
                       c, margin_x + 20, y_position - your_answer_p.height)
                   y_position -= your_answer_p.height + 3

                   # Correct Answer
                   correct_answer_p = Paragraph(
                       f"Correct Answer: {detail['correct_answer']}", styles['CorrectAnswerStyle'])
                   correct_answer_p.wrapOn(
                       c, width - 2 * margin_x - 20, height)
                   correct_answer_p.drawOn(
                       c, margin_x + 20, y_position - correct_answer_p.height)
                   y_position -= correct_answer_p.height + 10  # More space after each question

           else:
               y_position -= section_spacing
               c.setFont("Helvetica", 12)
               c.drawString(margin_x, y_position,
                            "Congratulations! All answers were correct.")

           # --- Footer ---
           c.setFont("Helvetica-Oblique", 9)
           c.setFillColor(darkblue)
           c.drawCentredString(
               width / 2.0, 30, f"Generated by Quiz Pool App on {time.strftime('%Y-%m-%d %H:%M:%S')}")
           c.setFillColor(black)  # Reset color for other drawings

           c.save()
           messagebox.showinfo(
               "PDF Saved", f"Quiz result saved to {filepath}", parent=self.root)
       except Exception as e:
           messagebox.showerror(
               "PDF Error", f"Failed to generate PDF: {e}", parent=self.root)

   def update_timer(self):
       """
       Updates the elapsed time display during a quiz every second.
       Schedules itself to run again after 1000 milliseconds.
       """
       elapsed = round(time.time() - self.start_time)
       self.time_label.config(text=f"Time Elapsed: {elapsed} seconds")
       self.timer_job = self.root.after(1000, self.update_timer)

   def cleanup(self):
       """Cleanup method to close database connection when app closes"""
       if hasattr(self, 'db_manager'):
           self.db_manager.disconnect()


if __name__ == "__main__":
   root = tk.Tk()
   app = QuizPoolApp(root)
   
   # Set up cleanup when window is closed
   def on_closing():
       app.cleanup()
       root.destroy()
   
   root.protocol("WM_DELETE_WINDOW", on_closing)
   root.mainloop()
