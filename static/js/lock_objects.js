// lock_objects.js
const canvas = document.getElementById('wall-canvas');
const ctx = canvas.getContext('2d');
const wallWidth = window.wallData.width;
const wallHeight = window.wallData.height;
const wallColor = window.wallData.color || '#ffffff';
const container = document.querySelector('.canvas-container');
const objectsLayer = document.getElementById('canvas-objects-layer');

// Set canvas dimensions
function resizeCanvas() {
    const scale = getScale();
    
    canvas.width = wallWidth * scale;
    canvas.height = wallHeight * scale;
    container.style.width = `${canvas.width}px`;
    container.style.height = `${canvas.height}px`;
    
    drawWall();
    renderObjects();
    updateDimensionLabels(scale);
}

function getScale() {
    const wallSpace = document.querySelector('.wall-space');
    const availableWidth = wallSpace.clientWidth - 40;
    const availableHeight = wallSpace.clientHeight - 40;
    
    const scaleX = availableWidth / wallWidth;
    const scaleY = availableHeight / wallHeight;
    
    return Math.min(scaleX, scaleY);
}

// Draw the wall background
function drawWall() {
    ctx.fillStyle = wallColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    const gridSize = 12;
    const scale = canvas.width / wallWidth;
    
    // Vertical lines
    for (let x = 0; x <= wallWidth; x += gridSize) {
        const xPos = x * scale;
        ctx.beginPath();
        ctx.moveTo(xPos, 0);
        ctx.lineTo(xPos, canvas.height);
        ctx.stroke();
    }
    
    // Horizontal lines
    for (let y = 0; y <= wallHeight; y += gridSize) {
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
        
        // Y is now measured from the floor up
        div.style.left = `${obj.x * scale}px`;
        div.style.top = `${(wallHeight - obj.y - obj.height) * scale}px`;
        div.style.width = `${obj.width * scale}px`;
        div.style.height = `${obj.height * scale}px`;
        div.textContent = obj.name;
        div.setAttribute('data-id', obj.id);
        div.setAttribute('data-x', obj.x);
        div.setAttribute('data-y', obj.y);
        div.setAttribute('data-width', obj.width);
        div.setAttribute('data-height', obj.height);
        
        if (checkCollisions(obj)) {
            div.style.border = '2px solid red';
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
    widthLabel.textContent = `${wallWidth.toFixed(1)} in`;
    container.appendChild(widthLabel);

    // Create height label
    const heightLabel = document.createElement('div');
    heightLabel.className = 'dimension-label height-label';
    heightLabel.textContent = `${wallHeight.toFixed(1)} in`;
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
                event.target.style.zIndex = '10';
                measurementManager.clearMeasurementLines();
            },
            move(event) {
                const target = event.target;
                const width = parseFloat(target.getAttribute('data-width'));
                const height = parseFloat(target.getAttribute('data-height'));
                
                // Calculate new position in inches
                const newX = parseFloat(target.getAttribute('data-x')) + event.dx / scale;
                // For Y position: subtract from wall height since we're measuring from floor
                const newY = Math.max(0, Math.min(wallHeight - height, 
                    parseFloat(target.getAttribute('data-y')) + event.dy / scale));
                
                // Update position attributes
                target.setAttribute('data-x', newX);
                target.setAttribute('data-y', newY);
                
                // Update visual position (convert to top-left origin for display)
                target.style.left = `${newX * scale}px`;
                target.style.top = `${(wallHeight - newY - height) * scale}px`;
                
                // Draw measurement lines
                measurementManager.drawMeasurementLines(
                    newX, 
                    newY, 
                    width, 
                    height, 
                    wallWidth, 
                    wallHeight, 
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
                    target.style.border = '2px solid red';
                } else {
                    target.style.border = 'none';
                }
            },
            end(event) {
                const target = event.target;
                const id = target.getAttribute('data-id');
                const x = parseFloat(target.getAttribute('data-x'));
                const y = parseFloat(target.getAttribute('data-y'));
                
                // Save position to database
                updateObjectPosition(id, x, y);
                
                target.style.zIndex = '2';
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
    fetch(`${window.urls.updatePosition}/${objId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({ x, y })
    }).catch(error => console.error('Error updating position:', error));
}

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