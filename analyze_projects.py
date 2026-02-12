#!/usr/bin/env python3
import re

def parse_hn_thread(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    projects = {}  # Use dict to deduplicate by URL
    current_project = None
    in_project_thread = False

    for i, line in enumerate(lines):
        # Check for top-level comment (starts with username + timestamp without parent links)
        # Pattern: username + time + "ago" but NOT containing "parent"
        if re.search(r'^[a-zA-Z0-9_-]+\s+\d+\s+(second|minute|hour|day)s?\s+ago\s+\|', line):
            # Check if this is a top-level comment (no "parent" in the line)
            if '| parent |' not in line and '| root | parent |' not in line:
                # Save previous project if exists
                if current_project and current_project['url']:
                    url = current_project['url']
                    if url not in projects:
                        projects[url] = current_project
                    else:
                        # Already exists, just add to reply count
                        projects[url]['replies'] += current_project['replies']

                # Extract username
                username = line.split()[0]

                # Look ahead for URL
                url = None
                description_lines = []

                for j in range(i+1, min(i+20, len(lines))):
                    next_line = lines[j].strip()

                    # Found a URL
                    if next_line.startswith('http'):
                        url = next_line
                    # Found the reply marker - end of this comment's content
                    elif next_line == 'reply':
                        break
                    # Collect description
                    elif next_line and not re.match(r'^[a-zA-Z0-9_-]+\s+\d+\s+(second|minute|hour|day)', next_line):
                        if next_line not in ['[–]', '']:
                            description_lines.append(next_line)

                # Only track if there's a URL
                if url:
                    current_project = {
                        'username': username,
                        'url': url,
                        'description': ' '.join(description_lines[:5]),
                        'replies': 0
                    }
                    in_project_thread = True
                else:
                    in_project_thread = False
                    current_project = None

            # This is a nested reply (has "parent" in it)
            elif in_project_thread and current_project:
                current_project['replies'] += 1

    # Add last project
    if current_project and current_project['url']:
        url = current_project['url']
        if url not in projects:
            projects[url] = current_project
        else:
            projects[url]['replies'] += current_project['replies']

    return list(projects.values())

def main():
    projects = parse_hn_thread('/Users/adrian/personal/personal/personal-proj.txt')

    # Sort by number of replies (descending)
    projects_sorted = sorted(projects, key=lambda x: x['replies'], reverse=True)

    print("Top 10 Projects with Most Replies:\n")
    print("=" * 100)

    for i, proj in enumerate(projects_sorted[:10], 1):
        print(f"\n{i}. {proj['username']} - {proj['replies']} replies")
        print(f"   URL: {proj['url']}")
        desc = proj['description'][:120] + '...' if len(proj['description']) > 120 else proj['description']
        print(f"   Description: {desc}")
        print("-" * 100)

    print(f"\n\nTotal unique projects found: {len(projects)}")
    print(f"Total replies across all projects: {sum(p['replies'] for p in projects)}")

if __name__ == '__main__':
    main()
