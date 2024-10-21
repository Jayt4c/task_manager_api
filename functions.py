import os
import time
from flask import current_app, session, flash, redirect, url_for

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'jpg', 'png'}

def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(filename):
    """Returns the size of the file in a human-readable format."""
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        return f"{size / 1024:.2f} KB"  # Convert bytes to KB
    return "N/A"

def get_file_date(filename):
    """Returns the last modified date of the file."""
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return time.ctime(os.path.getmtime(filepath))
    return "N/A"

def register_helpers(app):
    """Make helper functions available in templates."""
    app.context_processor(lambda: dict(get_file_size=get_file_size, get_file_date=get_file_date))
