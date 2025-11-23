import os
import requests
import sys

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN is not set")
    sys.exit(1)
REPO_OWNER = "Gan-Shmual"
REPO_NAME = "Gan-shmuel---Green-team"
API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def create_pull_request(head_branch="development", base_branch="main", title=None, body=None):
    if not title:
        title = f"Auto-merge: {head_branch} -> {base_branch}"
    
    if not body:
        body = f"Automated pull request created after successful tests on {head_branch} branch."
    
    url = f"{API_BASE}/pulls"
    data = {
        "title": title,
        "head": head_branch,
        "base": base_branch,
        "body": body
    }

    response = requests.post(url, json=data, headers=HEADERS)

    if response.status_code == 201:
        pr_data = response.json()
        print(f"Pull Request created: #{pr_data['number']}")
        print(f"URL: {pr_data['html_url']}")
        return pr_data['number']
    elif response.status_code == 422:
        print("Pull Request already exists or no changes to merge")
        return get_existing_pr(head_branch, base_branch)
    else:
        print(f"Failed to create PR: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def get_existing_pr(head_branch="development", base_branch="main"):
    url = f"{API_BASE}/pulls"
    params = {
        "head": f"{REPO_OWNER}:{head_branch}",
        "base": base_branch,
        "state": "open"
    }

    response = requests.get(url, params=params, headers=HEADERS)

    if response.status_code == 200:
        prs = response.json()
        if prs:
            print(f"Found existing PR: #{prs[0]['number']}")
            return prs[0]['number']
        
    return None

def merge_pull_request(pr_number, merge_method="merge"):
    url = f"{API_BASE}/pulls/{pr_number}/merge"
    data = {
        "merge_method": merge_method
    }

    response = requests.put(url, json=data, headers=HEADERS)

    if response.status_code == 200:
        print(f"Pull Request #{pr_number} merged successfully")
        return True
    else:
        print(f"Failed to merge PR: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def check_pr_mergeable(pr_number):
    url = f"{API_BASE}/pulls/{pr_number}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        pr_data = response.json()
        mergeable = pr_data.get('mergeable')
        if mergeable is True:
            print(f"PR #{pr_number} is mergeable")
            return True
        elif mergeable is False:
            print(f"PR #{pr_number} has merge conflicts")
            return False
        else:
            print(f"Checking if PR #{pr_number} is mergeable...")
            return None
        
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 github_api.py <create|merge> [pr_number]")
        sys.exit(1)
    
    command = sys.argv[1]

    if command == "create":
        pr_number = create_pull_request()
        if pr_number:
            sys.exit(0)
        else:
            sys.exit(1)

    elif command == "merge":
        if len(sys.argv) < 3:
            print("Error: PR number required for merge command")
            sys.exit(1)
        
        pr_number = int(sys.argv[2])

        import time
        for _ in range(5):
            mergeable = check_pr_mergeable(pr_number)
            if mergeable is True:
                break
            elif mergeable is False:
                sys.exit(1)
            time.sleep(2)
        else:
            print("Timeout waiting for Github to determine mergeability")
            sys.exit(1)
        
        if merge_pull_request(pr_number):
            sys.exit(0)
        else:
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
