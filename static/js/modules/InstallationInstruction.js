export class InstallationInstruction {
    constructor(wallData, artworkData) {
        this.wallData = wallData;
        this.artworkData = artworkData;
        this.modal = null;
    }

    show() {
        console.log("Wall Data:", this.wallData);
        console.log("Artwork Data:", this.artworkData);
        // Create modal container
        this.modal = document.createElement('div');
        this.modal.className = 'modal fade';
        this.modal.id = 'installationInstructionModal';
        this.modal.tabIndex = '-1';
        this.modal.setAttribute('aria-hidden', 'true');
        
        // Modal dialog
        const modalDialog = document.createElement('div');
        modalDialog.className = 'modal-dialog modal-lg';
        
        // Modal content
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        
        // Modal header
        const modalHeader = document.createElement('div');
        modalHeader.className = 'modal-header';
        modalHeader.innerHTML = `
            <h5 class="modal-title">Installation Instructions</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        `;
        
        // Modal body
        const modalBody = document.createElement('div');
        modalBody.className = 'modal-body';
        this.buildForm(modalBody);
        
        // Modal footer
        const modalFooter = document.createElement('div');
        modalFooter.className = 'modal-footer';
        modalFooter.innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" id="saveInstructionsBtn">Submit</button>
        `;
        
        // --- Wrap body and footer in a form ---
        const form = document.createElement('form');
        form.appendChild(modalBody);
        form.appendChild(modalFooter);

        modalContent.appendChild(modalHeader);
        modalContent.appendChild(form);
        modalDialog.appendChild(modalContent);
        this.modal.appendChild(modalDialog);
        
        // Add to DOM
        document.body.appendChild(this.modal);
        
        // Initialize Bootstrap modal
        const modalInstance = new bootstrap.Modal(this.modal);
        modalInstance.show();
        
        // Set up event listeners
        this.modal.addEventListener('hidden.bs.modal', () => {
            this.modal.remove();
        });
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveInstructions();
        });
    }

    buildForm(container) {
        if (this.artworkData.length === 0) {
            container.innerHTML = '<p>No artwork added to this wall yet.</p>';
            return;
        }

        // First Piece Hung section
        container.innerHTML += `
            <div class="mb-3">
                <label class="form-label fw-bold">First Piece Hung</label>
        `;
        
        this.artworkData.forEach((art, index) => {
            container.innerHTML += `
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="firstPiece" id="firstPiece${index}" 
                           value="${art.name}" ${index === 0 ? 'checked' : ''}>
                    <label class="form-check-label" for="firstPiece${index}">
                        ${art.name}
                    </label>
                </div>
            `;
        });
        
        // Wall Measure section
        container.innerHTML += `
            </div>
            <div class="mb-3">
                <label class="form-label fw-bold">Wall Measure</label>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="wallMeasure" id="wallMeasureLeft" value="left" checked>
                    <label class="form-check-label" for="wallMeasureLeft">
                        From Left Wall
                    </label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="wallMeasure" id="wallMeasureRight" value="right">
                    <label class="form-check-label" for="wallMeasureRight">
                        From Right Wall
                    </label>
                </div>
            </div>
        `;
        
        // Height Measure section
        container.innerHTML += `
            <div class="mb-3">
                <label class="form-label fw-bold">Height Measure</label>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="heightMeasure" id="heightMeasureFloor" value="floor" checked>
                    <label class="form-check-label" for="heightMeasureFloor">
                        From Floor
                    </label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="heightMeasure" id="heightMeasureCeiling" value="ceiling">
                    <label class="form-check-label" for="heightMeasureCeiling">
                        From Ceiling
                    </label>
                </div>
            </div>
        `;
    }

    getSelectedValue(name) {
        const selected = document.querySelector(`input[name="${name}"]:checked`);
        return selected ? selected.value : null;
    }

    calculateHangLocations() {
        const wallRef = this.getSelectedValue('wallMeasure');
        const heightRef = this.getSelectedValue('heightMeasure');
        const wallWidth = this.wallData.width;
        const wallHeight = this.wallData.height;

        const locations = {};

        console.log("Calculating hang locations for:", this.artworkData);

        this.artworkData.forEach(art => {
            // Accept both DB and guest objects
            const position = art.position || { x: art.x_position ?? 0, y: art.y_position ?? 0 };
            const hangingPoint = art.hanging_point ?? 0;
            const width = art.width ?? 0;
            const height = art.height ?? 0;

            // Skip if we don't have valid dimensions
            if (width <= 0 || height <= 0) {
                console.warn("Skipping artwork with invalid dimensions:", art);
                return;
            }

            // Get bottom-left position
            const bottomLeftX = position.x;
            const bottomLeftY = position.y;

            // Calculate center position
            const centerX = bottomLeftX + (width / 2);

            // Calculate top edge (in wall coordinates where 0 is bottom)
            const topEdge = bottomLeftY + height;

            // Hanging point is top edge minus hanging point offset
            let hangX = centerX;
            let hangY = topEdge - hangingPoint;

            // Adjust based on measurement preferences
            if (wallRef === "right") {
                hangX = wallWidth - hangX;
            }
            if (heightRef === "ceiling") {
                hangY = wallHeight - hangY;
            }

            locations[art.name] = { x: hangX, y: hangY };
        });

        // Sort by hang_x ascending, then hang_y descending
        const sortedEntries = Object.entries(locations).sort((a, b) => {
            if (a[1].x !== b[1].x) {
                return a[1].x - b[1].x;
            }
            return b[1].y - a[1].y;
        });

        return Object.fromEntries(sortedEntries);
    }

    generateInstructionLines() {
        const locations = this.calculateHangLocations();
        if (!locations || Object.keys(locations).length === 0) {
            return [];
        }

        const wallRef = this.getSelectedValue('wallMeasure');
        const heightRef = this.getSelectedValue('heightMeasure');
        const firstName = this.getSelectedValue('firstPiece');
        const names = Object.keys(locations);
        
        if (!names.includes(firstName)) {
            return ["Error: First piece not found in artwork list."];
        }

        const firstIndex = names.indexOf(firstName);
        const instructions = [];

        // Add header with general instructions
        instructions.push("GALLERY WALL INSTALLATION INSTRUCTIONS");
        instructions.push("=".repeat(50));
        instructions.push(`Wall: ${this.wallData.name}`);
        instructions.push(`Total Artworks: ${this.artworkData.length}`);
        instructions.push(`Reference Point: From ${wallRef} wall, from ${heightRef}`);
        instructions.push(`Starting Piece: ${firstName}`);
        instructions.push("");
        instructions.push("GENERAL INSTALLATION TIPS:");
        instructions.push("- Use a level to ensure each piece is straight");
        instructions.push("- Mark all hanging points with pencil before starting");
        instructions.push("- Consider using painter's tape to test layout before installing");
        instructions.push("- For heavy pieces, use appropriate wall anchors");
        instructions.push("");
        instructions.push("MEASUREMENT INSTRUCTIONS:");
        instructions.push("=".repeat(50));

        // A) Measure from wall/floor to first piece
        const first = { name: firstName, ...locations[firstName] };
        const xInitial = wallRef === "left" ? "RIGHT" : "LEFT";
        const yInitial = heightRef === "floor" ? "UP" : "DOWN";
        const xDir = wallRef === "left" ? "LEFT" : "RIGHT";
        const yDir = heightRef === "floor" ? "DOWN" : "UP";
        const adjustedY = first.y;

        instructions.push(`1. STARTING POINT - ${first.name}:`);
        instructions.push(`   • From ${wallRef.toUpperCase()} wall edge, measure ${xInitial} ${first.x.toFixed(3)}"`);
        instructions.push(`   • From ${heightRef.toUpperCase()}, measure ${yInitial} ${adjustedY.toFixed(3)}"`);
        instructions.push(`   • Mark this point with a pencil - this is your starting nail position`);
        instructions.push("");

        // Forward pass (first+1 to end)
        let stepNum = 2;
        let prev = first;
        for (let i = firstIndex + 1; i < names.length; i++) {
            const curr = { name: names[i], ...locations[names[i]] };
            // Calculate relative X
            const deltaX = curr.x - prev.x;
            const relDir = deltaX >= 0 ? "RIGHT" : "LEFT";
            const relDist = Math.abs(deltaX).toFixed(3);

            instructions.push(`${stepNum}. ${curr.name}:`);
            instructions.push(`   • From ${prev.name} nail position, measure ${relDir} ${relDist}""`);
            instructions.push(`   • From FLOOR, measure UP ${curr.y.toFixed(3)}"`);
            instructions.push(`   • Mark this point for ${curr.name}'s nail`);
            instructions.push("");
            prev = curr;
            stepNum++;
        }

        // Backward pass (first-1 to start)
        prev = first;
        for (let i = firstIndex - 1; i >= 0; i--) {
            const curr = { name: names[i], ...locations[names[i]] };
            // Calculate relative X
            const deltaX = curr.x - prev.x;
            const relDir = deltaX >= 0 ? "RIGHT" : "LEFT";
            const relDist = Math.abs(deltaX).toFixed(3);

            instructions.push(`${stepNum}. ${curr.name}:`);
            instructions.push(`   • From ${prev.name} nail position, measure ${relDir} ${relDist}""`);
            instructions.push(`   • From FLOOR, measure UP ${curr.y.toFixed(3)}"`);
            instructions.push(`   • Mark this point for ${curr.name}'s nail`);
            instructions.push("");
            prev = curr;
            stepNum++;
        }

        // Final instructions
        instructions.push("FINAL STEPS:");
        instructions.push("=".repeat(50));
        instructions.push("- Double check all measurements before installing nails");
        instructions.push("- Install all nails at marked positions");
        instructions.push("- Hang artwork starting with your chosen first piece");
        instructions.push("- Step back periodically to check alignment and spacing");
        instructions.push("- Enjoy your beautifully arranged gallery wall!");
        
        return instructions;
    }

    saveInstructions() {
        const textLines = this.generateInstructionLines();
        console.log("Generated instructions:", textLines);

        if (!textLines || textLines.length === 0) {
            const errorMsg = this.artworkData.length === 0 
                ? "No artwork added to this wall yet."
                : "Could not calculate positions for the artworks. Please check that all artworks have valid dimensions and positions.";
            this.showAlert("Error", errorMsg);
            return;
        }

        // Always use .txt extension
        const wallName = this.wallData.name.replace(/[^a-zA-Z0-9 _]/g, "").trim();
        const defaultFilename = `Installation_Instructions_${wallName || 'Wall'}.txt`;

        // Save as plain text
        const blob = new Blob([textLines.join('\n')], { type: 'text/plain' });

        // Create download link and trigger file explorer
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = defaultFilename;
        document.body.appendChild(a);
        a.click();

        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);

        // Close modal
        bootstrap.Modal.getInstance(this.modal).hide();
    }

    showAlert(title, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            <strong>${title}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        this.modal.querySelector('.modal-body').prepend(alertDiv);
    }
}