// menu-html.js

const offcanvasMenuHTML = `
<div class="offcanvas-header border-bottom">
            <h5 class="offcanvas-title fw-bold" id="sidebarMenuLabel">MENU</h5>
            <button type="button" class="btn btn-link text-dark fs-4 p-0" data-bs-dismiss="offcanvas" aria-label="Close" style="line-height: 1;">
                <i class="bi bi-arrow-left"></i>
            </button>
        </div>
        <div class="offcanvas-body d-flex flex-column">
            <ul class="navbar-nav flex-column">
                <li class="nav-item">
                    <a class="nav-link py-2" href="/timers-page"><i class="bi bi-clock me-2"></i>Timers</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link py-2" href="/notes-page"><i class="bi bi-journal-text me-2"></i>Notes</a>
                </li>
            </ul>
            <ul class="navbar-nav flex-column mt-auto"> <!-- Pushes this section to the bottom -->
                 <li class="nav-item">
                    <hr class="my-2">
                    <button class="nav-link text-danger py-2" id="logout">
                        <i class="bi bi-box-arrow-right me-2"></i>Log Out
                    </button>
                </li>
            </ul>
        </div>
        </div>
`;

function inserHeader(placeholderId) {
    const placeholderElement = document.getElementById(placeholderId);
    if (placeholderElement) {
        placeholderElement.innerHTML = offcanvasMenuHTML;
    } else {
        console.error(`Елемент-плейсхолдер з ID "${placeholderId}" не знайдено.`);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    inserHeader('sidebarMenu');
});
