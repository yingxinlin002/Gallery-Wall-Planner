export class WallCanvas {
    constructor(canvasElement, wallWidth, wallHeight, wallColor = '#ffffff') {
        this.canvas = canvasElement;
        this.ctx = canvasElement.getContext('2d');
        this.wallWidth = wallWidth;
        this.wallHeight = wallHeight;
        this.wallColor = wallColor;
        this.scale = 1;
        
        this.resize();
        this.drawGrid();
    }

    resize() {
        const container = this.canvas.parentElement;
        this.scale = Math.min(
            container.clientWidth / this.wallWidth,
            container.clientHeight / this.wallHeight
        );
        
        this.canvas.width = this.wallWidth * this.scale;
        this.canvas.height = this.wallHeight * this.scale;
        
        this.drawGrid();
    }

    drawGrid() {
        this.ctx.fillStyle = this.wallColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.strokeStyle = '#e0e0e0';
        this.ctx.lineWidth = 1;
        const gridSize = 12; // inches
        
        // Vertical lines
        for (let x = 0; x <= this.wallWidth; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.scale, 0);
            this.ctx.lineTo(x * this.scale, this.canvas.height);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= this.wallHeight; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.scale);
            this.ctx.lineTo(this.canvas.width, y * this.scale);
            this.ctx.stroke();
        }
    }

    // In WallCanvas.js
    getScale() {
        // Return the scale factor (pixels per inch)
        return Math.min(
            this.canvas.width / this.wallWidth,
            this.canvas.height / this.wallHeight
        );
    }

    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawGrid();
    }
}