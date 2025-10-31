document.addEventListener('DOMContentLoaded', function() {
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    const addCalendarButton = document.getElementById('addCalendarButton');

    let currentStudyPlanData = null; // Store the generated study plan data

    // Chat state
    let chatHistory = [];
    let conversationState = 'idle'; // 'idle', 'awaiting_topic', 'generating'

    // Toggle chat window
    chatBubble.addEventListener('click', () => {
        chatWindow.classList.add('show');
        if (conversationState === 'idle') {
            startConversation();
        }
    });

    closeChat.addEventListener('click', () => {
        chatWindow.classList.remove('show');
    });

    // Send message
    sendChatBtn.addEventListener('click', handleUserInput);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleUserInput();
        }
    });

    function startConversation() {
        addBotMessage("Hello! I'm your study plan assistant. What topic would you like to learn about?");
        conversationState = 'awaiting_topic';
    }

    function handleUserInput() {
        const userInput = chatInput.value.trim();
        if (userInput === '') return;

        addUserMessage(userInput);
        chatInput.value = '';

        if (conversationState === 'awaiting_topic') {
            generateStudyPlan(userInput);
        }
    }

    async function generateStudyPlan(topic) {
        conversationState = 'generating';
        addBotMessage("Great! I'm generating a study plan for you. This might take a moment...");

        try {
            const response = await fetch('/api/generate-study-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic: topic })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);
            addBotMessage("I've created your study plan! You can view it on the main page.");
            conversationState = 'idle';

        } catch (error) {
            console.error('Error generating study plan:', error);
            addBotMessage("I'm sorry, but I encountered an error while generating your study plan. Please try again.");
            conversationState = 'awaiting_topic';
        }
    }

    function addMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', `${sender}-message`);
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        chatHistory.push({ sender, message });
    }

    function addUserMessage(message) {
        addMessage('user', message);
    }

    function addBotMessage(message) {
        addMessage('bot', message);
    }

    // Function to display results (adapted for chat)
    function displayResults(data) {
        currentStudyPlanData = data; // Store the data globally
        resultsSection.classList.remove('hidden');
        document.getElementById('resultTitle').textContent = `Study Plan: ${data.topic}`;
        document.getElementById('resultSubtitle').textContent = `${data.duration_weeks}-week study roadmap`;
        document.getElementById('planSummary').textContent = data.summary;

        const objectivesList = document.getElementById('learningObjectives');
        objectivesList.innerHTML = '';
        if (data.learning_objectives && data.learning_objectives.length > 0) {
            data.learning_objectives.forEach(objective => {
                const li = document.createElement('li');
                li.textContent = objective;
                objectivesList.appendChild(li);
            });
        }

        const conceptsList = document.getElementById('keyConcepts');
        conceptsList.innerHTML = '';
        if (data.key_concepts && data.key_concepts.length > 0) {
            data.key_concepts.forEach(concept => {
                const li = document.createElement('li');
                li.textContent = concept;
                conceptsList.appendChild(li);
            });
        }

        const milestonesContainer = document.getElementById('milestones');
        milestonesContainer.innerHTML = '';
        if (data.milestones && data.milestones.length > 0) {
            data.milestones.forEach(milestone => {
                const milestoneDiv = document.createElement('div');
                milestoneDiv.className = 'bg-gray-50 p-4 rounded-md';
                milestoneDiv.innerHTML = `
                    <div class="font-bold text-gray-800 mb-1">${milestone.title}</div>
                    <div class="text-gray-600 mb-2 text-sm">${milestone.description}</div>
                    <div class="text-xs text-gray-500 mb-2">Estimated time: ${milestone.estimated_hours} hours</div>
                    <ul class="list-disc pl-5 text-sm">
                        ${milestone.tasks.map(task => `<li>${task}</li>`).join('')}
                    </ul>
                `;
                milestonesContainer.appendChild(milestoneDiv);
            });
        }

        const resourcesSection = document.getElementById('resourcesSection');
        const resourcesContainer = document.getElementById('resources');
        resourcesContainer.innerHTML = '';
        if (data.resources && data.resources.length > 0) {
            resourcesSection.classList.remove('hidden');
            data.resources.forEach(resource => {
                const resourceDiv = document.createElement('div');
                resourceDiv.className = 'flex items-start';
                let iconClass = 'fa-file-alt';
                if (resource.type) {
                    const type = resource.type.toLowerCase();
                    if (type.includes('book')) iconClass = 'fa-book';
                    else if (type.includes('video')) iconClass = 'fa-video';
                    else if (type.includes('course')) iconClass = 'fa-graduation-cap';
                    else if (type.includes('article')) iconClass = 'fa-newspaper';
                }
                resourceDiv.innerHTML = `
                    <div class="flex-shrink-0 mt-1"><i class="fas ${iconClass} text-gray-500"></i></div>
                    <div class="ml-3">
                        <span class="font-medium text-gray-800">${resource.title}</span>
                        <span class="text-xs text-gray-500 ml-2">${resource.type || ''}</span>
                        <div class="text-sm text-gray-600">${resource.description || ''}</div>
                    </div>
                `;
                resourcesContainer.appendChild(resourceDiv);
            });
        } else {
            resourcesSection.classList.add('hidden');
        }

        const recommendationsSection = document.getElementById('recommendationsSection');
        const recommendationsContent = document.getElementById('recommendations');
        if (data.recommendations) {
            recommendationsSection.classList.remove('hidden');
            recommendationsContent.textContent = data.recommendations;
        } else {
            recommendationsSection.classList.add('hidden');
        }

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });

        // Display calendar events info if available
        if (data.calendar_events_info && data.calendar_events_info.created_events && data.calendar_events_info.created_events.length > 0) {
            let calendarMessage = "Study plan added to calendar:";
            data.calendar_events_info.created_events.forEach(event => {
                if (event.htmlLink) {
                    calendarMessage += ` <a href="${event.htmlLink}" target="_blank" class="text-primary-600 hover:underline">${event.summary}</a>`;
                } else if (event.error) {
                    calendarMessage += ` Failed to add ${event.summary}: ${event.error}`; 
                }
            });
            addBotMessage(calendarMessage);
        } else if (data.calendar_events_info && data.calendar_events_info.error) {
            addBotMessage(`Failed to add study plan to calendar: ${data.calendar_events_info.error}`);
        }
    }

    async function handleAddtoCalendar() {
        if (!currentStudyPlanData) {
            alert("Please generate a study plan first.");
            return;
        }

        // The calendar event creation is already handled in the backend upon study plan generation.
        // This button will simply inform the user or potentially trigger a re-creation if needed.
        // For now, let's just show a message or link to the calendar if events were created.
        if (currentStudyPlanData.calendar_events_info && currentStudyPlanData.calendar_events_info.created_events && currentStudyPlanData.calendar_events_info.created_events.length > 0) {
            let message = "Study plan events were already added to your calendar:";
            currentStudyPlanData.calendar_events_info.created_events.forEach(event => {
                if (event.htmlLink) {
                    message += ` <a href="${event.htmlLink}" target="_blank" class="text-primary-600 hover:underline">${event.summary}</a>`;
                }
            });
            addBotMessage(message);
        } else {
            addBotMessage("No calendar events were created or an error occurred during creation. Please check the server logs for more details.");
        }
    }

    // Facial Expression Analysis Feature Logic
    const facialAnalysisContainer = document.getElementById('facialAnalysisContainer');
    const startCameraButton = document.getElementById('startCameraButton');
    const stopCameraButton = document.getElementById('stopCameraButton');
    const cameraStatus = document.getElementById('cameraStatus');
    const cameraFeed = document.getElementById('cameraFeed');
    const faceCanvas = document.getElementById('faceCanvas');
    const expressionFeedback = document.getElementById('expressionFeedback');
    let stream = null;
    let captureInterval = null;
    let facialAnalysisEnabled = false;

    async function checkFacialAnalysisSetting() {
        try {
            const response = await fetch('/settings');
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const settings = await response.json();
            facialAnalysisEnabled = settings.ENABLE_FACIAL_ANALYSIS === 'true';

            if (facialAnalysisEnabled) {
                facialAnalysisContainer.classList.remove('hidden');
            } else {
                facialAnalysisContainer.classList.add('hidden');
            }
        } catch (error) {
            console.error('Error loading facial analysis setting:', error);
            facialAnalysisContainer.classList.add('hidden'); // Hide if error
        }
    }

    async function startCamera() {
        if (!facialAnalysisEnabled) {
            alert('Facial Expression Analysis is not enabled in settings.');
            return;
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            cameraFeed.srcObject = stream;
            cameraFeed.classList.remove('hidden');
            faceCanvas.classList.remove('hidden');
            startCameraButton.disabled = true;
            stopCameraButton.disabled = false;
            cameraStatus.textContent = 'Camera: On';
            expressionFeedback.textContent = 'Analyzing expressions...';

            // Set canvas dimensions to match video
            cameraFeed.addEventListener('loadedmetadata', () => {
                faceCanvas.width = cameraFeed.videoWidth;
                faceCanvas.height = cameraFeed.videoHeight;
            });

            captureInterval = setInterval(captureFrame, 1000); // Capture frame every 1 second

        } catch (error) {
            console.error('Error accessing camera:', error);
            cameraStatus.textContent = `Camera: Error - ${error.message}`;
            alert(`Could not start camera: ${error.message}. Please ensure you have a camera and have granted permission.`);
            stopCamera(); // Ensure UI is reset on error
        }
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        cameraFeed.srcObject = null;
        cameraFeed.classList.add('hidden');
        faceCanvas.classList.add('hidden');
        const context = faceCanvas.getContext('2d');
        context.clearRect(0, 0, faceCanvas.width, faceCanvas.height);
        startCameraButton.disabled = false;
        stopCameraButton.disabled = true;
        cameraStatus.textContent = 'Camera: Off';
        expressionFeedback.textContent = '';
        if (captureInterval) {
            clearInterval(captureInterval);
            captureInterval = null;
        }
    }

    async function captureFrame() {
        if (!cameraFeed.srcObject || cameraFeed.paused || cameraFeed.ended) {
            console.warn('Video feed not active, skipping frame capture.');
            return;
        }

        const context = faceCanvas.getContext('2d');
        context.drawImage(cameraFeed, 0, 0, faceCanvas.width, faceCanvas.height);
        const imageDataUrl = faceCanvas.toDataURL('image/jpeg', 0.8); // Get image as base64 JPEG

        try {
            const response = await fetch('/api/analyze-expression', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageDataUrl })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            if (result.expression) {
                expressionFeedback.textContent = `You seem: ${result.expression} (Confidence: ${(result.confidence * 100).toFixed(2)}%)`;
            } else if (result.message) {
                expressionFeedback.textContent = result.message;
            } else {
                expressionFeedback.textContent = 'No face detected or analysis inconclusive.';
            }

        } catch (error) {
            console.error('Error sending frame for analysis:', error);
            expressionFeedback.textContent = `Analysis Error: ${error.message}`;
        }
    }

    // Event Listeners for camera control buttons
    startCameraButton.addEventListener('click', startCamera);
    stopCameraButton.addEventListener('click', stopCamera);

    // Event Listener for Add to Calendar button
    addCalendarButton.addEventListener('click', handleAddtoCalendar);

    // Initial check for facial analysis setting when page loads
    checkFacialAnalysisSetting();
});