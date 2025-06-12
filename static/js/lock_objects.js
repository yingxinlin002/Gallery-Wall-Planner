// lock_objects.js
const canvas = document.getElementById('wall-canvas');
const ctx = canvas.getContext('2d');
const wallWidth = window.wallData.width;
const wallHeight = window.wallData.height;
const wallColor = window.wallData.color || '#ffffff';

// Measurement lines manager
const measurementManager = new MeasurementLinesManager(document.querySelector('.canvas-container'));

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

// Draw all permanent objects
function drawObjects() {
    const scale = canvas.width / wallWidth;
    window.wallData.permanentObjects.forEach(obj => {
        drawObject(obj, scale);
    });
}

function drawObject(obj, scale) {
    const yPos = wallHeight - obj.y - obj.height; // Convert to bottom-left origin
    
    ctx.fillStyle = 'rgba(200, 200, 255, 0.7)';
    ctx.strokeStyle = '#0000aa';
    ctx.lineWidth = 2;
    
    ctx.beginPath();
    ctx.rect(
        obj.x * scale,
        yPos * scale,
        obj.width * scale,
        obj.height * scale
    );
    ctx.fill();
    ctx.stroke();
    
    // Draw object name
    ctx.fillStyle = '#000';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(
        obj.name,
        (obj.x + obj.width/2) * scale,
        (yPos + obj.height/2) * scale
    );
}

// Make objects draggable with measurement lines
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
                // Subtract dy to account for bottom-left origin
                const newY = Math.max(0, Math.min(wallHeight - height, 
                    parseFloat(target.getAttribute('data-y')) - event.dy / scale));
                
                // Update position attributes
                target.setAttribute('data-x', newX);
                target.setAttribute('data-y', newY);
                
                // Update visual position (convert to bottom-left origin)
                const canvasY = wallHeight - newY - height;
                target.style.left = `${newX * scale}px`;
                target.style.top = `${canvasY * scale}px`;
                
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
                if (checkCollisions(target)) {
                    target.classList.add('collision-highlight');
                } else {
                    target.classList.remove('collision-highlight');
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

function checkCollisions(target) {
    const id = target.getAttribute('data-id');
    const x = parseFloat(target.getAttribute('data-x'));
    const y = parseFloat(target.getAttribute('data-y'));
    const width = parseFloat(target.getAttribute('data-width'));
    const height = parseFloat(target.getAttribute('data-height'));
    
    // Check against other objects
    const objects = window.wallData.permanentObjects;
    for (const obj of objects) {
        if (obj.id != id && checkRectOverlap(
            {x, y, width, height},
            obj
        )) {
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

function updateDimensionLabels() {
    const widthLabel = document.querySelector('.width-label');
    const heightLabel = document.querySelector('.height-label');
    widthLabel.textContent = `${wallWidth.toFixed(1)} in`;
    heightLabel.textContent = `${wallHeight.toFixed(1)} in`;
    
    const canvasRect = canvas.getBoundingClientRect();
    const containerRect = canvas.parentElement.getBoundingClientRect();
    
    widthLabel.style.left = `${canvasRect.left - containerRect.left + canvasRect.width/2}px`;
    widthLabel.style.bottom = `${containerRect.bottom - canvasRect.bottom - 5}px`;
    widthLabel.style.transform = 'translateX(-50%)';
    
    heightLabel.style.right = `${containerRect.right - canvasRect.right - 5}px`;
    heightLabel.style.top = `${canvasRect.top - containerRect.top + canvasRect.height/2}px`;
    heightLabel.style.transform = 'translateY(-50%) rotate(-90deg)';
    heightLabel.style.transformOrigin = 'left center';
}

// Initialize on load/resize
window.addEventListener('load', () => {
    resizeCanvas();
    makeObjectsDraggable();
    updateDimensionLabels();
});

window.addEventListener('resize', () => {
    resizeCanvas();
    updateDimensionLabels();
});