import { MeasurementLinesManager } from './measurement_lines_manager.js';
import { positionCanvasObjects, makeObjectsDraggable } from './canvas_objects.js';
import { setupCollapsibleMenus } from './collapsible.js';

window.addEventListener('load', () => {
    const canvas = document.getElementById('wall-canvas');
    const wallWidth = window.wallWidth;
    const wallHeight = window.wallHeight;
    const measurementManager = new MeasurementLinesManager(document.querySelector('.canvas-container'));

    // Set z-index for proper layering
    document.getElementById('canvas-objects-layer').style.zIndex = '2';
    document.querySelectorAll('.canvas-object').forEach(obj => {
        obj.style.zIndex = '2';
    });

    // Initial setup
    resizeCanvas();
    positionCanvasObjects(canvas, wallWidth);
    makeObjectsDraggable(canvas, wallWidth, wallHeight, measurementManager);
    updateDimensionLabels();
    setupCollapsibleMenus();

    // Check for collisions initially and periodically
    checkCollisions();
    setInterval(checkCollisions, 500);
});

window.addEventListener('resize', () => {
    const canvas = document.getElementById('wall-canvas');
    const wallWidth = window.wallWidth;
    positionCanvasObjects(canvas, wallWidth);
    updateDimensionLabels();
});

// You can move checkCollisions and updateDimensionLabels to their own modules if desired.