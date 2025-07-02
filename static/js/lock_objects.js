import { CollisionDetector } from './modules/CollisionDetector.js';
import { MeasurementManager } from './modules/MeasurementManager.js';

const canvas = document.getElementById('wall-canvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('canvas-container');
const objectsLayer = document.getElementById('canvas-objects-layer');

// Initialize MeasurementManager
const measurementManager = new MeasurementManager(container);
const collisionDetector = new CollisionDetector();

// Set canvas dimensions
function resizeCanvas() {
    const scale = getScale();
    
    canvas.width = window.wallData.width * scale;
    canvas.height = window.wallData.height * scale;
    
    drawWall();
    renderObjects();
    updateDimensionLabels(scale);
}

function getScale() {
    const wallSpace = document.querySelector('.wall-space');
    const availableWidth = wallSpace.clientWidth - 40;
    const availableHeight = wallSpace.clientHeight - 40;
    
    const scaleX = availableWidth / window.wallData.width;
    const scaleY = availableHeight / window.wallData.height;
    
    return Math.min(scaleX, scaleY);
}

// Draw the wall background
function drawWall() {
    ctx.fillStyle = window.wallData.color || '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    const gridSize = 12;
    const scale = canvas.width / window.wallData.width;
    
    // Vertical lines
    for (let x = 0; x <= window.wallData.width; x += gridSize) {
        const xPos = x * scale;
        ctx.beginPath();
        ctx.moveTo(xPos, 0);
        ctx.lineTo(xPos, canvas.height);
        ctx.stroke();
    }
    
    // Horizontal lines
    for (let y = 0; y <= window.wallData.height; y += gridSize) {
        const yPos = y * scale;
        ctx.beginPath();
        ctx.moveTo(0, yPos);
        ctx.lineTo(canvas.width, yPos);
        ctx.stroke();
    }
}

// Render all objects on the canvas
function renderObjects() {
    objectsLayer.innerHTML = '';
    const scale = getScale();
    
    window.wallData.permanentObjects.forEach(obj => {
        const div = document.createElement('div');
        div.className = 'canvas-object';
        div.id = `object-${obj.id}`;
        
        // Y is measured from the floor up
        div.style.left = `${obj.x * scale}px`;
        div.style.top = `${(window.wallData.height - obj.y - obj.height) * scale}px`;
        div.style.width = `${obj.width * scale}px`;
        div.style.height = `${obj.height * scale}px`;
        div.setAttribute('data-id', obj.id);
        div.setAttribute('data-x', obj.x);
        div.setAttribute('data-y', obj.y);
        div.setAttribute('data-width', obj.width);
        div.setAttribute('data-height', obj.height);
        
        // Add content to the object
        div.innerHTML = `
            <div class="object-content">
                <div class="object-name">${obj.name}</div>
                ${obj.image_path ? `<img src="${obj.image_path}" class="object-image">` : ''}
            </div>
        `;
        
        if (collisionDetector.checkCollisions(obj, window.wallData.permanentObjects)) {
            div.classList.add('collision-highlight');
        }
        
        objectsLayer.appendChild(div);
    });
    
    makeObjectsDraggable();
}

function updateDimensionLabels(scale) {
    // Remove existing labels if any
    document.querySelectorAll('.dimension-label').forEach(el => el.remove());

    // Create width label
    const widthLabel = document.createElement('div');
    widthLabel.className = 'dimension-label width-label';
    widthLabel.textContent = `${window.wallData.width.toFixed(1)} in`;
    container.appendChild(widthLabel);

    // Create height label
    const heightLabel = document.createElement('div');
    heightLabel.className = 'dimension-label height-label';
    heightLabel.textContent = `${window.wallData.height.toFixed(1)} in`;
    container.appendChild(heightLabel);
}

// Make objects draggable with measurement lines
function makeObjectsDraggable() {
    const scale = getScale();
    
    interact('.canvas-object').draggable({
        inertia: true,
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: 'parent',
                endOnly: true
            })
        ],
        listeners: {
            start(event) {
                event.target.classList.add('dragging');
                measurementManager.clear();
            },
            move(event) {
                const target = event.target;
                const width = parseFloat(target.getAttribute('data-width'));
                const height = parseFloat(target.getAttribute('data-height'));
                const scale = getScale();

                // Get previous wall coordinates (inches from left, inches from floor)
                let prevX = parseFloat(target.getAttribute('data-x'));
                let prevY = parseFloat(target.getAttribute('data-y'));

                // Apply drag delta (convert pixels to inches)
                let newX = prevX + event.dx / scale;
                // CORRECT: Subtract dy because screen Y increases downward but wall Y increases upward
                let newY = prevY - event.dy / scale;

                // Constrain within wall bounds
                const constrainedX = Math.max(0, Math.min(window.wallData.width - width, newX));
                const constrainedY = Math.max(0, Math.min(window.wallData.height - height, newY));

                // Update DOM position (convert back to screen coordinates)
                target.style.left = `${constrainedX * scale}px`;
                // CORRECT: Convert wall Y (0=floor) to screen Y (0=top)
                target.style.top = `${(window.wallData.height - constrainedY - height) * scale}px`;
                
                // Update data attributes (in wall coordinates)
                target.setAttribute('data-x', constrainedX);
                target.setAttribute('data-y', constrainedY);

                // Draw measurement lines
                measurementManager.drawMeasurements(
                    constrainedX,
                    constrainedY,
                    width,
                    height,
                    window.wallData.width,
                    window.wallData.height,
                    scale
                );

                // Check for collisions
                const obj = {
                    id: target.getAttribute('data-id'),
                    x: constrainedX,
                    y: constrainedY,
                    width: width,
                    height: height
                };

                if (collisionDetector.checkCollisions(obj, window.wallData.permanentObjects)) {
                    target.classList.add('collision-highlight');
                    document.getElementById('collision-indicator').classList.remove('d-none');
                } else {
                    target.classList.remove('collision-highlight');
                    document.getElementById('collision-indicator').classList.add('d-none');
                }
            },
            end(event) {
                const target = event.target;
                const id = target.getAttribute('data-id');
                const x = parseFloat(target.getAttribute('data-x'));
                const y = parseFloat(target.getAttribute('data-y'));

                // Update the object in our local data immediately
                const objIndex = window.wallData.permanentObjects.findIndex(o => o.id == id);
                if (objIndex !== -1) {
                    window.wallData.permanentObjects[objIndex].x = x;
                    window.wallData.permanentObjects[objIndex].y = y;
                }

                // Save position to database
                updateObjectPosition(id, x, y);

                target.classList.remove('dragging');
                measurementManager.clear();
            }
        }
    });
}

function updateObjectPosition(objId, x, y) {
    const url = `${window.urls.updatePosition}${objId}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({ x, y })
    })
    .then(response => {
        if (!response.ok) {
            console.error('Error updating position:', response.statusText);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // The local data is already updated in the drag end handler.
            // const objIndex = window.wallData.permanentObjects.findIndex(o => o.id == objId);
            // if (objIndex !== -1) {
            //     window.wallData.permanentObjects[objIndex].x = x;
            //     window.wallData.permanentObjects[objIndex].y = y;
            // }
        }
    })
    .catch(error => console.error('Error updating position:', error));
}

// Handle sidebar toggle
document.getElementById('toggleSidebar').addEventListener('click', function() {
    const leftPanel = document.getElementById('leftPanel');
    const icon = this.querySelector('i');
    
    leftPanel.classList.toggle('collapsed');
    icon.classList.toggle('bi-chevron-left');
    icon.classList.toggle('bi-chevron-right');
});

// Handle object edit/delete buttons
document.addEventListener('click', function(e) {
    if (e.target.closest('.edit-btn')) {
        const btn = e.target.closest('.edit-btn');
        const objId = btn.getAttribute('data-id');
        const obj = window.wallData.permanentObjects.find(o => o.id == objId);
        
        if (obj) {
            const modal = new bootstrap.Modal(document.getElementById('editItemModal'));
            const form = document.getElementById('editItemForm');
            
            // Populate form
            document.getElementById('editObjId').value = obj.id;
            form.querySelector('[name="name"]').value = obj.name;
            form.querySelector('[name="width"]').value = obj.width;
            form.querySelector('[name="height"]').value = obj.height;
            form.querySelector('[name="x"]').value = obj.x;
            form.querySelector('[name="y"]').value = obj.y;
            
            modal.show();
        }
    }
    
    if (e.target.closest('.delete-btn')) {
        if (confirm('Are you sure you want to delete this fixture?')) {
            const btn = e.target.closest('.delete-btn');
            const objId = btn.getAttribute('data-id');
            
            fetch(`${window.urls.deleteObject.replace(/0$/, objId)}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken
                }
            })
            .then(response => {
                if (response.ok) {
                    // Remove from DOM and data
                    btn.closest('.list-group-item').remove();
                    window.wallData.permanentObjects = window.wallData.permanentObjects.filter(o => o.id != objId);
                    renderObjects();
                } else {
                    console.error('Error deleting object:', response.statusText);
                }
            })
            .catch(error => console.error('Error deleting object:', error));
        }
    }
});

// Initialize on load/resize
window.addEventListener('load', () => {
    resizeCanvas();
    makeObjectsDraggable();
});

window.addEventListener('resize', () => {
    resizeCanvas();
});

// Add ResizeObserver for responsive resizing
const resizeObserver = new ResizeObserver(() => {
    resizeCanvas();
});

const wallSpace = document.querySelector('.wall-space');
if (wallSpace) {
    resizeObserver.observe(wallSpace);
}

window.addEventListener('beforeunload', () => {
    resizeObserver.disconnect();
});