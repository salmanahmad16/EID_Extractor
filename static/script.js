document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const extractBtn = document.getElementById('extractBtn');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const fileName = document.getElementById('fileName');
    const jsonOutput = document.getElementById('jsonOutput');
    const resultSection = document.getElementById('resultSection');
    const countrySelect = document.getElementById('country');
    const sideSelect = document.getElementById('side');

    // Drag & Drop
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });

    function handleFile(file) {
        fileInput.files = createFileList(file); // Update input files
        fileName.textContent = file.name;
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                previewContainer.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        } else {
            imagePreview.src = '';
            previewContainer.classList.remove('hidden');
            fileName.textContent = `${file.name} (PDF)`;
        }
        
        extractBtn.disabled = false;
        resultSection.classList.add('hidden');
    }

    // Helper to manually set file input files (for drag & drop)
    function createFileList(file) {
        const dt = new DataTransfer();
        dt.items.add(file);
        return dt.files;
    }

    // Extract
    extractBtn.addEventListener('click', async () => {
        if (!fileInput.files.length) return;

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('country', countrySelect.value);
        formData.append('side', sideSelect.value);

        extractBtn.disabled = true;
        extractBtn.textContent = 'Extracting...';
        jsonOutput.textContent = '';
        resultSection.classList.add('hidden');

        try {
            const response = await fetch('/api/extract', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            jsonOutput.textContent = JSON.stringify(data, null, 4);
            resultSection.classList.remove('hidden');
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during extraction.');
        } finally {
            extractBtn.disabled = false;
            extractBtn.textContent = 'Extract Data';
        }
    });
});
