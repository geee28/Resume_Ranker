import gradio as gr
import pandas as pd
import os

# We'll use your existing `job_text` variable from your code block above.
# If it isn't defined yet, initialize it:
try:
    job_text
except NameError:
    job_text = ""


def save_job_description(desc: str):
    """Stores job description into your existing global `job_text` variable."""
    global job_text
    job_text = read_job_description_from_text(desc or "")
    gr.Info("Job description saved!")


def add_candidate(name: str, file_path: str, state_list: list):
    state_list = list(state_list or [])
    name = (name or "").strip()

    if not name:
        gr.Warning("Please enter a candidate name.")
        df = pd.DataFrame(state_list) if state_list else pd.DataFrame(columns=["name", "path"])
        return state_list, df, name, file_path, gr.update(choices=_dropdown_choices_from_state(state_list), value=None)

    if not file_path or not os.path.isfile(file_path):
        gr.Warning("Please upload a resume file (.pdf/.txt/.docx).")
        df = pd.DataFrame(state_list) if state_list else pd.DataFrame(columns=["name", "path"])
        return state_list, df, name, file_path, gr.update(choices=_dropdown_choices_from_state(state_list), value=None)

    state_list.append({"name": name, "path": file_path})
    gr.Info(f"Added {name}")
    df = pd.DataFrame(state_list)

    # Clear inputs and refresh dropdown choices
    return state_list, df, "", None, gr.update(choices=_dropdown_choices_from_state(state_list), value=None)


def _dropdown_choices_from_state(state_list: list):
    """Return choices as (label, value) pairs. Use file path as the unique value."""
    state_list = state_list or []
    choices = []
    for item in state_list:
        label = f"{item['name']} — {os.path.basename(item['path'])}"
        value = item["path"]  # unique key
        choices.append((label, value))
    return choices


def remove_candidate(selected_path: str, state_list: list):
    """
    Remove a candidate by its file path (unique) and return:
      - updated state
      - updated table DataFrame
      - updated dropdown choices (cleared selection)
    """
    state_list = list(state_list or [])
    if not selected_path:
        gr.Warning("Please select a candidate to remove.")
        df = pd.DataFrame(state_list) if state_list else pd.DataFrame(columns=["name", "path"])
        return state_list, df, gr.update(choices=_dropdown_choices_from_state(state_list), value=None)

    # filter out the selected
    new_state = [c for c in state_list if c["path"] != selected_path]
    if len(new_state) == len(state_list):
        gr.Warning("Candidate not found.")
    else:
        gr.Info("Removed candidate.")

    df = pd.DataFrame(new_state) if new_state else pd.DataFrame(columns=["name", "path"])
    return new_state, df, gr.update(choices=_dropdown_choices_from_state(new_state), value=None)


def get_results(state_list: list):
    """Read files -> text, then call rank_candidates(job_text, candidates)."""
    global job_text
    if not job_text or not job_text.strip():
        gr.Warning("Job description is empty. Please save it first.")
        return pd.DataFrame()

    if not state_list:
        gr.Warning("No candidates added yet.")
        return pd.DataFrame()

    # Build (name, resume_text) list
    candidates = []
    for item in state_list:
        try:
            text = read_file_to_text(item["path"])
        except Exception as e:
            gr.Warning(f"Failed to read {item['name']}: {e}")
            continue
        candidates.append((item["name"], text))

    if not candidates:
        gr.Warning("Could not read any candidate files.")
        return pd.DataFrame()

    df = rank_candidates(job_text, candidates, top_k=10)
    return df


with gr.Blocks(title="Job → Candidates Ranking") as demo:
    gr.Markdown("## Job Description")
    jd_box = gr.Textbox(
        lines=8,
        label="Paste the Job Description",
        placeholder="Describe the role, responsibilities, must-haves, and nice-to-haves..."
    )
    save_jd_btn = gr.Button("Save Job Description", variant="primary")

    gr.Markdown("## Add Candidates")
    candidates_state = gr.State([])  # list of {"name":..., "path":...}

    with gr.Row():
        name_in = gr.Textbox(label="Candidate Name", placeholder="e.g., Jane Doe")
        file_in = gr.File(
            label="Resume (.pdf/.txt/.docx)",
            file_types=[".pdf", ".txt", ".docx"],
            type="filepath"
        )

    with gr.Row():
        add_btn = gr.Button("Add candidate", variant="secondary")
        run_btn = gr.Button("Get results", variant="primary")

    with gr.Row():
        remove_dd = gr.Dropdown(
            label="Select candidate to remove",
            choices=[],  # will be populated dynamically
            interactive=True
        )
    remove_btn = gr.Button("🗑️ Remove selected", variant="secondary")

    table = gr.Dataframe(
        headers=["name", "path"],
        value=pd.DataFrame(columns=["name", "path"]),
        interactive=False,
        label="Saved candidates"
    )

    results_df = gr.Dataframe(label="Ranking Results", interactive=False)

    # Wire events
    save_jd_btn.click(save_job_description, inputs=[jd_box], outputs=None)
    add_btn.click(add_candidate, inputs=[name_in, file_in, candidates_state],
                  outputs=[candidates_state, table, name_in, file_in, remove_dd])
    remove_btn.click(remove_candidate, inputs=[remove_dd, candidates_state],
                     outputs=[candidates_state, table, remove_dd])
    run_btn.click(get_results, inputs=[candidates_state], outputs=[results_df])

demo.launch(share=True)
