import requests
import csv
import time

# Replace with your actual GitHub token
GITHUB_TOKEN = "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"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_users_in_dublin():
    users = []
    query = "location:Dublin+followers:>50"
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/search/users?q={query}&per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)
        print(f"Fetching page {page}...")

        if response.status_code == 403:
            print("Rate limit hit. Sleeping for 60 seconds...")
            time.sleep(60)  # Sleep to handle rate limit
            continue

        if response.status_code != 200:
            print("Error fetching data:", response.json())
            break

        data = response.json()
        users.extend(data['items'])

        if len(data['items']) < per_page:
            break

        page += 1

    return users

def get_user_details(username):
    user_url = f"https://api.github.com/users/{username}"
    user_data = requests.get(user_url, headers=HEADERS).json()

    return {
        'login': user_data.get('login'),
        'name': user_data.get('name'),
        'company': clean_company_name(user_data.get('company')),
        'location': user_data.get('location'),
        'email': user_data.get('email'),
        'hireable': user_data.get('hireable'),
        'bio': user_data.get('bio'),
        'public_repos': user_data.get('public_repos'),
        'followers': user_data.get('followers'),
        'following': user_data.get('following'),
        'created_at': user_data.get('created_at'),
    }

def clean_company_name(company):
    if company:
        company = company.strip().upper()
        if company.startswith('@'):
            company = company[1:]
    return company

def get_user_repos(username):
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=500"
    response = requests.get(repos_url, headers=HEADERS)
    
    if response.status_code == 403:
        print(f"Rate limit hit while fetching repos for {username}. Sleeping for 60 seconds...")
        time.sleep(60)  # Handle rate limit by sleeping
        response = requests.get(repos_url, headers=HEADERS)  # Retry

    repos_data = response.json()

    repos = []
    for repo in repos_data:
        repos.append({
            'login': username,
            'full_name': repo['full_name'],
            'created_at': repo['created_at'],
            'stargazers_count': repo['stargazers_count'],
            'watchers_count': repo['watchers_count'],
            'language': repo['language'],
            'has_projects': repo['has_projects'],
            'has_wiki': repo['has_wiki'],
            'license_name': repo['license']['key'] if repo['license'] else None,
        })

    return repos

def save_users_to_csv(users):
    with open('users.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['login', 'name', 'company', 'location', 'email', 'hireable', 'bio', 'public_repos', 'followers', 'following', 'created_at'])
        writer.writeheader()
        writer.writerows(users)

def save_repos_to_csv(repos):
    with open('repositories.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['login', 'full_name', 'created_at', 'stargazers_count', 'watchers_count', 'language', 'has_projects', 'has_wiki', 'license_name'])
        writer.writeheader()
        writer.writerows(repos)

if __name__ == "__main__":
    users = get_users_in_dublin()
    detailed_users = []
    for user in users:
        user_info = get_user_details(user['login'])
        detailed_users.append(user_info)
    
    save_users_to_csv(detailed_users)

    all_repos = []
    for user in detailed_users:
        repos = get_user_repos(user['login'])
        all_repos.extend(repos)

    save_repos_to_csv(all_repos)
    print("Done")
