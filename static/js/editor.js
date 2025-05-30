import { EvenSpacing } from './even_spacing.js';
import { MeasurementLinesManager } from './measurement_lines_manager.js';
document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    const currentWall = window.currentWallData;
    let selectedArtworkId = null;
    let selectedLineId = null;
    let artworkElements = {};
    let lineElements = {};
    let scaleFactor = 1;
    let isSidebarCollapsed = false;

    // Initialize the editor when DOM is loaded
    setTimeout(() => {
        initializeCanvas();
        loadArtwork();
        loadSnapLines();
        setupEventListeners();
        console.log('Editor initialized');
    }, 100);

    function initializeCanvas() {
        console.log('Initializing canvas...');
        const container = document.getElementById('canvas-container');
        const wallBg = document.getElementById('wall-background');

        console.log('Container dimensions:', container.clientWidth, container.clientHeight);
        console.log('Wall dimensions:', currentWall.width, currentWall.height);

        const maxWidth = container.clientWidth * 0.9;
        const maxHeight = container.clientHeight * 0.9;
        const widthRatio = maxWidth / currentWall.width;
        const heightRatio = maxHeight / currentWall.height;

        scaleFactor = Math.min(widthRatio, heightRatio);
        const scaledWidth = currentWall.width * scaleFactor;
        const scaledHeight = currentWall.height * scaleFactor;

        console.log('Scale factor:', scaleFactor);
        console.log('Scaled dimensions:', scaledWidth, scaledHeight);

        wallBg.style.width = scaledWidth + 'px';
        wallBg.style.height = scaledHeight + 'px';
        wallBg.style.backgroundColor = currentWall.color;
        wallBg.style.left = (container.clientWidth - scaledWidth) / 2 + 'px';
        wallBg.style.top = (container.clientHeight - scaledHeight) / 2 + 'px';

        console.log('Wall background position:', wallBg.offsetLeft, wallBg.offsetTop);

        // Wall reference object for measurement manager
        const wallRef = {
            wallLeft: wallBg.offsetLeft,
            wallRight: wallBg.offsetLeft + wallBg.clientWidth,
            wallTop: wallBg.offsetTop,
            wallBottom: wallBg.offsetTop + wallBg.clientHeight,
            wallWidth: currentWall.width,
            wallHeight: currentWall.height,
            canvasHeight: container.clientHeight,
            scale: scaleFactor
        };

        console.log('Wall reference:', wallRef);

        window.measurementManager = new MeasurementLinesManager(container, wallRef);

        // Move click listener inside initialization
        wallBg.addEventListener('click', () => {
            window.measurementManager.clearMeasurementLines();
        });
    }

    function setupEventListeners() {
        // Add any additional event listeners here
    }

    window.toggleSidebar = function() {
        const sidebar = document.getElementById('sidebar');
        const toggleIcon = document.getElementById('sidebar-toggle-icon');
        isSidebarCollapsed = !isSidebarCollapsed;
        if (isSidebarCollapsed) {
            sidebar.classList.add('sidebar-collapsed');
            toggleIcon.classList.remove('fa-chevron-left');
            toggleIcon.classList.add('fa-chevron-right');
        } else {
            sidebar.classList.remove('sidebar-collapsed');
            toggleIcon.classList.remove('fa-chevron-right');
            toggleIcon.classList.add('fa-chevron-left');
        }
    };

    window.toggleSection = function(sectionId) {
        const section = document.getElementById(sectionId);
        const header = section.previousElementSibling;
        const icon = header.querySelector('.fa-chevron-down');
        if (section.style.display === 'none') {
            section.style.display = 'block';
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        } else {
            section.style.display = 'none';
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        }
    };

    window.selectArtwork = function(artworkId) {
        if (selectedArtworkId) {
            const prevBtn = document.querySelector(`.artwork-btn[data-artwork-id="${selectedArtworkId}"]`);
            const prevElement = artworkElements[selectedArtworkId];
            if (prevBtn) prevBtn.classList.remove('selected');
            if (prevElement) prevElement.classList.remove('selected');
        }
        selectedArtworkId = artworkId;
        const btn = document.querySelector(`.artwork-btn[data-artwork-id="${artworkId}"]`);
        const element = artworkElements[artworkId];
        if (btn) btn.classList.add('selected');
        if (element) {
            element.classList.add('selected');
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Show measurement lines for this artwork
            window.showArtworkMeasurements(artworkId);
        }
        console.log('Selected artwork:', artworkId);
    };

    function loadArtwork() {
        // Load unplaced artwork
        window.unplacedArtworkData.forEach(function(artwork) {
            addArtworkToCanvas({
                id: artwork.id,
                name: artwork.name,
                width: artwork.width,
                height: artwork.height,
                x: 0,
                y: 0,
                isPlaced: false
            });
        });
        // Load placed artwork
        window.currentWallArtworkData.forEach(function(artwork) {
            addArtworkToCanvas({
                id: artwork.id,
                name: artwork.name,
                width: artwork.width,
                height: artwork.height,
                x: artwork.x_position,
                y: artwork.y_position,
                isPlaced: true
            });
        });
    }

    function addArtworkToCanvas(artwork) {
        const container = document.getElementById('canvas-container');
        const wallBg = document.getElementById('wall-background');

        // Wait for wallBg to be properly sized
        if (!wallBg.clientWidth || !wallBg.clientHeight) {
            setTimeout(() => addArtworkToCanvas(artwork), 100);
            return;
        }

        const element = document.createElement('div');
        element.className = 'artwork-draggable';
        element.id = 'artwork-' + artwork.id;
        element.dataset.artworkId = artwork.id;
        element.style.width = (artwork.width * scaleFactor) + 'px';
        element.style.height = (artwork.height * scaleFactor) + 'px';

        if (artwork.isPlaced) {
            element.style.left = (wallBg.offsetLeft + artwork.x * scaleFactor) + 'px';
            element.style.top = (wallBg.offsetTop + artwork.y * scaleFactor) + 'px';
        } else {
            // Position unplaced artwork just outside the wall (right side)
            element.style.left = (wallBg.offsetLeft + wallBg.clientWidth + 20) + 'px';
            element.style.top = (wallBg.offsetTop + 20) + 'px';
        }

        element.textContent = artwork.name;
        makeDraggable(element, artwork.id);
        container.appendChild(element);
        artworkElements[artwork.id] = element;
    }

    function makeDraggable(element, artworkId) {
        let isDragging = false;
        let offsetX, offsetY;
        element.addEventListener('mousedown', startDrag);
        function startDrag(e) {
            isDragging = true;
            offsetX = e.clientX - element.getBoundingClientRect().left;
            offsetY = e.clientY - element.getBoundingClientRect().top;
            element.style.zIndex = '100';
            document.addEventListener('mousemove', drag);
            document.addEventListener('mouseup', stopDrag);
            e.preventDefault();
        }
        function drag(e) {
            if (!isDragging) return;
            const newLeft = e.clientX - offsetX;
            const newTop = e.clientY - offsetY;
            element.style.left = newLeft + 'px';
            element.style.top = newTop + 'px';
        }
        function stopDrag() {
            isDragging = false;
            element.style.zIndex = '';
            document.removeEventListener('mousemove', drag);
            document.removeEventListener('mouseup', stopDrag);
            const wallBg = document.getElementById('wall-background');
            const wallRect = wallBg.getBoundingClientRect();
            const artRect = element.getBoundingClientRect();
            const isOnWall = !(
                artRect.right < wallRect.left || 
                artRect.left > wallRect.right || 
                artRect.bottom < wallRect.top || 
                artRect.top > wallRect.bottom
            );
            if (isOnWall) {
                const x = (artRect.left - wallRect.left) / scaleFactor;
                const y = (artRect.top - wallRect.top) / scaleFactor;
                console.log(`Artwork ${artworkId} placed at (${x.toFixed(1)}, ${y.toFixed(1)})`);
                element.classList.add('placed');
            } else {
                // TODO: Handle artwork moved off wall
            }
        }
    }

    function loadSnapLines() {
        window.wallLinesData.forEach(function(line) {
            addSnapLineToCanvas({
                id: line.id,
                name: line.name,
                orientation: line.orientation,
                position: line.position
            });
        });
    }

    function addSnapLineToCanvas(line) {
        const container = document.getElementById('canvas-container');
        const wallBg = document.getElementById('wall-background');
        const element = document.createElement('div');
        element.className = `snap-line ${line.orientation}-line`;
        element.id = 'line-' + line.id;
        element.dataset.lineId = line.id;
        if (line.orientation === 'horizontal') {
            element.style.width = wallBg.clientWidth + 'px';
            element.style.height = '2px';
            element.style.left = wallBg.offsetLeft + 'px';
            element.style.top = (wallBg.offsetTop + (wallBg.clientHeight * line.position / 100)) + 'px';
        } else {
            element.style.width = '2px';
            element.style.height = wallBg.clientHeight + 'px';
            element.style.left = (wallBg.offsetLeft + (wallBg.clientWidth * line.position / 100)) + 'px';
            element.style.top = wallBg.offsetTop + 'px';
        }
        container.appendChild(element);
        lineElements[line.id] = element;
    }

    window.showSnapLineModal = function(line = null) {
        const modal = document.getElementById('snap-line-modal');
        const title = document.getElementById('modal-title');
        const saveBtn = document.getElementById('modal-save-btn');
        if (line) {
            title.textContent = 'Edit Snap Line';
            document.getElementById('line-name').value = line.name;
            document.getElementById('line-orientation').value = line.orientation;
            document.getElementById('line-position').value = line.position;
            selectedLineId = line.id;
            saveBtn.textContent = 'Update';
        } else {
            title.textContent = 'Add Snap Line';
            document.getElementById('line-name').value = '';
            document.getElementById('line-orientation').value = 'horizontal';
            document.getElementById('line-position').value = 50;
            selectedLineId = null;
            saveBtn.textContent = 'Save';
        }
        modal.style.display = 'flex';
    };

    window.closeModal = function() {
        document.getElementById('snap-line-modal').style.display = 'none';
    };

    window.saveSnapLine = function() {
        const name = document.getElementById('line-name').value.trim();
        const orientation = document.getElementById('line-orientation').value;
        const position = parseInt(document.getElementById('line-position').value);
        if (!name) {
            alert('Please enter a name for the snap line');
            return;
        }
        if (isNaN(position) || position < 0 || position > 100) {
            alert('Please enter a valid position between 0 and 100');
            return;
        }
        const lineData = {
            id: selectedLineId || generateId(),
            name: name,
            orientation: orientation,
            position: position,
            wall_id: currentWall.id
        };
        if (selectedLineId) {
            updateSnapLine(lineData);
        } else {
            addNewSnapLine(lineData);
        }
        closeModal();
    };

    function addNewSnapLine(lineData) {
        // TODO: Send to server via AJAX
        console.log('Adding new snap line:', lineData);
        addSnapLineToCanvas(lineData);
        const list = document.getElementById('snap-lines-section');
        if (list.querySelector('.no-items-message')) {
            list.innerHTML = '';
        }
        const item = document.createElement('div');
        item.className = 'snap-line-item';
        item.innerHTML = `
            <button class="snap-line-btn" 
                    onclick="editSnapLine('${lineData.id}')"
                    data-line-id="${lineData.id}">
                ${lineData.name} (${lineData.position}% ${lineData.orientation})
            </button>
        `;
        list.appendChild(item);
    }

    function updateSnapLine(lineData) {
        // TODO: Send update to server via AJAX
        console.log('Updating snap line:', lineData);
        const element = document.getElementById('line-' + lineData.id);
        if (element) {
            const wallBg = document.getElementById('wall-background');
            if (lineData.orientation === 'horizontal') {
                element.style.top = (wallBg.offsetTop + (wallBg.clientHeight * lineData.position / 100)) + 'px';
            } else {
                element.style.left = (wallBg.offsetLeft + (wallBg.clientWidth * lineData.position / 100)) + 'px';
            }
        }
        const btn = document.querySelector(`.snap-line-btn[data-line-id="${lineData.id}"]`);
        if (btn) {
            btn.textContent = `${lineData.name} (${lineData.position}% ${lineData.orientation})`;
        }
    }

    window.editSnapLine = function(lineId) {
        const element = lineElements[lineId];
        if (!element) return;
        const isHorizontal = element.classList.contains('horizontal-line');
        const wallBg = document.getElementById('wall-background');
        let position;
        if (isHorizontal) {
            position = ((parseFloat(element.style.top) - wallBg.offsetTop) / wallBg.clientHeight) * 100;
        } else {
            position = ((parseFloat(element.style.left) - wallBg.offsetLeft) / wallBg.clientWidth) * 100;
        }
        const btn = document.querySelector(`.snap-line-btn[data-line-id="${lineId}"]`);
        const name = btn ? btn.textContent.split(' (')[0] : 'Line ' + lineId;
        window.showSnapLineModal({
            id: lineId,
            name: name,
            orientation: isHorizontal ? 'horizontal' : 'vertical',
            position: Math.round(position)
        });
    };

    function generateId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    window.evenSpacing = function() {
        if (!window.evenSpacingInstance) {
            window.evenSpacingInstance = new EvenSpacing({
                currentWall: window.currentWallData,
                currentWallArtworkData: window.currentWallArtworkData,
                updateArtworkPosition: function(artworkId, x, y) {
                    // Update the visual element
                    const element = artworkElements[artworkId];
                    if (element) {
                        const wallBg = document.getElementById('wall-background');
                        element.style.left = (wallBg.offsetLeft + x * scaleFactor) + 'px';
                        element.style.top = (wallBg.offsetTop + y * scaleFactor) + 'px';
                        element.classList.add('placed');
                    }
                    // Update the artwork data
                    const artwork = window.currentWallArtworkData.find(a => a.id === artworkId);
                    if (artwork) {
                        artwork.x_position = x;
                        artwork.y_position = y;
                    }
                }
            });
        }
        window.evenSpacingInstance.toggle();
    };

    window.showArtworkMeasurements = function(artworkId) {
        const artwork = window.currentWallArtworkData.find(a => a.id === artworkId);
        if (!artwork) return;
        const measurements = `Width: ${artwork.width} Height: ${artwork.height}`;
        const element = artworkElements[artworkId];
        if (element) {
            element.setAttribute('data-measurements', measurements);
            element.classList.add('show-measurements');
        }
        console.log('Showing measurements for artwork:', artworkId, measurements);
    };

    window.hideArtworkMeasurements = function(artworkId) {
        const element = artworkElements[artworkId];
        if (element) {
            element.removeAttribute('data-measurements');
            element.classList.remove('show-measurements');
        }
        console.log('Hiding measurements for artwork:', artworkId);
    };

    window.addArtworkToWall = function(artworkId) {
        let artwork = window.unplacedArtworkData.find(a => a.id === artworkId);
        if (!artwork) return;

        artwork.x_position = 1;
        artwork.y_position = 1;
        artwork.isPlaced = true;

        window.currentWallArtworkData.push(artwork);
        window.unplacedArtworkData = window.unplacedArtworkData.filter(a => a.id !== artworkId);

        addArtworkToCanvas(artwork);

        const btn = document.querySelector(`.artwork-btn[data-artwork-id="${artworkId}"]`);
        if (btn) {
            const item = btn.closest('.artwork-item');
            if (item) item.remove();
        }

        fetch(`/update_artwork_position/${artworkId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || ''
            },
            body: JSON.stringify({
                x_position: artwork.x_position,
                y_position: artwork.y_position,
                wall_id: window.currentWallData.id
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert('Failed to save artwork position!');
            }
        })
        .catch(() => alert('Failed to save artwork position!'));
    };
});