document.addEventListener('DOMContentLoaded', function() {
    // File upload handling
    document.getElementById('imageUpload').addEventListener('change', function(e) {
        const fileName = e.target.files[0] ? e.target.files[0].name : 'No file selected';
        document.getElementById('fileName').textContent = fileName;
    });

    // Expose functions to global scope for button onclick handlers
    window.toggleOptionalFields = function() {
        const optionalFields = document.getElementById('optionalFields');
        const toggleBtn = document.getElementById('toggleOptionalBtn');
        
        if (optionalFields.style.display === 'none' || optionalFields.style.display === '') {
            optionalFields.style.display = 'block';
            toggleBtn.textContent = '- Additional Options';
        } else {
            optionalFields.style.display = 'none';
            toggleBtn.textContent = '+ Additional Options';
        }
    };

    window.createArtwork = function() {
        const form = document.getElementById('artworkForm');
        const formData = new FormData(form);

        // Add validation for required fields
        const requiredFields = ['name', 'width', 'height', 'hanging'];
        let isValid = true;
        
        requiredFields.forEach(field => {
            const input = form.elements[field];
            if (!input.value || input.value.trim() === '') {
                alert(`Please fill in the ${field} field`);
                input.focus();
                isValid = false;
                return;
            }
            
            // Additional validation for number fields
            if (['width', 'height', 'hanging'].includes(field)) {
                if (isNaN(input.value) || Number(input.value) <= 0) {
                    alert(`Please enter a valid positive number for ${field}`);
                    input.focus();
                    isValid = false;
                    return;
                }
            }
        });
        
        if (!isValid) return;

        fetch(window.location.pathname, {
            method: "POST",
            body: formData,
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload artworks in the editor (assuming you have a method for this)
                if (window.editor && typeof window.editor.reloadArtworks === "function") {
                    window.editor.reloadArtworks().then(() => {
                        // Optionally, refresh the EvenSpacing modal if open
                        if (window.evenSpacingModal && window.evenSpacingModal.modalInstance._isShown) {
                            window.evenSpacingModal.init(); // or .show() if you want to reopen
                        }
                    });
                } else {
                    // fallback: reload the page
                    window.location.reload();
                }
            } else {
                alert(data.error || "Failed to create artwork.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.error || 'An error occurred while creating the artwork');
        });
    };

    window.addArtworkToList = function(artwork) {
        const artworkList = document.getElementById('artworkList');
        
        // Remove "no artworks" message if present
        if (artworkList.querySelector('.text-muted')) {
            artworkList.innerHTML = '';
        }
        
        // Create new artwork item
        const item = document.createElement('div');
        item.className = 'artwork-item';
        
        let details = '';
        if (artwork.medium) details += `${artwork.medium} | `;
        if (artwork.price > 0) details += `$${artwork.price.toFixed(2)} | `;
        if (artwork.nfs) details += 'NFS';
        
        item.innerHTML = `
            <div class="artwork-name">${artwork.name} (${artwork.width}" × ${artwork.height}")</div>
            <div class="artwork-details">${details}</div>
        `;
        
        artworkList.prepend(item);
    };

    window.goBackToEditor = function() {
        window.location.href = window.goBackToEditorUrl + '?refresh=' + new Date().getTime();
    };

    // Hotkey: Pressing Enter triggers Create Artwork
    document.getElementById('artworkForm').addEventListener('keydown', function(e) {
        // Only trigger if Enter is pressed and not on a textarea or button
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA' && e.target.type !== 'submit' && e.target.type !== 'button') {
            e.preventDefault();
            window.createArtwork();
        }
    });
});