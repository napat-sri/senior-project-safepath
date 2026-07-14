import { getUserId } from './identity';

const LANGFLOW_SCRIPT_ID = 'langflow-embedded-chat-script';
const LANGFLOW_SCRIPT_SRC = 'https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js';
const LANGFLOW_WINDOW_TITLE = 'SafePath Bot';
const LANGFLOW_FLOW_ID = process.env.VUE_APP_LANGFLOW_CHATBOT_FLOW_ID;
const LANGFLOW_API_KEY = process.env.VUE_APP_LANGFLOW_API_KEY;
// console.log("FLOW_ID: ", LANGFLOW_FLOW_ID);
// console.log("API_KEY: ", LANGFLOW_API_KEY);
// Langflow is private. The chat widget reaches it through the public frontend
// gateway, which proxies /langflow/* to langflow:7860 (prefix stripped). This
// keeps the call same-origin (no mixed-content / CORS issues).
//const LANGFLOW_HOST_URL = process.env.VUE_APP_LANGFLOW_HOST || 'https://safepath.duckdns.org/langflow';
const LANGFLOW_HOST_URL = process.env.VUE_APP_LANGFLOW_HOST

function mountChatWidget(containerId) {
  const chatContainer = document.getElementById(containerId);

  if (chatContainer) {
    // Carry the current identity as the chat session_id so all of a visitor's
    // chatbot messages group under one Langfuse session. getUserId() returns
    // the guest id today; once auth lands it returns the member id — no change
    // needed here. (The widget has no user_id prop, so session_id is the only
    // identity field it can forward to Langfuse.)
    const sessionId = getUserId();
    chatContainer.innerHTML = `
      <langflow-chat
        window_title="${LANGFLOW_WINDOW_TITLE}"
        flow_id="${LANGFLOW_FLOW_ID}"
        host_url="${LANGFLOW_HOST_URL}"
        api_key="${LANGFLOW_API_KEY}"
        session_id="${sessionId}"

        chat_position="bottom-left"
  
        width="450" 
        height="600"

        chat_window_style='{"boxShadow": "0px 4px 12px rgba(0,0,0,0.5)", "borderRadius": "12px"}'
        chat_trigger_style='{"backgroundColor": "#6366f1"}'>
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
