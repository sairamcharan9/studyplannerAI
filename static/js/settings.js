document.addEventListener('DOMContentLoaded', function() {
    const settingsForm = document.getElementById('settingsForm');
    const aiProviderSelect = document.getElementById('ai_provider');
    const ollamaSettings = document.getElementById('ollama-settings');
    const openrouterSettings = document.getElementById('openrouter-settings');
    const geminiSettings = document.getElementById('gemini-settings');
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');

    // Function to toggle visibility of settings sections
    function toggleSettings(provider) {
        ollamaSettings.style.display = 'none';
        openrouterSettings.style.display = 'none';
        geminiSettings.style.display = 'none';

        if (provider === 'ollama') {
            ollamaSettings.style.display = 'block';
        } else if (provider === 'openrouter') {
            openrouterSettings.style.display = 'block';
        } else if (provider === 'gemini') {
            geminiSettings.style.display = 'block';
        }
    }

    // Initial toggle based on current selection
    toggleSettings(aiProviderSelect.value);

    // Event listener for AI provider change
    aiProviderSelect.addEventListener('change', function() {
        toggleSettings(this.value);
    });

    // Handle form submission
    settingsForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Reset messages
        successMessage.classList.add('hidden');
        errorMessage.classList.add('hidden');

        const formData = new FormData(settingsForm);
        const jsonData = {};
        for (const [key, value] of formData.entries()) {
            if (value) { // Only include non-empty values
                jsonData[key] = value;
            }
        }

        try {
            const response = await fetch('/settings', {
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
            successMessage.classList.remove('hidden');

        } catch (error) {
            console.error('Error saving settings:', error);
            errorMessage.classList.remove('hidden');
        }
    });

    // Fetch and populate initial settings
    async function loadInitialSettings() {
        try {
            const response = await fetch('/api/settings/get');
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const settings = await response.json();

            // Populate form fields
            document.getElementById('ai_provider').value = settings.AI_PROVIDER || 'ollama';
            document.getElementById('ollama_host').value = settings.OLLAMA_HOST || '';
            document.getElementById('ollama_model').value = settings.OLLAMA_MODEL || '';
            document.getElementById('openrouter_api_key').placeholder = settings.OPENROUTER_API_KEY ? '********' : '';
            document.getElementById('openrouter_model').value = settings.OPENROUTER_MODEL || '';
            document.getElementById('gemini_api_key').placeholder = settings.GEMINI_API_KEY ? '********' : '';
            document.getElementById('gemini_model').value = settings.GEMINI_MODEL || '';

            // Toggle settings visibility based on loaded provider
            toggleSettings(settings.AI_PROVIDER || 'ollama');

        } catch (error) {
            console.error('Error loading initial settings:', error);
        }
    }

    loadInitialSettings();
});
