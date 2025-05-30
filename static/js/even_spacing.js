// even_spacing.js - Even spacing functionality for artwork editor

class EvenSpacing {
    constructor(editor) {
        this.editor = editor;
        this.selectedArtworks = [];
        this.DEFAULT_Y_POSITION = 62; // Default height in inches
        this.MIN_SPACING = 0.5; // Minimum spacing between artworks in inches
        
        this.initModal();
    }
    
    initModal() {
        // Create modal HTML
        const modalHTML = `
        <div id="even-spacing-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="even-spacing-title">Even Spacing</h3>
                    <span class="close" onclick="evenSpacing.closeModal()">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="form-section">
                        <h4>Spacing Boundaries (inches)</h4>
                        <div class="form-group">
                            <label for="left-boundary">Left Boundary:</label>
                            <input type="number" id="left-boundary" class="form-control" value="0" step="0.1">
                        </div>
                        <div class="form-group">
                            <label for="right-boundary">Right Boundary:</label>
                            <input type="number" id="right-boundary" class="form-control" value="${this.editor.currentWall.width.toFixed(1)}" step="0.1">
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h4>Artwork Position</h4>
                        <div class="form-group">
                            <label for="y-position">Center height from floor (standard: 62"):</label>
                            <input type="number" id="y-position" class="form-control" value="${this.DEFAULT_Y_POSITION}" step="0.1">
                            <small>Distance from bottom of wall</small>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h4>Select Artworks (click to select order)</h4>
                        <div class="artwork-list-container">
                            <div id="even-spacing-artworks" class="artwork-list">
                                ${this.generateArtworkList()}
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-section">
                        <span id="selected-count">Selected: 0</span>
                        <span id="total-width">Total Width: 0.0"</span>
                        <span id="spacing-value">Spacing: -</span>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="evenSpacing.applySpacing()">Apply Spacing</button>
                    <button class="btn btn-secondary" onclick="evenSpacing.closeModal()">Cancel</button>
                </div>
            </div>
        </div>
        `;
        
        // Add modal to DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Set up event listeners
        document.getElementById('left-boundary').addEventListener('input', () => this.updateSpacingPreview());
        document.getElementById('right-boundary').addEventListener('input', () => this.updateSpacingPreview());
        
        // Initialize artwork selection
        this.setupArtworkSelection();
    }
    
    generateArtworkList() {
        let html = '';
        this.editor.currentWallArtworkData.forEach(artwork => {
            html += `
            <div class="artwork-item" data-artwork-id="${artwork.id}" onclick="evenSpacing.toggleArtworkSelection('${artwork.id}')">
                ${artwork.name} (${artwork.width}" × ${artwork.height}")
            </div>
            `;
        });
        return html;
    }
    
    setupArtworkSelection() {
        // This will be handled by the toggleArtworkSelection method
    }
    
    toggleArtworkSelection(artworkId) {
        const artworkItem = document.querySelector(`.artwork-item[data-artwork-id="${artworkId}"]`);
        const artwork = this.editor.currentWallArtworkData.find(a => a.id === artworkId);
        
        // Toggle selection
        const index = this.selectedArtworks.findIndex(a => a.id === artworkId);
        if (index >= 0) {
            // Already selected - remove it
            this.selectedArtworks.splice(index, 1);
            artworkItem.classList.remove('selected');
        } else {
            // Not selected - add it
            this.selectedArtworks.push(artwork);
            artworkItem.classList.add('selected');
        }
        
        // Update order indicators
        this.updateOrderIndicators();
        this.updateInfoDisplay();
    }
    
    updateOrderIndicators() {
        document.querySelectorAll('.artwork-item').forEach(item => {
            const orderSpan = item.querySelector('.order-indicator');
            if (orderSpan) orderSpan.remove();
            
            const artworkId = item.dataset.artworkId;
            const index = this.selectedArtworks.findIndex(a => a.id === artworkId);
            
            if (index >= 0) {
                const span = document.createElement('span');
                span.className = 'order-indicator';
                span.textContent = ` (${index + 1})`;
                item.appendChild(span);
            }
        });
    }
    
    updateInfoDisplay() {
        // Update selected count
        document.getElementById('selected-count').textContent = `Selected: ${this.selectedArtworks.length}`;
        
        // Update total width
        const totalWidth = this.selectedArtworks.reduce((sum, artwork) => sum + artwork.width, 0);
        document.getElementById('total-width').textContent = `Total Width: ${totalWidth.toFixed(1)}"`;
        
        // Update spacing preview
        this.updateSpacingPreview();
    }
    
    updateSpacingPreview() {
        if (this.selectedArtworks.length === 0) {
            document.getElementById('spacing-value').textContent = 'Spacing: -';
            return;
        }
        
        try {
            const left = parseFloat(document.getElementById('left-boundary').value);
            const right = parseFloat(document.getElementById('right-boundary').value);
            const totalWidth = this.selectedArtworks.reduce((sum, artwork) => sum + artwork.width, 0);
            
            if (right > left) {
                const spacing = (right - left - totalWidth) / (this.selectedArtworks.length + 1);
                document.getElementById('spacing-value').textContent = `Spacing: ${spacing.toFixed(1)}"`;
            }
        } catch (e) {
            document.getElementById('spacing-value').textContent = 'Spacing: -';
        }
    }
    
    validateInputs() {
        try {
            const left = parseFloat(document.getElementById('left-boundary').value);
            const right = parseFloat(document.getElementById('right-boundary').value);
            const yPos = parseFloat(document.getElementById('y-position').value);
            
            if (isNaN(left)) throw new Error("Please enter a valid number for left boundary");
            if (isNaN(right)) throw new Error("Please enter a valid number for right boundary");
            if (isNaN(yPos)) throw new Error("Please enter a valid number for Y position");
            
            if (left < 0 || right > this.editor.currentWall.width) {
                throw new Error(`Boundaries must be between 0 and ${this.editor.currentWall.width} inches`);
            }
            
            if (left >= right) {
                throw new Error("Left boundary must be less than right boundary");
            }
            
            if (yPos < 0 || yPos > this.editor.currentWall.height) {
                throw new Error(`Y position must be between 0 and ${this.editor.currentWall.height} inches`);
            }
            
            return { left, right, yPos };
        } catch (error) {
            alert(error.message);
            return null;
        }
    }
    
    applySpacing() {
        const inputs = this.validateInputs();
        if (!inputs) return;
        
        if (this.selectedArtworks.length === 0) {
            alert("Please select at least one artwork");
            return;
        }
        
        const { left, right, yPos } = inputs;
        const totalWidth = this.selectedArtworks.reduce((sum, artwork) => sum + artwork.width, 0);
        const availableSpace = right - left;
        
        if (availableSpace < totalWidth) {
            alert("Not enough space for selected artworks");
            return;
        }
        
        const spacing = (availableSpace - totalWidth) / (this.selectedArtworks.length + 1);
        
        if (spacing < this.MIN_SPACING) {
            if (!confirm(`Calculated spacing (${spacing.toFixed(1)}") is very small. Continue anyway?`)) {
                return;
            }
        }
        
        // Position artworks
        let currentX = left + spacing;
        const wallHeight = this.editor.currentWall.height;
        
        this.selectedArtworks.forEach(artwork => {
            // Calculate position in inches (wall coordinates)
            const x = currentX;
            // Calculate Y position so center is at yPos from floor (bottom of wall)
            const y = wallHeight - yPos - (artwork.height / 2);
            
            // Update artwork position in editor
            this.editor.updateArtworkPosition(artwork.id, x, y);
            
            currentX += artwork.width + spacing;
        });
        
        this.closeModal();
    }
    
    showModal() {
        // Reset selections
        this.selectedArtworks = [];
        document.querySelectorAll('.artwork-item').forEach(item => item.classList.remove('selected'));
        this.updateInfoDisplay();
        
        // Show modal
        document.getElementById('even-spacing-modal').style.display = 'block';
    }
    
    closeModal() {
        document.getElementById('even-spacing-modal').style.display = 'none';
    }
}

// Initialize even spacing when editor is ready
function initEvenSpacing(editor) {
    window.evenSpacing = new EvenSpacing(editor);
}