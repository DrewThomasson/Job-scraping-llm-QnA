# Job-scraping-llm-QnA
using gpt4all to qua scraped data from LinkedIn

needed installs: 


gpt4all- for loading and running the llms


tqdm -for the terminal loading bar

selenium and firefox are needed for the web scraping from indeed

`pip install tqdm gpt4all ollama selenium PyQt5`

run using `Python run.py` for a modifed json output that answers the specified questions

run using `python run_csv_output.py` for a csv output file that answers the specified questions

## To update all of the code with a git pull withoput a warning run

`git fetch --all && git reset --hard origin/main`
