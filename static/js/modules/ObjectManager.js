export class ObjectManager {
    constructor(wallCanvas, measurementManager, collisionDetector) {
        this.wallCanvas = wallCanvas;
        this.measurementManager = measurementManager;
        this.collisionDetector = collisionDetector;
        this.objects = [];
        this.selectedObject = null;
        
        this.initInteractJS();
    }

    initInteractJS() {
        // You can add global Interact.js settings here if needed.
        // For example, set up custom actions, plugins, or default options.
        // If not needed, leave this empty.
    }

    initObjects(objectsData) {
        objectsData.forEach(objData => {
            this.addObject(objData);
        });
    }

    addObject(objData) {
        console.log('Adding object with dimensions:', {
            width: objData.width,
            height: objData.height,
            x: objData.x,
            y: objData.y
        });

        // Create the object with all necessary properties
        const object = {
            id: objData.id,
            name: objData.name,
            width: objData.width,
            height: objData.height,
            x: objData.x,
            y: objData.y,
            image_path: objData.image_path,
            element: null,
            isColliding: false
        };
        
        // Create and store the DOM element
        object.element = this.createObjectElement(object);
        
        // Add to objects array
        this.objects.push(object);
        
        // Position and make draggable
        this.positionObject(object);
        this.makeDraggable(object);
        
        return object;
    }

    createObjectElement(object) {
        const objectLayer = document.getElementById('canvas-objects-layer');
        if (!objectLayer) {
            console.error('Canvas objects layer not found');
            return null;
        }
        const objectElement = document.createElement('div');
        
        objectElement.className = 'canvas-object';
        objectElement.id = `object-${object.id}`;
        
        // Set data attributes for positioning
        objectElement.setAttribute('data-id', object.id);
        objectElement.setAttribute('data-x', object.x);
        objectElement.setAttribute('data-y', object.y);
        objectElement.setAttribute('data-width', object.width);
        objectElement.setAttribute('data-height', object.height);
        
        // Create object content
        const contentHTML = `
            <div class="object-content">
                <span class="object-name">${object.name}</span>
                ${object.image_path ? `<img src="/static/${object.image_path}" alt="${object.name}" class="object-image">` : ''}
            </div>
            <div class="object-handle object-handle-resize"></div>
        `;
        
        objectElement.innerHTML = contentHTML;
        objectLayer.appendChild(objectElement);
        
        return objectElement;
    }

    positionObject(object) {
        const scale = this.wallCanvas.getScale();
        console.log('Positioning object with scale:', scale, 'Calculated dimensions:', {
            width: object.width * scale,
            height: object.height * scale
        });
        const element = object.element;
        
        if (!element) return;
        
        // Convert inches to pixels using the scale
        const widthPx = object.width * scale;
        const heightPx = object.height * scale;
        const leftPx = object.x * scale;
        const topPx = object.y * scale;
        
        element.style.width = `${widthPx}px`;
        element.style.height = `${heightPx}px`;
        element.style.left = `${leftPx}px`;
        element.style.top = `${topPx}px`;
        
        // Update data attributes
        element.setAttribute('data-width', object.width);
        element.setAttribute('data-height', object.height);
        element.setAttribute('data-x', object.x);
        element.setAttribute('data-y', object.y);
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
                    event.target.style.zIndex = '100';
                    this.measurementManager.clear();
                },
                move: (event) => {
                    // Update object position in inches
                    object.x += event.dx / scale;
                    object.y += event.dy / scale;
                    
                    // Keep within wall bounds
                    object.x = Math.max(0, Math.min(object.x, this.wallCanvas.wallWidth - object.width));
                    object.y = Math.max(0, Math.min(object.y, this.wallCanvas.wallHeight - object.height));
                    
                    // Update visual position
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
                    
                    // Send position update to server
                    this.updateObjectPosition(object);
                },
                end: (event) => {
                    event.target.style.zIndex = '2';
                    this.measurementManager.clear();
                }
            }
        });
    }

    updateObjectPosition(object) {
        const url = window.urls.updatePosition(object.id);
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({ 
                x: object.x, 
                y: object.y 
            })
        }).catch(error => {
            console.error('Error updating position:', error);
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