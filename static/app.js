// Complete exam system with navigation and state management
var nos = [];
var curr = 0;
var data = {};
const NOT_MARKED = 0;
const MARKED = 1;
const BOOKMARKED = 2;
const MARKED_BOOKMARKED = 3;
const SUBMITTED = 4;
const SUBMITTED_BOOKMARKED = 5;

// Global variables for question counts
var attemptedCount = 0;
var totalCount = 0;
var remainingCount = 0;

// Utility function to get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
        document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
        getCookie('csrftoken');
}

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

// Fetch API wrapper with CSRF token
async function apiRequest(url, data, method = 'POST') {
    const response = await fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

function mySnackBar() {
    var x = document.getElementById("snackbar");
    if (x) {
        x.className = "show";
        setTimeout(function () { x.className = x.className.replace("show", ""); }, 10000);
    }
}

// Camera and audio globals
var stream = null;
var capture = null;
var cameraStream = null;
var audioContext = null;
var analyser = null;
var microphone = null;
var javascriptNode = null;
var array = null;
var values = 0;
var length = null;

function startStreaming() {
    stream = document.getElementById("stream");
    capture = document.getElementById("capture");

    var mediaSupport = 'mediaDevices' in navigator;
    navigator.getUserMedia = navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia;

    if (mediaSupport && null == cameraStream) {
        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then(function (mediaStream) {
                cameraStream = mediaStream;
                if (stream) {
                    stream.srcObject = mediaStream;
                    stream.play();
                }

                try {
                    audioContext = new AudioContext();
                    analyser = audioContext.createAnalyser();
                    microphone = audioContext.createMediaStreamSource(mediaStream);
                    javascriptNode = audioContext.createScriptProcessor(2048, 1, 1);

                    analyser.smoothingTimeConstant = 0.8;
                    analyser.fftSize = 1024;

                    microphone.connect(analyser);
                    analyser.connect(javascriptNode);
                    javascriptNode.connect(audioContext.destination);

                    javascriptNode.onaudioprocess = function () {
                        array = new Uint8Array(analyser.frequencyBinCount);
                        analyser.getByteFrequencyData(array);
                        values = 0;

                        length = array.length;
                        for (var i = 0; i < length; i++) {
                            values += (array[i]);
                        }
                    }
                } catch (e) {
                    console.log("Audio context error: " + e);
                }
            })
            .catch(function (err) {
                console.log("Unable to access camera: " + err);
            });
    }
}

function stopStreaming() {
    if (null != cameraStream) {
        var track = cameraStream.getTracks()[0];
        track.stop();
        if (stream) stream.load();
        cameraStream = null;
    }
}

function captureSnapshot() {
    if (null != cameraStream && capture && stream) {
        var ctx = capture.getContext('2d');
        ctx.drawImage(stream, 0, 0, capture.width, capture.height);
        var d1 = capture.toDataURL("image/png");
        var res = d1.replace("data:image/png;base64,", "");

        var average = 0;
        if (length > 0) average = values / length;

        // console.log(average)
        // console.log(Math.round(average - 40));

        if (average) {
            $.post("/video_feed", {
                data: { 'imgData': res, 'voice_db': average, 'testid': tid }
            },
                function (data) {
                    // console.log(data);

                    // Handle Termination
                    if (data.status === 'terminate') {
                        if (typeof Swal !== 'undefined') {
                            Swal.fire({
                                icon: 'error',
                                title: 'Exam Terminated',
                                text: 'You have exceeded the maximum number of violations (10). Your exam is being submitted.',
                                allowOutsideClick: false,
                                timer: 5000,
                                timerProgressBar: true
                            }).then(() => {
                                // Simulate finish button click
                                document.getElementById('finishBtn').click();
                            });
                        } else {
                            alert("Exam Terminated: Excessive Violations.");
                            document.getElementById('finishBtn').click();
                        }
                        return; // Stop processing
                    }

                    if (data.warning) {
                        // Play alert sound if available
                        try {
                            const audio = new Audio('/static/assets/alert.mp3');
                            audio.play().catch(e => console.log("Audio play failed"));
                        } catch (e) { }

                        // Show visual alert
                        if (typeof Swal !== 'undefined') {
                            const Toast = Swal.mixin({
                                toast: true,
                                position: 'top-end',
                                showConfirmButton: false,
                                timer: 3000,
                                timerProgressBar: true,
                                didOpen: (toast) => {
                                    toast.addEventListener('mouseenter', Swal.stopTimer)
                                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                                }
                            });

                            Toast.fire({
                                icon: 'error',
                                title: data.warning
                            });
                        } else {
                            // Fallback if SweetAlert not loaded
                            console.warn("VIOLATION:", data.warning);
                            // Maybe use a custom div or standard alert (though alert is blocking)
                            // document.getElementById('warning-banner').innerText = data.warning;
                        }
                    }
                });
        }
    }
    setTimeout(captureSnapshot, 1000);
}


// MAIN INITIALIZATION
$(document).ready(function () {
    var url = window.location.href;

    // Window focus handling
    window.onfocus = function (event) {
        mySnackBar();
        if (typeof tid !== 'undefined') {
            $.ajax({
                data: { 'testid': tid },
                type: "POST",
                url: "/window_event"
            });
        }
    };

    // Check if we are on the exam page
    // The URL pattern is like /give-test/<test_id>/
    if (url.includes('/give-test/') && !url.endsWith('/give-test/')) {
        console.log("Exam page detected");

        var list = url.split('/');
        // Handle trailing slash
        var testId = list[list.length - 1];
        if (!testId) testId = list[list.length - 2];

        $('.question').remove();

        // Initialize exam
        $.ajax({
            type: "POST",
            url: "/randomize", // or window.location.href if that's where get flag is handled? No, randomize is separate
            // Actually, looks like randomize view returns the list of question IDs
            dataType: "json",
            data: { id: testId },
            success: function (temp) {
                console.log("Questions loaded:", temp);
                nos = temp;
                make_array();
                display_ques(1);
                ques_grid();
            },
            error: function (xhr, status, error) {
                console.log("Randomize error:", error);
                // Fallback if randomize fails? 
            }
        });

        // Timer setup
        var timeElem = $('#time');
        if (timeElem.length > 0) {
            var time = parseInt(timeElem.text());
            if (!isNaN(time)) {
                startTimer(time, timeElem);
                sendTime();
                flag_time = true;
            }
        }
    }

    // EVENT LISTENERS - Attached inside ready to ensure elements exist

    $('#nextBtn').on('click', function (e) {
        e.preventDefault();
        console.log("Next button clicked, current:", curr, "total:", nos.length);
        if (curr < nos.length - 1) {
            curr += 1;
            display_ques(curr + 1);
        } else {
            alert("You are at the last question!");
        }
    });

    $('#prevBtn').on('click', function (e) {
        e.preventDefault();
        console.log("Prev button clicked, current:", curr);
        if (curr > 0) {
            curr -= 1;
            display_ques(curr + 1);
        } else {
            alert("You are at the first question!");
        }
    });

    $('#submitBtn').on('click', async function (e) {
        e.preventDefault();

        // Get the selected answer
        const selectedOption = document.querySelector('input[name="answer-options"]:checked');
        const selectedAnswer = selectedOption ? selectedOption.value : null;

        if (!selectedAnswer) {
            alert("Please select an answer before submitting!");
            return;
        }

        // Update status
        if (!data[curr + 1]) data[curr + 1] = {};
        data[curr + 1].marked = selectedAnswer;
        data[curr + 1].status = SUBMITTED;

        try {
            const response = await apiRequest(window.location.href, {
                flag: 'mark',
                qid: nos[curr],
                ans: selectedAnswer
            }, 'POST');

            console.log('Answer posted successfully', response);

            // Update question grid and counters
            document.getElementById('question-list').innerHTML = '';
            ques_grid();
            updateQuestionCounter();

            // Move to next question automatically
            if (curr < nos.length - 1) {
                curr += 1;
                display_ques(curr + 1);
            }
        } catch (error) {
            console.error("Error submitting answer:", error);
            alert("Failed to submit answer. Please try again.");
        }
    });

    $('#bookmarkBtn').on('click', function (e) {
        e.preventDefault();
        if (!data[curr + 1]) return;

        const status = data[curr + 1].status;

        // Toggle bookmark status
        if (status == MARKED) {
            data[curr + 1].status = MARKED_BOOKMARKED;
        }
        else if (status == SUBMITTED) {
            data[curr + 1].status = SUBMITTED_BOOKMARKED;
        }
        else if (status == MARKED_BOOKMARKED) {
            data[curr + 1].status = MARKED;
        }
        else if (status == SUBMITTED_BOOKMARKED) {
            data[curr + 1].status = SUBMITTED;
        }
        else if (status == BOOKMARKED) {
            data[curr + 1].status = NOT_MARKED;
        }
        else {
            data[curr + 1].status = BOOKMARKED;
        }

        // Update question grid and counters
        document.getElementById('question-list').innerHTML = '';
        ques_grid();
        updateQuestionCounter();
    });

    // Question grid click handler (delegated)
    $('#question-list').on('click', '.question-btn', function () {
        var id = parseInt($(this).text());
        curr = id - 1;
        display_ques(curr + 1);
    });

    // Finish button
    $('#finishBtn').on('click', function (e) {
        e.preventDefault();
        funSubmitExam();
    });

    // Disable right click and copy paste
    $('body').bind('select cut copy paste', function (e) {
        e.preventDefault();
    });
    $("body").on("contextmenu", function (e) {
        return false;
    });

    // Radio button change handler
    $(document).on('change', 'input[name="answer-options"]', function () {
        const selectedValue = this.value;
        const selectedLabel = $(this).closest('.form-check').find('label');

        // Update visual feedback
        $('.form-check-label').removeClass('selected-answer').css('background-color', 'transparent');
        selectedLabel.addClass('selected-answer').css('background-color', 'rgba(0, 255, 0, 0.6)');

        // Update data structure
        if (!data[curr + 1]) data[curr + 1] = {};
        data[curr + 1].marked = selectedValue;
        if (data[curr + 1].status !== SUBMITTED && data[curr + 1].status !== SUBMITTED_BOOKMARKED) {
            data[curr + 1].status = MARKED;
        }

        // Update grid and counters
        $('#question-list').empty();
        ques_grid();
        updateQuestionCounter();
    });
});


var unmark_all = function () {
    // Uncheck all radio buttons
    $('input[name="answer-options"]').prop('checked', false);

    // Reset any visual highlights
    $('.form-check-label').removeClass('selected-answer');
    $('.form-check-input').closest('.form-check').find('.form-check-label').css("background-color", 'transparent');
}

var display_ques = async function (move) {
    unmark_all();
    if (!nos || !nos[curr]) return;

    console.log("Displaying question:", move, "qid:", nos[curr]);

    try {
        const response = await apiRequest(window.location.href, { flag: 'get', no: nos[curr] }, 'POST');

        // document.getElementById('que').textContent = response['q'];
        $('#que').text(response['q']);

        // Update labels for radio buttons
        $('#option-a').next('label').text('𝐀.  ' + response['a']);
        $('#option-b').next('label').text('𝐁.  ' + response['b']);
        $('#option-c').next('label').text('𝐂.  ' + response['c']);
        $('#option-d').next('label').text('𝐃.  ' + response['d']);

        $('#queid').text('Question No. ' + (move));
        $('#mark').text('[MAX MARKS: ' + response['marks'] + ']'); // Updated format to match template

        // Restore selected answer if exists
        if (data[curr + 1] && data[curr + 1].marked != null) {
            const selectedOption = $('#option-' + data[curr + 1].marked);
            if (selectedOption.length) {
                selectedOption.prop('checked', true);
                selectedOption.closest('.form-check').find('label').addClass('selected-answer').css('background-color', 'rgba(0, 255, 0, 0.6)');
            }
        }

        updateQuestionCounter();
    } catch (error) {
        console.error("Error getting question:", error);
    }
}

var flag_time = false;

function startTimer(duration, display) {
    var timer = duration, hours, minutes, seconds;

    var interval = setInterval(function () {
        hours = parseInt(timer / 3600, 10);
        minutes = parseInt((timer % 3600) / 60, 10);
        seconds = parseInt(timer % 60, 10);

        hours = hours < 10 ? "0" + hours : hours;
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.text(hours + ":" + minutes + ":" + seconds);

        if (--timer < 0) {
            finish_test();
            clearInterval(interval);
            flag_time = false;
        }
    }, 1000);
}

async function finish_test() {
    console.log("finish_test called");

    // Ensure all answered questions are saved before marking as completed
    for (let i = 1; i <= nos.length; i++) {
        if (data[i] && data[i].marked && data[i].status !== SUBMITTED && data[i].status !== SUBMITTED_BOOKMARKED) {
            const qid = nos[i - 1];
            const ans = data[i].marked;

            try {
                await apiRequest(window.location.href, {
                    flag: 'mark',
                    qid: qid,
                    ans: ans
                }, 'POST');
            } catch (error) {
                console.error("Error saving answer:", error);
            }
        }
    }

    try {
        const response = await apiRequest(window.location.href, { flag: 'completed' }, 'POST');
        console.log("Test completed successfully", response);
        window.location.replace('/student_index'); // Verify this URL exists, or use /
    } catch (error) {
        console.error("Error completing test:", error);
        // Still redirect even if there's an error
        window.location.replace('/');
    }
}

function sendTime() {
    var intervalTime = setInterval(function () {
        if (flag_time == false) {
            clearInterval(intervalTime);
            return;
        }
        var time = $('#time').text();
        if (!time) return;

        var parts = time.split(':');
        var seconds = 0;
        if (parts.length === 3) {
            seconds = parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
        }

        $.ajax({
            type: 'POST',
            url: window.location.href, // Use current URL which handles the 'time' flag in views.py
            dataType: "json",
            data: { flag: 'time', time: seconds },
        });
    }, 5000);
}

var marked = function () {
    var count = 0;
    if (!nos) return 0;
    for (var i = 1; i <= nos.length; i++) {
        if (data[i] && (data[i].status == SUBMITTED || data[i].status == SUBMITTED_BOOKMARKED)) {
            count++;
        }
    }
    return count;
}

// Function to update question counters
function updateQuestionCounter() {
    if (!nos) return;
    totalCount = nos.length;
    attemptedCount = marked();
    remainingCount = totalCount - attemptedCount;

    // Update the modal content if it exists
    var modalContent = $('#swal2-html-container');
    if (modalContent.length > 0) {
        var tableHtml = '<table><tr><td>TOTAL QUESTIONS:</td><td>' + totalCount + '</td></tr><tr><td>ATTEMPTED:</td><td>' + attemptedCount + '</td></tr><tr><td>REMAINING:</td><td>' + remainingCount + '</td></tr></table>';
        modalContent.html(tableHtml);
    }
}

var ques_grid = function () {
    if (!nos) return;
    // console.log("Generating question grid for", nos.length, "questions");
    document.getElementById("overlay").style.display = "block";
    $('#question-list').empty();

    for (var i = 1; i <= nos.length; i++) {
        if (!data[i]) data[i] = { marked: null, status: NOT_MARKED };

        var color = '';
        var status = data[i].status;
        if (status == NOT_MARKED) {
            color = '#1976D2'; // Blue
        }
        else if (status == SUBMITTED) {
            color = '#42ed62'; // Green
        }
        else if (status == BOOKMARKED || status == SUBMITTED_BOOKMARKED) {
            color = '#e6ed7b'; // Yellow
        }
        else {
            color = '#f44336'; // Red
        }

        var j = i < 10 ? "0" + i : i;
        var buttonHtml = '<div class="col-sm-2 mb-2"><button class="btn btn-primary question-btn" style="background-color:' + color + '; color:white; width:100%; height:40px; border:none;">' + j + '</button></div>';
        $('#question-list').append(buttonHtml);
    }
}

var make_array = function () {
    if (!nos) return;
    for (var i = 0; i < nos.length; i++) {
        data[i + 1] = { marked: null, status: NOT_MARKED };
    }

    if (typeof answers !== 'undefined' && answers) {
        try {
            // Check if answers is already an object or string
            var ansObj = answers;
            if (typeof answers === 'string') {
                // Clean up potential template artifacts
                var div = document.createElement('div');
                div.innerHTML = answers;
                ansObj = JSON.parse(div.textContent || div.innerText || '{}');
            }

            for (var key in ansObj) {
                var idx = parseInt(key) + 1;
                if (data[idx]) {
                    data[idx].marked = ansObj[key];
                    data[idx].status = SUBMITTED;
                }
            }
        } catch (e) {
            console.log("Error parsing answers:", e);
        }
    }

    updateQuestionCounter();
}

function funSubmitExam() {
    // console.log("funSubmitExam called");
    updateQuestionCounter();

    if (typeof Swal === 'undefined') {
        if (confirm("Are you sure you want to finish the exam?")) {
            finish_test();
        }
        return;
    }

    Swal.fire({
        title: '<strong>FINISH EXAM</strong>',
        icon: 'warning',
        html:
            '<table><tr><td>TOTAL QUESTIONS:</td><td>' + totalCount + '</td></tr><tr><td>ATTEMPTED:</td><td>' + attemptedCount + '</td></tr><tr><td>REMAINING:</td><td>' + remainingCount + '</td></tr></table>',
        showCloseButton: false,
        showCancelButton: true,
        focusConfirm: true,
        confirmButtonText: 'OK, FINISH MY EXAM!',
        confirmButtonAriaLabel: 'We are abide by rules!'
    }).then((result) => {
        if (result.isConfirmed) {
            finish_test();
        }
    })
}

// Global key handlers
document.addEventListener('keyup', (e) => {
    if (e.key == 'PrintScreen') {
        if (navigator.clipboard) navigator.clipboard.writeText('');
        alert('Screenshots disabled!');
    }
});

document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key == 'p') {
        alert('This section is not allowed to print or export to PDF');
        e.cancelBubble = true;
        e.preventDefault();
        e.stopImmediatePropagation();
    }
});


// Environment Check Polling
function checkEnvironment() {
    // Only check if test_id (tid) is defined (i.e. we are in an exam)
    if (typeof tid === 'undefined' || !tid) return;

    $.ajax({
        url: '/exams/check-environment/',
        type: 'GET',
        data: { test_id: tid },
        success: function (response) {
            if (!response.is_safe) {
                console.warn("Unsafe environment detected:", response.checks);

                // Show alert
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        icon: 'error',
                        title: 'Prohibited Environment Detected',
                        text: 'Virtual Machine, Debugger, or Sandbox detected! This is a violation.',
                        allowOutsideClick: false,
                        confirmButtonText: 'I Understand'
                    });
                } else {
                    alert("Prohibited Environment Detected (VM/Debugger)!");
                }
            }
        },
        error: function (err) {
            console.error("Environment check failed:", err);
        }
    });
}

// Start polling every 30 seconds
setInterval(checkEnvironment, 30000);
