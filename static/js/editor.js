import { EvenSpacing } from './even_spacing.js';
import { MeasurementLinesManager } from './measurement_lines_manager.js';

document.addEventListener('DOMContentLoaded', function() {
    // Wall and artwork data from template
    const currentWall = window.currentWallData;
    let artworks = window.currentWallArtworkData || [];

    // Canvas setup
    const container = document.getElementById('canvas-container');
    const canvas = document.getElementById('wall-canvas');
    const ctx = canvas.getContext('2d');

    // Track mouse state
    let isDragging = false;
    let draggingArtwork = null;
    let dragOffset = { x: 0, y: 0 };
    let lastRenderTime = 0;
    const dragFrameRate = 60; // Limit drag updates to 60fps

    // Calculate scale factor
    function getScale() {
        return Math.min(
            container.clientWidth / currentWall.width,
            container.clientHeight / currentWall.height
        );
    }

    // Draw wall and grid
    function drawWallCanvas() {
        const scale = getScale();
        canvas.width = currentWall.width * scale;
        canvas.height = currentWall.height * scale;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Wall background
        ctx.fillStyle = currentWall.color || '#fff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Grid lines (every 12 units)
        ctx.strokeStyle = '#cccccc';
        ctx.lineWidth = 1;
        const gridSize = 12;
        for (let x = 0; x <= currentWall.width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x * scale, 0);
            ctx.lineTo(x * scale, canvas.height);
            ctx.stroke();
        }
        for (let y = 0; y <= currentWall.height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y * scale);
            ctx.lineTo(canvas.width, y * scale);
            ctx.stroke();
        }
    }

    // Draw all artworks as rectangles
    function drawArtworksOnCanvas() {
        drawWallCanvas();
        const scale = getScale();
        
        artworks.forEach(artwork => {
            ctx.save();
            
            // Different styles for dragging vs static
            if (artwork === draggingArtwork) {
                ctx.strokeStyle = '#FF5722';
                ctx.lineWidth = 3;
                ctx.fillStyle = 'rgba(255, 87, 34, 0.2)';
            } else {
                ctx.strokeStyle = '#5F3FCA';
                ctx.lineWidth = 2;
                ctx.fillStyle = 'rgba(95, 63, 202, 0.1)';
            }
            
            // Draw artwork rectangle
            ctx.fillRect(
                artwork.x_position * scale,
                artwork.y_position * scale,
                artwork.width * scale,
                artwork.height * scale
            );
            ctx.strokeRect(
                artwork.x_position * scale,
                artwork.y_position * scale,
                artwork.width * scale,
                artwork.height * scale
            );
            
            // Artwork label
            ctx.fillStyle = '#222';
            ctx.font = `${Math.max(10, 14 * scale)}px Arial`;
            ctx.fillText(
                artwork.name,
                artwork.x_position * scale + 4,
                artwork.y_position * scale + 18
            );
            
            ctx.restore();
        });
    }

    // Get mouse position relative to canvas in wall units
    function getMousePosition(e) {
        const rect = canvas.getBoundingClientRect();
        const scale = getScale();
        return {
            x: (e.clientX - rect.left) / scale,
            y: (e.clientY - rect.top) / scale
        };
    }

    // Find artwork at position (x, y)
    function getArtworkAtPosition(x, y) {
        // Check artworks in reverse order (top to bottom in z-index)
        for (let i = artworks.length - 1; i >= 0; i--) {
            const artwork = artworks[i];
            if (x >= artwork.x_position &&
                x <= artwork.x_position + artwork.width &&
                y >= artwork.y_position &&
                y <= artwork.y_position + artwork.height) {
                return artwork;
            }
        }
        return null;
    }

    // Canvas event listeners
    canvas.addEventListener('mousedown', function(e) {
        const mousePos = getMousePosition(e);
        draggingArtwork = getArtworkAtPosition(mousePos.x, mousePos.y);
        
        if (draggingArtwork) {
            isDragging = true;
            dragOffset = {
                x: mousePos.x - draggingArtwork.x_position,
                y: mousePos.y - draggingArtwork.y_position
            };
            
            // Bring artwork to front (move to end of array)
            const index = artworks.indexOf(draggingArtwork);
            if (index > -1 && index < artworks.length - 1) {
                artworks.splice(index, 1);
                artworks.push(draggingArtwork);
            }
            
            drawArtworksOnCanvas();
            canvas.style.cursor = 'grabbing';
        }
    });

    canvas.addEventListener('mousemove', function(e) {
        if (!isDragging || !draggingArtwork) return;
        
        // Throttle rendering for performance
        const now = performance.now();
        if (now - lastRenderTime < 1000 / dragFrameRate) return;
        lastRenderTime = now;
        
        const mousePos = getMousePosition(e);
        
        // Calculate new position with boundary checking
        draggingArtwork.x_position = Math.max(0, 
            Math.min(currentWall.width - draggingArtwork.width, 
                    mousePos.x - dragOffset.x));
                    
        draggingArtwork.y_position = Math.max(0, 
            Math.min(currentWall.height - draggingArtwork.height, 
                    mousePos.y - dragOffset.y));
        
        drawArtworksOnCanvas();
    });

    canvas.addEventListener('mouseup', function(e) {
        if (isDragging && draggingArtwork) {
            // Save to backend
            saveArtworkPosition(draggingArtwork);
        }
        isDragging = false;
        draggingArtwork = null;
        canvas.style.cursor = '';
        drawArtworksOnCanvas();
    });

    canvas.addEventListener('mouseleave', function(e) {
        if (isDragging && draggingArtwork) {
            saveArtworkPosition(draggingArtwork);
        }
        isDragging = false;
        draggingArtwork = null;
        canvas.style.cursor = '';
        drawArtworksOnCanvas();
    });

    // Change cursor when hovering over artwork
    canvas.addEventListener('mousemove', function(e) {
        if (isDragging) return;
        
        const mousePos = getMousePosition(e);
        const artwork = getArtworkAtPosition(mousePos.x, mousePos.y);
        canvas.style.cursor = artwork ? 'grab' : '';
    });

    // Save artwork position to server
    function saveArtworkPosition(artwork) {
        fetch(`/update_artwork_position/${artwork.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || ''
            },
            body: JSON.stringify({
                x_position: artwork.x_position,
                y_position: artwork.y_position,
                wall_id: currentWall.id
            })
        }).catch(error => {
            console.error('Error saving artwork position:', error);
        });
    }

    // Redraw on resize
    window.addEventListener('resize', function() {
        drawArtworksOnCanvas();
    });

    // Initial draw
    drawArtworksOnCanvas();
});