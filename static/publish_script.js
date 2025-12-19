var clicks_to_delete = 0

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

function OpenModal(titulo) {
    document.getElementById("modal-title").innerText = titulo;
    
    document.getElementById("input-delete-title").value = titulo;

    document.getElementById("overlay").style.display = "block";
    document.getElementById("modal").style.display = "block";
}

function CloseModal() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("modal").style.display = "none";
    clicks_to_delete = 0;
}

function Confirm_delete() {
    clicks_to_delete++;
    console.log("Cliques:", clicks_to_delete);
    if (clicks_to_delete === 1) {
        document.getElementById("delete_button").innerText = "Tem certeza?";
    }
    else if (clicks_to_delete === 2) {
        document.getElementById("delete-form").submit();
        clicks_to_delete = 0;
    }
}
