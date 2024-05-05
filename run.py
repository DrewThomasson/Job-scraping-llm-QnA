import json
from gpt4all import GPT4All
from tqdm import tqdm

def load_data(filename):
    """ Load the JSON file containing job postings """
    with open(filename, 'r') as file:
        return json.load(file)

def initialize_model():
    """ Initialize the GPT4All model """
    return GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
    #or Meta-Llama-3-8B-Instruct.Q4_0.gguf for llama 3 8B

def process_jobs(job_posts, model):
    """ Process each job posting to generate the formatted response and print input and output """
    output = {}
    for job_url, job_details in tqdm(job_posts.items(), desc="Processing Jobs"):
        # Prepare the input details to print
        input_details = f"""
        Job Title: {job_details.get('Job Title', 'No entry found for Job Title')}
        Company Name: {job_details.get('Company Name', 'No entry found for Company Name')}
        Location: {job_details.get('Location', 'No entry found for Location')}
        Salary: {job_details.get('Salary', 'No entry found for Salary')}
        Job Type: {job_details.get('Job Type', 'No entry found for Job Type')}
        Job Description: {job_details.get('Job Description', 'No entry found for Job Description')}
        """

        # Print the input details
        print(f"Input for {job_url}:\n{input_details}")

        # Create the prompt
        prompt = f"""
        Please analyze the job details and answer in the specified format:
        {input_details}
        -- Answer format: "Job Title: {{answer}}, Salary: {{answer}}, Location: {{answer}}, Type: {{answer}}, Description: {{answer}}"
        """

        # Print the custom prompt for clarity in debugging
        print(f"Prompt for {job_url}:")
        print(prompt)

        # Generate output from the model
        generated_output = model.generate(prompt, max_tokens=150)

        # Print the generated output for monitoring
        print(f"Generated Output for {job_url}:")
        print(generated_output)

        # Store the output
        output[job_url] = generated_output

    return output


def save_results(output):
    """ Save the processed outputs to a file """
    with open('processed_job_posts.json', 'w') as outfile:
        json.dump(output, outfile, indent=4)
    print("Processing complete and data saved.")

def main():
    # Load job postings from a JSON file
    job_posts = load_data('job_posts.json')

    # Initialize the GPT4All model
    model = initialize_model()

    # Process each job posting and generate answers
    processed_data = process_jobs(job_posts, model)

    # Save the processed data to a new JSON file
    save_results(processed_data)

if __name__ == "__main__":
    main()

