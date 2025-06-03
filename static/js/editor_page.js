import { EvenSpacing } from './even_spacing.js';
import { MeasurementLinesManager } from './measurement_lines_manager.js';

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar collapse
    document.getElementById('toggleSidebarBtn').addEventListener('click', function() {
        document.getElementById('sidebar').classList.toggle('collapsed');
    });

    // Add artwork to canvas
    document.querySelectorAll('.add-artwork-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const artworkId = this.getAttribute('data-artwork-id');
            const artwork = window.unplacedArtworkData.find(a => a.id == artworkId);
            if (artwork) {
                addArtworkToCanvas(artwork);
            }
        });
    });

    // Create artwork form
    document.getElementById('createArtworkForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        fetch('/artwork-manual', {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Add to imported list
                addArtworkToImportedList(data.artwork);
                window.unplacedArtworkData.push(data.artwork);
                document.getElementById('createArtworkForm').reset();
                bootstrap.Modal.getInstance(document.getElementById('createArtworkModal')).hide();
            } else {
                alert(data.error || 'Error creating artwork');
            }
        });
    });

    // Canvas logic
    const canvas = document.getElementById('wall-canvas');
    const layer = document.getElementById('canvas-artwork-layer');
    const wall = window.currentWallData;
    let placedArtworks = window.currentWallArtworkData || [];

    // Draw wall
    function drawWall() {
        const ctx = canvas.getContext('2d');
        const scale = getScale();
        canvas.width = wall.width * scale;
        canvas.height = wall.height * scale;
        ctx.fillStyle = wall.color || '#fff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 1;
        for (let x = 0; x <= wall.width; x += 12) {
            ctx.beginPath();
            ctx.moveTo(x * scale, 0);
            ctx.lineTo(x * scale, canvas.height);
            ctx.stroke();
        }
        for (let y = 0; y <= wall.height; y += 12) {
            ctx.beginPath();
            ctx.moveTo(0, y * scale);
            ctx.lineTo(canvas.width, y * scale);
            ctx.stroke();
        }
    }

    function getScale() {
        const container = document.getElementById('canvas-container');
        return Math.min(
            container.clientWidth / wall.width,
            container.clientHeight / wall.height
        );
    }

    function renderArtworks() {
        layer.innerHTML = '';
        const scale = getScale();
        placedArtworks.forEach(artwork => {
            const div = document.createElement('div');
            div.className = 'canvas-artwork';
            div.style.left = (artwork.x_position * scale) + 'px';
            div.style.top = (artwork.y_position * scale) + 'px';
            div.style.width = (artwork.width * scale) + 'px';
            div.style.height = (artwork.height * scale) + 'px';
            div.textContent = artwork.name;
            div.setAttribute('data-id', artwork.id);
            layer.appendChild(div);

            // Make draggable
            interact(div).draggable({
                inertia: true,
                modifiers: [
                    interact.modifiers.restrictRect({
                        restriction: 'parent',
                        endOnly: true
                    })
                ],
                listeners: {
                    move(event) {
                        let x = (parseFloat(div.style.left) || 0) + event.dx;
                        let y = (parseFloat(div.style.top) || 0) + event.dy;
                        div.style.left = x + 'px';
                        div.style.top = y + 'px';
                    },
                    end(event) {
                        // Save new position to DB
                        const scale = getScale();
                        const x = parseFloat(div.style.left) / scale;
                        const y = parseFloat(div.style.top) / scale;
                        const id = div.getAttribute('data-id');
                        fetch(`/update_artwork_position/${id}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': window.csrfToken
                            },
                            body: JSON.stringify({
                                x_position: x,
                                y_position: y,
                                wall_id: wall.id
                            })
                        });
                        // Update local data
                        const art = placedArtworks.find(a => a.id == id);
                        if (art) {
                            art.x_position = x;
                            art.y_position = y;
                        }
                    }
                }
            });
        });
    }

    function addArtworkToCanvas(artwork) {
        // Place at (0,0) or next available spot
        artwork.x_position = 0;
        artwork.y_position = 0;
        artwork.wall_id = wall.id;
        placedArtworks.push(artwork);
        renderArtworks();
        // Save to DB
        fetch(`/update_artwork_position/${artwork.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({
                x_position: 0,
                y_position: 0,
                wall_id: wall.id
            })
        });
    }

    function addArtworkToImportedList(artwork) {
        const list = document.getElementById('importedArtworkList');
        const div = document.createElement('div');
        div.className = 'd-flex align-items-center justify-content-between border rounded p-2 mb-2';
        div.innerHTML = `<span>${artwork.name}</span>
            <button class="btn btn-sm btn-primary add-artwork-btn" data-artwork-id="${artwork.id}">Add</button>`;
        div.querySelector('.add-artwork-btn').addEventListener('click', function() {
            addArtworkToCanvas(artwork);
        });
        list.prepend(div);
    }

    // Initial render
    drawWall();
    renderArtworks();
    window.addEventListener('resize', () => {
        drawWall();
        renderArtworks();
    });
});