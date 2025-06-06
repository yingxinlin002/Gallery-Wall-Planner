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
from sqlalchemy import create_engine
from config import load_config
from gallery.models.user import User
from gallery.models.base import db
from authlib.integrations.base_client.errors import MismatchingStateError
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret")
def validate_mysql_config(conf):
    required = ['user', 'password', 'host', 'db']
    missing = [k for k in required if not conf.get(k)]
    if missing:
        raise EnvironmentError(f"Missing required MySQL config keys: {', '.join(missing)}")

def make_mysql_url(conf, hide_password=True):
    password = '***' if hide_password else conf['password']
    port = conf.get('port', '3306')  # default fallback
    return f"mysql+pymysql://{conf['user']}:{password}@{conf['host']}:{port}/{conf['db']}"

config = load_config()
auth_config = config['authentik']
db_config = config['database']

if db_config['type'] == 'mysql':
    validate_mysql_config(db_config)
    db_url = make_mysql_url(db_config, hide_password=False)
    safe_url = make_mysql_url(db_config, hide_password=True)

elif db_config['type'] == 'sqlite':
    db_url = f"sqlite:///{db_config.get('path', './gallery.db')}"
    safe_url = db_url

else:
    raise ValueError("Unsupported database type")

engine = create_engine(db_url)
print(f"Using {db_config['type'].upper()} database: {safe_url}")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)
csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()

def load_projects_for_user(user_id):
    from gallery.models.exhibit import Gallery
    return Gallery.query.filter_by(user_id=user_id).all()

def load_temp_projects_for_guest(guest_id):
    # Placeholder until guest save logic is implemented
    return []

def get_current_wall():
    wall_id = session.get("current_wall_id")
    if wall_id is not None:
        wall = db.session.get(Wall, wall_id)
        return wall
    # Optionally, return the first wall if no wall is selected
    wall = Wall.query.first()
    return wall

@app.route("/", methods=["GET"])
def landing_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template("landing_page.html")

@app.route("/home", methods=["GET"])
def home():
    user = session.get('user')
    user_id = session.get('user_id')

    if user_id:
        # Logged in user - fetch saved projects from DB
        projects = load_projects_for_user(user_id)
    else:
        # Guest user - optionally assign temp guest ID to session for temp saves
        if 'guest_id' not in session:
            session['guest_id'] = str(uuid.uuid4())
        guest_id = session['guest_id']
        # Load temp data from session or a temporary store keyed by guest_id
        projects = load_temp_projects_for_guest(guest_id)
    
    last_project_exists = bool(projects)
    return render_template("home.html", last_project_exists=last_project_exists, user=user)

@app.route('/guest')
def guest():
    session.clear()
    session['user'] = {'name': 'Guest'}
    session['user_id'] = None 
    return redirect(url_for('home'))


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
        gallery_name = request.form.get('exhibit_name', '').strip()
        user_id = session.get('user_id')

        if not gallery_name:
            flash("Exhibit name is required.")
            return redirect(url_for('new_gallery'))

        # Allow guests to create galleries (user_id will be None)
        if not user_id:
            flash("You are creating an exhibit as a guest. Log in to save your work.", "info")

        from gallery.models.exhibit import Gallery
        gallery = Gallery(name=gallery_name, user_id=user_id)
        db.session.add(gallery)
        db.session.commit()

        session['current_gallery_id'] = gallery.id
        return redirect(url_for('load_exhibit'))

    return render_template('new_exhibit.html')

@app.route('/load-exhibit', methods=['GET'])
def load_exhibit():
    # You can fetch the current exhibit or all exhibits for the guest
    from gallery.models.exhibit import Gallery
    gallery_id = session.get('current_gallery_id')
    gallery = Gallery.query.get(gallery_id) if gallery_id else None
    return render_template('load_exhibit.html', gallery=gallery)

@app.route('/create-wall', methods=['GET', 'POST'])
def create_wall():
    gallery_id = session.get('current_gallery_id')

    if not gallery_id:
        flash("Please create a gallery first.")
        return redirect(url_for('new_gallery'))

    if request.method == 'POST':
        name = request.form.get('wall_name')
        width = float(request.form.get('wall_width'))
        height = float(request.form.get('wall_height'))
        color = request.form.get('wall_color', 'White')

        wall = Wall(name=name, width=width, height=height, color=color, gallery_id=gallery_id)
        db.session.add(wall)
        db.session.commit()

        session['current_wall_id'] = wall.id
        return redirect(url_for('edit_permanent_objects'))  # or whatever next step

    return render_template('create_wall.html')

@app.route('/select-wall-space', methods=['GET', 'POST'])
def select_wall_space():
    gallery_id = session.get('current_gallery_id')

    if not gallery_id:
        flash("Please load a gallery first.")
        return redirect(url_for('load_gallery'))

    if request.method == 'POST':
        selected_wall_id = request.form.get('wall_id')
        wall = Wall.query.filter_by(id=selected_wall_id, gallery_id=gallery_id).first()

        if not wall:
            flash("Wall not found or doesn't belong to this gallery.")
            return redirect(url_for('select_wall_space'))

        session['current_wall_id'] = wall.id
        flash(f"Loaded wall: {wall.name}")
        return redirect(url_for('edit_permanent_objects'))

    walls = Wall.query.filter_by(gallery_id=gallery_id).all()
    current_wall = get_current_wall()  # ✅ Add this
    return render_template('select_wall_space.html', walls=walls, current_wall=current_wall)  # ✅ And pass it in

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

@app.route('/select-wall/<wall_id>')
def select_wall(wall_id):
    session["current_wall_id"] = wall_id
    return redirect(url_for('select_wall_space'))

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
                wall_id=None,  # leave at None for now
                user_id=session.get('user_id')
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

# @app.route("/load", methods=["POST"])
# def load_wall():
#     return redirect(url_for('select_wall_space'))

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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing_page'))

authentik = oauth.register(
    name='authentik',
    client_id=auth_config['client_id'],
    client_secret=auth_config['client_secret'],
    access_token_url=auth_config['token_url'],
    server_metadata_url=auth_config['metadata_url'],
    authorize_url=auth_config['authorize_url'],
    client_kwargs={
        'scope': auth_config['scope'],
    },
)

@app.route('/auth/callback')
def auth_callback():
    try:
        token = authentik.authorize_access_token()
    except MismatchingStateError:
        return "Error: State mismatch. Please try logging in again.", 400

    userinfo = authentik.userinfo()
    sub = userinfo.get('sub')
    if not sub:
        return "Error: Missing user identifier in token.", 400

    # Check if user already exists
    user = User.query.filter_by(sub=sub).first()

    if not user:
        # Create new user record
        user = User(
            sub=sub,
            email=userinfo.get('email'),
            name=userinfo.get('name'),
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Optional: update existing user info
        user.email = userinfo.get('email')
        user.name = userinfo.get('name')
        db.session.commit()

    # Store internal DB user id in session for app use
    session['user_id'] = user.id
    session['user'] = userinfo  # if you want full user info in session

    return redirect(url_for('home'))

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")  # Default to 0.0.0.0
    port = int(os.environ.get("HOST_PORT", 8080))  # Default to 8080
    app.run(debug=True, host=host, port=port)