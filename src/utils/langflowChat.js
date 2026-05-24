const LANGFLOW_SCRIPT_ID = 'langflow-embedded-chat-script';
const LANGFLOW_SCRIPT_SRC = 'https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js';
const LANGFLOW_WINDOW_TITLE = 'Simple Agent';
const LANGFLOW_FLOW_ID = 'dd195420-870e-4896-8b6c-794902b319b1';
const LANGFLOW_HOST_URL = 'http://localhost:7860';
const LANGFLOW_API_KEY = 'sk-XZOSAs4iJxFFXp0081ugpVHcgqko-eR68ZHlaoyNcAY';

function mountChatWidget(containerId) {
  const chatContainer = document.getElementById(containerId);

  if (chatContainer) {
    chatContainer.innerHTML = `
      <langflow-chat
        window_title="${LANGFLOW_WINDOW_TITLE}"
        flow_id="${LANGFLOW_FLOW_ID}"
        host_url="${LANGFLOW_HOST_URL}"
        api_key="${LANGFLOW_API_KEY}">
      </langflow-chat>
    `;
  }
}

export function mountLangflowChat(containerId) {
  if (typeof document === 'undefined') {
    return;
  }

  if (window.customElements && window.customElements.get('langflow-chat')) {
    mountChatWidget(containerId);
    return;
  }

  const existingScript = document.getElementById(LANGFLOW_SCRIPT_ID);

  if (existingScript) {
    existingScript.addEventListener('load', () => mountChatWidget(containerId), { once: true });
    return;
  }

  const script = document.createElement('script');
  script.id = LANGFLOW_SCRIPT_ID;
  script.src = LANGFLOW_SCRIPT_SRC;
  script.onload = () => mountChatWidget(containerId);

  document.body.appendChild(script);
}
