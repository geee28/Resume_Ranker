# Resume Ranker

### Problem: 
Recruiters often face hundreds of resumes per role. Manually identifying the most relevant candidates is time-consuming and error-prone, and it’s easy to overlook both obvious and subtle matches!

### Solution:
This tool uses modern embedding models to represent both the job description and resumes as high-dimensional vectors. By comparing these embeddings with cosine similarity, it ranks candidates from most to least relevant, speeding up shortlisting while improving accuracy.

### Detailed Approach (backend):
Let's break the problem into simple blocks of concepts/code: 
- Accept a job description as text - perform cleaning operations if needed 
- Allow for candidate names and resumes to be uploaded (file types supported currently: .pdf, .docx and .txt)
- Load the embedding model and compute embeddings for both - job description and list of candidate resumes
- Use cosine similarity to find and rank the candidate resumes! 


### Future Direction:
The next steps look like this: 
- Add "Remove candidate" to remove specific candidates and regenerate rankings instead of re-running the entire pipeline!
- Add better cleaning and preprocessing strategies for the text inputs 
- Use summarization tools to generate a summary for why the respective candidate would be perfect for the role 
- The ranking currently solely depends on the embedding model - therefore a good idea would be to experiment with different embedding models! 
- Frontend - there's always room for improvement in this! 

### How to run and replicate the project in your local system? 
Step 1: Use the requirements.txt file to ensure all the necessary libraries have been downloaded. You can do this by running the following command: 

<code> pip install -r requirements.txt </code>

Step 2: Simply run the app.py file. It will prompt you to a URL link that renders a simple gradio frontend for the project! 

<code> python app.py </code>


### Feedback
Always open to suggestions! This work has been exploratory and I'd love to make it better! 