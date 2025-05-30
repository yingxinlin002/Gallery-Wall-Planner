// Add this to your editor.js or create a new MeasurementLinesManager class

class MeasurementLinesManager {
    constructor(canvas, wallRef) {
        this.canvas = canvas;
        this.wallRef = wallRef;
        this.measurementLines = [];
        this.measurementTexts = [];
    }

    clearMeasurementLines() {
        // Remove all measurement lines and text
        this.measurementLines.forEach(line => line.remove());
        this.measurementTexts.forEach(text => text.remove());
        this.measurementLines = [];
        this.measurementTexts = [];
    }

    drawMeasurementLines(x1, y1, x2, y2) {
        // Clear existing measurement lines and texts
        this.clearMeasurementLines();

        // Convert to canvas coordinates
        const cx1 = this.wallRef.wallLeft + x1 * this.wallRef.scale;
        const cy1 = this.wallRef.canvasHeight - (this.wallRef.wallBottom + y2 * this.wallRef.scale);
        const cx2 = this.wallRef.wallLeft + x2 * this.wallRef.scale;
        const cy2 = this.wallRef.canvasHeight - (this.wallRef.wallBottom + y1 * this.wallRef.scale);

        // Wall boundaries
        const wallTop = this.wallRef.canvasHeight - (this.wallRef.wallBottom + this.wallRef.wallHeight * this.wallRef.scale);

        // Create a container for measurement elements
        const container = document.createElement('div');
        container.style.position = 'absolute';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100%';
        container.style.height = '100%';
        container.style.pointerEvents = 'none';
        this.canvas.appendChild(container);

        // Left measurement line
        const leftLine = document.createElement('div');
        leftLine.style.position = 'absolute';
        leftLine.style.top = `${cy1}px`;
        leftLine.style.left = `${this.wallRef.wallLeft}px`;
        leftLine.style.width = `${cx1 - this.wallRef.wallLeft}px`;
        leftLine.style.height = '1px';
        leftLine.style.backgroundColor = 'gray';
        leftLine.style.borderTop = '1px dashed gray';
        container.appendChild(leftLine);
        this.measurementLines.push(leftLine);

        // Left distance text
        const leftDist = x1;
        const leftText = document.createElement('div');
        leftText.style.position = 'absolute';
        leftText.style.top = `${cy1 - 20}px`;
        leftText.style.left = `${(this.wallRef.wallLeft + cx1) / 2 - 20}px`;
        leftText.style.width = '40px';
        leftText.style.textAlign = 'center';
        leftText.textContent = `${leftDist.toFixed(1)}"`;
        leftText.style.color = 'black';
        leftText.style.fontSize = '12px';
        container.appendChild(leftText);
        this.measurementTexts.push(leftText);

        // Right measurement line
        const rightLine = document.createElement('div');
        rightLine.style.position = 'absolute';
        rightLine.style.top = `${cy1}px`;
        rightLine.style.left = `${cx2}px`;
        rightLine.style.width = `${this.wallRef.wallRight - cx2}px`;
        rightLine.style.height = '1px';
        rightLine.style.backgroundColor = 'gray';
        rightLine.style.borderTop = '1px dashed gray';
        container.appendChild(rightLine);
        this.measurementLines.push(rightLine);

        // Right distance text
        const rightDist = this.wallRef.wallWidth - x2;
        const rightText = document.createElement('div');
        rightText.style.position = 'absolute';
        rightText.style.top = `${cy1 - 20}px`;
        rightText.style.left = `${(cx2 + this.wallRef.wallRight) / 2 - 20}px`;
        rightText.style.width = '40px';
        rightText.style.textAlign = 'center';
        rightText.textContent = `${rightDist.toFixed(1)}"`;
        rightText.style.color = 'black';
        rightText.style.fontSize = '12px';
        container.appendChild(rightText);
        this.measurementTexts.push(rightText);

        // Top measurement line
        const topLine = document.createElement('div');
        topLine.style.position = 'absolute';
        topLine.style.top = `${wallTop}px`;
        topLine.style.left = `${cx1}px`;
        topLine.style.width = '1px';
        topLine.style.height = `${cy1 - wallTop}px`;
        topLine.style.backgroundColor = 'gray';
        topLine.style.borderLeft = '1px dashed gray';
        container.appendChild(topLine);
        this.measurementLines.push(topLine);

        // Top distance text
        const topDist = this.wallRef.wallHeight - y2;
        const topText = document.createElement('div');
        topText.style.position = 'absolute';
        topText.style.top = `${(wallTop + cy1) / 2 - 10}px`;
        topText.style.left = `${cx1 + 10}px`;
        topText.style.width = '40px';
        topText.style.textAlign = 'left';
        topText.textContent = `${topDist.toFixed(1)}"`;
        topText.style.color = 'black';
        topText.style.fontSize = '12px';
        container.appendChild(topText);
        this.measurementTexts.push(topText);

        // Bottom measurement line
        const bottomLine = document.createElement('div');
        bottomLine.style.position = 'absolute';
        bottomLine.style.top = `${cy2}px`;
        bottomLine.style.left = `${cx1}px`;
        bottomLine.style.width = '1px';
        bottomLine.style.height = `${(this.wallRef.canvasHeight - this.wallRef.wallBottom) - cy2}px`;
        bottomLine.style.backgroundColor = 'gray';
        bottomLine.style.borderLeft = '1px dashed gray';
        container.appendChild(bottomLine);
        this.measurementLines.push(bottomLine);

        // Bottom distance text
        const bottomDist = y1;
        const bottomText = document.createElement('div');
        bottomText.style.position = 'absolute';
        bottomText.style.top = `${(cy2 + (this.wallRef.canvasHeight - this.wallRef.wallBottom)) / 2 - 10}px`;
        bottomText.style.left = `${cx1 + 10}px`;
        bottomText.style.width = '40px';
        bottomText.style.textAlign = 'left';
        bottomText.textContent = `${bottomDist.toFixed(1)}"`;
        bottomText.style.color = 'black';
        bottomText.style.fontSize = '12px';
        container.appendChild(bottomText);
        this.measurementTexts.push(bottomText);

        // Store the container for cleanup
        this.measurementContainer = container;
        this.measurementLines.push(container);
    }
}

export { MeasurementLinesManager };