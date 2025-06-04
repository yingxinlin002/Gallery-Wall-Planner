//import { EvenSpacing } from './even_spacing.js';
//import { MeasurementLinesManager } from './measurement_lines_manager.js';

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Loaded: Starting wall editor setup');

    // Get essential elements
    const canvas = document.getElementById('wall-canvas');
    const layer = document.getElementById('canvas-artwork-layer');
    const container = document.getElementById('canvas-container');
    console.log('Container dimensions:', {
        width: container.clientWidth,
        height: container.clientHeight,
        offsetWidth: container.offsetWidth,
        offsetHeight: container.offsetHeight
    });
    const wall = window.currentWallData;

    console.log('Canvas element:', canvas); // Should log the canvas element
    console.log('Wall data:', wall); // Should log the wall data

    // Check if essential elements exist
    if (!canvas || !layer || !container || !wall) {
        console.error('Essential elements not found:', {canvas, layer, container, wall});
    } else {
        let placedArtworks = window.currentWallArtworkData || [];
        let permanentObjects = wall.permanentObjects || [];

        // Draw wall
        function drawWall() {
            if (!canvas || !wall) return;

            const ctx = canvas.getContext('2d');
            const scale = getScale();
            console.log('Drawing wall with scale:', scale); // Debug log

            // Set canvas dimensions in pixels
            canvas.width = wall.width * scale;
            canvas.height = wall.height * scale;
            console.log('Canvas dimensions:', canvas.width, 'x', canvas.height); // Debug log

            // Clear canvas
            ctx.fillStyle = wall.color || '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw grid (in inches)
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 1;
            
            // Vertical lines (every 12 inches)
            for (let x = 0; x <= wall.width; x += 12) {
                const xPos = x * scale;
                ctx.beginPath();
                ctx.moveTo(xPos, 0);
                ctx.lineTo(xPos, canvas.height);
                ctx.stroke();
            }
            
            // Horizontal lines (every 12 inches)
            for (let y = 0; y <= wall.height; y += 12) {
                const yPos = y * scale;
                ctx.beginPath();
                ctx.moveTo(0, yPos);
                ctx.lineTo(canvas.width, yPos);
                ctx.stroke();
            }

            // Draw permanent objects
            permanentObjects.forEach(obj => {
                drawObject(ctx, obj, scale, true);
            });
        }

        function drawObject(ctx, obj, scale, isPermanent = false) {
            const yPos = wall.height - obj.y - obj.height; // Convert to bottom-left origin
            
            ctx.fillStyle = isPermanent ? 'rgba(200, 200, 255, 0.7)' : 'rgba(255, 255, 200, 0.7)';
            ctx.strokeStyle = isPermanent ? '#0000aa' : '#aaaa00';
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

        function getScale() {
            if (!container || !wall || !wall.width || !wall.height) {
                console.error('Missing required data for scaling');
                return 1;
            }
            
            const containerWidth = container.clientWidth;
            const containerHeight = container.clientHeight;
            const scaleX = containerWidth / wall.width;
            const scaleY = containerHeight / wall.height;
            const scale = Math.min(scaleX, scaleY);
            
            console.log('Scaling:', {
                containerSize: `${containerWidth}x${containerHeight}`,
                wallSize: `${wall.width}x${wall.height}`,
                calculatedScale: scale
            });
            
            return scale;
        }

        function renderArtworks() {
            layer.innerHTML = '';
            const scale = getScale();
            
            placedArtworks.forEach(artwork => {
                const div = document.createElement('div');
                div.className = 'canvas-artwork';
                div.id = `artwork-${artwork.id}`;
                
                // Convert to bottom-left origin
                const yPos = wall.height - artwork.y_position - artwork.height;
                
                div.style.left = `${artwork.x_position * scale}px`;
                div.style.top = `${yPos * scale}px`;
                div.style.width = `${artwork.width * scale}px`;
                div.style.height = `${artwork.height * scale}px`;
                div.textContent = artwork.name;
                div.setAttribute('data-id', artwork.id);
                div.setAttribute('data-x', artwork.x_position);
                div.setAttribute('data-y', artwork.y_position);
                div.setAttribute('data-width', artwork.width);
                div.setAttribute('data-height', artwork.height);
                
                // Check for collisions
                if (checkCollisions(artwork)) {
                    div.style.border = '2px solid red';
                }
                
                layer.appendChild(div);
            });

            // Make artworks draggable
            makeArtworksDraggable();
        }

        function checkCollisions(artwork) {
            // Check against other artworks
            for (const other of placedArtworks) {
                if (other.id !== artwork.id && 
                    checkRectOverlap(artwork, other)) {
                    return true;
                }
            }
            
            // Check against permanent objects
            for (const obj of permanentObjects) {
                if (checkRectOverlap(artwork, obj)) {
                    return true;
                }
            }
            
            return false;
        }

        function checkRectOverlap(a, b) {
            return a.x_position < b.x + b.width &&
                   a.x_position + a.width > b.x &&
                   a.y_position < b.y + b.height &&
                   a.y_position + a.height > b.y;
        }

        function makeArtworksDraggable() {
            const scale = getScale();
            
            interact('.canvas-artwork').draggable({
                inertia: true,
                modifiers: [
                    interact.modifiers.restrictRect({
                        restriction: 'parent',
                        endOnly: true
                    })
                ],
                listeners: {
                    start(event) {
                        event.target.style.zIndex = '3';
                    },
                    move(event) {
                        const target = event.target;
                        const width = parseFloat(target.getAttribute('data-width'));
                        const height = parseFloat(target.getAttribute('data-height'));
                        
                        // Calculate new position (in inches)
                        const newX = parseFloat(target.getAttribute('data-x')) + event.dx / scale;
                        const newY = parseFloat(target.getAttribute('data-y')) + event.dy / scale;
                        
                        // Update position attributes
                        target.setAttribute('data-x', newX);
                        target.setAttribute('data-y', newY);
                        
                        // Update visual position (convert to bottom-left origin)
                        const yPos = wall.height - newY - height;
                        target.style.left = `${newX * scale}px`;
                        target.style.top = `${yPos * scale}px`;
                        
                        // Check for collisions
                        const artwork = {
                            id: target.getAttribute('data-id'),
                            x_position: newX,
                            y_position: newY,
                            width: width,
                            height: height
                        };
                        
                        if (checkCollisions(artwork)) {
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
                        updateArtworkPosition(id, x, y);
                        
                        // Update local data
                        const artwork = placedArtworks.find(a => a.id == id);
                        if (artwork) {
                            artwork.x_position = x;
                            artwork.y_position = y;
                        }
                        
                        target.style.zIndex = '2';
                    }
                }
            });
        }

        function updateArtworkPosition(id, x, y) {
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
            }).catch(error => console.error('Error updating position:', error));
        }


        // Add artwork to canvas
        document.querySelectorAll('.add-artwork-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const artworkId = this.getAttribute('data-artwork-id');
                const artwork = window.unplacedArtworkData.find(a => a.id == artworkId);
                if (artwork) {
                    // Default position (top-left corner)
                    artwork.x_position = 0;
                    artwork.y_position = wall.height - artwork.height; // Bottom-left origin
                    artwork.wall_id = wall.id;
                    
                    placedArtworks.push(artwork);
                    renderArtworks();
                    
                    // Save to DB
                    updateArtworkPosition(artwork.id, artwork.x_position, artwork.y_position);
                }
            });
        });

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
                window.location.href = window.artworkManualUrl || '/artwork-manual';
            });
        }
    }
});