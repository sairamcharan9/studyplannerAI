// StudyplannerAI main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // Form submission
    const studyPlanForm = document.getElementById('studyPlanForm');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');

    // Example buttons
    const exampleButtons = document.querySelectorAll('.example-btn');
    
    // Action buttons
    const printButton = document.getElementById('printButton');
    const downloadButton = document.getElementById('downloadButton');
    const newPlanButton = document.getElementById('newPlanButton');
    const topicInput = document.getElementById('topic');
    const suggestionsContainer = document.getElementById('suggestions-container');
    let suggestionDebounceTimer;

    // Handle topic input for smart suggestions
    if (topicInput && suggestionsContainer) {
        topicInput.addEventListener('input', () => {
            clearTimeout(suggestionDebounceTimer);
            suggestionDebounceTimer = setTimeout(async () => {
                const query = topicInput.value.trim();
                if (query.length > 2) {
                    try {
                        const response = await fetch(`/api/suggestions?query=${encodeURIComponent(query)}`);
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        const suggestions = await response.json();
                        displaySuggestions(suggestions);
                    } catch (error) {
                        console.error('Error fetching suggestions:', error);
                        suggestionsContainer.classList.add('hidden');
                    }
                } else {
                    suggestionsContainer.classList.add('hidden');
                }
            }, 300); // Debounce for 300ms
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!topicInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                suggestionsContainer.classList.add('hidden');
            }
        });
    }

    // Function to display suggestions
    function displaySuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            suggestionsContainer.classList.add('hidden');
            return;
        }

        suggestionsContainer.innerHTML = '';
        suggestions.forEach(suggestion => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'p-2 cursor-pointer hover:bg-gray-100';
            suggestionItem.textContent = suggestion;
            suggestionItem.addEventListener('click', () => {
                topicInput.value = suggestion;
                suggestionsContainer.classList.add('hidden');
            });
            suggestionsContainer.appendChild(suggestionItem);
        });
        suggestionsContainer.classList.remove('hidden');
    }

    // Handle form submission
    if (studyPlanForm) {
        studyPlanForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading indicator
            loadingIndicator.classList.remove('hidden');
            resultsSection.classList.add('hidden');
            
            // Get form data
            const formData = new FormData(studyPlanForm);
            const jsonData = {};
            
            // Process goals - convert comma-separated string to array
            const goalsValue = formData.get('goals');
            if (goalsValue && goalsValue.trim() !== '') {
                const goalsArray = goalsValue.split(',').map(goal => goal.trim()).filter(goal => goal !== '');
                jsonData.goals = goalsArray;
                formData.delete('goals');  // Remove from formData so we don't double-process
            }
            
            // Convert FormData to JSON
            for (const [key, value] of formData.entries()) {
                if (key === 'include_resources' || key === 'generate_goals') {
                    jsonData[key] = value === 'on';
                } else if (key === 'depth_level' || key === 'duration_weeks') {
                    jsonData[key] = parseInt(value, 10);
                } else if (value === '') {
                    // Skip empty values to reduce payload size
                    continue;
                } else {
                    jsonData[key] = value;
                }
            }
            
            try {
                // Send data to API
                const response = await fetch('/api/generate-study-plan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(jsonData)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                
                const data = await response.json();
                displayResults(data);
                
                // Hide loading, show results
                loadingIndicator.classList.add('hidden');
                resultsSection.classList.remove('hidden');
                
                // Scroll to results
                resultsSection.scrollIntoView({ behavior: 'smooth' });
                
            } catch (error) {
                console.error('Error generating study plan:', error);
                loadingIndicator.classList.add('hidden');
                
                // Show error message
                alert('An error occurred while generating your study plan. Please try again.');
            }
        });
    }
    
    // Handle example buttons
    if (exampleButtons) {
        exampleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const topic = this.getAttribute('data-topic');
                if (topic) {
                    document.getElementById('topic').value = topic;
                    // Scroll to form
                    studyPlanForm.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }
    
    // Handle print button
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }
    
    // Handle download as PDF
    if (downloadButton) {
        downloadButton.addEventListener('click', function() {
            alert('PDF download functionality will be implemented in future updates.');
            // For actual implementation, would use a library like html2pdf.js
        });
    }
    
    // Handle new plan button
    if (newPlanButton) {
        newPlanButton.addEventListener('click', function() {
            resultsSection.classList.add('hidden');
            studyPlanForm.reset();
            studyPlanForm.scrollIntoView({ behavior: 'smooth' });
        });
    }
    
    // Function to display results
    function displayResults(data) {
        // Set title and topic
        document.getElementById('resultTitle').textContent = `Study Plan: ${data.topic}`;
        document.getElementById('resultSubtitle').textContent = `${data.duration_weeks}-week study roadmap`;
        
        // Set summary
        document.getElementById('planSummary').textContent = data.summary;
        
        // Set learning objectives
        const objectivesList = document.getElementById('learningObjectives');
        objectivesList.innerHTML = '';
        if (data.learning_objectives && data.learning_objectives.length > 0) {
            data.learning_objectives.forEach(objective => {
                const li = document.createElement('li');
                li.textContent = objective;
                objectivesList.appendChild(li);
            });
        }
        
        // Set key concepts
        const conceptsList = document.getElementById('keyConcepts');
        conceptsList.innerHTML = '';
        if (data.key_concepts && data.key_concepts.length > 0) {
            data.key_concepts.forEach(concept => {
                const li = document.createElement('li');
                li.textContent = concept;
                conceptsList.appendChild(li);
            });
        }
        
        // Set milestones
        const milestonesContainer = document.getElementById('milestones');
        milestonesContainer.innerHTML = '';
        if (data.milestones && data.milestones.length > 0) {
            data.milestones.forEach(milestone => {
                const milestoneDiv = document.createElement('div');
                milestoneDiv.className = 'bg-gray-50 p-4 rounded-md';
                
                const titleDiv = document.createElement('div');
                titleDiv.className = 'font-bold text-gray-800 mb-1';
                titleDiv.textContent = milestone.title;
                
                const descDiv = document.createElement('div');
                descDiv.className = 'text-gray-600 mb-2 text-sm';
                descDiv.textContent = milestone.description;
                
                const hoursDiv = document.createElement('div');
                hoursDiv.className = 'text-xs text-gray-500 mb-2';
                hoursDiv.textContent = `Estimated time: ${milestone.estimated_hours} hours`;
                
                const tasksList = document.createElement('ul');
                tasksList.className = 'list-disc pl-5 text-sm';
                
                milestone.tasks.forEach(task => {
                    const taskItem = document.createElement('li');
                    taskItem.textContent = task;
                    tasksList.appendChild(taskItem);
                });
                
                milestoneDiv.appendChild(titleDiv);
                milestoneDiv.appendChild(descDiv);
                milestoneDiv.appendChild(hoursDiv);
                milestoneDiv.appendChild(tasksList);
                
                milestonesContainer.appendChild(milestoneDiv);
            });
        }
        
        // Set resources
        const resourcesSection = document.getElementById('resourcesSection');
        const resourcesContainer = document.getElementById('resources');
        resourcesContainer.innerHTML = '';
        
        if (data.resources && data.resources.length > 0) {
            resourcesSection.classList.remove('hidden');
            
            data.resources.forEach(resource => {
                const resourceDiv = document.createElement('div');
                resourceDiv.className = 'flex items-start';
                
                // Icon based on resource type
                const iconDiv = document.createElement('div');
                iconDiv.className = 'flex-shrink-0 mt-1';
                
                let iconClass = 'fa-file-alt'; // default
                if (resource.type) {
                    const type = resource.type.toLowerCase();
                    if (type.includes('book')) iconClass = 'fa-book';
                    else if (type.includes('video')) iconClass = 'fa-video';
                    else if (type.includes('course')) iconClass = 'fa-graduation-cap';
                    else if (type.includes('article')) iconClass = 'fa-newspaper';
                    else if (type.includes('document')) iconClass = 'fa-file-alt';
                    else if (type.includes('tool')) iconClass = 'fa-tools';
                    else if (type.includes('community')) iconClass = 'fa-users';
                }
                
                iconDiv.innerHTML = `<i class="fas ${iconClass} text-gray-500"></i>`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'ml-3';
                
                const titleSpan = document.createElement('span');
                if (resource.url) {
                    const titleLink = document.createElement('a');
                    titleLink.href = resource.url;
                    titleLink.target = '_blank';
                    titleLink.className = 'text-primary-600 hover:underline font-medium';
                    titleLink.textContent = resource.title;
                    titleSpan.appendChild(titleLink);
                } else {
                    titleSpan.className = 'font-medium text-gray-800';
                    titleSpan.textContent = resource.title;
                }
                
                const typeSpan = document.createElement('span');
                typeSpan.className = 'text-xs text-gray-500 ml-2';
                typeSpan.textContent = resource.type || '';
                
                const descDiv = document.createElement('div');
                descDiv.className = 'text-sm text-gray-600';
                descDiv.textContent = resource.description || '';
                
                contentDiv.appendChild(titleSpan);
                contentDiv.appendChild(typeSpan);
                contentDiv.appendChild(descDiv);
                
                resourceDiv.appendChild(iconDiv);
                resourceDiv.appendChild(contentDiv);
                
                resourcesContainer.appendChild(resourceDiv);
            });
        } else {
            resourcesSection.classList.add('hidden');
        }
        
        // Set recommendations
        const recommendationsSection = document.getElementById('recommendationsSection');
        const recommendationsContent = document.getElementById('recommendations');
        
        if (data.recommendations) {
            recommendationsSection.classList.remove('hidden');
            recommendationsContent.textContent = data.recommendations;
        } else {
            recommendationsSection.classList.add('hidden');
        }
    }
});
