// Add this to your editor.js or create a new MeasurementLinesManager class

export class MeasurementLinesManager {
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

    drawMeasurementLines(x, y, width, height, scale, canvas, wallWidth, wallHeight) {
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
        const leftLine = this.createLine(left, top, left, 0, 'vertical');
        const leftText = this.createText(left / 2, top / 2, `${x.toFixed(1)}"`, 'vertical');

        // Right measurement line
        const rightLine = this.createLine(right, top, right, 0, 'vertical');
        const rightText = this.createText((right + canvas.width) / 2, top / 2, `${(wallWidth - x - width).toFixed(1)}"`, 'vertical');

        // Top measurement line
        const topLine = this.createLine(left, top, 0, top, 'horizontal');
        const topText = this.createText(left / 2, top / 2, `${(wallHeight - y - height).toFixed(1)}"`, 'horizontal');

        // Bottom measurement line
        const bottomLine = this.createLine(left, bottom, 0, bottom, 'horizontal');
        const bottomText = this.createText(left / 2, (bottom + canvas.height) / 2, `${y.toFixed(1)}"`, 'horizontal');

        this.measurementLines.push(leftLine, rightLine, topLine, bottomLine);
        this.measurementTexts.push(leftText, rightText, topText, bottomText);
    }

    createLine(x1, y1, x2, y2, orientation) {
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