// MeasurementManager.js - Modified to work without ES6 modules
class MeasurementManager {
    constructor(container) {
        this.container = container;
        this.linesContainer = null;
        this.createLinesContainer();
    }

    createLinesContainer() {
        this.linesContainer = document.createElement('div');
        this.linesContainer.className = 'measurement-lines-container';
        this.linesContainer.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 5;
        `;
        this.container.appendChild(this.linesContainer);
    }

    clear() {
        this.linesContainer.innerHTML = '';
    }

    drawMeasurements(x, y, width, height, wallWidth, wallHeight, scale) {
        this.clear();
        
        // Convert to canvas coordinates (y=0 at bottom)
        const canvasY = wallHeight - y - height;
        
        const left = x * scale;
        const top = canvasY * scale;
        const right = (x + width) * scale;
        const bottom = (canvasY + height) * scale;
        const canvasWidth = wallWidth * scale;
        const canvasHeight = wallHeight * scale;

        // Left measurement (distance from left edge)
        this.createMeasurementLine(left, top, left, 0, 'left', `${x.toFixed(1)}"`);
        
        // Right measurement (distance from right edge)
        this.createMeasurementLine(right, top, right, 0, 'right', `${(wallWidth - x - width).toFixed(1)}"`);
        
        // Top measurement (distance from top edge)
        this.createMeasurementLine(left, top, 0, top, 'top', `${(wallHeight - y - height).toFixed(1)}"`);
        
        // Bottom measurement (distance from bottom edge)
        this.createMeasurementLine(left, bottom, 0, bottom, 'bottom', `${y.toFixed(1)}"`);
    }

    createMeasurementLine(x1, y1, x2, y2, position, text) {
        const line = document.createElement('div');
        line.className = `measurement-line ${position}`;
        line.style.cssText = `
            position: absolute;
            border: 1px dashed rgba(100, 100, 100, 0.7);
        `;
        
        if (position === 'left' || position === 'right') {
            line.style.left = `${x1}px`;
            line.style.top = `${y2}px`;
            line.style.width = '1px';
            line.style.height = `${y1 - y2}px`;
        } else {
            line.style.left = `${x2}px`;
            line.style.top = `${y1}px`;
            line.style.width = `${x1 - x2}px`;
            line.style.height = '1px';
        }
        
        const label = document.createElement('div');
        label.className = 'measurement-label';
        label.textContent = text;
        label.style.cssText = `
            position: absolute;
            background: rgba(255, 255, 255, 0.8);
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 12px;
            color: #333;
        `;
        
        if (position === 'left' || position === 'right') {
            label.style.left = `${x1}px`;
            label.style.top = `${(y1 + y2) / 2}px`;
            label.style.transform = 'translate(-50%, -50%)';
        } else {
            label.style.left = `${(x1 + x2) / 2}px`;
            label.style.top = `${y1}px`;
            label.style.transform = 'translate(-50%, -50%) rotate(-90deg)';
        }
        
        this.linesContainer.appendChild(line);
        this.linesContainer.appendChild(label);
    }
}