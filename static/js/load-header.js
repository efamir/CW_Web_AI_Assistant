

const headerHTML = `
<div class="container-fluid px-3 px-sm-4">
            <a class="navbar-brand d-flex align-items-center" href="/main-page">
                <i class="bi bi-bounding-box-circles fs-4 me-2 text-primary"></i>
                <span class="fw-bold">Jarvice</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu" aria-controls="sidebarMenu" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
        </div>
`;

function inserHeader(placeholderId) {
    const placeholderElement = document.getElementById(placeholderId);
    if (placeholderElement) {
        placeholderElement.innerHTML = headerHTML;
    } else {
        console.error(`Елемент-плейсхолдер з ID "${placeholderId}" не знайдено.`);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    inserHeader('header');
});
