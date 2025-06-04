import { WallCanvas } from './modules/WallCanvas.js';
import { ObjectManager } from './modules/ObjectManager.js';
import { MeasurementManager } from './modules/MeasurementManager.js';
import { CollisionDetector } from './modules/CollisionDetector.js';

class LockObjectsApp {
    constructor() {
        this.wallData = window.wallData;
        this.urls = window.urls;
        this.csrfToken = window.csrfToken;
        
        this.initElements();
        this.initModules();
        this.initEventListeners();
        this.initSidebarToggle();
    }
    
    initElements() {
        this.elements = {
            wallCanvas: document.getElementById('wall-canvas'),
            canvasContainer: document.querySelector('.canvas-container'),
            leftPanel: document.getElementById('leftPanel'),
            toggleSidebarBtn: document.getElementById('toggleSidebar'),
            sidebarToggleIcon: document.getElementById('sidebarToggleIcon'),
            permanentObjectsList: document.getElementById('permanentObjectsList'),
            collisionIndicator: document.getElementById('collision-indicator'),
            saveBtn: document.getElementById('saveBtn'),
            newItemForm: document.getElementById('newItemForm'),
            editItemForm: document.getElementById('editItemForm'),
            editItemModal: new bootstrap.Modal(document.getElementById('editItemModal'))
        };
    }
    
    initModules() {
        this.wallCanvas = new WallCanvas(
            this.elements.wallCanvas, 
            this.wallData.width, 
            this.wallData.height, 
            this.wallData.color
        );
        
        this.measurementManager = new MeasurementManager(
            this.elements.canvasContainer
        );
        
        this.collisionDetector = new CollisionDetector();
        
        this.objectManager = new ObjectManager(
            this.wallCanvas,
            this.measurementManager,
            this.collisionDetector
        );
        
        // Initialize with existing objects
        this.objectManager.initObjects(this.wallData.permanentObjects);
    }
    
    initEventListeners() {
        // Window resize
        window.addEventListener('resize', () => {
            this.wallCanvas.resize();
            this.objectManager.objects.forEach(obj => {
                this.objectManager.positionObject(obj);
            });
        });
        
        // Save button
        this.elements.saveBtn.addEventListener('click', (e) => {
            if (this.hasCollisions()) {
                e.preventDefault();
                this.showCollisionModal();
            }
        });
        
        // Continue anyway button
        document.getElementById('continueAnywayBtn').addEventListener('click', () => {
            document.querySelector('.footer-buttons form').submit();
        });
        
        // Edit buttons
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const itemId = btn.getAttribute('data-id');
                this.showEditModal(itemId);
            });
        });
        
        // Delete buttons
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const itemId = btn.getAttribute('data-id');
                if (confirm('Are you sure you want to delete this fixture?')) {
                    this.deleteObject(itemId);
                }
            });
        });
        
        // New item form submission
        this.elements.newItemForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleNewItemForm();
        });makeObjectsDraggable
        
        // Collision detection interval
        setInterval(() => {
            const hasCollisions = this.hasCollisions();
            this.elements.collisionIndicator.classList.toggle('d-none', !hasCollisions);
        }, 500);
    }
    
    initSidebarToggle() {
        this.elements.toggleSidebarBtn.addEventListener('click', () => {
            this.elements.leftPanel.classList.toggle('collapsed');
            const isCollapsed = this.elements.leftPanel.classList.contains('collapsed');
            
            this.elements.sidebarToggleIcon.classList.toggle('bi-chevron-left', !isCollapsed);
            this.elements.sidebarToggleIcon.classList.toggle('bi-chevron-right', isCollapsed);
            
            // Trigger resize after animation completes
            setTimeout(() => {
                this.wallCanvas.resize();
                this.objectManager.objects.forEach(obj => {
                    this.objectManager.positionObject(obj);
                });
            }, 300);
        });
    }
    
    hasCollisions() {
        return this.objectManager.objects.some(obj => obj.isColliding);
    }
    
    showCollisionModal() {
        const modal = new bootstrap.Modal(document.getElementById('collisionModal'));
        modal.show();
    }
    
    showEditModal(itemId) {
        const object = this.objectManager.objects.find(obj => obj.id == itemId);
        if (!object) return;
        
        // Populate the edit form
        document.getElementById('editObjId').value = object.id;
        const modalBody = this.elements.editItemForm.querySelector('.modal-body');
        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="editItemName" class="form-label">Name</label>
                        <input type="text" class="form-control" id="editItemName" name="name" value="${object.name}" required>
                    </div>
                    <div class="mb-3">
                        <label for="editItemWidth" class="form-label">Width (inches)</label>
                        <input type="number" class="form-control" id="editItemWidth" name="width" min="0" step="0.1" value="${object.width}" required>
                    </div>
                    <div class="mb-3">
                        <label for="editItemHeight" class="form-label">Height (inches)</label>
                        <input type="number" class="form-control" id="editItemHeight" name="height" min="0" step="0.1" value="${object.height}" required>
                    </div>
                    <div class="mb-3">
                        <label for="editItemColor" class="form-label">Color</label>
                        <input type="color" class="form-control form-control-color" id="editItemColor" name="color" value="${object.color || '#6495ed'}">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="position-controls">
                        <h6>Position</h6>
                        <div class="mb-3">
                            <label for="editItemX" class="form-label">X Position (inches)</label>
                            <input type="number" class="form-control" id="editItemX" name="x" min="0" step="0.1" value="${object.x}">
                        </div>
                        <div class="mb-3">
                            <label for="editItemY" class="form-label">Y Position (inches)</label>
                            <input type="number" class="form-control" id="editItemY" name="y" min="0" step="0.1" value="${object.y}">
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.elements.editItemModal.show();
    }
    
    deleteObject(itemId) {
        fetch(`${window.urls.deleteObject}/${itemId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            }
        }).then(response => {
            if (response.ok) {
                window.location.reload();
            }
        });
    }
    
    handleNewItemForm() {
        const formData = new FormData(this.elements.newItemForm);
        
        fetch(window.urls.addObject, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Add the new object to the list
                this.addObjectToList(data.object);
                // Add the object to the canvas
                this.objectManager.addObject(data.object);
                // Close the modal
                bootstrap.Modal.getInstance(this.elements.newItemForm.closest('.modal')).hide();
                // Reset the form
                this.elements.newItemForm.reset();
                console.log('Object added successfully:', data.object);
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while adding the fixture');
        });
    }

    addObjectToList(obj) {
        const newItem = document.createElement('div');
        newItem.className = 'list-group-item wall-item d-flex justify-content-between align-items-center';
        newItem.setAttribute('draggable', 'true');
        newItem.setAttribute('data-id', obj.id);
        newItem.setAttribute('data-obj', JSON.stringify(obj));
        newItem.innerHTML = `
            <span>${obj.name}</span>
            <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary edit-btn" data-id="${obj.id}">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-outline-danger delete-btn" data-id="${obj.id}">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        
        this.elements.permanentObjectsList.appendChild(newItem);
        
        // Reattach event listeners to the new buttons
        newItem.querySelector('.edit-btn').addEventListener('click', (e) => {
            const itemId = e.currentTarget.getAttribute('data-id');
            this.showEditModal(itemId);
        });
        
        newItem.querySelector('.delete-btn').addEventListener('click', (e) => {
            const itemId = e.currentTarget.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this fixture?')) {
                this.deleteObject(itemId);
            }
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LockObjectsApp();
});