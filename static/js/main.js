// TasVID - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme preference or use device preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.classList.toggle('dark', savedTheme === 'dark');
        if (themeToggle) {
            themeToggle.checked = savedTheme === 'dark';
        }
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        body.classList.add('dark');
        if (themeToggle) {
            themeToggle.checked = true;
        }
    }
    
    // Theme toggle event listener
    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            body.classList.toggle('dark');
            localStorage.setItem('theme', body.classList.contains('dark') ? 'dark' : 'light');
        });
    }
    
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navbarNav = document.querySelector('.navbar-nav');
    
    if (mobileMenuBtn && navbarNav) {
        mobileMenuBtn.addEventListener('click', function() {
            navbarNav.classList.toggle('show');
        });
    }
    
    // URL analyzer functionality
    const analyzeForm = document.getElementById('analyze-form');
    const videoUrlInput = document.getElementById('video-url');
    const analyzeBtn = document.getElementById('analyze-btn');
    const videoPreview = document.getElementById('video-preview');
    const formatOptions = document.getElementById('format-options');
    const downloadForm = document.getElementById('download-form');
    const downloadBtn = document.getElementById('download-btn');
    
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = videoUrlInput.value.trim();
            if (!url) {
                showAlert('Please enter a YouTube URL', 'danger');
                return;
            }
            
            // Show loading state
            analyzeBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
            analyzeBtn.disabled = true;
            
            // Clear previous results
            if (videoPreview) {
                videoPreview.innerHTML = '';
            }
            if (formatOptions) {
                formatOptions.innerHTML = '';
            }
            if (downloadBtn) {
                downloadBtn.disabled = true;
            }
            
            // Send AJAX request to analyze URL
            fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'url': url
                })
            })
            .then(response => response.json())
            .then(data => {
                // Reset button state
                analyzeBtn.innerHTML = 'Analyze';
                analyzeBtn.disabled = false;
                
                if (data.success) {
                    // Display video preview
                    displayVideoPreview(data.video_info);
                    
                    // Display format options
                    displayFormatOptions(data.video_info.formats);
                    
                    // Enable download button
                    if (downloadBtn) {
                        downloadBtn.disabled = false;
                    }
                    
                    // Show success message
                    showAlert('Video analyzed successfully! Select a format to download.', 'success');
                    
                    // Scroll to format options
                    if (formatOptions) {
                        formatOptions.scrollIntoView({ behavior: 'smooth' });
                    }
                } else {
                    showAlert(data.message || 'Failed to analyze video. Please check the URL and try again.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                analyzeBtn.innerHTML = 'Analyze';
                analyzeBtn.disabled = false;
                showAlert('An error occurred. Please try again.', 'danger');
            });
        });
    }
    
    // Download functionality
    if (downloadForm) {
        downloadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = videoUrlInput.value.trim();
            const selectedFormat = document.querySelector('input[name="format"]:checked');
            const compression = document.getElementById('compression').value;
            
            if (!url) {
                showAlert('Please enter a YouTube URL', 'danger');
                return;
            }
            
            if (!selectedFormat) {
                showAlert('Please select a format', 'danger');
                return;
            }
            
            // Show loading state
            downloadBtn.innerHTML = '<span class="spinner"></span> Starting Download...';
            downloadBtn.disabled = true;
            
            // Get format details
            const formatId = selectedFormat.dataset.formatId;
            const resolution = selectedFormat.dataset.resolution;
            
            // Send AJAX request to start download
            fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'url': url,
                    'format_id': formatId,
                    'resolution': resolution,
                    'compression': compression
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show download progress
                    showDownloadProgress(data.download_id);
                    
                    // Show success message
                    showAlert('Download started! You can view progress below.', 'success');
                } else {
                    downloadBtn.innerHTML = 'Download';
                    downloadBtn.disabled = false;
                    showAlert(data.message || 'Failed to start download. Please try again.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                downloadBtn.innerHTML = 'Download';
                downloadBtn.disabled = false;
                showAlert('An error occurred. Please try again.', 'danger');
            });
        });
    }
    
    // Batch download functionality
    const batchForm = document.getElementById('batch-form');
    const batchUrlsInput = document.getElementById('batch-urls');
    const batchBtn = document.getElementById('batch-btn');
    
    if (batchForm) {
        batchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const urls = batchUrlsInput.value.trim();
            const formatId = document.getElementById('batch-format').value;
            const resolution = document.getElementById('batch-resolution').value;
            const compression = document.getElementById('batch-compression').value;
            
            if (!urls) {
                showAlert('Please enter YouTube URLs', 'danger');
                return;
            }
            
            // Show loading state
            batchBtn.innerHTML = '<span class="spinner"></span> Starting Batch Download...';
            batchBtn.disabled = true;
            
            // Send AJAX request to start batch download
            fetch('/batch-download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'urls': urls,
                    'format_id': formatId,
                    'resolution': resolution,
                    'compression': compression
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show batch progress
                    showBatchProgress(data.batch_id);
                    
                    // Show success message
                    showAlert('Batch download started! You can view progress below.', 'success');
                } else {
                    batchBtn.innerHTML = 'Start Batch Download';
                    batchBtn.disabled = false;
                    showAlert(data.message || 'Failed to start batch download. Please try again.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                batchBtn.innerHTML = 'Start Batch Download';
                batchBtn.disabled = false;
                showAlert('An error occurred. Please try again.', 'danger');
            });
        });
    }
    
    // Helper functions
    function displayVideoPreview(videoInfo) {
        if (!videoPreview) return;
        
        videoPreview.innerHTML = `
            <div class="card fade-in">
                <div class="video-thumbnail">
                    <img src="${videoInfo.thumbnail}" alt="${videoInfo.title}">
                </div>
                <div class="card-body">
                    <h3 class="video-title">${videoInfo.title}</h3>
                    <div class="video-meta">
                        <span><i class="fas fa-clock"></i> ${videoInfo.duration}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    function displayFormatOptions(formats) {
        if (!formatOptions) return;
        
        let html = '<h3>Select Format</h3>';
        html += '<div class="format-options">';
        
        formats.forEach((format, index) => {
            html += `
                <div class="format-option fade-in" style="animation-delay: ${index * 0.1}s">
                    <input type="radio" name="format" id="format-${index}" 
                           data-format-id="${format.format_id}" 
                           data-resolution="${format.resolution}">
                    <label for="format-${index}">
                        <div class="format-name">
                            <strong>${format.resolution}</strong> - ${format.format}
                        </div>
                        <div class="format-size">
                            <i class="fas fa-file"></i> ${format.size}
                        </div>
                    </label>
                </div>
            `;
        });
        
        html += '</div>';
        
        // Add compression options
        html += `
            <div class="form-group fade-in" style="animation-delay: ${formats.length * 0.1}s">
                <label for="compression" class="form-label">Compression Level</label>
                <select id="compression" name="compression" class="form-select">
                    <option value="none">No Compression</option>
                    <option value="low">Low Compression</option>
                    <option value="auto" selected>Auto (Recommended)</option>
                    <option value="high">High Compression</option>
                </select>
            </div>
        `;
        
        formatOptions.innerHTML = html;
        
        // Add click event to format options
        const formatOptionElements = document.querySelectorAll('.format-option');
        formatOptionElements.forEach(option => {
            option.addEventListener('click', function() {
                // Uncheck all options
                formatOptionElements.forEach(opt => {
                    opt.classList.remove('selected');
                });
                
                // Check clicked option
                this.classList.add('selected');
                const radio = this.querySelector('input[type="radio"]');
                radio.checked = true;
                
                // Enable download button
                if (downloadBtn) {
                    downloadBtn.disabled = false;
                }
            });
        });
    }
    
    function showDownloadProgress(downloadId) {
        const progressContainer = document.getElementById('download-progress');
        if (!progressContainer) return;
        
        // Create progress element
        const progressElement = document.createElement('div');
        progressElement.className = 'card fade-in';
        progressElement.innerHTML = `
            <div class="card-header">
                <h3>Download Progress</h3>
            </div>
            <div class="card-body">
                <div class="progress-info">
                    <div class="progress-status">Status: <span id="status-${downloadId}">Starting...</span></div>
                    <div class="progress-details">
                        <span id="progress-percent-${downloadId}">0%</span> - 
                        <span id="progress-speed-${downloadId}">0 KB/s</span> - 
                        <span id="progress-eta-${downloadId}">Calculating...</span>
                    </div>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" id="progress-bar-${downloadId}" style="width: 0%"></div>
                </div>
                <div class="progress-filename" id="progress-filename-${downloadId}"></div>
            </div>
            <div class="card-footer">
                <button class="btn btn-danger btn-sm" onclick="cancelDownload('${downloadId}')">Cancel</button>
            </div>
        `;
        
        progressContainer.innerHTML = '';
        progressContainer.appendChild(progressElement);
        
        // Reset download button
        if (downloadBtn) {
            downloadBtn.innerHTML = 'Download';
            downloadBtn.disabled = false;
        }
        
        // Start progress polling
        pollDownloadProgress(downloadId);
    }
    
    function pollDownloadProgress(downloadId) {
        const statusElement = document.getElementById(`status-${downloadId}`);
        const percentElement = document.getElementById(`progress-percent-${downloadId}`);
        const speedElement = document.getElementById(`progress-speed-${downloadId}`);
        const etaElement = document.getElementById(`progress-eta-${downloadId}`);
        const progressBar = document.getElementById(`progress-bar-${downloadId}`);
        const filenameElement = document.getElementById(`progress-filename-${downloadId}`);
        
        if (!statusElement || !percentElement || !speedElement || !etaElement || !progressBar) return;
        
        const checkProgress = () => {
            fetch(`/download-status/${downloadId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const downloadInfo = data.download_info;
                        
                        // Update status
                        statusElement.textContent = downloadInfo.status.charAt(0).toUpperCase() + downloadInfo.status.slice(1);
                        
                        // Update progress bar
                        const progress = downloadInfo.progress || 0;
                        progressBar.style.width = `${progress}%`;
                        percentElement.textContent = `${Math.round(progress)}%`;
                        
                        // Update speed and ETA
                        speedElement.textContent = downloadInfo.speed || '0 KB/s';
                        etaElement.textContent = downloadInfo.eta || 'Calculating...';
                        
                        // Update filename
                        if (downloadInfo.filename) {
                            filenameElement.textContent = downloadInfo.filename;
                        }
                        
                        // Continue polling if not completed or error
                        if (downloadInfo.status !== 'completed' && downloadInfo.status !== 'error' && downloadInfo.status !== 'cancelled') {
                            setTimeout(checkProgress, 1000);
                        } else if (downloadInfo.status === 'completed') {
                            statusElement.textContent = 'Completed';
                            showAlert('Download completed successfully!', 'success');
                            
                            // Add to history (this would normally happen server-side)
                            // Here we're just updating the UI
                            const historyContainer = document.getElementById('download-history');
                            if (historyContainer) {
                                const historyItem = document.createElement('div');
                                historyItem.className = 'card fade-in';
                                historyItem.innerHTML = `
                                    <div class="card-body">
                                        <h4>${downloadInfo.filename}</h4>
                                        <p>Downloaded to: ${downloadInfo.output_path || 'Unknown location'}</p>
                                    </div>
                                `;
                                historyContainer.prepend(historyItem);
                            }
                        } else if (downloadInfo.status === 'error') {
                            statusElement.textContent = 'Error';
                            showAlert(`Download error: ${downloadInfo.error || 'Unknown error'}`, 'danger');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error checking progress:', error);
                    setTimeout(checkProgress, 2000); // Retry with longer delay on error
                });
        };
        
        // Start checking progress
        checkProgress();
    }
    
    function showBatchProgress(batchId) {
        const batchProgressContainer = document.getElementById('batch-progress');
        if (!batchProgressContainer) return;
        
        // Create progress element
        const progressElement = document.createElement('div');
        progressElement.className = 'card fade-in';
        progressElement.innerHTML = `
            <div class="card-header">
                <h3>Batch Download Progress</h3>
            </div>
            <div class="card-body">
                <div class="batch-stats">
                    <div>Status: <span id="batch-status-${batchId}">Starting...</span></div>
                    <div>Completed: <span id="batch-completed-${batchId}">0</span> / <span id="batch-total-${batchId}">0</span></div>
                    <div>Failed: <span id="batch-failed-${batchId}">0</span></div>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" id="batch-progress-bar-${batchId}" style="width: 0%"></div>
                </div>
            </div>
        `;
        
        batchProgressContainer.innerHTML = '';
        batchProgressContainer.appendChild(progressElement);
        
        // Reset batch button
        if (batchBtn) {
            batchBtn.innerHTML = 'Start Batch Download';
            batchBtn.disabled = false;
        }
        
        // Start progress polling
        pollBatchProgress(batchId);
    }
    
    function pollBatchProgress(batchId) {
        const statusElement = document.getElementById(`batch-status-${batchId}`);
        const completedElement = document.getElementById(`batch-completed-${batchId}`);
        const totalElement = document.getElementById(`batch-total-${batchId}`);
        const failedElement = document.getElementById(`batch-failed-${batchId}`);
        const progressBar = document.getElementById(`batch-progress-bar-${batchId}`);
        
        if (!statusElement || !completedElement || !totalElement || !failedElement || !progressBar) return;
        
        const checkProgress = () => {
            fetch(`/batch-status/${batchId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const batchInfo = data.batch_info;
                        
                        // Update status
                        statusElement.textContent = batchInfo.status.charAt(0).toUpperCase() + batchInfo.status.slice(1);
                        
                        // Update stats
                        completedElement.textContent = batchInfo.completed;
                        totalElement.textContent = batchInfo.total;
                        failedElement.textContent = batchInfo.failed;
                        
                        // Update progress bar
                        const progress = (batchInfo.completed / batchInfo.total) * 100;
                        progressBar.style.width = `${progress}%`;
                        
                        // Continue polling if not completed
                        if (batchInfo.status !== 'completed') {
                            setTimeout(checkProgress, 2000);
                        } else {
                            statusElement.textContent = 'Completed';
                            showAlert('Batch download completed!', 'success');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error checking batch progress:', error);
                    setTimeout(checkProgress, 3000); // Retry with longer delay on error
                });
        };
        
        // Start checking progress
        checkProgress();
    }
    
    // Alert function
    function showAlert(message, type) {
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) return;
        
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} fade-in`;
        alertElement.textContent = message;
        
        // Add close button
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'close';
        closeButton.innerHTML = '&times;';
        closeButton.style.float = 'right';
        closeButton.style.cursor = 'pointer';
        closeButton.style.border = 'none';
        closeButton.style.background = 'none';
        closeButton.style.fontSize = '1.25rem';
        closeButton.style.fontWeight = 'bold';
        closeButton.style.lineHeight = '1';
        closeButton.addEventListener('click', function() {
            alertElement.remove();
        });
        
        alertElement.prepend(closeButton);
        
        // Add to container
        alertContainer.appendChild(alertElement);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertElement.style.opacity = '0';
            setTimeout(() => {
                alertElement.remove();
            }, 300);
        }, 5000);
    }
});

// Global functions
function cancelDownload(downloadId) {
    fetch(`/cancel-download/${downloadId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const statusElement = document.getElementById(`status-${downloadId}`);
            if (statusElement) {
                statusElement.textContent = 'Cancelled';
            }
            showAlert('Download cancelled', 'warning');
        } else {
            showAlert(data.message || 'Failed to cancel download', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('An error occurred while cancelling download', 'danger');
    });
}

// Show alert function for global access
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} fade-in`;
    alertElement.textContent = message;
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'close';
    closeButton.innerHTML = '&times;';
    closeButton.style.float = 'right';
    closeButton.style.cursor = 'pointer';
    closeButton.style.border = 'none';
    closeButton.style.background = 'none';
    closeButton.style.fontSize = '1.25rem';
    closeButton.style.fontWeight = 'bold';
    closeButton.style.lineHeight = '1';
    closeButton.addEventListener('click', function() {
        alertElement.remove();
    });
    
    alertElement.prepend(closeButton);
    
    // Add to container
    alertContainer.appendChild(alertElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertElement.style.opacity = '0';
        setTimeout(() => {
            alertElement.remove();
        }, 300);
    }, 5000);
}
