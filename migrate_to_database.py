"""
Migration script to convert existing JSON quiz data to database tables
Run this script once to migrate your existing quiz_data.json to the database
"""

import json
import pyodbc
from SDP_FINAL_PROJECT_FULL import DatabaseManager

def migrate_json_to_database():
    """Migrates existing JSON quiz data to database tables"""
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    if not db_manager.connect():
        print("Failed to connect to database!")
        return False
    
    try:
        # Load existing JSON data
        with open("quiz_data.json", "r") as file:
            quiz_data = json.load(file)
        
        print(f"Found {len(quiz_data)} quiz subjects in JSON file")
        
        for subject, questions in quiz_data.items():
            # Clean subject name for table name
            table_name = ''.join(c for c in subject if c.isalnum() or c in ('_', '-')).strip()
            
            print(f"Migrating '{subject}' to table '{table_name}'...")
            
            # Create table if it doesn't exist
            if not db_manager.table_exists(table_name):
                if db_manager.create_quiz_table(table_name):
                    print(f"  [OK] Created table '{table_name}'")
                else:
                    print(f"  [ERROR] Failed to create table '{table_name}'")
                    continue
            else:
                print(f"  [SKIP] Table '{table_name}' already exists, skipping...")
                continue
            
            # Insert questions
            for question_text, options, correct_answer in questions:
                if db_manager.insert_question(table_name, question_text, 
                                             options[0], options[1], options[2], options[3], correct_answer):
                    print(f"    [OK] Added question: {question_text[:50]}...")
                else:
                    print(f"    [ERROR] Failed to add question: {question_text[:50]}...")
        
        print("\nMigration completed!")
        return True
        
    except FileNotFoundError:
        print("quiz_data.json file not found. No migration needed.")
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        return False
    finally:
        db_manager.disconnect()

if __name__ == "__main__":
    print("Starting migration from JSON to Database...")
    migrate_json_to_database()
