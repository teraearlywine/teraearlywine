```python
import os
import base64
import datetime
from github import Github, InputGitTreeElement, GithubException
import openai
from dotenv import load_dotenv

load_dotenv()

# Load credentials from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

REPO_NAME = 'teraearlywine/teraearlywine'

if not GITHUB_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Both GITHUB_TOKEN and OPENAI_API_KEY must be set as environment variables.")

# Authenticate with GitHub
github_client = Github(GITHUB_TOKEN)

try:
    repo = github_client.get_repo(REPO_NAME)
    print(f"Authenticated to repository: {repo.full_name}")
except GithubException as e:
    print(f"Authentication failed: {e.data['message']}")
    raise

# Authenticate with OpenAI
openai.api_key = OPENAI_API_KEY

# Get the default branch
default_branch = repo.default_branch

# Create a new branch with a timestamp
new_branch_name = f'code-improvements-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
source_branch = repo.get_branch(default_branch)
repo.create_git_ref(ref=f'refs/heads/{new_branch_name}', sha=source_branch.commit.sha)

# List to hold updated files
element_list = []

# Function to process files
def process_file(file_content):
    if file_content.size > 1_000_000:
        file_content = repo.get_contents(file_content.path, ref=default_branch)
        
    decoded_content = base64.b64decode(file_content.content).decode('utf-8')

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that improves Python code quality. Only return the code itself."
            },
            {
                "role": "user",
                "content": f"Improve the following Python code for better readability, efficiency, and compliance with PEP8 standards:\n\n{decoded_content}"
            }
        ],
        temperature=0.7,
        max_tokens=1500,
    )

    return response.choices[0].message.content.strip()

# Iterate over files in the repository
contents = repo.get_contents("", ref=default_branch)

while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path))
    elif file_content.path.endswith('.py'):
        improved_code = process_file(file_content)
        element = InputGitTreeElement(
            path=file_content.path,
            mode='100644',
            type='blob',
            content=improved_code
        )
        element_list.append(element)

# Commit the changes if there are any
if element_list:
    base_tree = repo.get_git_tree(source_branch.commit.sha)
    tree = repo.create_git_tree(element_list, base_tree)
    parent_commit = repo.get_git_commit(source_branch.commit.sha)
    commit_message = 'Automated code improvements using GPT-4'
    commit = repo.create_git_commit(commit_message, tree, [parent_commit])
    repo.get_git_ref(f'heads/{new_branch_name}').edit(commit.sha)

    # Create a Pull Request
    pull_request = repo.create_pull(
        title='Automated Code Improvements',
        body='This PR includes code improvements made by GPT-4.',
        head=new_branch_name,
        base=default_branch
    )
    print(f'Pull Request created: {pull_request.html_url}')
else:
    print('No Python files found to improve.')
```