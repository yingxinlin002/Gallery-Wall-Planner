// static/js/even_spacing.js
export class EvenSpacing {
    constructor(editor) {
        this.editor = editor;
        this.DEFAULT_Y_POSITION = 62; // Default height in inches
        this.MIN_SPACING = 0.5; // Minimum spacing between artworks in inches
        this.selectedArtworks = [];
    }

    init() {
        // Remove old modal if it exists
        const oldModal = document.getElementById('evenSpacingModal');
        if (oldModal) {
            oldModal.parentNode.removeChild(oldModal);
        }
        this.setupUI();
        this.bindEvents();
    }

    setupUI() {
        this.modal = document.createElement('div');
        this.modal.className = 'modal fade';
        this.modal.id = 'evenSpacingModal';
        this.modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header py-2">
                        <h5 class="modal-title">Even Spacing</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                        <div class="row g-3">
                            <!-- Left: Spacing controls -->
                            <div class="col-md-6">
                                <label class="form-label mb-1">Spacing Boundaries (inches)</label>
                                <div class="input-group input-group-sm mb-1">
                                    <span class="input-group-text">Left:</span>
                                    <input type="number" class="form-control" id="leftBoundary" value="0" step="0.1">
                                </div>
                                <div class="input-group input-group-sm mb-2">
                                    <span class="input-group-text">Right:</span>
                                    <input type="number" class="form-control" id="rightBoundary" value="${this.editor.wall.width}" step="0.1">
                                </div>
                                <label class="form-label mb-1">Center height from floor</label>
                                <div class="input-group input-group-sm mb-1">
                                    <input type="number" class="form-control" id="yPosition" value="${this.DEFAULT_Y_POSITION}" step="0.1">
                                    <span class="input-group-text">inches</span>
                                </div>
                                <div class="form-text small mb-1">Standard: 62" from floor</div>
                                <div class="d-flex justify-content-between small mb-1">
                                    <span id="selectedCount">Selected: 0</span>
                                    <span id="totalWidth">Total Width: 0.0"</span>
                                    <span id="spacingInfo">Spacing: -</span>
                                </div>
                            </div>
                            <!-- Right: Select Artworks -->
                            <div class="col-md-6">
                                <label class="form-label mb-1">Select Artworks (click to select order left to right)</label>
                                <select multiple class="form-select form-select-sm" id="artworkList" size="14" style="width: 100%;">
                                    ${this.editor.placedArtworks.map(artwork => 
                                        `<option value="${artwork.id}">${artwork.name} (${artwork.width}" × ${artwork.height}")</option>`
                                    ).join('')}
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer py-2">
                        <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-sm btn-primary" id="applySpacing">Apply Spacing</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.modal);
        this.modalInstance = new bootstrap.Modal(this.modal);
    }

    bindEvents() {
        const artworkList = this.modal.querySelector('#artworkList');
        
        // Artwork selection - handle Ctrl/Cmd+click
        artworkList.addEventListener('click', (e) => {
            if (e.target.tagName === 'OPTION') {
                e.preventDefault();
                const option = e.target;
                const artworkId = parseInt(option.value);
                
                // Find if this artwork is already selected
                const existingIndex = this.selectedArtworks.findIndex(a => a.id === artworkId);
                
                if (existingIndex >= 0) {
                    // Remove from selection
                    this.selectedArtworks.splice(existingIndex, 1);
                    option.selected = false;
                } else {
                    // Add to selection (at end)
                    const artwork = this.editor.placedArtworks.find(a => a.id == artworkId);
                    if (artwork) {
                        this.selectedArtworks.push(artwork);
                        option.selected = true;
                    }
                }
                
                this.updateDisplay();
            }
        });

        // Boundary inputs
        ['leftBoundary', 'rightBoundary'].forEach(id => {
            this.modal.querySelector(`#${id}`).addEventListener('input', () => {
                this.updateDisplay();
            });
        });

        // Apply button
        this.modal.querySelector('#applySpacing').addEventListener('click', () => {
            this.applySpacing();
        });
    }

    updateSelection() {
        const select = this.modal.querySelector('#artworkList');
        const selectedOptions = Array.from(select.selectedOptions);
        
        // Get selected artworks in the order they were selected
        this.selectedArtworks = selectedOptions.map(option => {
            return this.editor.placedArtworks.find(a => a.id == option.value);
        });
    }

    // updateDisplay() method to show selection order
    updateDisplay() {
        const select = this.modal.querySelector('#artworkList');
        const options = Array.from(select.options);
        
        // Update all options to show selection order
        options.forEach(option => {
            const artworkId = parseInt(option.value);
            const index = this.selectedArtworks.findIndex(a => a.id === artworkId);
            
            // Remove any existing order number
            let text = option.text.replace(/ \(\d+\)$/, '');
            
            // Add order number if selected
            if (index >= 0) {
                text += ` (${index + 1})`;
            }
            
            option.text = text;
            option.selected = index >= 0;
        });

        // Update info labels
        const totalWidth = this.selectedArtworks.reduce((sum, artwork) => sum + artwork.width, 0);
        this.modal.querySelector('#selectedCount').textContent = `Selected: ${this.selectedArtworks.length}`;
        this.modal.querySelector('#totalWidth').textContent = `Total Width: ${totalWidth.toFixed(1)}"`;

        // Calculate and display projected spacing
        try {
            const left = parseFloat(this.modal.querySelector('#leftBoundary').value);
            const right = parseFloat(this.modal.querySelector('#rightBoundary').value);
            
            if (right > left && this.selectedArtworks.length > 0) {
                const spacing = (right - left - totalWidth) / (this.selectedArtworks.length + 1);
                this.modal.querySelector('#spacingInfo').textContent = `Spacing: ${spacing.toFixed(1)}"`;
            }
        } catch (e) {
            // Ignore parsing errors
        }
    }

    validateInputs() {
        try {
            const left = parseFloat(this.modal.querySelector('#leftBoundary').value);
            const right = parseFloat(this.modal.querySelector('#rightBoundary').value);
            const wallWidth = this.editor.wall.width;

            if (left < 0 || right > wallWidth) {
                alert('Boundaries must be within wall dimensions.');
                return [null, null];
            }

            if (left >= right) {
                alert('Left boundary must be less than right boundary.');
                return [null, null];
            }

            return [left, right];
        } catch (e) {
            alert('Please enter valid numbers for boundaries.');
            return [null, null];
        }
    }

    getYPosition() {
        try {
            const yPos = parseFloat(this.modal.querySelector('#yPosition').value);
            const wallHeight = this.editor.wall.height;

            if (yPos < 0 || yPos > wallHeight) {
                alert(`Y position must be between 0 and ${wallHeight} inches`);
                return null;
            }

            // Convert from floor distance to wall coordinates (from bottom)
            return wallHeight - yPos;
        } catch (e) {
            alert('Please enter a valid number for Y position');
            return null;
        }
    }

    async applySpacing() {
        const [left, right] = this.validateInputs();
        if (left === null) return;

        const yPosCenter = this.getYPosition();
        if (yPosCenter === null) return;

        if (this.selectedArtworks.length === 0) {
            alert('Please select at least one artwork.');
            return;
        }

        const totalWidth = this.selectedArtworks.reduce((sum, artwork) => sum + artwork.width, 0);
        const availableSpace = right - left;

        if (availableSpace < totalWidth) {
            alert('Not enough space for selected artworks.');
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

        for (const artwork of this.selectedArtworks) {
            // Calculate position in inches (wall coordinates)
            artwork.x_position = currentX;
            // Calculate Y position so center is at yPosCenter
            artwork.y_position = yPosCenter - (artwork.height / 2);

            // Update in database
            await this.editor.updateArtworkPosition(artwork.id, artwork.x_position, artwork.y_position);

            currentX += artwork.width + spacing;
        }

        // Refresh the display
        this.editor.renderArtworks();
        this.modalInstance.hide();
    }

    show() {
        // Reset selection
        this.selectedArtworks = [];
        this.modal.querySelector('#artworkList').selectedIndex = -1;
        this.updateDisplay();
        
        // Show modal
        this.modalInstance.show();
    }
}