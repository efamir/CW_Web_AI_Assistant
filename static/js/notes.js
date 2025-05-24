const token = localStorage.getItem("token"); // або інший спосіб отримати токен

const notesListContainer = document.getElementById("notesListContainer");
const noNotesMessage = document.getElementById("noNotesMessage");

const noteIdInput = document.getElementById("noteIdInput");
const noteContentInput = document.getElementById("noteContentInput");
const saveNoteButton = document.getElementById("saveNoteButton");

function renderNote(note) {
    const noteDiv = document.createElement("div");
    noteDiv.className = "col-md-6 col-lg-4 note-item-wrapper";
    noteDiv.dataset.noteId = note.id;

    noteDiv.innerHTML = `
        <div class="card shadow-sm note-card h-100">
            <div class="card-body d-flex flex-column">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <button class="btn btn-sm btn-icon text-danger p-0" onclick="deleteNote('${note.id}')" title="Delete Note">
                            <i class="bi bi-trash-fill fs-5"></i>
                        </button>
                    </div>
                </div>
                <p class="card-text note-content flex-grow-1" id="noteContentPreview-${note.id}">${note.text}</p>
                <p class="card-text mt-auto pt-2"><small class="text-muted">Created: <span id="noteLastUpdated-${note.id}">${new Date(note.created_at).toLocaleString()}</span></small></p>
            </div>
        </div>
    `;

    notesListContainer.appendChild(noteDiv);
}

async function loadNotes() {
    try {
        const response = await fetch("/notes", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ token })
        });

        if (!response.ok) throw new Error("Failed to load notes");

        const notes = await response.json();

        notesListContainer.innerHTML = "";

        if (notes.length === 0) {
            noNotesMessage.style.display = "block";
        } else {
            noNotesMessage.style.display = "none";
            notes.forEach(renderNote);
        }
    } catch (error) {
        console.error("Error loading notes:", error);
    }
}

async function addNote(text) {
    try {
        const response = await fetch("/create_note", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ token, text })
        });

        if (!response.ok) throw new Error("Failed to add note");

        const newNote = await response.json();

        renderNote(newNote);
        noNotesMessage.style.display = "none";
    } catch (error) {
        console.error("Error adding note:", error);
        alert("Не вдалося додати нотатку. Спробуйте ще раз.");
    }
}

saveNoteButton.addEventListener("click", () => {
    const text = noteContentInput.value.trim();
    if (text === "") {
        alert("Будь ласка, введіть текст нотатки");
        return;
    }

    addNote(text);

    noteContentInput.value = "";
    noteIdInput.value = "";
    const addNoteModalEl = document.getElementById("addNoteModal");
    const modal = bootstrap.Modal.getInstance(addNoteModalEl);
    modal.hide();
});

async function deleteNote(noteId) {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Токен не знайдено. Будь ласка, увійдіть.");
        return;
    }


    try {
        const response = await fetch("/note", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                note_id: noteId,
                token: token
            }),
        });

        if (!response.ok) {
            throw new Error(`Помилка видалення: ${response.status}`);
        }

        const result = await response.json();

        const noteElem = document.querySelector(`.note-item-wrapper[data-note-id='${noteId}']`);
        if (noteElem) {
            noteElem.remove();
        }

        if (notesListContainer.children.length === 0) {
            noNotesMessage.style.display = "block";
        }

    } catch (error) {
        console.error("Помилка при видаленні нотатки:", error);
        alert("Не вдалося видалити нотатку. Спробуйте ще раз.");
    }
}





document.addEventListener("DOMContentLoaded", loadNotes);
