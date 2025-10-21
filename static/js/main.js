document.addEventListener('DOMContentLoaded', function() {
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');

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
    }
});
