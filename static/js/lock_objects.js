// Initialize canvas and wall dimensions
const canvas = document.getElementById('wall-canvas');
const ctx = canvas.getContext('2d');
const wallWidth = window.wallWidth;
const wallHeight = window.wallHeight;
const wallColor = window.wallColor;

// Set canvas dimensions
function resizeCanvas() {
    const container = canvas.parentElement;
    const scale = Math.min(
        container.clientWidth / wallWidth,
        container.clientHeight / wallHeight
    );
    
    canvas.width = wallWidth * scale;
    canvas.height = wallHeight * scale;
    drawWall();
    drawObjects();
    updateDimensionLabels();
}

// Draw the wall background
function drawWall() {
    ctx.fillStyle = wallColor || '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.strokeStyle = '#cccccc';
    ctx.lineWidth = 1;
    const gridSize = 12;
    const scale = canvas.width / wallWidth;
    
    for (let x = 0; x <= wallWidth; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x * scale, 0);
        ctx.lineTo(x * scale, canvas.height);
        ctx.stroke();
    }
    for (let y = 0; y <= wallHeight; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y * scale);
        ctx.lineTo(canvas.width, y * scale);
        ctx.stroke();
    }
}

// Draw all permanent objects (names and rectangles)
// You may need to fetch object data via AJAX or embed as JSON in a <script> tag if you want to avoid Jinja here.

function drawObjects() {
    // This function should be updated to use JS data, not Jinja.
    // For now, you can leave it empty or implement AJAX fetching if needed.
}

// Position canvas objects based on data attributes
function positionCanvasObjects() {
    const scale = canvas.width / wallWidth;
    document.querySelectorAll('.canvas-object').forEach(div => {
        const x = parseFloat(div.getAttribute('data-x')) * scale;
        const y = parseFloat(div.getAttribute('data-y')) * scale;
        const width = parseFloat(div.getAttribute('data-width')) * scale;
        const height = parseFloat(div.getAttribute('data-height')) * scale;
        div.style.left = x + 'px';
        div.style.top = y + 'px';
        div.style.width = width + 'px';
        div.style.height = height + 'px';
        div.style.lineHeight = height + 'px';
        div.style.textAlign = 'center';
    });
}

// Make objects draggable
function makeObjectsDraggable() {
    const scale = canvas.width / wallWidth;
    interact('.canvas-object').draggable({
        inertia: true,
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: 'parent',
                endOnly: true
            })
        ],
        listeners: {
            move: function(event) {
                const target = event.target;
                let x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx / scale;
                let y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy / scale;
                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);
                positionCanvasObjects();
                updateObjectPosition(target.id.replace('object-', ''), x, y);
            }
        }
    });
}

function updateObjectPosition(objId, x, y) {
    fetch(`/update_object_position/${objId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({ x: x, y: y })
    });
}

// Collapsible menu
document.querySelectorAll('.collapsible').forEach(button => {
    button.addEventListener('click', () => {
        button.classList.toggle('active');
        const content = button.nextElementSibling;
        content.style.display = content.style.display === 'block' ? 'none' : 'block';
    });
});

// Save button
document.getElementById('save-btn').addEventListener('click', () => {
    const hasCollisions = false; // Replace with actual collision detection
    if (hasCollisions) {
        const collisionModal = new bootstrap.Modal(document.getElementById('collisionModal'));
        collisionModal.show();
    } else {
        window.location.href = window.editorUrl;
    }
});

// Continue anyway button
document.getElementById('continueAnywayBtn').addEventListener('click', () => {
    window.location.href = window.editorUrl;
});

// Edit buttons
document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const itemId = btn.getAttribute('data-id');
        const editModal = new bootstrap.Modal(document.getElementById('editItemModal'));
        editModal.show();
    });
});

// Delete buttons
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const itemId = btn.getAttribute('data-id');
        if (confirm('Are you sure you want to delete this item?')) {
            fetch(`/delete_permanent_object/${itemId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                }
            }).then(response => {
                if (response.ok) {
                    window.location.reload();
                }
            });
        }
    });
});

function updateDimensionLabels() {
    const widthLabel = document.querySelector('.width-label');
    const heightLabel = document.querySelector('.height-label');
    widthLabel.textContent = `${wallWidth.toFixed(1)} in`;
    heightLabel.textContent = `${wallHeight.toFixed(1)} in`;
    const canvasRect = canvas.getBoundingClientRect();
    const containerRect = canvas.parentElement.getBoundingClientRect();
    widthLabel.style.left = `${canvasRect.left - containerRect.left + canvasRect.width/2}px`;
    widthLabel.style.bottom = `${containerRect.bottom - canvasRect.bottom - 5}px`;
    widthLabel.style.top = '';
    widthLabel.style.right = '';
    widthLabel.style.transform = 'translateX(-50%)';
    heightLabel.style.right = `${containerRect.right - canvasRect.right - 5}px`;
    heightLabel.style.top = `${canvasRect.top - containerRect.top + canvasRect.height/2}px`;
    heightLabel.style.left = '';
    heightLabel.style.bottom = '';
    heightLabel.style.transform = 'translateY(-50%) rotate(-90deg)';
    heightLabel.style.transformOrigin = 'left center';
}

// Initialize on load/resize
window.addEventListener('load', () => {
    resizeCanvas();
    positionCanvasObjects();
    makeObjectsDraggable();
    updateDimensionLabels();
});
window.addEventListener('resize', () => {
    resizeCanvas();
    positionCanvasObjects();
    updateDimensionLabels();
});