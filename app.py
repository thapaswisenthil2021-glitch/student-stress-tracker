from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
from datetime import datetime, timedelta
import json
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'  # Change this in production

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login or register to access this page.', 'warning')
            return redirect(url_for('register'))
        return f(*args, **kwargs)
    return decorated_function

# Database initialization with migration support
def init_db():
    conn = sqlite3.connect('stress_data.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            age INTEGER,
            gender TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')
    
    # Create main table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stress_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            academic_pressure INTEGER NOT NULL,
            sleep_hours REAL NOT NULL,
            physical_activity INTEGER NOT NULL,
            social_support INTEGER NOT NULL,
            workload_hours INTEGER NOT NULL,
            stress_level INTEGER NOT NULL,
            stress_score REAL NOT NULL,
            recommendations TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            rating INTEGER,
            message TEXT NOT NULL,
            mood TEXT,
            page TEXT,
            browser TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if all columns exist, add missing ones
    cursor.execute("PRAGMA table_info(stress_records)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add missing columns if they don't exist
    if 'user_id' not in columns:
        cursor.execute('ALTER TABLE stress_records ADD COLUMN user_id INTEGER DEFAULT NULL')
    
    if 'age' not in columns:
        cursor.execute('ALTER TABLE stress_records ADD COLUMN age INTEGER NOT NULL DEFAULT 18')
    
    if 'gender' not in columns:
        cursor.execute('ALTER TABLE stress_records ADD COLUMN gender TEXT NOT NULL DEFAULT "Unknown"')
    
    if 'stress_score' not in columns:
        cursor.execute('ALTER TABLE stress_records ADD COLUMN stress_score REAL NOT NULL DEFAULT 0')
    
    # Create chart cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chart_cache (
            id INTEGER PRIMARY KEY,
            data TEXT,
            last_updated DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def migrate_old_data():
    """Migrate old data if needed"""
    try:
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        
        # Check if we have old data without age/gender columns
        cursor.execute("PRAGMA table_info(stress_records)")
        columns = cursor.fetchall()
        
        # If we have old records but missing columns, we need to handle them
        cursor.execute("SELECT COUNT(*) FROM stress_records")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Found {count} existing records. Old data will need default values.")
        
        conn.close()
    except Exception as e:
        print(f"Migration check error: {e}")

@app.route('/')
def index():
    # Redirect to register if not logged in
    if 'user_id' not in session:
        return redirect(url_for('register'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, redirect to assessment
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        age = request.form.get('age', '')
        gender = request.form.get('gender', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required!')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!')
            return redirect(url_for('register'))
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('stress_data.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, email, password, full_name, age, gender)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, hashed_password, full_name, age if age else None, gender))
            
            conn.commit()
            
            # Get the new user's ID
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            
            # Auto login after registration
            session['user_id'] = user[0]
            session['username'] = username
            session['full_name'] = full_name
            
            flash(f'Welcome {username}! Your account has been created successfully.', 'success')
            return redirect(url_for('index'))
            
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                flash('Username already exists!')
            elif 'email' in str(e):
                flash('Email already registered!')
            else:
                flash('Registration failed. Please try again.')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to assessment
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please enter username and password!')
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, username))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[3], password):  # password is at index 3
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                         (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user[0]))
            conn.commit()
            
            # Set session
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['full_name'] = user[4]
            
            flash(f'Welcome back, {user[1]}!', 'success')
            conn.close()
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!')
            
        conn.close()
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('register'))

@app.route('/profile')
@login_required
def profile():
    conn = sqlite3.connect('stress_data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # Get user's assessment stats
    cursor.execute('''
        SELECT COUNT(*), AVG(stress_score), MAX(stress_score), MIN(stress_score)
        FROM stress_records WHERE user_id = ?
    ''', (session['user_id'],))
    stats = cursor.fetchone()
    
    conn.close()
    
    return render_template('profile.html', user=user, stats=stats)

# Feedback Routes
@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        try:
            # Get form data
            feedback_type = request.form.get('feedback_type', '').strip()
            rating = request.form.get('rating', '')
            message = request.form.get('message', '').strip()
            mood = request.form.get('mood', '')
            page = request.form.get('page', '')
            browser = request.form.get('browser', '')
            
            # Validation
            if not feedback_type:
                flash('Please select a feedback type!', 'warning')
                return redirect(url_for('feedback'))
            
            if not message:
                flash('Please enter your feedback message!', 'warning')
                return redirect(url_for('feedback'))
            
            if len(message) > 500:
                flash('Feedback message is too long (max 500 characters)!', 'warning')
                return redirect(url_for('feedback'))
            
            # Convert rating to int if provided
            if rating:
                try:
                    rating = int(rating)
                except ValueError:
                    rating = None
            else:
                rating = None
            
            # Save to database
            conn = sqlite3.connect('stress_data.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback 
                (user_id, username, feedback_type, rating, message, mood, page, browser)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'], 
                session['username'], 
                feedback_type, 
                rating, 
                message, 
                mood, 
                page, 
                browser
            ))
            
            conn.commit()
            conn.close()
            
            flash('Thank you for your feedback! We appreciate your input.', 'success')
            return redirect(url_for('index'))
            
        except sqlite3.Error as e:
            flash(f'Database error: {str(e)}', 'danger')
            return redirect(url_for('feedback'))
        except Exception as e:
            flash(f'Error submitting feedback: {str(e)}', 'danger')
            return redirect(url_for('feedback'))
    
    return render_template('feedback.html')

@app.route('/feedback/history')
@login_required
def feedback_history():
    try:
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        
        # Get user's feedback history
        cursor.execute('''
            SELECT id, feedback_type, rating, message, status, 
                   strftime('%Y-%m-%d %H:%M', created_at) as created
            FROM feedback
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (session['user_id'],))
        
        feedbacks = cursor.fetchall()
        conn.close()
        
        return render_template('feedback_history.html', feedbacks=feedbacks)
    
    except sqlite3.Error as e:
        flash(f'Error loading feedback history: {str(e)}', 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/feedback/delete/<int:feedback_id>', methods=['GET', 'POST'])
@login_required
def delete_feedback(feedback_id):
    try:
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        
        # Verify ownership
        cursor.execute('SELECT user_id FROM feedback WHERE id = ?', (feedback_id,))
        feedback = cursor.fetchone()
        
        if feedback and feedback[0] == session['user_id']:
            cursor.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
            conn.commit()
            flash('Feedback deleted successfully!', 'success')
        else:
            flash('Feedback not found or unauthorized!', 'danger')
        
        conn.close()
        
    except sqlite3.Error as e:
        flash(f'Error deleting feedback: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('feedback_history'))

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_stress():
    try:
        # Get form data with validation
        name = request.form.get('name', '').strip()
        if not name:
            flash("Please enter your name")
            return redirect(url_for('index'))
        
        try:
            age = int(request.form.get('age', 18))
            if age < 12 or age > 30:
                flash("Age must be between 12 and 30")
                return redirect(url_for('index'))
        except ValueError:
            flash("Please enter a valid age")
            return redirect(url_for('index'))
        
        gender = request.form.get('gender', 'Unknown')
        if gender not in ['Male', 'Female', 'Other']:
            gender = 'Unknown'
        
        try:
            academic_pressure = int(request.form.get('academic_pressure', 3))
            if academic_pressure < 1 or academic_pressure > 5:
                academic_pressure = 3
        except ValueError:
            academic_pressure = 3
        
        try:
            sleep_hours = float(request.form.get('sleep_hours', 7))
            if sleep_hours < 4 or sleep_hours > 12:
                sleep_hours = 7
        except ValueError:
            sleep_hours = 7
        
        try:
            physical_activity = int(request.form.get('physical_activity', 3))
            if physical_activity < 1 or physical_activity > 5:
                physical_activity = 3
        except ValueError:
            physical_activity = 3
        
        try:
            social_support = int(request.form.get('social_support', 3))
            if social_support < 1 or social_support > 5:
                social_support = 3
        except ValueError:
            social_support = 3
        
        try:
            workload_hours = int(request.form.get('workload_hours', 40))
            if workload_hours < 10 or workload_hours > 80:
                workload_hours = 40
        except ValueError:
            workload_hours = 40
        
        # Calculate stress score (weighted average)
        score = calculate_stress_score(
            academic_pressure, sleep_hours, physical_activity,
            social_support, workload_hours
        )
        
        # Determine stress level
        stress_level, level_text, color = get_stress_level_info(score)
        
        # Generate recommendations
        recommendations = generate_recommendations(
            academic_pressure, sleep_hours, physical_activity,
            social_support, workload_hours, score
        )
        
        # Save to database
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO stress_records
                (user_id, name, age, gender, academic_pressure, sleep_hours, physical_activity,
                 social_support, workload_hours, stress_level, stress_score, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], name, age, gender, academic_pressure, sleep_hours, physical_activity,
                  social_support, workload_hours, stress_level, score, json.dumps(recommendations)))
            
            conn.commit()
        except sqlite3.Error as e:
            flash(f"Database error: {str(e)}")
            return redirect(url_for('index'))
        finally:
            conn.close()
        
        return render_template('result.html',
                             name=name,
                             score=round(score, 1),
                             level_text=level_text,
                             color=color,
                             academic_pressure=academic_pressure,
                             sleep_hours=sleep_hours,
                             physical_activity=physical_activity,
                             social_support=social_support,
                             workload_hours=workload_hours,
                             recommendations=recommendations,
                             stress_level=stress_level)
    
    except Exception as e:
        flash(f"Error processing your data: {str(e)}")
        return redirect(url_for('index'))

def calculate_stress_score(academic, sleep, activity, support, workload):
    """Calculate stress score based on weighted factors"""
    # Normalize sleep hours (ideal is 8, less sleep = higher stress)
    sleep_score = max(0, (8 - min(sleep, 8)) * 2.5)  # 0-20 points
    
    # Academic pressure (1-5 scale, higher = more stress)
    academic_score = (academic - 1) * 6.25  # 0-25 points
    
    # Physical activity (1-5 scale, lower = more stress)
    activity_score = (5 - activity) * 3.75  # 0-15 points
    
    # Social support (1-5 scale, lower = more stress)
    support_score = (5 - support) * 5  # 0-20 points
    
    # Workload hours (capped at 80 hours)
    workload_score = min(workload / 80 * 20, 20)  # 0-20 points
    
    return sleep_score + academic_score + activity_score + support_score + workload_score

def get_stress_level_info(score):
    """Get stress level information based on score"""
    if score < 30:
        return 1, "Low Stress", "success"
    elif score < 60:
        return 2, "Moderate Stress", "warning"
    else:
        return 3, "High Stress", "danger"

def generate_recommendations(academic, sleep, activity, support, workload, score):
    """Generate personalized recommendations based on stress factors"""
    recommendations = []
    
    # Academic pressure recommendations
    if academic >= 4:
        recommendations.append("Consider time management techniques like Pomodoro (25 min focus, 5 min break)")
        recommendations.append("Break study sessions into smaller, manageable chunks")
    elif academic >= 3:
        recommendations.append("Maintain consistent study schedule to avoid last-minute pressure")
    
    # Sleep recommendations
    if sleep < 7:
        recommendations.append(f"Aim for 7-9 hours of sleep (currently {sleep} hours)")
        recommendations.append("Establish a consistent sleep schedule, even on weekends")
        recommendations.append("Avoid screens 1 hour before bedtime")
    elif sleep > 9:
        recommendations.append(f"Consider if excessive sleep ({sleep} hours) indicates fatigue or depression")
    
    # Physical activity recommendations
    if activity <= 2:
        recommendations.append("Try to incorporate 30 minutes of moderate activity daily")
        recommendations.append("Start with walking, yoga, or stretching exercises")
    elif activity <= 3:
        recommendations.append("Maintain your current activity level for stress management")
    
    # Social support recommendations
    if support <= 2:
        recommendations.append("Connect with friends or join study groups for support")
        recommendations.append("Consider talking to a counselor or mentor")
    elif support <= 3:
        recommendations.append("Strengthen existing social connections for better support")
    
    # Workload recommendations
    if workload > 50:
        recommendations.append("Prioritize tasks using Eisenhower Matrix (urgent vs important)")
        recommendations.append("Schedule regular breaks using the 52-17 rule (52 min work, 17 min break)")
    elif workload > 40:
        recommendations.append("Balance study time with relaxation activities")
    
    # General recommendations based on stress level
    if score >= 60:
        recommendations.append("Consider consulting a mental health professional")
        recommendations.append("Practice mindfulness meditation for 10 minutes daily")
        recommendations.append("Try progressive muscle relaxation techniques")
    elif score >= 30:
        recommendations.append("Practice deep breathing exercises (4-7-8 technique)")
        recommendations.append("Maintain a balanced routine with leisure activities")
        recommendations.append("Keep a gratitude journal to focus on positive aspects")
    else:
        recommendations.append("Great job! Maintain your current healthy habits")
        recommendations.append("Continue monitoring stress levels regularly")
        recommendations.append("Share your stress management strategies with peers")
    
    return recommendations

@app.route('/history')
@login_required
def history():
    try:
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        
        # Get user-specific records
        cursor.execute('''
            SELECT id, timestamp, name, stress_level, stress_score, age, gender
            FROM stress_records 
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (session['user_id'],))
        
        records = cursor.fetchall()
        conn.close()
        
        # Map stress levels to text
        level_map = {1: "Low", 2: "Moderate", 3: "High"}
        records_with_text = []
        for record in records:
            record_list = list(record)
            record_list[3] = level_map.get(record_list[3], "Unknown")
            records_with_text.append(record_list)
        
        return render_template('history.html', records=records_with_text)
    
    except Exception as e:
        flash(f"Error loading history: {str(e)}")
        return render_template('history.html', records=[])

@app.route('/chart')
@login_required
def chart():
    try:
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        
        # Get data for chart (only user's data)
        cursor.execute('''
            SELECT
                strftime('%Y-%m-%d', timestamp) as date,
                AVG(stress_score) as avg_stress_score,
                AVG(stress_level) as avg_stress_level,
                COUNT(*) as count
            FROM stress_records
            WHERE user_id = ?
            GROUP BY strftime('%Y-%m-%d', timestamp)
            ORDER BY date DESC
            LIMIT 30
        ''', (session['user_id'],))
        chart_data = cursor.fetchall()
        
        # Get distribution (only user's data)
        cursor.execute('''
            SELECT stress_level, COUNT(*) as count
            FROM stress_records
            WHERE user_id = ?
            GROUP BY stress_level
            ORDER BY stress_level
        ''', (session['user_id'],))
        distribution = cursor.fetchall()
        
        # Get gender distribution (from user's profile)
        cursor.execute('SELECT gender FROM users WHERE id = ?', (session['user_id'],))
        user_gender = cursor.fetchone()
        gender_dist = [(user_gender[0] if user_gender and user_gender[0] else 'Unknown', 1)]
        
        # Get age statistics (from user's data)
        cursor.execute('''
            SELECT
                CASE
                    WHEN age < 18 THEN 'Under 18'
                    WHEN age BETWEEN 18 AND 21 THEN '18-21'
                    WHEN age BETWEEN 22 AND 25 THEN '22-25'
                    ELSE '26+'
                END as age_group,
                COUNT(*) as count,
                AVG(stress_score) as avg_score
            FROM stress_records
            WHERE user_id = ?
            GROUP BY age_group
            ORDER BY age_group
        ''', (session['user_id'],))
        age_dist = cursor.fetchall()
        
        # Get factor averages (only user's data)
        cursor.execute('''
            SELECT
                AVG(academic_pressure) as avg_academic,
                AVG(sleep_hours) as avg_sleep,
                AVG(physical_activity) as avg_activity,
                AVG(social_support) as avg_support,
                AVG(workload_hours) as avg_workload
            FROM stress_records
            WHERE user_id = ?
        ''', (session['user_id'],))
        factor_avgs = cursor.fetchone()
        
        conn.close()
        
        return render_template('chart.html',
                             chart_data=chart_data,
                             distribution=distribution,
                             gender_dist=gender_dist,
                             age_dist=age_dist,
                             factor_avgs=factor_avgs)
    
    except Exception as e:
        flash(f"Error loading charts: {str(e)}")
        return render_template('chart.html',
                             chart_data=[],
                             distribution=[],
                             gender_dist=[],
                             age_dist=[],
                             factor_avgs=(0, 0, 0, 0, 0))

@app.route('/db-table')
@login_required
def db_table():
    """Render the `stress_records` table as an HTML page for inspection."""
    try:
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(stress_records)')
        cols = [col[1] for col in cursor.fetchall()]
        cursor.execute('SELECT * FROM stress_records WHERE user_id = ? ORDER BY timestamp DESC', (session['user_id'],))
        rows = cursor.fetchall()
        conn.close()
        return render_template('db_table.html', cols=cols, rows=rows)
    except Exception as e:
        flash(f"Error loading DB table: {str(e)}")
        return redirect(url_for('index'))

@app.route('/record/<int:record_id>')
@login_required
def view_record(record_id):
    try:
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stress_records WHERE id = ? AND user_id = ?', (record_id, session['user_id']))
        record = cursor.fetchone()
        conn.close()
        
        if record:
            # Parse recommendations from JSON
            recommendations = json.loads(record[12]) if len(record) > 12 and record[12] else []
            
            # Get stress level info
            stress_level = record[10] if len(record) > 10 else 1
            level_map = {1: ("Low", "success"), 2: ("Moderate", "warning"), 3: ("High", "danger")}
            level_text, color = level_map.get(stress_level, ("Unknown", "secondary"))
            
            return render_template('result.html',
                                 name=record[2] if len(record) > 2 else "Unknown",
                                 score=round(record[11], 1) if len(record) > 11 and record[11] else "N/A",
                                 level_text=level_text,
                                 color=color,
                                 academic_pressure=record[4] if len(record) > 4 else 3,
                                 sleep_hours=record[5] if len(record) > 5 else 7,
                                 physical_activity=record[6] if len(record) > 6 else 3,
                                 social_support=record[7] if len(record) > 7 else 3,
                                 workload_hours=record[8] if len(record) > 8 else 40,
                                 recommendations=recommendations,
                                 from_history=True)
        else:
            flash("Record not found!")
            return redirect(url_for('history'))
    
    except Exception as e:
        flash(f"Error loading record: {str(e)}")
        return redirect(url_for('history'))

@app.route('/api/chart-data')
@login_required
def get_chart_data():
    """API endpoint for chart data (for real-time updates)"""
    try:
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        
        # Get data for last 30 days (only user's data)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT
                strftime('%Y-%m-%d', timestamp) as date,
                AVG(stress_score) as avg_stress,
                COUNT(*) as count
            FROM stress_records
            WHERE user_id = ? AND date >= ?
            GROUP BY strftime('%Y-%m-%d', timestamp)
            ORDER BY date
        ''', (session['user_id'], thirty_days_ago))
        
        data = cursor.fetchall()
        
        # Get latest data timestamp
        cursor.execute('SELECT MAX(timestamp) FROM stress_records WHERE user_id = ?', (session['user_id'],))
        last_update = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'labels': [row[0] for row in data],
            'data': [float(row[1]) if row[1] else 0 for row in data],
            'counts': [row[2] for row in data],
            'updated': last_update or datetime.now().isoformat(),
            'total_records': sum(row[2] for row in data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset-db')
def reset_database():
    """Reset database (for development only - remove in production)"""
    if os.path.exists('stress_data.db'):
        os.remove('stress_data.db')
        flash("Database reset successfully!")
    init_db()
    return redirect(url_for('register'))

if __name__ == '__main__':
    # Create static folders if they don't exist
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("Initializing database...")
    init_db()
    migrate_old_data()
    
    # Verify feedback table exists
    try:
        conn = sqlite3.connect('stress_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
        if cursor.fetchone():
            print("✓ Feedback table verified")
        else:
            print("✗ Feedback table not found")
        conn.close()
    except Exception as e:
        print(f"Error verifying feedback table: {e}")
    
    print("Starting Student Stress Tracker...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, port=5000)