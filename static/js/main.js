// Custom JavaScript for Quiz Pool App

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
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

    // Quiz timer functionality
    if (document.getElementById('quiz-timer')) {
        startQuizTimer();
    }

    // Option selection highlighting
    var optionInputs = document.querySelectorAll('input[name^="question_"]');
    optionInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            // Remove selected class from all options in this question
            var questionNumber = this.name.split('_')[1];
            var allOptions = document.querySelectorAll('input[name="question_' + questionNumber + '"]');
            allOptions.forEach(function(option) {
                option.closest('.option-item').classList.remove('selected');
            });
            
            // Add selected class to current option
            this.closest('.option-item').classList.add('selected');
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Quiz timer function
function startQuizTimer() {
    var startTime = Date.now();
    var timerElement = document.getElementById('quiz-timer');
    
    function updateTimer() {
        var elapsed = Math.floor((Date.now() - startTime) / 1000);
        var minutes = Math.floor(elapsed / 60);
        var seconds = elapsed % 60;
        
        timerElement.textContent = 'Time: ' + 
            (minutes < 10 ? '0' : '') + minutes + ':' + 
            (seconds < 10 ? '0' : '') + seconds;
    }
    
    // Update timer every second
    setInterval(updateTimer, 1000);
    updateTimer(); // Initial call
}

// Confirm delete function
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Show loading state for buttons
function showLoading(button, text) {
    var originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> ' + (text || 'Loading...');
    button.disabled = true;
    
    return function() {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

// Form auto-save functionality
function autoSaveForm(formId, interval) {
    var form = document.getElementById(formId);
    if (!form) return;
    
    var inputs = form.querySelectorAll('input, textarea, select');
    var saveData = {};
    
    // Load saved data
    var savedData = localStorage.getItem('autosave_' + formId);
    if (savedData) {
        try {
            saveData = JSON.parse(savedData);
            inputs.forEach(function(input) {
                if (saveData[input.name]) {
                    input.value = saveData[input.name];
                }
            });
        } catch (e) {
            console.log('Error loading saved data:', e);
        }
    }
    
    // Auto-save functionality
    inputs.forEach(function(input) {
        input.addEventListener('input', function() {
            saveData[input.name] = input.value;
            localStorage.setItem('autosave_' + formId, JSON.stringify(saveData));
        });
    });
    
    // Clear saved data on successful submit
    form.addEventListener('submit', function() {
        localStorage.removeItem('autosave_' + formId);
    });
}

// Quiz progress tracking
function updateQuizProgress(currentQuestion, totalQuestions) {
    var progressBar = document.getElementById('quiz-progress');
    if (progressBar) {
        var percentage = (currentQuestion / totalQuestions) * 100;
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
        
        var progressText = document.getElementById('quiz-progress-text');
        if (progressText) {
            progressText.textContent = 'Question ' + currentQuestion + ' of ' + totalQuestions;
        }
    }
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show success message
        var toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = 
            '<div class="d-flex">' +
                '<div class="toast-body">Copied to clipboard!</div>' +
                '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
            '</div>';
        
        document.body.appendChild(toast);
        var bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            document.body.removeChild(toast);
        });
    });
}

// Print functionality
function printPage() {
    window.print();
}

// Download PDF functionality
function downloadPDF(url) {
    var link = document.createElement('a');
    link.href = url;
    link.download = '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
