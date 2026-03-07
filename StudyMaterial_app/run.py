from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    db.create_all()
    # Add new columns if they don't exist
    with db.engine.connect() as conn:
        # Check if columns exist
        result = conn.execute(text("PRAGMA table_info(note)"))
        columns = [row[1] for row in result.fetchall()]
        if 'course' not in columns:
            conn.execute(text("ALTER TABLE note ADD COLUMN course VARCHAR(100) NOT NULL DEFAULT ''"))
        if 'semester' not in columns:
            conn.execute(text("ALTER TABLE note ADD COLUMN semester VARCHAR(50) NOT NULL DEFAULT ''"))
        if 'subject' not in columns:
            conn.execute(text("ALTER TABLE note ADD COLUMN subject VARCHAR(100) NOT NULL DEFAULT ''"))
        conn.commit()

if __name__ == '__main__':
    app.run(debug=True)