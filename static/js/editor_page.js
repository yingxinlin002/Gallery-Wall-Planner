import { EvenSpacing } from './even_spacing.js';
import { MeasurementManager } from './modules/MeasurementManager.js';
import { InstallationInstruction } from './modules/InstallationInstruction.js'; // <-- Add this import

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
        // Initialize with only artworks that are actually placed on this wall
        let allArtworks = window.allArtworkData || [];
        let placedArtworks = (window.currentWallArtworkData || []).filter(
            a => a.wall_id === window.currentWallData.id
        );
        let permanentObjects = wall.permanentObjects || [];

        // Draw wall
        function drawWall() {
            if (!canvas || !wall) return;

            const ctx = canvas.getContext('2d');
            const scale = getScale();
            
            // Set canvas dimensions in pixels
            canvas.width = wall.width * scale;
            canvas.height = wall.height * scale;

            // Position the canvas container to match the scaled dimensions
            container.style.width = `${canvas.width}px`;
            container.style.height = `${canvas.height}px`;
            
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

            // Add dimension labels
            addDimensionLabels(scale);
        }

        function addDimensionLabels(scale) {
            // Remove existing labels if any
            document.querySelectorAll('.dimension-label').forEach(el => el.remove());

            // Create width label
            const widthLabel = document.createElement('div');
            widthLabel.className = 'dimension-label width-label';
            widthLabel.textContent = `${wall.width}"`;
            document.getElementById('canvas-container').appendChild(widthLabel);

            // Create height label
            const heightLabel = document.createElement('div');
            heightLabel.className = 'dimension-label height-label';
            heightLabel.textContent = `${wall.height}"`;
            document.getElementById('canvas-container').appendChild(heightLabel);
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
            
            // Get the wall-space container dimensions
            const wallSpace = document.querySelector('.wall-space');
            const availableWidth = wallSpace.clientWidth - 40; // Subtract padding
            const availableHeight = wallSpace.clientHeight - 40; // Subtract padding
            
            // Calculate scale factors
            const scaleX = availableWidth / wall.width;
            const scaleY = availableHeight / wall.height;
            
            // Use the smaller scale to ensure everything fits
            const scale = Math.min(scaleX, scaleY);
            
            // Add some minimum scale if needed
            return Math.max(scale, 0.1); // Ensure it doesn't get too small
        }

        // Modify renderArtworks to only show placed artworks
        function renderArtworks() {
            layer.innerHTML = '';
            const scale = getScale();

            placedArtworks.forEach(artwork => {
                // Only render if artwork has wall_id matching current wall
                if (artwork.wall_id === window.currentWallData.id) {
                    const div = document.createElement('div');
                    div.className = 'canvas-artwork';
                    div.id = `artwork-${artwork.id}`;

                    // Use saved position, default to top-left if not set
                    const xPos = artwork.x_position || 0;
                    const yPos = artwork.y_position || (wall.height - artwork.height);

                    // Convert to bottom-left origin
                    const canvasY = wall.height - yPos - artwork.height;

                    div.style.left = `${xPos * scale}px`;
                    div.style.top = `${canvasY * scale}px`;
                    div.style.width = `${artwork.width * scale}px`;
                    div.style.height = `${artwork.height * scale}px`;
                    div.textContent = artwork.name;
                    div.setAttribute('data-id', artwork.id);
                    div.setAttribute('data-x', xPos);
                    div.setAttribute('data-y', yPos);
                    div.setAttribute('data-width', artwork.width);
                    div.setAttribute('data-height', artwork.height);

                    if (checkCollisions(artwork)) {
                        div.style.border = '2px solid red';
                    }

                    layer.appendChild(div);
                }
            });

            makeArtworksDraggable();
        }

        function checkCollisions(artwork) {
            // Check against other placed artworks
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
            console.log('Attempting to make arstworks draggable');
            if (typeof interact === 'undefined') {
                console.error('Interact.js not loaded!');
                return;
            }

            const artworks = document.querySelectorAll('.canvas-artwork');
            console.log(`Found ${artworks.length} artworks to make draggable`);
            
            const scale = getScale();
            const measurementManager = new MeasurementManager(document.getElementById('canvas-container'));
            
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
                        measurementManager.clear(); // Clear any existing lines
                    },
                    move(event) {
                        const target = event.target;
                        const width = parseFloat(target.getAttribute('data-width'));
                        const height = parseFloat(target.getAttribute('data-height'));
                        
                        // Calculate new position (in inches)
                        const newX = parseFloat(target.getAttribute('data-x')) + event.dx / scale;
                        // Subtract dy instead of adding to account for bottom-left origin
                        const newY = Math.max(0, Math.min(wall.height - height, 
                            parseFloat(target.getAttribute('data-y')) - event.dy / scale));
                        
                        // Update position attributes
                        target.setAttribute('data-x', newX);
                        target.setAttribute('data-y', newY);
                        
                        // Update visual position (convert to bottom-left origin)
                        const yPos = wall.height - newY - height;
                        target.style.left = `${newX * scale}px`;
                        target.style.top = `${yPos * scale}px`;
                        
                        // Draw measurement lines
                        measurementManager.drawMeasurements(
                            newX, 
                            newY, 
                            width, 
                            height, 
                            wall.width, 
                            wall.height, 
                            scale
                        );
                        
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
                        measurementManager.clear(); // Clear lines when dragging ends
                    }
                }
            }).on('dragstart', function(event) {
                console.log('Drag started for:', event.target);
            });
        }

        // Update the updateArtworkPosition function to handle removal
        function updateArtworkPosition(id, x, y, wall_id = null) {
            fetch(`/update_artwork_position/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({
                    x_position: x,
                    y_position: y,
                    wall_id: wall_id !== null ? wall_id : window.currentWallData.id
                })
            }).catch(error => console.error('Error updating position:', error));
        }


        // Add artwork to canvas
        document.querySelectorAll('.add-artwork-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const artworkId = parseInt(this.getAttribute('data-artwork-id'));
                const artwork = allArtworks.find(a => a.id === artworkId);
                
                if (artwork) {
                    // Only set default position if not already placed
                    if (artwork.x_position === null || artwork.y_position === null) {
                        artwork.x_position = 0;
                        artwork.y_position = wall.height - artwork.height;
                    }
                    
                    artwork.wall_id = wall.id;
                    placedArtworks.push(artwork);
                    renderArtworks();
                    
                    // Toggle button visibility
                    this.style.display = 'none';
                    this.nextElementSibling.style.display = 'block';
                    
                    updateArtworkPosition(artwork.id, artwork.x_position, artwork.y_position, wall.id);
                }
            });
        });

        // Remove artwork from canvas
        document.querySelectorAll('.remove-artwork-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const artworkId = parseInt(this.getAttribute('data-artwork-id'));
                const artwork = allArtworks.find(a => a.id === artworkId);
                
                if (artwork) {
                    // Clear position and wall reference
                    artwork.x_position = null;
                    artwork.y_position = null;
                    artwork.wall_id = null;
                    
                    // Remove from placed artworks array
                    placedArtworks = placedArtworks.filter(a => a.id !== artworkId);
                    renderArtworks();
                    
                    // Toggle button visibility
                    this.style.display = 'none';
                    this.previousElementSibling.style.display = 'block';
                    
                    // Update in database
                    updateArtworkPosition(artworkId, null, null, null);
                }
            });
        });

        // Initial render
        drawWall();
        renderArtworks();

        // Add ResizeObserver for responsive resizing
        const resizeObserver = new ResizeObserver(() => {
            drawWall();
            renderArtworks();
        });

        // Observe the wall-space container
        const wallSpace = document.querySelector('.wall-space');
        if (wallSpace) {
            resizeObserver.observe(wallSpace);
        }

        // Clean up observer on unload
        window.addEventListener('beforeunload', () => {
            resizeObserver.disconnect();
        });

        // Still keep window resize event for extra safety (optional)
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

        // Save Changes button handler
        const saveChangesBtn = document.getElementById('saveChangesBtn');
        if (saveChangesBtn) {
            saveChangesBtn.addEventListener('click', async function() {
                try {
                    // Check if user is logged in (has user_id in session)
                    const response = await fetch('/check-auth-status');
                    const authStatus = await response.json();
                    
                    if (authStatus.authenticated) {
                        // User is logged in - save changes
                        await saveAllChanges();
                        alert('Changes saved successfully!');
                    } else {
                        // Guest user - prompt to log in
                        if (confirm('Please log in to save your changes. Would you like to log in now?')) {
                            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                        }
                    }
                } catch (error) {
                    console.error('Error saving changes:', error);
                    alert('Failed to save changes. Please try again.');
                }
            });
        }

        // --- EvenSpacing Integration ---
        const editor = {
            wall: window.currentWallData,
            placedArtworks: placedArtworks,
            updateArtworkPosition: updateArtworkPosition,
            renderArtworks: renderArtworks
        };

        const evenSpacing = new EvenSpacing(editor);
        evenSpacing.init();

        // Connect the even spacing button
        const evenSpacingBtn = document.getElementById('evenSpacingBtn');
        if (evenSpacingBtn) {
            evenSpacingBtn.addEventListener('click', function() {
                evenSpacing.show();
            });
        }
        // --- End EvenSpacing Integration ---

        // --- Installation Instruction Integration ---
        const calcInstructionBtn = document.getElementById('calcInstructionBtn');
        if (calcInstructionBtn) {
            calcInstructionBtn.addEventListener('click', () => {
                const instruction = new InstallationInstruction(
                    window.currentWallData,
                    window.currentWallArtworkData
                );
                instruction.show();
            });
        }
        // --- End Installation Instruction Integration ---

        // Save Temporary Work button handler
        const saveGuestBtn = document.getElementById('saveGuestBtn');
        if (saveGuestBtn) {
            saveGuestBtn.addEventListener('click', async function() {
                try {
                    const currentState = getCurrentWallState(); // You must implement this function!
                    const response = await fetch('/save-guest-work', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': window.csrfToken
                        },
                        body: JSON.stringify(currentState)
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert('Work saved temporarily!');
                    } else {
                        alert('Error saving work: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Error saving work: ' + error.message);
                }
            });
        }

        // Create Account & Save button handler
        const convertBtn = document.getElementById('convertAndSaveBtn');
        if (convertBtn) {
            convertBtn.addEventListener('click', function() {
                const modal = new bootstrap.Modal(document.getElementById('accountCreationModal'));
                modal.show();
            });
        }

        // Modal "Create Account" button handler
        const confirmRegBtn = document.getElementById('confirmRegistrationBtn');
        if (confirmRegBtn) {
            confirmRegBtn.addEventListener('click', async function() {
                const form = document.getElementById('registrationForm');
                if (!form.checkValidity()) {
                    form.classList.add('was-validated');
                    return;
                }
                try {
                    const currentState = getCurrentWallState();
                    const registrationData = {
                        name: document.getElementById('name').value,
                        email: document.getElementById('email').value,
                        password: document.getElementById('password').value
                    };
                    const response = await fetch('/save-guest-work', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': window.csrfToken
                        },
                        body: JSON.stringify({
                            convert_to_user: true,
                            ...registrationData,
                            ...currentState
                        })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert('Account created and work saved permanently!');
                        bootstrap.Modal.getInstance(document.getElementById('accountCreationModal')).hide();
                        window.location.reload();
                    } else {
                        alert('Error creating account: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Error creating account: ' + error.message);
                }
            });
        }

        // Helper function to get current wall state
        function getCurrentWallState() {
            return {
                wall: window.currentWallData,
                artworks: Array.from(document.querySelectorAll('#canvas-artwork-layer .artwork')).map(el => ({
                    id: el.dataset.artworkId,
                    x: parseFloat(el.style.left),
                    y: parseFloat(el.style.top),
                    width: parseFloat(el.dataset.width),
                    height: parseFloat(el.dataset.height)
                })),
                snapLines: window.currentWallData.wall_lines || []
            };
        }
    }
});

async function saveAllChanges() {
    // Since we're already saving positions when they're changed (via updateArtworkPosition),
    // this function can just confirm everything is saved
    return Promise.resolve();
}