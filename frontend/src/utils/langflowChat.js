import { getUserId } from "./identity";

const LANGFLOW_SCRIPT_ID = "langflow-embedded-chat-script";
const LANGFLOW_SCRIPT_SRC =
  "https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js";
const LANGFLOW_WINDOW_TITLE = "SafePath Bot";
const LANGFLOW_FLOW_ID = process.env.VUE_APP_LANGFLOW_CHATBOT_FLOW_ID;
const LANGFLOW_HOST_URL = process.env.VUE_APP_LANGFLOW_HOST;
//console.log("FLOW_ID: ", LANGFLOW_FLOW_ID);
//console.log("HOST_URL: ", LANGFLOW_HOST_URL)

function mountChatWidget(containerId) {
  const chatContainer = document.getElementById(containerId);
  if (chatContainer) {
    // Chat session_id = "chat_" + guest id. The guest id identifies the visitor
    // (filter Session ID in TEXT mode by it to see all their activity), while the
    // "chat_" prefix namespaces this flow so it never shares an Agent-memory
    // bucket with the route flow ("route_...") — that shared-session bleed is
    // what makes the chatbot hallucinate route JSON. getUserId() returns the
    // guest id today; once auth lands it returns the member id — no change here.
    const sessionId = `chat_${getUserId()}`;

    chatContainer.innerHTML = `
    <langflow-chat
  window_title="SafePath Bot"
  flow_id="${LANGFLOW_FLOW_ID}"
  host_url="${LANGFLOW_HOST_URL}"
  session_id="${sessionId}"
  chat_position="top-left" width="400" height="550"

  online="true"
  online_message="Ask me about safe routes in Berlin."
  placeholder="Type a message"

  chat_trigger_style='{"backgroundColor": "#6366f1"}'
  chat_window_style='{"backgroundColor": "#e5ddd5", "boxShadow": "0px 4px 12px rgba(0,0,0,0.5)",
                      "borderRadius": "12px"}'
  bot_message_style='{"backgroundColor": "#f1f5f9", "color": "#0f172a", "borderRadius": "8px 8px 8px 2px",
                      "padding": "10px 14px", "boxShadow": "0 1px 1px rgba(0,0,0,0.12)", "maxWidth": "78%"}'
  user_message_style='{"backgroundColor": "#6366f1", "color": "#ffffff", "borderRadius": "8px 8px 2px 8px",
                        "padding": "10px 14px", "boxShadow": "0 1px 1px rgba(0,0,0,0.12)", "maxWidth": "78%"}'
  input_container_style='{"backgroundColor": "#f0f0f0", "padding": "12px"}'
  input_style='{"backgroundColor": "#ffffff", "border": "none", "borderRadius": "8px", "padding": "10px"}'
  send_button_style='{"borderRadius": "50%", "width": "36px", "height": "36px", "padding": "8px 7px 6px 5px"}'
  send_icon_style='{"color": "#ffffff"}'>
</langflow-chat>
    `;
  }
}

export function mountLangflowChat(containerId) {
  if (typeof document === "undefined") {
    return;
  }

  if (window.customElements && window.customElements.get("langflow-chat")) {
    mountChatWidget(containerId);
    return;
  }

  const existingScript = document.getElementById(LANGFLOW_SCRIPT_ID);

  if (existingScript) {
    existingScript.addEventListener(
      "load",
      () => mountChatWidget(containerId),
      { once: true },
    );
    return;
  }

  const script = document.createElement("script");
  script.id = LANGFLOW_SCRIPT_ID;
  script.src = LANGFLOW_SCRIPT_SRC;
  script.onload = () => mountChatWidget(containerId);

  document.body.appendChild(script);
}