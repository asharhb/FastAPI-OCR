
    document.addEventListener('DOMContentLoaded', function() {
        const fileInput = document.getElementById('file');
        const fileName = document.getElementById('file-name');
        const form = document.getElementById('upload-form');
        const resultCard = document.getElementById('result-card');
        const loader = document.getElementById('loader');
        const copyBtn = document.getElementById('copy-btn');

        // Update file name when file is selected
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileName.textContent = this.files[0].name;
                fileName.style.display = 'block';
            } else {
                fileName.style.display = 'none';
            }
        });

        // Handle form submission
        form.addEventListener('submit', function(e) {
            // Show loader
            loader.classList.add('active');

            // Hide previous result if any
            resultCard.classList.remove('active');
        });

        // Copy result to clipboard
        copyBtn.addEventListener('click', function() {
            const resultText = document.getElementById('result-text');

            // Create a temporary textarea element
            const textarea = document.createElement('textarea');
            textarea.value = resultText.textContent;
            document.body.appendChild(textarea);

            // Select and copy the text
            textarea.select();
            document.execCommand('copy');

            // Remove the temporary textarea
            document.body.removeChild(textarea);

            // Update button text temporarily
            const originalText = this.textContent;
            this.textContent = 'Copied!';

            // Reset button text after 2 seconds
            setTimeout(() => {
                this.textContent = originalText;
            }, 2000);
        });
    });
    