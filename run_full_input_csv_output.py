import json
import csv
from gpt4all import GPT4All
from tqdm import tqdm

def load_data(filename):
    """ Load the JSON file containing job postings """
    with open(filename, 'r') as file:
        return json.load(file)

def initialize_model():
    """ Initialize the GPT4All model """
    return GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")
    # or Meta-Llama-3-8B-Instruct.Q4_0.gguf for llama 3 8B
    # orca-mini-3b-gguf2-q4_0.gguf
    # for this longer context i had to download the model from this link
    # https://huggingface.co/crusoeai/Llama-3-8B-Instruct-262k-GGUF/blob/main/llama-3-8b-instruct-262k.Q4_0.gguf
    # Phi-3-mini-128k-instruct

def process_jobs(job_posts, model):
    """ Process each job posting to extract details and generate the formatted response """
    with open('job_results.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the headers to the CSV file
        writer.writerow(['Job URL', 'Job Title', 'Company Name', 'Location', 'Salary', 'Job Type', 'Job Description', 'Experience Required', 'Qualifications', 'Security Clearance', 'Job Location', 'Position Type', 'Programming Languages', 'Raw Generated Output'])

        for job_url, job_details in tqdm(job_posts.items(), desc="Processing Jobs"):
            # Convert entire job_details dictionary into a readable string for the prompt
            details_str = json.dumps(job_details)

            # Create the prompt for the model to extract all job details
            prompt = f"""
            Given the following job data:
            {details_str}
            Please extract and respond with the specific details:
            - What is the job title? (State 'Not mentioned' if not specified)
            - What company is offering the job? (State 'Not mentioned' if not specified)
            - Where is the job located? (State 'Not mentioned' if not specified)
            - What is the salary range? (State 'Not mentioned' if not specified)
            - What type of job is it (full-time, part-time, contract, etc.)? (State 'Not mentioned' if not specified)
            - Provide a brief description of the job. (State 'Not mentioned' if not specified)
            - Does the job require experience? If yes, how many years? (State 'Not mentioned' if not specified)
            - Which qualifications are preferred and which are required? (State 'Not mentioned' if not specified)
            - Is security clearance or US citizenship required? (State 'Not mentioned' if not specified)
            - Is the position on-site, hybrid, or remote? (State 'Not mentioned' if not specified)
            - What programming languages should the candidate know? (State 'Not mentioned' if not specified)
            """

            # Generate output from the model
            generated_output = model.generate(prompt, max_tokens=500)

            # Print the generated output
            print(f"Generated Output for {job_url}: {generated_output}")

            # Parse the output into structured format for CSV
            parsed_output = parse_generated_output(generated_output)

            # Write to CSV using the parsed output
            writer.writerow([
                job_url,
                parsed_output.get('What is the job title?', 'Not mentioned'),
                parsed_output.get('What company is offering the job?', 'Not mentioned'),
                parsed_output.get('Where is the job located?', 'Not mentioned'),
                parsed_output.get('What is the salary range?', 'Not mentioned'),
                parsed_output.get('What type of job is it?', 'Not mentioned'),
                parsed_output.get('Provide a brief description of the job.', 'Not mentioned'),
                parsed_output.get('Does the job require experience?', 'Not mentioned'),
                parsed_output.get('Which qualifications are preferred and which are required?', 'Not mentioned'),
                parsed_output.get('Is security clearance or US citizenship required?', 'Not mentioned'),
                parsed_output.get('Is the position on-site, hybrid, or remote?', 'Not mentioned'),
                parsed_output.get('What programming languages should the candidate know?', 'Not mentioned'),
                generated_output  # Include raw generated output
            ])

def parse_generated_output(generated_output):
    """ Parse the generated output from the model into a structured dictionary """
    output_dict = {}
    lines = generated_output.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            output_dict[key.strip()] = value.strip()
    return output_dict

def main():
    # Load job postings from a JSON file
    job_posts = load_data('job_posts.json')

    # Initialize the GPT4All model
    model = initialize_model()

    # Process each job posting and extract details
    process_jobs(job_posts, model)

if __name__ == "__main__":
    main()
