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
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KcEY", "default_secret")  # Required for flashing messages ## Adding OAuth Support
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
    
    permanent_objects = [obj.to_dict() for obj in wall.permanent_objects]
    
    return render_template('lock_objects.html', 
                           wall=wall, 
                           permanent_objects=permanent_objects)

@app.route('/update_permanent_object', methods=['POST'])
def update_permanent_object():
    try:
        obj_id = request.form.get('obj_id')
        name = request.form.get('name')
        width = float(request.form.get('width', 0))
        height = float(request.form.get('height', 0))
        x = float(request.form.get('x', 0))
        y = float(request.form.get('y', 0))
        
        from gallery.models.permanent_object import PermanentObject
        obj = PermanentObject.query.get_or_404(obj_id)
        obj.name = name
        obj.width = width
        obj.height = height
        obj.x = x
        obj.y = y
        
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
    from gallery.models.wall_line import SingleLine as WallLine
    current_wall = get_current_wall()
    
    # Get all artworks
    all_artwork = Artwork.query.all()
    
    # Get only artworks placed on current wall
    current_wall_artwork = Artwork.query.filter_by(wall_id=current_wall.id).all() if current_wall else []
    
    # Get unplaced artworks (wall_id is None or not current wall)
    unplaced_artwork = [a for a in all_artwork if a.wall_id != current_wall.id] if current_wall else all_artwork
    
    wall_lines = WallLine.query.filter_by(wall_id=current_wall.id).all() if current_wall else []
    
    return render_template(
        'editor.html',
        current_wall=current_wall.to_dict() if current_wall else None,
        all_artwork=[a.to_dict() for a in all_artwork],  # For complete list
        current_wall_artwork=[a.to_dict() for a in current_wall_artwork],  # Artworks on wall
        unplaced_artwork=[a.to_dict() for a in unplaced_artwork],  # Artworks not on wall
        wall_lines=[l.to_dict() for l in wall_lines]
    )

@app.route('/update_artwork_position/<int:artwork_id>', methods=['POST'])
def update_artwork_position(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    data = request.get_json()
    
    # Update all relevant fields
    artwork.x_position = data.get('x_position')
    artwork.y_position = data.get('y_position')
    artwork.wall_id = data.get('wall_id')  # This can be None when removing
    
    db.session.commit()
    return jsonify({
        'success': True,
        'artwork': artwork.to_dict()
    })

@app.route('/artwork-manual', methods=['GET', 'POST'])
def artwork_manual():
    wall = get_current_wall()
    
    if request.method == 'POST':
        try:
            # Helper function to safely convert form values to float
            def get_float(form, field, default=0.0):
                value = form.get(field)
                return float(value) if value else default

            # Create new artwork - IMPORTANT: Set wall_id=None
            artwork = Artwork(
                name=request.form.get('name', '').strip(),
                width=get_float(request.form, 'width'),
                height=get_float(request.form, 'height'),
                hanging_point=get_float(request.form, 'hanging'),
                medium=request.form.get('medium', '').strip(),
                depth=get_float(request.form, 'depth'),
                price=get_float(request.form, 'price'),
                nfs=bool(request.form.get('nfs')),
                wall_id=None  # This is the key change - don't assign to wall immediately
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
            app.logger.info(f"Created artwork: {artwork.id}, wall_id: {artwork.wall_id}")
            
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
    # Add save logic
    return redirect(url_for('select_wall_space'))

oauth = OAuth(app)

@app.route('/login')
def login():
    redirect_uri = os.environ.get("AUTHENTIK_REDIRECT_URI", url_for('auth_callback', _external=True))
    return authentik.authorize_redirect(redirect_uri)

authentik = oauth.register(
    name='authentik',
    client_id=os.environ.get("AUTHENTIK_CLIENT_ID", "CLIENT_ID"),
    client_secret=os.environ.get("AUTHENTIK_CLIENT_SECRET", "CLIENT_SECRET"),
    access_token_url=os.environ.get("AUTHENTIK_TOKEN_URL", "https://auth.example.com/application/o/token/"),
    server_metadata_url=os.environ.get("AUTHENTIK_METADATA_URL", "https://auth.example.com/application/o/application-slug/.well-known/openid-configuration"),
    authorize_url=os.environ.get("AUTHENTIK_AUTHORIZE_URL", "https://auth.example.com/application/o/authorize/"),
    client_kwargs={
        'scope': os.environ.get("AUTHENTIK_SCOPE", "openid email profile"),
    },
)

@app.route('/auth/callback')
def auth_callback():
    token = authentik.authorize_access_token()
    userinfo = authentik.userinfo()
    session['user'] = userinfo
    return redirect('/')

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")  # Default to 0.0.0.0
    port = int(os.environ.get("HOST_PORT", 8080))  # Default to 8080
    app.run(debug=True, host=host, port=port)