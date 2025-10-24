"""
Database Manager Module for Quiz Pool App
Handles all database operations for the Quiz Pool App
"""

import pyodbc


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
    
    def create_registered_teachers_table(self):
        """Creates the RegisteredTeachers table for storing teacher login credentials"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE dbo.RegisteredTeachers (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                TeacherID INT NOT NULL,
                TeacherName NVARCHAR(255) NOT NULL,
                Email NVARCHAR(255) NOT NULL UNIQUE,
                Password NVARCHAR(255) NOT NULL,
                RegistrationDate DATETIME DEFAULT GETDATE(),
                IsActive BIT DEFAULT 1,
                FOREIGN KEY (TeacherID) REFERENCES dbo.Teachers(ID)
            )
            """
            
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error creating RegisteredTeachers table: {e}")
            return False
    
    def get_all_teachers(self):
        """Gets all teachers from the Teachers table"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID, TeacherName, EducationMailID FROM dbo.Teachers ORDER BY TeacherName")
            
            teachers = []
            for row in cursor.fetchall():
                teachers.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2]
                })
            
            cursor.close()
            return teachers
            
        except Exception as e:
            print(f"Error getting teachers: {e}")
            return []
    
    def validate_teacher_email(self, teacher_id, email):
        """Validates if the email matches the teacher's email in the database"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT EducationMailID FROM dbo.Teachers WHERE ID = ?", teacher_id)
            
            row = cursor.fetchone()
            if row and row[0].lower() == email.lower():
                cursor.close()
                return True
            
            cursor.close()
            return False
            
        except Exception as e:
            print(f"Error validating teacher email: {e}")
            return False
    
    def register_teacher(self, teacher_id, teacher_name, email, password):
        """Registers a new teacher"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            insert_query = """
            INSERT INTO dbo.RegisteredTeachers (TeacherID, TeacherName, Email, Password)
            VALUES (?, ?, ?, ?)
            """
            
            cursor.execute(insert_query, teacher_id, teacher_name, email, password)
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Error registering teacher: {e}")
            return False
    
    def authenticate_teacher(self, email, password):
        """Authenticates a registered teacher"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT ID, TeacherID, TeacherName, Email 
                FROM dbo.RegisteredTeachers 
                WHERE Email = ? AND Password = ? AND IsActive = 1
            """, email, password)
            
            row = cursor.fetchone()
            if row:
                teacher_data = {
                    'id': row[0],
                    'teacher_id': row[1],
                    'name': row[2],
                    'email': row[3]
                }
                cursor.close()
                return teacher_data
            
            cursor.close()
            return None
            
        except Exception as e:
            print(f"Error authenticating teacher: {e}")
            return None
    
    def create_teacher_folder(self, teacher_id, teacher_name):
        """Creates a folder/namespace for a teacher's quizzes"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            # Create a folder table for the teacher
            folder_name = f"Teacher_{teacher_id}_{teacher_name.replace(' ', '_')}"
            cursor = self.connection.cursor()
            
            # Check if folder already exists
            cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{folder_name}_Metadata'")
            folder_exists = cursor.fetchone()[0] > 0
            
            if folder_exists:
                print(f"Teacher folder already exists: {folder_name}_Metadata")
                cursor.close()
                return True
            
            # Create a metadata table for the teacher's folder
            create_folder_query = f"""
            CREATE TABLE dbo.{folder_name}_Metadata (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                QuizName NVARCHAR(255) NOT NULL,
                QuizTableName NVARCHAR(255) NOT NULL,
                TimerMinutes INT DEFAULT 0,
                NegativeMarking BIT DEFAULT 1,
                CreatedDate DATETIME DEFAULT GETDATE(),
                LastModified DATETIME DEFAULT GETDATE(),
                QuestionCount INT DEFAULT 0
            )
            """
            
            cursor.execute(create_folder_query)
            self.connection.commit()
            cursor.close()
            print(f"Teacher folder created: {folder_name}_Metadata")
            return True
            
        except Exception as e:
            print(f"Error creating teacher folder: {e}")
            return False
    
    def create_simple_quiz(self, quiz_name, timer_minutes=0, teacher_name="Admin"):
        """Creates a simple quiz table - NEW SIMPLIFIED APPROACH"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            # Clean quiz name for table name
            table_name = ''.join(c for c in quiz_name if c.isalnum() or c in ('_', '-')).strip()
            if not table_name:
                table_name = quiz_name.replace(' ', '_').replace('-', '_')
            
            # Add teacher prefix to make it unique
            teacher_prefix = teacher_name.replace(' ', '_').replace('-', '_')
            full_table_name = f"{teacher_prefix}_{table_name}"
            
            cursor = self.connection.cursor()
            
            # Check if table already exists
            cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{full_table_name}'")
            table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                print(f"Quiz table already exists: {full_table_name}")
                cursor.close()
                return True  # Return success for existing table
            
            # Create the quiz table with timer and negative marking
            create_quiz_query = f"""
            CREATE TABLE dbo.{full_table_name} (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                Question NVARCHAR(MAX) NOT NULL,
                Option1 NVARCHAR(MAX) NOT NULL,
                Option2 NVARCHAR(MAX) NOT NULL,
                Option3 NVARCHAR(MAX) NOT NULL,
                Option4 NVARCHAR(MAX) NOT NULL,
                RightAnswer INT NOT NULL CHECK (RightAnswer IN (1, 2, 3, 4)),
                TimerMinutes INT DEFAULT {timer_minutes},
                NegativeMarking BIT DEFAULT 1,
                CreatedDate DATETIME DEFAULT GETDATE()
            )
            """
            
            cursor.execute(create_quiz_query)
            self.connection.commit()
            cursor.close()
            
            print(f"Successfully created quiz table: {full_table_name}")
            return True
            
        except Exception as e:
            print(f"Error creating simple quiz: {e}")
            return False
    
    def get_simple_quizzes(self, teacher_name="Admin"):
        """Gets all quizzes for a teacher using simple approach"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            teacher_prefix = teacher_name.replace(' ', '_').replace('-', '_')
            cursor = self.connection.cursor()
            
            # Get all tables that start with teacher prefix
            cursor.execute(f"""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME LIKE '{teacher_prefix}_%' 
                AND TABLE_SCHEMA = 'dbo'
                ORDER BY TABLE_NAME
            """)
            
            quizzes = []
            for row in cursor.fetchall():
                table_name = row[0]
                quiz_display_name = table_name.replace(f"{teacher_prefix}_", "").replace("_", " ").title()
                
                # Get timer and negative marking info
                try:
                    cursor.execute(f"SELECT TOP 1 TimerMinutes, NegativeMarking FROM dbo.{table_name}")
                    timer_info = cursor.fetchone()
                    timer_minutes = timer_info[0] if timer_info and timer_info[0] else 0
                    negative_marking = bool(timer_info[1]) if timer_info and timer_info[1] is not None else True
                except:
                    timer_minutes = 0
                    negative_marking = True
                
                quizzes.append({
                    'name': quiz_display_name,
                    'table_name': table_name,
                    'timer_minutes': timer_minutes,
                    'negative_marking': negative_marking
                })
            
            cursor.close()
            return quizzes
            
        except Exception as e:
            print(f"Error getting simple quizzes: {e}")
            return []
    
    def get_teacher_quizzes(self, teacher_id, teacher_name):
        """Gets all quizzes for a specific teacher"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            folder_name = f"Teacher_{teacher_id}_{teacher_name.replace(' ', '_')}"
            cursor = self.connection.cursor()
            
            cursor.execute(f"SELECT QuizName, QuizTableName, TimerMinutes, NegativeMarking FROM dbo.{folder_name}_Metadata ORDER BY CreatedDate DESC")
            
            quizzes = []
            for row in cursor.fetchall():
                quizzes.append({
                    'name': row[0],
                    'table_name': row[1],
                    'timer_minutes': row[2] or 0,
                    'negative_marking': bool(row[3])
                })
            
            cursor.close()
            return quizzes
            
        except Exception as e:
            print(f"Error getting teacher quizzes: {e}")
            return []
    
    def is_teacher_registered(self, email):
        """Checks if a teacher is already registered"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM dbo.RegisteredTeachers WHERE Email = ?", email)
            
            count = cursor.fetchone()[0]
            cursor.close()
            return count > 0
            
        except Exception as e:
            print(f"Error checking if teacher is registered: {e}")
            return False
    
    def get_all_registered_teachers(self):
        """Gets all registered teachers for student selection"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT rt.TeacherID, rt.TeacherName, rt.Email, t.EducationMailID
                FROM dbo.RegisteredTeachers rt
                JOIN dbo.Teachers t ON rt.TeacherID = t.ID
                WHERE rt.IsActive = 1
                ORDER BY rt.TeacherName
            """)
            
            teachers = []
            for row in cursor.fetchall():
                teachers.append({
                    'teacher_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'education_email': row[3]
                })
            
            cursor.close()
            return teachers
            
        except Exception as e:
            print(f"Error getting registered teachers: {e}")
            return []
    
    def get_quiz_info(self, table_name):
        """Gets quiz information including timer and negative marking settings"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT TOP 1 TimerMinutes, NegativeMarking FROM dbo.{table_name}")
            
            row = cursor.fetchone()
            if row:
                quiz_info = {
                    'timer_minutes': row[0] or 0,
                    'negative_marking': bool(row[1])
                }
                cursor.close()
                return quiz_info
            
            cursor.close()
            return None
            
        except Exception as e:
            print(f"Error getting quiz info: {e}")
            return None
    
    def calculate_quiz_score(self, table_name, student_answers, negative_marking=True):
        """Calculates quiz score with CORRECT negative marking logic"""
        if not self.connection:
            if not self.connect():
                return {'score': 0, 'total': 0, 'percentage': 0, 'details': []}
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Question, Option1, Option2, Option3, Option4, RightAnswer FROM dbo.{table_name}")
            
            questions = cursor.fetchall()
            cursor.close()
            
            total = len(questions)
            correct_answers = 0
            wrong_answers = 0
            unanswered = 0
            details = []
            
            # First pass: count correct, wrong, and unanswered
            for i, (q_text, opt1, opt2, opt3, opt4, correct) in enumerate(questions):
                student_choice = student_answers.get(i, 0)
                options = [opt1, opt2, opt3, opt4]
                
                if student_choice == correct:
                    correct_answers += 1
                    details.append({
                        'question': q_text,
                        'student_answer': options[student_choice - 1] if student_choice else "No answer",
                        'correct_answer': options[correct - 1],
                        'is_correct': True,
                        'points': 1
                    })
                elif student_choice > 0:  # Wrong answer (student attempted)
                    wrong_answers += 1
                    details.append({
                        'question': q_text,
                        'student_answer': options[student_choice - 1] if student_choice else "No answer",
                        'correct_answer': options[correct - 1],
                        'is_correct': False,
                        'points': -0.25
                    })
                else:  # No answer
                    unanswered += 1
                    details.append({
                        'question': q_text,
                        'student_answer': "No answer",
                        'correct_answer': options[correct - 1],
                        'is_correct': False,
                        'points': 0
                    })
            
            # Calculate final score using CORRECT logic
            if negative_marking:
                # Score = Correct answers - (Wrong answers * 0.25)
                final_score = correct_answers - (wrong_answers * 0.25)
            else:
                # Score = Only correct answers (no negative marking)
                final_score = correct_answers
            
            # Calculate percentage based on total possible score
            percentage = (final_score / total) * 100 if total > 0 else 0
            
            return {
                'score': round(final_score, 2),
                'total': total,
                'correct_answers': correct_answers,
                'wrong_answers': wrong_answers,
                'unanswered': unanswered,
                'percentage': round(percentage, 2),
                'details': details,
                'negative_marking_applied': negative_marking
            }
            
        except Exception as e:
            print(f"Error calculating quiz score: {e}")
            return {'score': 0, 'total': 0, 'percentage': 0, 'details': []}
