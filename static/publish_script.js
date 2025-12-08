const titleInput = document.getElementById('titleInput')
const titleCount = document.getElementById('titleCount')

const descInput = document.getElementById('descInput')
const descCount = document.getElementById('descCount')

titleInput.addEventListener('input', () => {
    const len = titleInput.value.length;
    titleCount.textContent = `${len}/300`
});


descInput.addEventListener('input', () => {
    const len = descInput.value.length;
    descCount.textContent = `${len}/2000`
});


document.addEventListener('DOMContentLoaded', function() {
    const clearButton = document.querySelector('.clear-selection');
    const imageInput = document.getElementById('imageUpload');

    if (clearButton && imageInput) {
        clearButton.addEventListener('click', function() {
            imageInput.value = ''; 
        });
    }
});