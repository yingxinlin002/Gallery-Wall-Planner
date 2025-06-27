// lock_objects.js - Updated version
const canvas = document.getElementById('wall-canvas');
const ctx = canvas.getContext('2d');
const container = document.querySelector('.canvas-container');
const objectsLayer = document.getElementById('canvas-objects-layer');

// Measurement Lines Manager
class MeasurementLinesManager {
    constructor(container) {
        this.container = container;
        this.linesContainer = document.createElement('div');
        this.linesContainer.className = 'measurement-lines-container';
        container.appendChild(this.linesContainer);
    }

    drawMeasurementLines(x, y, width, height, wallWidth, wallHeight, scale) {
        this.clearMeasurementLines();
        
        // Convert to canvas coordinates
        const canvasX = x * scale;
        const canvasY = (wallHeight - y - height) * scale;
        const canvasWidth = width * scale;
        const canvasHeight = height * scale;
        
        // Left measurement
        this.createMeasurementLine(
            0, canvasY + canvasHeight/2, 
            canvasX, canvasY + canvasHeight/2,
            `${x.toFixed(1)} in`
        );
        
        // Right measurement
        this.createMeasurementLine(
            canvasX + canvasWidth, canvasY + canvasHeight/2,
            wallWidth * scale, canvasY + canvasHeight/2,
            `${(wallWidth - x - width).toFixed(1)} in`
        );
        
        // Top measurement (from top of object to top of wall)
        this.createMeasurementLine(
            canvasX + canvasWidth/2, 0,
            canvasX + canvasWidth/2, canvasY,
            `${(wallHeight - y - height).toFixed(1)} in`
        );
        
        // Bottom measurement (from bottom of object to floor)
        this.createMeasurementLine(
            canvasX + canvasWidth/2, canvasY + canvasHeight,
            canvasX + canvasWidth/2, wallHeight * scale,
            `${y.toFixed(1)} in`
        );
    }

    createMeasurementLine(x1, y1, x2, y2, labelText) {
        // Create line element
        const line = document.createElement('div');
        line.className = 'measurement-line';
        
        // Position and size the line
        const left = Math.min(x1, x2);
        const top = Math.min(y1, y2);
        const width = Math.abs(x2 - x1);
        const height = Math.abs(y2 - y1);
        
        line.style.left = `${left}px`;
        line.style.top = `${top}px`;
        line.style.width = `${width}px`;
        line.style.height = `${height}px`;
        
        // Create label
        if (labelText) {
            const label = document.createElement('div');
            label.className = 'measurement-label';
            label.textContent = labelText;
            
            // Position label based on line orientation
            if (height === 0) { // horizontal line
                label.style.left = `${left + width/2 - 20}px`;
                label.style.top = `${top - 25}px`;
            } else { // vertical line
                label.style.left = `${left - 40}px`;
                label.style.top = `${top + height/2 - 10}px`;
            }
            
            this.linesContainer.appendChild(label);
        }
        
        this.linesContainer.appendChild(line);
    }

    clearMeasurementLines() {
        this.linesContainer.innerHTML = '';
    }
}

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
        
        if (checkCollisions(obj)) {
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
    const measurementManager = new MeasurementLinesManager(container);
    
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
                measurementManager.clearMeasurementLines();
            },
            move(event) {
                const target = event.target;
                const width = parseFloat(target.getAttribute('data-width'));
                const height = parseFloat(target.getAttribute('data-height'));
                
                // Calculate new position in inches
                const newX = parseFloat(target.getAttribute('data-x')) + event.dx / scale;
                const newY = Math.max(0, Math.min(
                    window.wallData.height - height,
                    parseFloat(target.getAttribute('data-y')) + event.dy / scale
                ));
                
                // Update position attributes
                target.setAttribute('data-x', newX);
                target.setAttribute('data-y', newY);
                
                // Update visual position (convert to top-left origin for display)
                target.style.left = `${newX * scale}px`;
                target.style.top = `${(window.wallData.height - newY - height) * scale}px`;
                
                // Draw measurement lines
                measurementManager.drawMeasurementLines(
                    newX, 
                    newY, 
                    width, 
                    height, 
                    window.wallData.width, 
                    window.wallData.height, 
                    scale
                );
                
                // Check for collisions
                const obj = {
                    id: target.getAttribute('data-id'),
                    x: newX,
                    y: newY,
                    width: width,
                    height: height
                };
                
                if (checkCollisions(obj)) {
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
                
                // Save position to database
                updateObjectPosition(id, x, y);
                
                target.classList.remove('dragging');
                measurementManager.clearMeasurementLines();
            }
        }
    });
}

function checkCollisions(obj) {
    // Check against other objects
    const objects = window.wallData.permanentObjects;
    for (const other of objects) {
        if (other.id != obj.id && checkRectOverlap(obj, other)) {
            return true;
        }
    }
    
    return false;
}

function checkRectOverlap(a, b) {
    return a.x < b.x + b.width &&
           a.x + a.width > b.x &&
           a.y < b.y + b.height &&
           a.y + a.height > b.y;
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
            // Update the object in our local data
            const objIndex = window.wallData.permanentObjects.findIndex(o => o.id == objId);
            if (objIndex !== -1) {
                window.wallData.permanentObjects[objIndex].x = x;
                window.wallData.permanentObjects[objIndex].y = y;
            }
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