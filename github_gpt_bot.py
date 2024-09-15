from dotenv import load_dotenv
from github import Github, InputGitTreeElement, GithubException
import os

import openai
import base64
import datetime


load_dotenv()

# Replace with your own credentials
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

REPO_NAME = 'teraearlywine/teraearlywine'


if not GITHUB_TOKEN or not OPENAI_API_KEY:
    raise ValueError("GITHUB_TOKEN and OPENAI_API_KEY must be set as environment variables.")

# Authenticate with GitHub
g = Github(GITHUB_TOKEN)
try:
    repo = g.get_repo(REPO_NAME)
    print(f"Authenticated to repository: {repo.full_name}")
except GithubException as e:
    print(f"Authentication failed: {e.data['message']}")
    raise

# Authenticate with OpenAI
openai.api_key = OPENAI_API_KEY

# Get the default branch (usually 'main' or 'master')
default_branch = repo.default_branch

# Create a new branch with a timestamp
new_branch_name = f'code-improvements-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
sb = repo.get_branch(default_branch)
repo.create_git_ref(ref='refs/heads/' + new_branch_name, sha=sb.commit.sha)


# List to hold updated files
element_list = []

# Iterate over files in the repository
contents = repo.get_contents("", ref=default_branch)
while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path))
    elif file_content.path.endswith('.py'):
        # For large files, fetch content properly
        if file_content.size > 1_000_000:
            file_content = repo.get_contents(file_content.path, ref=default_branch)
        
        # Decode file content
        decoded_content = base64.b64decode(file_content.content).decode('utf-8')

        # Send code to GPT for improvement
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that improves Python code quality. Only return the code itself."},
                {"role": "user", "content": f"Improve the following Python code for better readability, efficiency, and compliance with PEP8 standards:\n\n{decoded_content}"}
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        improved_code = response.choices[0].message.content.strip()

        # Prepare the updated file for commit
        element = InputGitTreeElement(
            path=file_content.path,
            mode='100644',
            type='blob',
            content=improved_code
        )
        element_list.append(element)

# Commit the changes
if element_list:
    base_tree = repo.get_git_tree(sb.commit.sha)
    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(sb.commit.sha)
    commit_message = 'Automated code improvements using GPT-4'
    commit = repo.create_git_commit(commit_message, tree, [parent])
    repo.get_git_ref('heads/' + new_branch_name).edit(commit.sha)

    # Create a Pull Request
    pr = repo.create_pull(
        title='Automated Code Improvements',
        body='This PR includes code improvements made by GPT-4.',
        head=new_branch_name,
        base=default_branch
    )
    print(f'Pull Request created: {pr.html_url}')
else:
    print('No Python files found to improve.')