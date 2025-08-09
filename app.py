from backend import read_job_description_from_text, read_file_to_text, rank_candidates

import gradio as gr
import pandas as pd
import os


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
    """
    Append (name, path) to state list and return:
      - updated state list
      - updated table DataFrame
      - empty string for name field (to clear it)
      - None for file input (to clear it)
    """
    state_list = list(state_list or [])
    name = (name or "").strip()

    if not name:
        gr.Warning("Please enter a candidate name.")
        return state_list, pd.DataFrame(state_list) if state_list else pd.DataFrame(columns=["name", "path"]), name, file_path

    if not file_path or not os.path.isfile(file_path):
        gr.Warning("Please upload a resume file (.pdf/.txt/.docx).")
        return state_list, pd.DataFrame(state_list) if state_list else pd.DataFrame(columns=["name", "path"]), name, file_path

    state_list.append({"name": name, "path": file_path})
    gr.Info(f"Added {name}")

    df = pd.DataFrame(state_list)
    # Reset candidate name and file upload
    return state_list, df, "", None


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

    table = gr.Dataframe(
        headers=["name", "path"],
        value=pd.DataFrame(columns=["name", "path"]),
        interactive=False,
        label="Saved candidates"
    )

    results_df = gr.Dataframe(label="Ranking Results", interactive=False)

    # Wire events
    save_jd_btn.click(save_job_description, inputs=[jd_box], outputs=None)
    add_btn.click(add_candidate, inputs=[name_in, file_in, candidates_state], outputs=[candidates_state, table, name_in, file_in])
    run_btn.click(get_results, inputs=[candidates_state], outputs=[results_df])

demo.launch(share=True)
