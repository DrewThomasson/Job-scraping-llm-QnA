import json
from gpt4all import GPT4All
from tqdm import tqdm

def load_data(filename):
    """ Load the JSON file containing job postings """
    with open(filename, 'r') as file:
        return json.load(file)

def initialize_model():
    """ Initialize the GPT4All model """
    return GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
    #or Meta-Llama-3-8B-Instruct.Q4_0.gguf for llama 3 8B
    #orca-mini-3b-gguf2-q4_0.gguf


def process_jobs(job_posts, model):
    """ Process each job posting to generate the formatted response and print only the generated output """
    for job_url, job_details in tqdm(job_posts.items(), desc="Processing Jobs"):
        # Create the prompt from job details
        prompt = f"""
        Analyze the job details provided and generate a structured response to the following questions:
        - Job Title: {job_details.get('Job Title', 'No entry found for Job Title')}
        - Company Name: {job_details.get('Company Name', 'No entry found for Company Name')}
        - Location: {job_details.get('Location', 'No entry found for Location')}
        - Salary: {job_details.get('Salary', 'No entry found for Salary')}
        - Job Type: {job_details.get('Job Type', 'No entry found for Job Type')}
        - Job Description: {job_details.get('Job Description', 'No entry found for Job Description')}
        
        Questions:
        1. Does the job require experience? If yes, how many years?
        2. Which qualifications are preferred and which are required?
        3. Does it require security clearance or US citizenship?
        4. Is the position on-site, hybrid, or remote?
        5. What is the position type? (contract, temp-to-hire, full-time, part-time, etc.)
        6. What programming languages should the candidate know?

        Please respond in the format:
        - Experience Required: [Yes/No, if yes, years required]
        - Qualifications: [Preferred/Required: details]
        - Security Clearance: [Yes/No, if yes, specifics]
        - Job Location: [On-site/Hybrid/Remote]
        - Position Type: [Contract/Temp-to-Hire/Full-Time/Part-Time]
        - Programming Languages: [Languages required]
        """

        # Generate output from the model
        generated_output = model.generate(prompt, max_tokens=350)

        # Print the generated output
        print(f"Generated Output for {job_url}: {generated_output}")

def main():
    # Load job postings from a JSON file
    job_posts = load_data('job_posts.json')

    # Initialize the GPT4All model
    model = initialize_model()

    # Process each job posting and print generated answers
    process_jobs(job_posts, model)

if __name__ == "__main__":
    main()
