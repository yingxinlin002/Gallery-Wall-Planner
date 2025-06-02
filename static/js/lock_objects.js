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

    // Set all canvas objects to z-index 2
    document.querySelectorAll('.canvas-object').forEach(obj => {
        obj.style.zIndex = '2';
    });

    interact('.canvas-object').draggable({
        inertia: true,
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: 'parent',
                endOnly: true
            })
        ],
        listeners: {
            start: function(event) {
                measurementManager.clearMeasurementLines();
                // Bring the dragged element to the front
                event.target.style.zIndex = '3';
            },
            move: function(event) {
                const target = event.target;
                let x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx / scale;
                let y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy / scale;
                const width = parseFloat(target.getAttribute('data-width'));
                const height = parseFloat(target.getAttribute('data-height'));

                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);
                positionCanvasObjects();
                updateObjectPosition(target.id.replace('object-', ''), x, y);

                measurementManager.drawMeasurementLines(x, y, width, height, scale);
            },
            end: function(event) {
                measurementManager.clearMeasurementLines();
                // Reset z-index after dragging
                event.target.style.zIndex = '2';
            }
        }
    });
}

function updateObjectPosition(objId, x, y) {
    fetch(`${window.urls.updatePosition}/${objId}`, {
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
    const content = button.nextElementSibling;
    const chevron = button.querySelector('.bi');

    // If already active, ensure content is visible and chevron is up
    if (button.classList.contains('active')) {
        content.style.display = 'block';
        if (chevron) {
            chevron.classList.remove('bi-chevron-down');
            chevron.classList.add('bi-chevron-up');
        }
    }

    // Always add the click event to allow toggling
    button.addEventListener('click', () => {
        button.classList.toggle('active');
        if (content.style.display === 'block') {
            content.style.display = 'none';
            if (chevron) {
                chevron.classList.remove('bi-chevron-up');
                chevron.classList.add('bi-chevron-down');
            }
        } else {
            content.style.display = 'block';
            if (chevron) {
                chevron.classList.remove('bi-chevron-down');
                chevron.classList.add('bi-chevron-up');
            }
        }
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

// Measurement Lines Manager class
class MeasurementLinesManager {
    constructor(canvasContainer) {
        this.canvasContainer = canvasContainer;
        this.measurementLines = [];
        this.measurementTexts = [];
        this.container = null;
    }

    clearMeasurementLines() {
        this.measurementLines.forEach(line => line.remove());
        this.measurementTexts.forEach(text => text.remove());
        this.measurementLines = [];
        this.measurementTexts = [];
        if (this.container) {
            this.container.remove();
            this.container = null;
        }
    }

    drawMeasurementLines(x, y, width, height, scale) {
        this.clearMeasurementLines();

        // Create container for measurement elements
        this.container = document.createElement('div');
        this.container.style.position = 'absolute';
        this.container.style.top = '0';
        this.container.style.left = '0';
        this.container.style.width = '100%';
        this.container.style.height = '100%';
        this.container.style.pointerEvents = 'none';
        this.container.style.zIndex = '1'; // Lower than draggable objects
        this.canvasContainer.appendChild(this.container);

        // Calculate positions
        const left = x * scale;
        const top = y * scale;
        const right = (x + width) * scale;
        const bottom = (y + height) * scale;

        // Left measurement line
        const leftLine = this.createLine(left, top, left, 0, 'left', 'vertical');
        const leftText = this.createText(left / 2, top / 2, `${x.toFixed(1)}"`, 'vertical');

        // Right measurement line
        const rightLine = this.createLine(right, top, right, 0, 'right', 'vertical');
        const rightText = this.createText((right + canvas.width) / 2, top / 2, `${(wallWidth - x - width).toFixed(1)}"`, 'vertical');

        // Top measurement line
        const topLine = this.createLine(left, top, 0, top, 'top', 'horizontal');
        const topText = this.createText(left / 2, top / 2, `${(wallHeight - y - height).toFixed(1)}"`, 'horizontal');

        // Bottom measurement line
        const bottomLine = this.createLine(left, bottom, 0, bottom, 'bottom', 'horizontal');
        const bottomText = this.createText(left / 2, (bottom + canvas.height) / 2, `${y.toFixed(1)}"`, 'horizontal');

        this.measurementLines.push(leftLine, rightLine, topLine, bottomLine);
        this.measurementTexts.push(leftText, rightText, topText, bottomText);
    }

    createLine(x1, y1, x2, y2, position, orientation) {
        const line = document.createElement('div');
        line.style.position = 'absolute';
        line.style.backgroundColor = 'rgba(100, 100, 100, 0.5)';

        if (orientation === 'vertical') {
            line.style.left = `${x1}px`;
            line.style.top = `${y2}px`;
            line.style.width = '1px';
            line.style.height = `${y1 - y2}px`;
            line.style.borderLeft = '1px dashed gray';
        } else {
            line.style.left = `${x2}px`;
            line.style.top = `${y1}px`;
            line.style.width = `${x1 - x2}px`;
            line.style.height = '1px';
            line.style.borderTop = '1px dashed gray';
        }

        this.container.appendChild(line);
        return line;
    }

    createText(x, y, text, orientation) {
        const textEl = document.createElement('div');
        textEl.style.position = 'absolute';
        textEl.style.left = `${x}px`;
        textEl.style.top = `${y}px`;
        textEl.style.color = 'black';
        textEl.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
        textEl.style.padding = '2px 5px';
        textEl.style.borderRadius = '3px';
        textEl.style.fontSize = '12px';
        textEl.textContent = text;

        if (orientation === 'vertical') {
            textEl.style.transform = 'translate(-50%, -50%)';
        } else {
            textEl.style.transform = 'translate(-50%, -50%) rotate(-90deg)';
        }

        this.container.appendChild(textEl);
        return textEl;
    }
}

// Initialize measurement lines manager
const measurementManager = new MeasurementLinesManager(document.querySelector('.canvas-container'));

// Initialize on load/resize
window.addEventListener('load', () => {
    resizeCanvas();
    positionCanvasObjects();

    // Set z-index for proper layering
    document.getElementById('canvas-objects-layer').style.zIndex = '1';
    document.querySelectorAll('.canvas-object').forEach(obj => {
        obj.style.zIndex = '2';
    });

    makeObjectsDraggable();
    updateDimensionLabels();
    checkCollisions();
    setInterval(checkCollisions, 500);
});
window.addEventListener('resize', () => {
    resizeCanvas();
    positionCanvasObjects();
    updateDimensionLabels();
});

