document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('scan-video');
    const canvas = document.getElementById('scan-canvas');
    const context = canvas.getContext('2d');
    const btnStartScan = document.getElementById('btn-start-scan');
    const btnStartExam = document.getElementById('btn-start-exam');
    const progressBar = document.getElementById('scan-progress-bar');
    const progressContainer = document.getElementById('scan-progress-container');
    const statusBadge = document.getElementById('status-badge');
    const detectedObjectsDiv = document.getElementById('detected-objects');

    let isScanning = false;
    let scanInterval = null;
    let cleanFrames = 0;
    const REQUIRED_CLEAN_FRAMES = 5; // Reduced to 5 seconds for better usability
    const SCAN_INTERVAL_MS = 1000;

    // Access Webcam
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (err) {
            console.error("Error accessing webcam: " + err);
            alert("Could not access webcam. Please allow camera permissions.");
        });

    btnStartScan.addEventListener('click', function () {
        if (isScanning) return;
        startScan();
    });

    function startScan() {
        isScanning = true;
        cleanFrames = 0;
        btnStartScan.disabled = true;
        btnStartScan.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';
        progressContainer.style.display = 'flex';
        progressBar.style.width = '0%';
        progressBar.innerText = '0%';
        progressBar.classList.remove('bg-danger', 'bg-success');
        progressBar.classList.add('bg-primary');
        statusBadge.style.display = 'block';
        statusBadge.innerText = 'Scanning Environment...';
        statusBadge.className = 'badge bg-info fs-5';

        scanInterval = setInterval(captureAndSendFrame, SCAN_INTERVAL_MS);
    }

    function stopScan(success) {
        clearInterval(scanInterval);
        isScanning = false;
        btnStartScan.disabled = false;

        if (success) {
            btnStartScan.style.display = 'none';
            btnStartExam.style.display = 'inline-block';
            btnStartExam.classList.remove('disabled');
            statusBadge.innerText = 'Environment Clean! You may start.';
            statusBadge.className = 'badge bg-success fs-5';
            progressBar.classList.remove('bg-primary', 'bg-danger');
            progressBar.classList.add('bg-success');
            progressBar.style.width = '100%';
            progressBar.innerText = '100%';
        } else {
            btnStartScan.innerHTML = '<i class="fas fa-redo"></i> Retry Scan';
            statusBadge.innerText = 'Scan Failed: Prohibited Items Detected';
            statusBadge.className = 'badge bg-danger fs-5';
            progressBar.classList.remove('bg-primary', 'bg-success');
            progressBar.classList.add('bg-danger');
        }
    }

    function captureAndSendFrame() {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg', 0.8);

        // Prepare form data
        const formData = new FormData();
        formData.append('image', imageData);
        formData.append('test_id', TEST_ID);

        fetch(SCAN_API_URL, {
            method: 'POST',
            body: JSON.stringify({
                image: imageData,
                test_id: TEST_ID
            }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
            .then(response => response.json())
            .then(data => {
                console.log("Scan result:", data);
                updateUI(data);
            })
            .catch(error => {
                console.error('Error sending frame:', error);
            });
    }

    function updateUI(data) {
        // Update detected objects list
        if (data.detected && data.detected.length > 0) {
            const detectedHtml = data.detected.map(obj =>
                `<span class="badge bg-danger me-1">${obj}</span>`
            ).join('');
            detectedObjectsDiv.innerHTML = `<strong>Detected:</strong> ${detectedHtml}`;
        } else {
            detectedObjectsDiv.innerHTML = `<span class="text-muted">No prohibited items detected.</span>`;
        }

        if (data.clean) {
            cleanFrames++;
            const progress = Math.min((cleanFrames / REQUIRED_CLEAN_FRAMES) * 100, 100);
            progressBar.style.width = `${progress}%`;
            progressBar.innerText = `${Math.round(progress)}%`;

            if (cleanFrames >= REQUIRED_CLEAN_FRAMES) {
                stopScan(true);
            }
        } else {
            cleanFrames = 0; // Reset streak on violation
            progressBar.style.width = '0%';
            progressBar.innerText = 'Reset (Violation Detected)';
            progressBar.classList.add('bg-danger');
            setTimeout(() => progressBar.classList.remove('bg-danger'), 500);

            // Optional: Shake effect or alert
        }
    }

    // Utility to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
