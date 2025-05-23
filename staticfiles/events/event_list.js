/* 
for events app
events/templates/events/event_list.js
*/

console.log("Event List JavaScript loaded successfully");

let editRowIndex = -1;
let rowToDelete = null;
let whenInput = null;
let editWhenInput = null;
let currentEventId = null;

// Initialize date time pickers, scroll button, messages, and drag-over events
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded, initializing flatpickr");
    const whenInputElement = document.querySelector("#whenInput");
    const editWhenInputElement = document.querySelector("#editWhenInput");

    if (whenInputElement) {
        whenInput = flatpickr(whenInputElement, {
            enableTime: true,
            dateFormat: "F d, Y - h:i K",
            time_24hr: false,
            defaultHour: 12,
            defaultMinute: 0,
            onChange: (selectedDates, dateStr) => {
                console.log("Add Modal - Selected date:", dateStr, selectedDates);
            }
        });
        console.log("whenInput initialized");
    } else {
        console.error("whenInputElement not found");
    }

    if (editWhenInputElement) {
        editWhenInput = flatpickr(editWhenInputElement, {
            enableTime: true,
            dateFormat: "F d, Y - h:i K",
            time_24hr: false,
            defaultHour: 12,
            defaultMinute: 0,
            onChange: (selectedDates, dateStr) => {
                console.log("Edit Modal - Selected date:", dateStr, selectedDates);
            }
        });
        console.log("editWhenInput initialized");
    } else {
        console.error("editWhenInputElement not found");
    }

    // Initialize Event Detail Modal
    const eventModal = document.getElementById('event-detail-modal');
    const modalBackdrop = document.getElementById('modal-backdrop');
    const modalCloseBtn = eventModal.querySelector('.close-btn');

    function openEventModal(eventData, eventId) {
        console.log("Opening event modal for event ID:", eventId);
        console.log("Event data received:", eventData);

        // Get all modal elements
        const modalElements = {
            what: document.getElementById('modal-what'),
            when: document.getElementById('modal-when'),
            where: document.getElementById('modal-where'),
            who: document.getElementById('modal-who'),
            status: document.getElementById('modal-status'),
            createdBy: document.getElementById('modal-created-by')
        };

        // Debug log for modal elements
        console.log("Modal elements found:", {
            what: !!modalElements.what,
            when: !!modalElements.when,
            where: !!modalElements.where,
            who: !!modalElements.who,
            status: !!modalElements.status,
            createdBy: !!modalElements.createdBy
        });

        // Set values with logging
        if (modalElements.what) {
            modalElements.what.textContent = eventData.what || 'N/A';
            console.log("Setting what:", eventData.what);
        }
        if (modalElements.when) {
            modalElements.when.textContent = eventData.when || 'N/A';
            console.log("Setting when:", eventData.when);
        }
        if (modalElements.where) {
            modalElements.where.textContent = eventData.where || 'N/A';
            console.log("Setting where:", eventData.where);
        }
        if (modalElements.who) {
            modalElements.who.textContent = eventData.who || 'N/A';
            console.log("Setting who:", eventData.who);
        }
        if (modalElements.status) {
            const statusValue = eventData.statusDisplay || eventData.status || 'Ongoing';
            console.log("Attempting to set status to:", statusValue);
            modalElements.status.textContent = statusValue;
            modalElements.status.style.display = 'inline-block';
            modalElements.status.style.visibility = 'visible';
            modalElements.status.style.opacity = '1';
            console.log("Status element after setting:", {
                textContent: modalElements.status.textContent,
                display: modalElements.status.style.display,
                visibility: modalElements.status.style.visibility,
                opacity: modalElements.status.style.opacity
            });
        } else {
            console.error("Status element not found in modal");
        }
        if (modalElements.createdBy) {
            modalElements.createdBy.textContent = eventData.createdBy || 'Unknown';
            console.log("Setting createdBy:", eventData.createdBy);
        }

        // Show modal
        eventModal.classList.add('active');
        modalBackdrop.classList.add('active');
        modalCloseBtn.focus();
    }

    function closeEventModal() {
        eventModal.classList.remove('active');
        modalBackdrop.classList.remove('active');
    }

    modalCloseBtn.addEventListener('click', closeEventModal);
    modalBackdrop.addEventListener('click', closeEventModal);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && eventModal.classList.contains('active')) {
            closeEventModal();
        }
    });

    // Function to get CSRF token
    function getCsrfToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }

    // Add event listener for the "Add" button
    const addButton = document.querySelector('.add-btn');
    if (addButton) {
        addButton.addEventListener('click', openAddModal);
    } else {
        console.error("Add button not found");
    }

    // Add event listener for form submission
    const addForm = document.getElementById('addEventForm');
    if (addForm) {
        addForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log("Submitting add form to:", addForm.action);
            let whenValue = document.getElementById('whenInput').value;
            console.log("Add Event Form submitted");
            console.log("What:", document.getElementById('whatInput').value);
            console.log("When (original):", whenValue);
            console.log("Where:", document.getElementById('whereInput').value);
            console.log("Who:", document.getElementById('whoInput').value);
            console.log("Status:", document.getElementById('statusInput').value);

            // Normalize the time format
            whenValue = whenValue.replace(/\s(A|P)$/, ' $1M');
            console.log("When (normalized):", whenValue);

            if (!whenValue.match(/\d{1,2}:\d{2}\s(A|P|AM|PM)$/)) {
                console.warn("Invalid time format, missing valid time with AM/PM");
                alert("Please select a valid date and time with AM/PM (e.g., May 10, 2025 - 02:00 PM).");
                return;
            }

            document.getElementById('whenInput').value = whenValue;

            fetch(addForm.action, {
                method: 'POST',
                body: new FormData(addForm),
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log("Add Response Status:", response.status);
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`Network response was not ok: ${response.status} - ${text}`);
                    });
                }
                return response.json().catch(() => ({}));
            })
            .then(data => {
                console.log('Add Event Success:', data);
                fadeOutMessages(); // Trigger fade-out
                // Delay redirect to allow fade-out to complete
                setTimeout(() => {
                    window.location.href = '/events/list/';
                }, 3500); // 3.5 seconds (3000ms fade + 500ms remove)
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to add event: ' + error.message);
            });
        });
    }

    // Add event listener for edit form submission
    const editForm = document.getElementById('editEventForm');
    if (editForm) {
        editForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!editForm.action.includes('/events/edit/')) {
                console.error("Unexpected form action:", editForm.action);
                return;
            }
            console.log("Submitting edit form to:", editForm.action);
            let whenValue = document.getElementById('editWhenInput').value;
            console.log("Edit Event Form submitted");
            console.log("What:", document.getElementById('editWhatInput').value);
            console.log("When (original):", whenValue);
            console.log("Where:", document.getElementById('editWhereInput').value);
            console.log("Who:", document.getElementById('editWhoInput').value);
            console.log("Status:", document.getElementById('editStatusInput').value);

            // Normalize the time format
            whenValue = whenValue.replace(/\s(A|P)$/, ' $1M');
            console.log("When (normalized):", whenValue);

            if (!whenValue.match(/\d{1,2}:\d{2}\s(A|P|AM|PM)$/)) {
                console.warn("Invalid time format, missing valid time with AM/PM");
                alert("Please select a valid date and time with AM/PM (e.g., May 10, 2025 - 02:00 PM).");
                return;
            }

            document.getElementById('editWhenInput').value = whenValue;

            fetch(editForm.action, {
                method: 'POST',
                body: new FormData(editForm),
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log("Edit Response Status:", response.status);
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`Network response was not ok: ${response.status} - ${text}`);
                    });
                }
                return response.json().catch(() => ({}));
            })
            .then(data => {
                console.log('Edit Event Success:', data);
                fadeOutMessages(); // Trigger fade-out
                // Update table row status
                const row = document.querySelector(`tr[data-event-id="${currentEventId}"]`);
                if (row) {
                    const statusCell = row.querySelector('.status-column');
                    const newStatus = document.getElementById('editStatusInput').value;
                    const statusMap = {
                        'ongoing': 'Ongoing',
                        'done': 'Done',
                        'postponed': 'Postponed'
                    };
                    const statusDisplay = statusMap[newStatus] || 'Ongoing';
                    statusCell.textContent = statusDisplay;
                    row.setAttribute('data-status', newStatus);
                    row.setAttribute('data-status-display', statusDisplay);
                    console.log(`Updated table row status for event ID ${currentEventId} to ${statusDisplay}`);
                }
                // Update modal if open
                if (eventModal.classList.contains('active') && row && row.getAttribute('data-event-id') === currentEventId) {
                    const modalStatus = document.getElementById('modal-status');
                    if (modalStatus) {
                        const statusDisplay = document.getElementById('editStatusInput').value;
                        modalStatus.textContent = statusMap[statusDisplay] || 'Ongoing';
                        modalStatus.style.display = 'inline-block';
                        modalStatus.style.visibility = 'visible';
                        modalStatus.style.opacity = '1';
                        console.log(`Modal status updated to ${modalStatus.textContent} for event ID ${currentEventId}`);
                    }
                }
                // Delay redirect to allow fade-out to complete
                setTimeout(() => {
                    window.location.href = '/events/list/';
                }, 3500); // 3.5 seconds (3000ms fade + 500ms remove)
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to edit event: ' + error.message);
            });
        });
    }

    // Add event listener for delete form submission
    const deleteForm = document.getElementById('deleteEventForm');
    if (deleteForm) {
        deleteForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log("Submitting delete form to:", deleteForm.action);

            fetch(deleteForm.action, {
                method: 'POST',
                body: new FormData(deleteForm),
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log("Delete Response Status:", response.status);
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`Network response was not ok: ${response.status} - ${text}`);
                    });
                }
                return response.json().catch(() => ({}));
            })
            .then(data => {
                console.log('Delete Event Success:', data);
                fadeOutMessages(); // Trigger fade-out
                // Delay redirect to allow fade-out to complete
                setTimeout(() => {
                    window.location.href = '/events/list/';
                }, 3500); // 3.5 seconds (3000ms fade + 500ms remove)
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to delete event: ' + error.message);
            });
        });
    }

    // Add event listeners for "Edit", "Delete", and row clicks
    const eventRows = document.querySelectorAll('.event-row');
    eventRows.forEach(row => {
        const eventId = row.getAttribute('data-event-id');
        const editButton = row.querySelector('.action-btn.edit');
        const deleteButton = row.querySelector('.action-btn.delete');

        // Click event for row (to open event details modal)
        row.addEventListener('click', (e) => {
            if (e.target.closest('.action-buttons')) return;
            
            // Get all data attributes from the row
            const eventData = {
                what: row.getAttribute('data-what'),
                when: row.getAttribute('data-when'),
                where: row.getAttribute('data-where'),
                who: row.getAttribute('data-who'),
                status: row.getAttribute('data-status'),
                statusDisplay: row.getAttribute('data-status-display') || 'Ongoing',
                createdBy: row.getAttribute('data-created-by')
            };
            
            console.log("Event data from attributes:", eventData);
            openEventModal(eventData, eventId);
        });

        // Drag-over events
        row.addEventListener('dragover', (e) => {
            e.preventDefault(); // Allow drop effect
            if (!row.classList.contains('drag-over')) {
                row.classList.add('drag-over');
                console.log("Drag over detected on row with event ID:", eventId);
            }
        });

        row.addEventListener('dragleave', () => {
            row.classList.remove('drag-over');
        });

        row.addEventListener('dragend', () => {
            row.classList.remove('drag-over');
        });

        if (editButton) {
            editButton.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent row click
                openEditModal(editButton, eventId);
            });
        }

        if (deleteButton) {
            deleteButton.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent row click
                confirmDeleteRow(deleteButton, eventId);
            });
        }
    });

    // Add event listener for "Cancel" button in delete confirmation
    const cancelDeleteButton = document.querySelector('.dialog-btn.cancel-btn');
    if (cancelDeleteButton) {
        cancelDeleteButton.addEventListener('click', cancelDelete);
    } else {
        console.error("Cancel delete button not found");
    }

    // Add event listeners for "Exit" buttons in modals
    const exitButtons = document.querySelectorAll('.exit-btn');
    exitButtons.forEach(button => {
        const modalId = button.closest('.modal').id;
        button.addEventListener('click', () => {
            closeModal(modalId);
        });
    });

    // Initialize scroll button
    initializeScrollButton();

    // Fade out messages on initial load
    fadeOutMessages();
});

// Open the Add modal
function openAddModal() {
    console.log("Opening Add Modal");
    const addModal = document.getElementById('addModal');
    const whatInput = document.getElementById('whatInput');
    const whereInput = document.getElementById('whereInput');
    const whoInput = document.getElementById('whoInput');
    const statusInput = document.getElementById('statusInput');

    if (addModal && whatInput && whereInput && whoInput && statusInput) {
        addModal.style.display = 'flex';
        whatInput.value = '';
        if (whenInput) {
            whenInput.clear();
        }
        whereInput.value = '';
        whoInput.value = '';
        statusInput.value = 'ongoing';
        toggleScrollButton(addModal);
    } else {
        console.error("Add Modal or input elements not found");
    }
}

// Close the modal
function closeModal(modalId) {
    console.log("Closing modal: " + modalId);
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        toggleScrollButton(modal);
    } else {
        console.error("Modal not found: " + modalId);
    }
}

// Update the openEditModal function to work with new structure
function openEditModal(button, eventId) {
    console.log("Opening Edit Modal for event ID: " + eventId);
    currentEventId = eventId;
    const row = button.closest('tr');
    editRowIndex = row.rowIndex - 1;
    const cells = row.cells;

    const editWhatInput = document.getElementById('editWhatInput');
    const editWhenInputElement = document.getElementById('editWhenInput');
    const editWhereInput = document.getElementById('editWhereInput');
    const editWhoInput = document.getElementById('editWhoInput');
    const editStatusInput = document.getElementById('editStatusInput');
    const editModal = document.getElementById('editModal');
    const form = document.getElementById('editEventForm');

    if (editWhatInput && editWhenInputElement && editWhereInput && editWhoInput && editStatusInput && editModal && form) {
        editWhatInput.value = cells[0].textContent.trim();
        let dateStr = cells[1].textContent.trim();
        console.log("Edit Modal - Original dateStr:", dateStr);
        dateStr = dateStr.replace(/\s+/g, ' ').trim();
        dateStr = dateStr.replace(/\s(A|P)$/, ' $1M');
        console.log("Edit Modal - Normalized dateStr:", dateStr);
        if (editWhenInput) {
            try {
                editWhenInput.setDate(dateStr, true, 'F d, Y - h:i K');
                const setValue = editWhenInputElement.value;
                console.log("Edit Modal - Set date:", setValue);
                if (!setValue.match(/\d{1,2}:\d{2}\s(A|P|AM|PM)$/)) {
                    console.warn("Edit Modal - Invalid time format after set, defaulting to 12:00 PM");
                    const dateObj = new Date();
                    dateObj.setHours(12, 0);
                    editWhenInput.setDate(dateObj);
                }
            } catch (e) {
                console.error("Edit Modal - Date parsing error:", e);
                editWhenInput.clear();
                editWhenInput.setDate(new Date(), true, 'F d, Y - h:i K');
            }
        }
        editWhereInput.value = cells[2].textContent.trim();
        editWhoInput.value = cells[3].textContent.trim();
        const statusDisplay = row.getAttribute('data-status-display') || 'Ongoing';
        const statusMap = {
            'Ongoing': 'ongoing',
            'Done': 'done',
            'Postponed': 'postponed'
        };
        editStatusInput.value = statusMap[statusDisplay] || 'ongoing';
        console.log("Edit Modal - Set status:", editStatusInput.value, "(from status_display:", statusDisplay, ")");
        form.action = `/events/edit/${eventId}/`;
        editModal.style.display = 'flex';
        toggleScrollButton(editModal);
    } else {
        console.error("Edit Modal or input elements not found");
    }
}

// Show delete confirmation dialog
function confirmDeleteRow(button, eventId) {
    console.log("Opening Delete Confirmation for event ID: " + eventId);
    currentEventId = eventId;
    rowToDelete = button.closest('tr');
    const form = document.getElementById('deleteEventForm');
    const deleteConfirmDialog = document.getElementById('deleteConfirmDialog');

    if (form && deleteConfirmDialog) {
        form.action = `/events/delete/${eventId}/`;
        deleteConfirmDialog.style.display = 'flex';
        setTimeout(fadeOutMessages, 100);
    } else {
        console.error("Delete form or confirmation dialog not found");
    }
}

// Cancel delete action
function cancelDelete() {
    console.log("Canceling Delete action");
    rowToDelete = null;
    currentEventId = null;
    const deleteConfirmDialog = document.getElementById('deleteConfirmDialog');
    if (deleteConfirmDialog) {
        deleteConfirmDialog.style.display = 'none';
    } else {
        console.error("Delete confirmation dialog not found");
    }
}

// Scroll button functionality
function initializeScrollButton() {
    const scrollBtn = document.createElement('button');
    scrollBtn.className = 'scroll-btn';
    scrollBtn.innerHTML = '<i class="fas fa-arrow-down"></i>';
    document.body.appendChild(scrollBtn);

    scrollBtn.addEventListener('click', () => {
        const activeModal = document.querySelector('.modal[style*="display: flex"] .modal-content');
        if (activeModal) {
            activeModal.scrollTo({
                top: activeModal.scrollHeight,
                behavior: 'smooth'
            });
        }
    });
}

function toggleScrollButton(modal) {
    const scrollBtn = document.querySelector('.scroll-btn');
    if (!scrollBtn) return;

    if (modal.style.display === 'flex') {
        const modalContent = modal.querySelector('.modal-content');
        const isScrollable = modalContent.scrollHeight > modalContent.clientHeight;
        scrollBtn.style.display = isScrollable ? 'block' : 'none';
    } else {
        scrollBtn.style.display = 'none';
    }
}

// Fade out and remove messages
function fadeOutMessages() {
    console.log("fadeOutMessages called");
    const messagesContainer = document.querySelector('.messages');
    if (!messagesContainer) {
        console.log("No messages container found");
        return;
    }

    const messages = messagesContainer.querySelectorAll('.message');
    console.log(`Found ${messages.length} messages`);
    messages.forEach(message => {
        setTimeout(() => {
            console.log("Fading out message:", message.textContent);
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(() => {
                console.log("Removing message:", message.textContent);
                message.remove();
                if (messagesContainer.children.length === 0) {
                    console.log("Removing messages container");
                    messagesContainer.remove();
                }
            }, 500);
        }, 3000);
    });
}

console.log("openEditModal defined: " + (typeof openEditModal === 'function'));
console.log("confirmDeleteRow defined: " + (typeof confirmDeleteRow === 'function'));