export class InstallationInstruction {
    constructor(wallData, artworkData) {
        this.wallData = wallData;
        this.artworkData = artworkData;
        this.modal = null;
    }

    show() {
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
            <button type="button" class="btn btn-primary" id="saveInstructionsBtn">Save</button>
        `;
        
        // Assemble modal
        modalContent.appendChild(modalHeader);
        modalContent.appendChild(modalBody);
        modalContent.appendChild(modalFooter);
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
        
        document.getElementById('saveInstructionsBtn').addEventListener('click', () => {
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
        
        // File Type section
        container.innerHTML += `
            <div class="mb-3">
                <label class="form-label fw-bold">File Type</label>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="fileType" id="fileTypeWord" value="word" checked>
                    <label class="form-check-label" for="fileTypeWord">
                        Word
                    </label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="fileType" id="fileTypeExcel" value="excel">
                    <label class="form-check-label" for="fileTypeExcel">
                        Excel
                    </label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="fileType" id="fileTypePDF" value="pdf">
                    <label class="form-check-label" for="fileTypePDF">
                        PDF
                    </label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="fileType" id="fileTypeText" value="text">
                    <label class="form-check-label" for="fileTypeText">
                        Text (No Image)
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
        
        this.artworkData.forEach(art => {
            // Get bottom-left position
            const bottomLeftX = art.position.x;
            const bottomLeftY = art.position.y;
            
            // Calculate center position
            const centerX = bottomLeftX + (art.width / 2);
            
            // Calculate top edge (in wall coordinates where 0 is bottom)
            const topEdge = bottomLeftY + art.height;
            
            // Hanging point is top edge minus hanging point offset
            let hangX = centerX;
            let hangY = topEdge - art.hanging_point;
            
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
        const adjustedY = this.wallData.height - first.y;
        
        instructions.push(`1. STARTING POINT - ${first.name}:`);
        instructions.push(`   • From ${wallRef.toUpperCase()} wall edge, measure ${xInitial} ${first.x.toFixed(3)}"`);
        instructions.push(`   • From ${heightRef.toUpperCase()}, measure ${yInitial} ${adjustedY.toFixed(3)}"`);
        instructions.push(`   • Mark this point with a pencil - this is your starting nail position`);
        instructions.push("");

        // B) Forward pass (first+1 to end)
        let stepNum = 2;  // Starts at 2 because STARTING POINT is always 1
        let prevX = first.x, prevY = first.y;
        for (let i = firstIndex + 1; i < names.length; i++) {
            const curr = { name: names[i], ...locations[names[i]] };
            const dx = Math.abs(curr.x - prevX);
            const dy = Math.abs(curr.y - prevY);
            const yStepDir = curr.y > prevY ? "UP" : "DOWN";

            instructions.push(`${stepNum}. ${curr.name}:`);
            instructions.push(`   • From ${names[i-1]}'s nail position:`);
            instructions.push(`     → Measure ${xInitial} ${dx.toFixed(2)}"`);
            instructions.push(`     → Measure ${yStepDir} ${dy.toFixed(2)}"`);
            instructions.push(`   • Mark this point for ${curr.name}'s nail`);
            instructions.push("");
            
            stepNum++;
            prevX = curr.x;
            prevY = curr.y;
        }

        // D) Backward pass (first-1 to start)
        prevX = first.x;
        prevY = first.y;
        for (let i = firstIndex - 1; i >= 0; i--) {
            const curr = { name: names[i], ...locations[names[i]] };
            const dx = Math.abs(curr.x - prevX);
            const dy = Math.abs(curr.y - prevY);
            const yStepDir = curr.y > prevY ? "UP" : "DOWN";

            instructions.push(`${stepNum}. ${curr.name}:`);
            instructions.push(`   • From ${names[i+1]}'s nail position:`);
            instructions.push(`     → Measure ${xDir} ${dx.toFixed(2)}"`);
            instructions.push(`     → Measure ${yStepDir} ${dy.toFixed(2)}"`);
            instructions.push(`   • Mark this point for ${curr.name}'s nail`);
            instructions.push("");
            
            stepNum++;
            prevX = curr.x;
            prevY = curr.y;
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
        if (!textLines || textLines.length === 0) {
            this.showAlert("Error", "No instructions to save.");
            return;
        }

        const fileType = this.getSelectedValue('fileType');
        const extension = {
            "excel": ".xlsx",
            "word": ".docx", 
            "pdf": ".pdf",
            "text": ".txt"
        }[fileType] || ".txt";

        // Create default filename
        const wallName = this.wallData.name.replace(/[^a-zA-Z0-9 _]/g, "").trim();
        const defaultFilename = `Installation_Instructions_${wallName}${extension}`;

        // Create blob based on file type
        let blob;
        if (fileType === "text") {
            blob = new Blob([textLines.join('\n')], { type: 'text/plain' });
        } else {
            // For other file types, we'd need additional libraries or server-side processing
            // For now, we'll just save as text
            blob = new Blob([textLines.join('\n')], { type: 'text/plain' });
            this.showAlert("Info", "Currently only text export is implemented. Other formats coming soon.");
            return;
        }

        // Create download link
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = defaultFilename;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
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