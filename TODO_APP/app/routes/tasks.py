from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Task

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
def view_tasks():
    if 'username' not in session:
        flash('Please log in to view your tasks.', 'warning')
        return redirect(url_for('auth.login'))

    tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)

@tasks_bp.route('/add', methods=['POST'])
def add_task():
    if 'username' not in session:
        flash('Please log in to add tasks.', 'warning')
        return redirect(url_for('auth.login'))

    title = request.form.get('title')
    if title:
        new_task = Task(title=title, status='pending')
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    else:
        flash('Task title cannot be empty.', 'danger')

    return redirect(url_for('tasks.view_tasks'))

@tasks_bp.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_status(task_id):
    if 'username' not in session:
        flash('Please log in to update tasks.', 'warning')
        return redirect(url_for('auth.login'))
    
    task = Task.query.get_or_404(task_id)
    if task:
        if task.status == 'pending':
            task.status = 'working'
        elif task.status == 'working':
            task.status = 'done'
        else:
            task.status = 'pending'
        db.session.commit()
        flash('Task status updated successfully!', 'success')

    return redirect(url_for('tasks.view_tasks'))

@tasks_bp.route('/clear', methods=['POST'])
def clear_tasks():
    if 'username' not in session:
        flash('Please log in to clear tasks.', 'warning')
        return redirect(url_for('auth.login'))
    
    Task.query.delete()
    db.session.commit()
    flash('All tasks cleared successfully!', 'success')
    return redirect(url_for('tasks.view_tasks'))

