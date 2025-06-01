import { WallCanvas } from './WallCanvas.js';
import { ObjectManager } from './ObjectManager.js';
import { MeasurementManager } from './MeasurementManager.js';
import { CollisionDetector } from './CollisionDetector.js';

export function initCanvas(wallData) {
    // Initialize canvas
    const canvasElement = document.getElementById('wall-canvas');
    const canvasContainer = document.querySelector('.canvas-container');
    
    const wallCanvas = new WallCanvas(
        canvasElement,
        wallData.width,
        wallData.height,
        wallData.color
    );

    // Initialize managers
    const measurementManager = new MeasurementManager(canvasContainer);
    const collisionDetector = new CollisionDetector();
    const objectManager = new ObjectManager(
        wallCanvas,
        measurementManager,
        collisionDetector
    );

    // Initialize objects if any
    if (wallData.permanentObjects) {
        objectManager.initObjects(wallData.permanentObjects);
    }

    return {
        wallCanvas,
        objectManager,
        measurementManager,
        collisionDetector
    };
}