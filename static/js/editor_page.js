//import { EvenSpacing } from './even_spacing.js';
//import { MeasurementLinesManager } from './measurement_lines_manager.js';

document.addEventListener('DOMContentLoaded', function() {
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

    // Canvas logic
    const canvas = document.getElementById('wall-canvas');
    const layer = document.getElementById('canvas-artwork-layer');
    const container = document.getElementById('canvas-container');
    const wall = window.currentWallData;

    // Check if essential elements exist
    if (!canvas || !layer || !container || !wall) {
        console.error('Essential elements not found:', {canvas, layer, container, wall});
        return;
    }

    let placedArtworks = window.currentWallArtworkData || [];

    // Draw wall
    function drawWall() {
        if (!canvas || !wall) return;

        const ctx = canvas.getContext('2d');
        const scale = getScale();
        if (!scale) return;

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
        if (!container || !wall || !wall.width || !wall.height) {
            console.error('Missing required data for scaling');
            return 1; // Default scale if something is missing
        }
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

    // Initial render
    drawWall();
    renderArtworks();
    window.addEventListener('resize', () => {
        drawWall();
        renderArtworks();
    });

    // Add Artwork button handler
    const addArtworkBtn = document.getElementById('addArtworkBtn');
    if (addArtworkBtn) {
        addArtworkBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.artworkManualUrl) {
                window.location.href = window.artworkManualUrl;
            } else {
                console.error('artworkManualUrl is not defined');
                window.location.href = '/artwork-manual';
            }
        });
    }
});