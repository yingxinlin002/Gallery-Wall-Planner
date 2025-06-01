export class ObjectManager {
    constructor(wallCanvas, measurementManager, collisionDetector) {
        this.wallCanvas = wallCanvas;
        this.measurementManager = measurementManager;
        this.collisionDetector = collisionDetector;
        this.objects = [];
        this.selectedObject = null;
        
        this.initInteractJS();
    }

    initObjects(objectsData) {
        objectsData.forEach(objData => {
            this.addObject(objData);
        });
    }

    addObject(objData) {
        const object = {
            ...objData,
            element: this.createObjectElement(objData),
            isColliding: false
        };
        
        this.objects.push(object);
        this.positionObject(object);
        this.makeDraggable(object);
        
        return object;
    }

    createObjectElement(objData) {
        const objectLayer = document.getElementById('canvas-objects-layer');
        const objectElement = document.createElement('div');
        
        objectElement.className = 'canvas-object';
        objectElement.id = `object-${objData.id}`;
        objectElement.innerHTML = `
            <div class="object-content">
                <span class="object-name">${objData.name}</span>
                ${objData.image ? `<img src="${objData.image}" alt="${objData.name}" class="object-image">` : ''}
            </div>
            <div class="object-handle object-handle-resize"></div>
        `;
        
        objectLayer.appendChild(objectElement);
        return objectElement;
    }

    positionObject(object) {
        const scale = this.wallCanvas.getScale();
        const element = object.element;
        
        element.style.left = `${object.x * scale}px`;
        element.style.top = `${object.y * scale}px`;
        element.style.width = `${object.width * scale}px`;
        element.style.height = `${object.height * scale}px`;
    }

    makeDraggable(object) {
        const scale = this.wallCanvas.getScale();
        
        interact(object.element).draggable({
            inertia: true,
            modifiers: [
                interact.modifiers.restrictRect({
                    restriction: 'parent',
                    endOnly: false
                })
            ],
            listeners: {
                start: (event) => {
                    this.selectedObject = object;
                    object.element.style.zIndex = '100';
                    this.measurementManager.clear();
                },
                move: (event) => {
                    // Update object position
                    object.x += event.dx / scale;
                    object.y += event.dy / scale;
                    
                    // Keep within wall bounds
                    object.x = Math.max(0, Math.min(object.x, this.wallCanvas.wallWidth - object.width));
                    object.y = Math.max(0, Math.min(object.y, this.wallCanvas.wallHeight - object.height));
                    
                    this.positionObject(object);
                    
                    // Check for collisions
                    object.isColliding = this.collisionDetector.checkCollisions(object, this.objects);
                    this.updateObjectAppearance(object);
                    
                    // Show measurements
                    this.measurementManager.drawMeasurements(
                        object.x, 
                        object.y, 
                        object.width, 
                        object.height,
                        this.wallCanvas.wallWidth,
                        this.wallCanvas.wallHeight,
                        scale
                    );
                },
                end: (event) => {
                    object.element.style.zIndex = '2';
                    this.measurementManager.clear();
                    // Here you would typically save the new position to your backend
                }
            }
        });
    }

    updateObjectAppearance(object) {
        if (object.isColliding) {
            object.element.classList.add('collision-highlight');
        } else {
            object.element.classList.remove('collision-highlight');
        }
    }
}