// static/js/modules/SnapLineManager.js
export class SnapLineManager {
    constructor(editor) {
        this.editor = editor;
        this.lines = [];
        this.activeLine = null;
        this.isCreating = false;
        this.canvas = document.getElementById('wall-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.scale = this.editor.getScale();
        this.container = document.getElementById('canvas-container');
        this.snapDistance = 10; // pixels
        this.lineColor = '#3498db';
        this.snapColor = '#e74c3c';
        
        this.init();
    }

    init() {
        this.loadLines();
        this.setupEventListeners();
    }

    loadLines() {
        // Lines should be loaded from the editor's wall_lines data
        this.lines = (this.editor.wall.wall_lines || []).map(line => ({
            ...line,
            x: line.x_cord * this.scale,
            y: line.y_cord * this.scale,
            length: line.length * this.scale,
            angle: line.angle
        }));
        this.drawLines();
    }

    setupEventListeners() {
        // Add Snap Line button
        document.getElementById('addSnapLineBtn')?.addEventListener('click', () => this.startLineCreation());

        // Edit/Delete buttons in sidebar
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lineId = e.target.closest('.snap-line-item').dataset.lineId;
                this.editLine(lineId);
            });
        });

        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lineId = e.target.closest('.snap-line-item').dataset.lineId;
                this.deleteLine(lineId);
            });
        });

        // Canvas interaction
        this.canvas.addEventListener('mousedown', (e) => this.handleCanvasMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleCanvasMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.handleCanvasMouseUp());
    }

    startLineCreation() {
        // Show the modal
        const modalEl = document.getElementById('snapLineModal');
        if (!modalEl) {
            alert('Snap Line modal not found!');
            return;
        }
        // Reset form
        document.getElementById('snapLineForm').reset();
        // Set default label
        document.getElementById('distance-label').textContent = 'Distance from bottom (inches)';
        document.getElementById('distance').value = '';

        // Show modal (Bootstrap 5)
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();

        // Change label based on orientation
        document.getElementById('orientation').addEventListener('change', function() {
            if (this.value === 'horizontal') {
                document.getElementById('distance-label').textContent = 'Distance from bottom (inches)';
            } else {
                document.getElementById('distance-label').textContent = 'Distance from left (inches)';
            }
        });

        // Handle form submission
        const form = document.getElementById('snapLineForm');
        form.onsubmit = (e) => {
            e.preventDefault();
            const orientation = document.getElementById('orientation').value;
            const distance = parseFloat(document.getElementById('distance').value);

            // Get wall dimensions
            const wall = this.editor.wall;
            let newLine = {
                id: `line-${Date.now()}`,
                orientation: orientation,
                moveable: true,
                snap_to: true,
                wall_id: wall.id
            };

            if (orientation === 'horizontal') {
                newLine.x_cord = 0;
                newLine.y_cord = wall.height - distance;
                newLine.length = wall.width;
                newLine.angle = 0;
                newLine.alignment = 'center';
            } else {
                newLine.x_cord = distance;
                newLine.y_cord = 0;
                newLine.length = wall.height;
                newLine.angle = 90;
                newLine.alignment = 'center';
            }

            // Add to wall_lines and update
            if (!wall.wall_lines) wall.wall_lines = [];
            wall.wall_lines.push(newLine);

            // Optionally, save to backend here (AJAX/fetch)

            // Redraw lines
            this.loadLines();
            this.drawLines();

            // Hide modal
            modal.hide();
        };
    }

    handleCanvasMouseDown(e) {
        if (!this.isCreating) return;

        const rect = this.canvas.getBoundingClientRect();
        this.activeLine.x = e.clientX - rect.left;
        this.activeLine.y = e.clientY - rect.top;
    }

    handleCanvasMouseMove(e) {
        if (!this.isCreating || !this.activeLine) return;

        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        // Determine line orientation based on initial movement
        if (!this.activeLine.orientation) {
            const dx = Math.abs(mouseX - this.activeLine.x);
            const dy = Math.abs(mouseY - this.activeLine.y);
            this.activeLine.orientation = dx > dy ? 'horizontal' : 'vertical';
        }

        if (this.activeLine.orientation === 'horizontal') {
            this.activeLine.length = mouseX - this.activeLine.x;
            this.activeLine.angle = 0;
            this.activeLine.y = mouseY;
        } else {
            this.activeLine.length = mouseY - this.activeLine.y;
            this.activeLine.angle = 90;
            this.activeLine.x = mouseX;
        }

        this.drawLines();
    }

    handleCanvasMouseUp() {
        if (!this.isCreating || !this.activeLine) return;

        // Convert back to inches for storage
        const lineData = {
            x_cord: this.activeLine.x / this.scale,
            y_cord: this.activeLine.y / this.scale,
            length: Math.abs(this.activeLine.length) / this.scale,
            angle: this.activeLine.angle,
            orientation: this.activeLine.orientation,
            alignment: 'center',
            distance: 0,
            snap_to: true,
            moveable: true,
            wall_id: this.editor.wall.id
        };

        this.saveLine(lineData);
        this.isCreating = false;
        this.activeLine = null;
        this.container.style.cursor = '';
        this.drawLines();
    }

    async saveLine(lineData) {
        try {
            const response = await fetch('/save-snap-line', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify(lineData)
            });

            const result = await response.json();
            if (result.success) {
                this.lines.push(result.line);
                this.updateSidebar();
            }
        } catch (error) {
            console.error('Error saving snap line:', error);
        }
    }

    async deleteLine(lineId) {
        try {
            const response = await fetch(`/delete-snap-line/${lineId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': window.csrfToken
                }
            });

            if (response.ok) {
                this.lines = this.lines.filter(line => line.id !== lineId);
                this.drawLines();
                this.updateSidebar();
            }
        } catch (error) {
            console.error('Error deleting snap line:', error);
        }
    }

    editLine(lineId) {
        // Implement line editing functionality
        console.log('Editing line:', lineId);
    }

    drawLines() {
        // Clear previous lines
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.editor.drawWall(); // Redraw wall and grid

        // Draw all lines
        this.ctx.strokeStyle = this.lineColor;
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);

        this.lines.forEach(line => {
            this.ctx.beginPath();
            
            if (line.orientation === 'horizontal') {
                this.ctx.moveTo(0, line.y);
                this.ctx.lineTo(this.canvas.width, line.y);
            } else {
                this.ctx.moveTo(line.x, 0);
                this.ctx.lineTo(line.x, this.canvas.height);
            }
            
            this.ctx.stroke();
        });

        // Draw active line in creation
        if (this.isCreating && this.activeLine) {
            this.ctx.strokeStyle = '#ff0000';
            this.ctx.beginPath();
            
            if (this.activeLine.orientation === 'horizontal') {
                this.ctx.moveTo(this.activeLine.x, this.activeLine.y);
                this.ctx.lineTo(this.activeLine.x + this.activeLine.length, this.activeLine.y);
            } else {
                this.ctx.moveTo(this.activeLine.x, this.activeLine.y);
                this.ctx.lineTo(this.activeLine.x, this.activeLine.y + this.activeLine.length);
            }
            
            this.ctx.stroke();
        }

        this.ctx.setLineDash([]);
    }

    updateSidebar() {
        const sidebarContent = document.getElementById('snap-lines-content');
        if (!sidebarContent) return;

        sidebarContent.innerHTML = `
            <div class="snap-lines-list">
                ${this.lines.map(line => `
                    <div class="snap-line-item" data-line-id="${line.id}">
                        <span>${line.orientation} line (${line.distance}")</span>
                        <div class="line-actions">
                            <button class="btn btn-sm btn-edit"><i class="fas fa-edit"></i></button>
                            <button class="btn btn-sm btn-delete"><i class="fas fa-trash"></i></button>
                        </div>
                    </div>
                `).join('')}
                ${this.lines.length === 0 ? '<div class="empty-message">No snap lines added yet</div>' : ''}
            </div>
        `;

        // Reattach event listeners
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lineId = e.target.closest('.snap-line-item').dataset.lineId;
                this.editLine(lineId);
            });
        });

        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lineId = e.target.closest('.snap-line-item').dataset.lineId;
                this.deleteLine(lineId);
            });
        });
    }

    checkSnap(artwork) {
        if (!artwork) return null;

        const artworkRect = {
            left: artwork.x_position * this.scale,
            right: (artwork.x_position + artwork.width) * this.scale,
            top: (this.editor.wall.height - artwork.y_position - artwork.height) * this.scale,
            bottom: (this.editor.wall.height - artwork.y_position) * this.scale,
            centerX: (artwork.x_position + artwork.width / 2) * this.scale,
            centerY: (this.editor.wall.height - artwork.y_position - artwork.height / 2) * this.scale
        };

        for (const line of this.lines) {
            if (!line.snap_to) continue;

            if (line.orientation === 'horizontal') {
                // Check top, center, bottom alignment
                if (Math.abs(artworkRect.top - line.y) < this.snapDistance) {
                    return { y: line.y / this.scale - (this.editor.wall.height - artwork.height), type: 'top' };
                }
                if (Math.abs(artworkRect.centerY - line.y) < this.snapDistance) {
                    return { y: line.y / this.scale - (this.editor.wall.height - artwork.height / 2), type: 'center' };
                }
                if (Math.abs(artworkRect.bottom - line.y) < this.snapDistance) {
                    return { y: line.y / this.scale - this.editor.wall.height, type: 'bottom' };
                }
            } else {
                // Check left, center, right alignment
                if (Math.abs(artworkRect.left - line.x) < this.snapDistance) {
                    return { x: line.x / this.scale, type: 'left' };
                }
                if (Math.abs(artworkRect.centerX - line.x) < this.snapDistance) {
                    return { x: line.x / this.scale - artwork.width / 2, type: 'center' };
                }
                if (Math.abs(artworkRect.right - line.x) < this.snapDistance) {
                    return { x: line.x / this.scale - artwork.width, type: 'right' };
                }
            }
        }

        return null;
    }
}