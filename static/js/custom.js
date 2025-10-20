// Custom JavaScript for HR Internal System

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Form validation enhancement
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Loading states for buttons
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function() {
            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                var originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processando...';
                
                // Re-enable after 10 seconds as fallback
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });
    
    // Table row click handling
    document.querySelectorAll('.table-clickable tbody tr').forEach(function(row) {
        row.addEventListener('click', function() {
            var link = this.querySelector('a');
            if (link) {
                window.location.href = link.href;
            }
        });
        
        row.style.cursor = 'pointer';
    });
    
    // Search functionality
    var searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var searchTerm = this.value.toLowerCase();
            var searchableItems = document.querySelectorAll('.searchable-item');
            
            searchableItems.forEach(function(item) {
                var text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
    
    // Confirmation dialogs
    document.querySelectorAll('[data-confirm]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Auto-resize textareas
    document.querySelectorAll('textarea.auto-resize').forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // File upload preview
    document.querySelectorAll('input[type="file"]').forEach(function(input) {
        input.addEventListener('change', function() {
            var file = this.files[0];
            if (file) {
                var preview = document.querySelector('#' + this.id + '-preview');
                if (preview) {
                    if (file.type.startsWith('image/')) {
                        var reader = new FileReader();
                        reader.onload = function(e) {
                            preview.innerHTML = '<img src="' + e.target.result + '" class="img-thumbnail" style="max-width: 200px;">';
                        };
                        reader.readAsDataURL(file);
                    } else {
                        preview.innerHTML = '<div class="alert alert-info"><i class="bi bi-file-earmark"></i> ' + file.name + '</div>';
                    }
                }
            }
        });
    });
    
    // Copy to clipboard functionality
    document.querySelectorAll('[data-clipboard]').forEach(function(element) {
        element.addEventListener('click', function() {
            var text = this.getAttribute('data-clipboard');
            navigator.clipboard.writeText(text).then(function() {
                // Show success message
                var toast = document.createElement('div');
                toast.className = 'toast align-items-center text-white bg-success border-0';
                toast.innerHTML = '<div class="d-flex"><div class="toast-body">Copiado para a área de transferência!</div></div>';
                document.body.appendChild(toast);
                
                var bsToast = new bootstrap.Toast(toast);
                bsToast.show();
                
                setTimeout(function() {
                    document.body.removeChild(toast);
                }, 3000);
            });
        });
    });
    
    // Dynamic form fields
    document.querySelectorAll('.add-field').forEach(function(button) {
        button.addEventListener('click', function() {
            var template = document.querySelector('#' + this.getAttribute('data-template'));
            if (template) {
                var clone = template.cloneNode(true);
                clone.style.display = 'block';
                clone.removeAttribute('id');
                
                var container = document.querySelector('#' + this.getAttribute('data-container'));
                if (container) {
                    container.appendChild(clone);
                }
            }
        });
    });
    
    // Remove field functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-field')) {
            e.target.closest('.field-group').remove();
        }
    });
    
    // Status update via AJAX
    document.querySelectorAll('.status-toggle').forEach(function(toggle) {
        toggle.addEventListener('change', function() {
            var url = this.getAttribute('data-url');
            var status = this.checked ? 'active' : 'inactive';
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({status: status})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Status atualizado com sucesso!', 'success');
                } else {
                    showToast('Erro ao atualizar status.', 'danger');
                    this.checked = !this.checked; // Revert
                }
            })
            .catch(error => {
                showToast('Erro de conexão.', 'danger');
                this.checked = !this.checked; // Revert
            });
        });
    });
    
});

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showToast(message, type = 'info') {
    var toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    var container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    var bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        container.removeChild(toast);
    });
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-MZ', {
        style: 'currency',
        currency: 'MZN'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Calendar specific functions
function initializeCalendar(calendarEl, eventsUrl) {
    if (typeof FullCalendar !== 'undefined') {
        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'pt-br',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
            },
            events: eventsUrl,
            eventClick: function(info) {
                if (info.event.url) {
                    window.open(info.event.url, '_self');
                    info.jsEvent.preventDefault();
                }
            },
            eventDrop: function(info) {
                // Handle event move
                updateEventDates(info.event.id, info.event.start, info.event.end);
            },
            eventResize: function(info) {
                // Handle event resize
                updateEventDates(info.event.id, info.event.start, info.event.end);
            },
            height: 'auto',
            aspectRatio: 1.8,
            dayMaxEvents: true,
            moreLinkClick: 'popover'
        });
        
        calendar.render();
        return calendar;
    }
}

function updateEventDates(eventId, start, end) {
    fetch('/calendar/event/move/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            id: eventId,
            start: start.toISOString(),
            end: end ? end.toISOString() : null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Evento atualizado com sucesso!', 'success');
        } else {
            showToast('Erro ao atualizar evento.', 'danger');
        }
    })
    .catch(error => {
        showToast('Erro de conexão.', 'danger');
    });
}

// Knowledge base search
function initializeKnowledgeSearch() {
    var searchInput = document.querySelector('#knowledge-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            var query = this.value;
            if (query.length >= 3) {
                fetch('/knowledge/search-ajax/?q=' + encodeURIComponent(query))
                .then(response => response.json())
                .then(data => {
                    var resultsContainer = document.querySelector('#search-results');
                    if (resultsContainer) {
                        resultsContainer.innerHTML = '';
                        data.results.forEach(function(result) {
                            var item = document.createElement('a');
                            item.href = result.url;
                            item.className = 'list-group-item list-group-item-action';
                            item.innerHTML = `
                                <div class="d-flex w-100 justify-content-between">
                                    <h6 class="mb-1">${result.title}</h6>
                                    <small class="text-muted">${result.category}</small>
                                </div>
                            `;
                            resultsContainer.appendChild(item);
                        });
                    }
                });
            }
        }, 300));
    }
}

// Initialize components when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize calendar if element exists
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        var eventsUrl = calendarEl.getAttribute('data-events-url');
        initializeCalendar(calendarEl, eventsUrl);
    }
    
    // Initialize knowledge search
    initializeKnowledgeSearch();
    
    // Add fade-in animation to main content
    var mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
});