from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import os

from app import db
from app.models import Note, User

# blueprint for note-related routes; its name defines the blueprint
# prefix used by url_for() calls (e.g. 'notes.view_notes').
notes_bp = Blueprint('notes', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# view the user's notes list; homepage stays with auth blueprint
@notes_bp.route('/notes')
def view_notes():
    if 'username' not in session:
        flash('Please log in to view Dashboard.', 'warning')
        return redirect(url_for('auth.login'))

    username = session['username']
    user = User.query.filter_by(username=username).first()

    if username == 'admin':
        raw_notes = Note.query.all()
    else:
        admin = User.query.filter_by(username='admin').first()

        raw_notes = Note.query.filter(
            or_(Note.user_id == user.id, Note.user_id == admin.id)
        ).all()

    # Group notes by course > semester > subject
    notes_by_course = {}

    for n in raw_notes:
        file_path = os.path.join(UPLOAD_FOLDER, n.filename) if n.filename else None

        note_data = {
            'object': n,
            'is_file': os.path.isfile(file_path) if file_path else False
        }

        course = n.course
        semester = n.semester
        subject = n.subject

        if course not in notes_by_course:
            notes_by_course[course] = {}

        if semester not in notes_by_course[course]:
            notes_by_course[course][semester] = {}

        if subject not in notes_by_course[course][semester]:
            notes_by_course[course][semester][subject] = []

        notes_by_course[course][semester][subject].append(note_data)

    return render_template('dashboard.html', notes_by_course=notes_by_course)

@notes_bp.route('/add', methods=['POST'])
def add_note():
    if 'username' not in session:
        flash('Please log in to add notes.', 'warning')
        return redirect(url_for('auth.login'))

    title = request.form.get('title') or ''
    course = request.form.get('course')
    semester = request.form.get('semester')
    subject = request.form.get('subject')
    file = request.files.get('file')

    filename = None

    if not course or not semester or not subject:
        flash('Course, Semester, and Subject are required.', 'danger')
        return redirect(url_for('notes.view_notes'))

    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        if not title:
            title = filename

    if title:
        user = User.query.filter_by(username=session['username']).first()

        new_note = Note(
            title=title,
            filename=filename,
            course=course,
            semester=semester,
            subject=subject,
            user_id=user.id
        )

        db.session.add(new_note)
        db.session.commit()

        flash('Note added successfully!', 'success')
    else:
        flash('Note title cannot be empty.', 'danger')

    return redirect(url_for('notes.view_notes'))

@notes_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@notes_bp.route('/clear', methods=['POST'])
def clear_notes():
    if 'username' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    # allow only admin
    if session.get('username') != 'admin':
        flash('Only admin can clear all notes.', 'danger')
        return redirect(url_for('notes.view_notes'))

    Note.query.delete()
    db.session.commit()

    flash('All notes cleared successfully!', 'success')
    return redirect(url_for('notes.view_notes'))

@notes_bp.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):

    if 'username' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    if session.get('username') != 'admin':
        flash('Only admin can delete notes.', 'danger')
        return redirect(url_for('notes.view_notes'))

    note = Note.query.get(note_id)

    if note is None:
        flash('Note not found.', 'danger')
    else:
        file_path = os.path.join(UPLOAD_FOLDER, note.filename)

        if note.filename and os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        db.session.delete(note)
        db.session.commit()

        flash('Note deleted successfully!', 'success')

    return redirect(url_for('notes.view_notes'))

@notes_bp.route('/allnotes')
def all_notes():
    return Note.query.all()