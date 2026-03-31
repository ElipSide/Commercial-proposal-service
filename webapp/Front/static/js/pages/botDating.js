function getUserPhotoInput() {
    return document.getElementById('fileElem');
}

function getUserPhotoContainer() {
    return document.getElementById('User_photoIcon');
}

function renderUserPreview(imageSrc) {
    const container = getUserPhotoContainer();
    if (!container) {
        return;
    }

    const img = document.createElement('img');
    img.src = imageSrc;
    img.style.maxWidth = '100%';
    img.style.maxHeight = '100%';
    img.style.borderRadius = '10px';

    container.innerHTML = '';
    container.appendChild(img);
}

function user_images_load(elementId) {
    const input = getUserPhotoInput();
    if (!input) {
        return;
    }
    input.click();
}

function handleFiles(files, elementId) {
    const file = files && files[0];
    if (!file) {
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        renderUserPreview(e.target.result);
    };
    reader.readAsDataURL(file);
}
