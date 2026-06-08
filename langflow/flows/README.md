# Langflow flows

Flows committed to this folder are auto-loaded by the `langflow` service on
first startup (see `LANGFLOW_LOAD_FLOWS_PATH` in `docker-compose.yml`). This
is how teammates and CI get the same SafePath agent without rebuilding it in
the Langflow UI by hand.

## Exporting a flow

1. Open the Langflow UI: <http://localhost:7860>
2. Open the flow you want to share.
3. Click the menu (three dots) on the flow card or in the top bar and choose
   **Export** → **Download JSON**.
4. Save the file into this folder, e.g. `safepath-agent.json`.
5. Commit the JSON to git.

## Updating an existing flow

1. Edit the flow in the Langflow UI.
2. Re-export it as JSON.
3. Overwrite the existing file in this folder.
4. Commit the change so teammates pick it up on their next pull.

This is the test for creating a new webhook
