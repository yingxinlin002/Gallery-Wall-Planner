from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, jsonify
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from gallery.models.exhibit import db
from gallery.models.wall import Wall
from gallery.models.exhibit import Gallery
from gallery.models import db
from gallery.models.project_exporter import export_gallery_to_excel, import_gallery_from_excel
from flask_wtf import CSRFProtect
from gallery.models.artwork import Artwork

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
        wall = Wall(name=name, width=width, height=height, color=color, gallery_id=gallery.id)
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
    wall = Wall(name=name, width=width, height=height, color=color, gallery_id=gallery.id)
    db.session.add(wall)
    db.session.commit()
    session["current_wall_id"] = wall.id
    # Redirect to permanent object placement page
    return redirect(url_for('edit_permanent_objects'))

@app.route('/add_permanent_object', methods=['POST'])
def add_permanent_object():
    from gallery.models.permanent_object import PermanentObject
    try:
        wall_id = request.form.get('wall_id')
        name = request.form.get('name')
        width = float(request.form.get('width', 0))
        height = float(request.form.get('height', 0))
        x = float(request.form.get('x', 0))
        y = float(request.form.get('y', 0))
        color = request.form.get('color', '#6495ed')
        
        # Handle file upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(app.static_folder, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                image_path = os.path.join('uploads', filename)
        
        obj = PermanentObject(
            name=name,
            width=width,
            height=height,
            x=x,
            y=y,
            color=color,
            image_path=image_path,
            wall_id=wall_id
        )
        db.session.add(obj)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'object': obj.to_dict()
            })
        else:
            flash("Fixture added successfully", "success")
            return redirect(url_for('edit_permanent_objects'))
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        else:
            flash(f"Error adding fixture: {str(e)}", "error")
            return redirect(url_for('edit_permanent_objects'))
    
@app.route('/edit_permanent_objects')
def edit_permanent_objects():
    wall = get_current_wall()
    if not wall:
        flash("No wall selected", "error")
        return redirect(url_for('select_wall_space'))
    
    return render_template('lock_objects.html', wall=wall)

@app.route('/update_permanent_object', methods=['POST'])
def update_permanent_object():
    try:
        obj_id = request.form.get('obj_id')
        name = request.form.get('name')
        width = float(request.form.get('width', 0))
        height = float(request.form.get('height', 0))
        x = float(request.form.get('x', 0))
        y = float(request.form.get('y', 0))
        color = request.form.get('color', '#6495ed')
        
        from gallery.models.permanent_object import PermanentObject
        obj = PermanentObject.query.get_or_404(obj_id)
        obj.name = name
        obj.width = width
        obj.height = height
        obj.x = x
        obj.y = y
        obj.color = color
        
        # Handle file upload if needed
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(app.static_folder, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                obj.image_path = os.path.join('uploads', filename)
        
        db.session.commit()
        flash("Fixture updated successfully", "success")
        return redirect(url_for('edit_permanent_objects'))
    
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating fixture: {str(e)}", "error")
        return redirect(url_for('edit_permanent_objects'))

@app.route('/delete_permanent_object/<int:obj_id>', methods=['POST'])
def delete_permanent_object(obj_id):
    from gallery.models.permanent_object import PermanentObject
    obj = PermanentObject.query.get_or_404(obj_id)
    wall_id = obj.wall_id
    db.session.delete(obj)
    db.session.commit()
    flash("Permanent object deleted.", "success")
    return redirect(url_for('lock_objects', wall_id=wall_id))

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

@app.route('/create_wall', methods=['GET', 'POST'])
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

@app.route('/save_and_continue', methods=['POST'])
def save_and_continue():
    # Implement save logic if needed
    return redirect(url_for('editor'))

@app.route('/editor')
def editor():
    wall = get_current_wall()
    # Unplaced artworks: those not assigned to any wall
    unplaced_artwork = Artwork.query.filter_by(wall_id=None).all()
    return render_template(
        'editor.html',
        current_wall=wall,
        unplaced_artwork=unplaced_artwork,
        current_wall_artwork=getattr(wall, "artworks", []),
        wall_lines=getattr(wall, "snap_lines", [])
    )

@app.route('/artwork-manual', methods=['GET', 'POST'])
def artwork_manual():
    wall = get_current_wall()
    
    if request.method == 'POST':
        try:
            # Helper function to safely convert form values to float
            def get_float(form, field, default=0.0):
                value = form.get(field)
                return float(value) if value else default

            # Create new artwork
            artwork = Artwork(
                name=request.form.get('name', '').strip(),
                width=get_float(request.form, 'width'),
                height=get_float(request.form, 'height'),
                hanging_point=get_float(request.form, 'hanging'),
                medium=request.form.get('medium', '').strip(),
                depth=get_float(request.form, 'depth'),
                price=get_float(request.form, 'price'),
                nfs=bool(request.form.get('nfs')),
                wall_id=wall.id if wall else None
            )
            
            # Handle file upload
            if 'imageUpload' in request.files:
                file = request.files['imageUpload']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(app.static_folder, 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    upload_path = os.path.join(upload_dir, filename)
                    file.save(upload_path)
                    artwork.image_path = os.path.join('static', 'uploads', filename)
            
            db.session.add(artwork)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'artwork': artwork.to_dict()
                })
            return redirect(url_for('artwork_manual'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating artwork: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)}), 400
            flash(f"Error creating artwork: {str(e)}")
            return redirect(url_for('artwork_manual'))
    
    artworks = Artwork.query.filter_by(wall_id=None).all()
    if wall:
        artworks += wall.artworks
        
    return render_template('artwork_manually.html', artworks=artworks)

@app.route("/load", methods=["POST"])
def load_exhibit():
    return redirect(url_for('select_wall_space'))

@app.route('/delete-wall/<int:wall_id>', methods=['POST'])
def delete_wall(wall_id):
    wall = Wall.query.get_or_404(wall_id)
    db.session.delete(wall)
    db.session.commit()
    flash(f'Wall "{wall.name}" deleted.', "success")
    return redirect(url_for('select_wall_space'))

@app.route('/update_object_position/<int:obj_id>', methods=['POST'])
def update_object_position(obj_id):
    from gallery.models.permanent_object import PermanentObject
    obj = PermanentObject.query.get_or_404(obj_id)
    data = request.get_json()
    obj.x = data['x']
    obj.y = data['y']
    db.session.commit()
    return jsonify({'success': True})

@app.route('/save_and_continue_permanent_objects', methods=['POST'])
def save_and_continue_permanent_objects():
    # You can add any save logic here if needed
    return redirect(url_for('select_wall_space'))

@app.route('/update_artwork_position/<int:artwork_id>', methods=['POST'])
def update_artwork_position(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    data = request.get_json()
    artwork.x_position = data.get('x_position', artwork.x_position)
    artwork.y_position = data.get('y_position', artwork.y_position)
    artwork.wall_id = data.get('wall_id', artwork.wall_id)
    db.session.commit()
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True, port=11002, host="0.0.0.0")
