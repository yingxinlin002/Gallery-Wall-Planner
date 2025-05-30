from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from gallery.models.exhibit import db  # Import db from your models
from gallery.models.wall import Wall
from gallery.models.exhibit import Gallery, Wall
from gallery.models.project_exporter import export_gallery_to_excel, import_gallery_from_excel
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gallery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()

USER_DIR = os.path.join(os.path.expanduser("~"), "GalleryWallPlanner")
os.makedirs(USER_DIR, exist_ok=True)
TEMP_FILE = os.path.join(USER_DIR, "_temp.xlsx")


def get_current_wall():
    wall_id = session.get("current_wall_id")
    if wall_id is not None:
        wall = db.session.get(Wall, wall_id)
        return wall
    # Optionally, return the first wall if no wall is selected
    wall = Wall.query.first()
    return wall

@app.route("/", methods=["GET"])
def home():
    last_project_exists = os.path.exists(TEMP_FILE) and os.path.getsize(TEMP_FILE) > 6144
    return render_template("home.html", last_project_exists=last_project_exists)

@app.route("/continue", methods=["POST"])
def continue_last_project():
    try:
        # Import from Excel and add to the database
        import_gallery_from_excel(TEMP_FILE, db)  # Pass db if your function needs it
        return redirect(url_for('select_wall_space'))
    except Exception as e:
        flash(str(e))
        return redirect(url_for("home"))

@app.route('/new-gallery', methods=['GET', 'POST'])
def new_gallery():
    if request.method == 'POST':
        name = request.form.get('wall_name')
        width = float(request.form.get('wall_width'))
        height = float(request.form.get('wall_height'))
        color = request.form.get('wall_color')
        # Assume you have a gallery object or create one
        gallery = Gallery.query.first()  # Or however you want to select
        wall = Wall(name=name, width=width, height=height, color=color, gallery=gallery)
        db.session.add(wall)
        db.session.commit()
        return redirect(url_for('select_wall_space'))
    return render_template('new_gallery.html')

@app.route('/submit_wall', methods=['POST'])
def submit_wall():
    name = request.form.get('wall_name')
    width = float(request.form.get('wall_width'))
    height = float(request.form.get('wall_height'))
    color = request.form.get('wall_color')
    gallery = Gallery.query.first()
    if not gallery:
        gallery = Gallery(name="Default Gallery")
        db.session.add(gallery)
        db.session.commit()
    wall = Wall(name=name, width=width, height=height, color=color, gallery=gallery)
    db.session.add(wall)
    db.session.commit()
    session["current_wall_id"] = wall.id
    # Redirect to permanent object placement page
    return redirect(url_for('edit_permanent_objects'))

@app.route('/edit-permanent-objects')
def edit_permanent_objects():
    wall = get_current_wall()
    if wall is None:
        flash("No wall selected", "error")
        return redirect(url_for('select_wall_space'))
    
    return render_template('lock_objects.html', 
                         permanent_objects=wall.permanent_objects)

@app.route('/select-wall-space', methods=['GET'])
def select_wall_space():
    current_wall = get_current_wall()
    walls = Wall.query.all()
    return render_template(
        'select_wall_space.html',
        walls=walls,
        current_wall=current_wall,
        min=min
    )

@app.route('/select-wall/<wall_id>')
def select_wall(wall_id):
    session["current_wall_id"] = wall_id
    return redirect(url_for('select_wall_space'))

@app.route('/create-wall', methods=['GET', 'POST'])
def create_wall():
    if request.method == 'POST':
        name = request.form.get('wall_name')
        width = float(request.form.get('wall_width'))
        height = float(request.form.get('wall_height'))
        color = request.form.get('wall_color')
        wall = Wall(name=name, width=width, height=height, color=color)
        db.session.add(wall)
        db.session.commit()
        session["current_wall_id"] = wall.id
        return redirect(url_for('select_wall_space'))
    return render_template('new_gallery.html')


@app.route('/add_wall_object', methods=['POST'])
def add_wall_object():
    # Implement logic to add a new permanent object to the wall
    # For now, just redirect back
    return redirect(url_for('edit_permanent_objects'))

@app.route('/save_and_continue', methods=['POST'])
def save_and_continue():
    # Implement save logic if needed
    return redirect(url_for('editor'))

@app.route('/editor')
def editor():
    wall = get_current_wall()
    # For demo, pass empty lists for artwork and wall_lines
    return render_template(
        'editor.html',
        current_wall=wall,
        unplaced_artwork=[],
        current_wall_artwork=getattr(wall, "artworks", []),
        wall_lines=getattr(wall, "snap_lines", [])
    )

@app.route('/artwork-manual', methods=['GET', 'POST'])
def artwork_manual():
    if request.method == 'POST':
        # Parse form and add artwork to current wall or gallery
        pass
    # For demo, show all artworks in gallery
    wall = get_current_wall()
    artworks = getattr(wall, "artworks", []) if wall else []
    return render_template('artwork_manually.html', artworks=artworks)

@app.route("/load", methods=["POST"])
def load_exhibit():
    uploaded_file = request.files.get("file")
    if uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(USER_DIR, filename)
        uploaded_file.save(file_path)
        try:
            import_gallery_from_excel(file_path, db)  # Pass db if needed
            return redirect(url_for('select_wall_space'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for("home"))
    flash("No file selected.")
    return redirect(url_for("home"))

@app.route("/quit")
def quit_app():
    export_gallery_to_excel(TEMP_FILE, gallery)
    return send_file(TEMP_FILE, as_attachment=True, download_name="gallery_export.xlsx")

@app.route('/delete-wall/<int:wall_id>', methods=['POST'])
def delete_wall(wall_id):
    wall = Wall.query.get_or_404(wall_id)
    db.session.delete(wall)
    db.session.commit()
    flash(f'Wall "{wall.name}" deleted.', "success")
    return redirect(url_for('select_wall_space'))

if __name__ == "__main__":
    app.run(debug=True)
