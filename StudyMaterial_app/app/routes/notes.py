from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Note

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

    raw_notes = Note.query.all()
    # annotate notes with file existence so template can render links
    notes = []
    for n in raw_notes:
        file_path = os.path.join(UPLOAD_FOLDER, n.title)
        notes.append({
            'object': n,
            'is_file': os.path.isfile(file_path)
        })
    return render_template('dashboard.html', notes=notes)

@notes_bp.route('/add', methods=['POST'])
def add_note():
    if 'username' not in session:
        flash('Please log in to add notes.', 'warning')
        return redirect(url_for('auth.login'))
    
    title = request.form.get('title') or ''
    file = request.files.get('file')
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        # use filename as note title if no text provided
        if not title:
            title = filename
    
    if title:
        new_note = Note(title=title)
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
        flash('Please log in to clear notes.', 'warning')
        return redirect(url_for('auth.login'))
    
    Note.query.delete()
    db.session.commit()
    flash('All notes cleared successfully!', 'success')
    return redirect(url_for('notes.view_notes'))


@notes_bp.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    """Remove a single note by its ID. Also delete any associated file.

    The form in the dashboard submits to this endpoint, so that users can
    clear individual notes instead of nuking the whole table.
    """
    if 'username' not in session:
        flash('Please log in to delete notes.', 'warning')
        return redirect(url_for('auth.login'))

    note = Note.query.get(note_id)
    if note is None:
        flash('Note not found.', 'danger')
    else:
        # try removing file with the same name as the title, if it exists
        file_path = os.path.join(UPLOAD_FOLDER, note.title)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # ignore any errors deleting the file

        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully!', 'success')

    return redirect(url_for('notes.view_notes'))






