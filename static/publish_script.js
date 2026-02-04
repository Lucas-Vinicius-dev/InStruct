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

document.addEventListener('DOMContentLoaded', function() {
    const toggleButtons = document.querySelectorAll('.toggle-comments');
    
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.getAttribute('data-post');
            const commentsSection = document.getElementById('comments-' + postId);
            
            if (commentsSection.style.display === 'none') {
                commentsSection.style.display = 'block';
            } else {
                commentsSection.style.display = 'none';
            }
        });
    });
});

// prevenir scroll ao mandar um comentário
document.addEventListener('DOMContentLoaded', function() {
    const commentForms = document.querySelectorAll('.comment-form');
    
    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const scrollPosition = window.scrollY;
            localStorage.setItem('scrollPosition', scrollPosition);
        });
    });
    
// restaurade scroll após carregar a página
    window.addEventListener('load', function() {
        const savedPosition = localStorage.getItem('scrollPosition');
        if (savedPosition) {
            window.scrollTo(0, parseInt(savedPosition));
            localStorage.removeItem('scrollPosition');
        }
    });
});
