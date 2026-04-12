#!/usr/bin/env python3
"""Generate Lady Whistledown commentary for movie recommendations."""

import os
import sys
import json
import urllib.request
import urllib.error


def generate_commentary(movie_list: str) -> str:
    """Generate Lady Whistledown-style commentary for the movie list.
    
    Args:
        movie_list: The formatted list of movies from platelet-movie command
        
    Returns:
        Lady Whistledown's witty introduction
    """
    api_key = os.getenv("COPILOT_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not api_key:
        print("Warning: COPILOT_GITHUB_TOKEN/GITHUB_TOKEN not set, using fallback commentary", file=sys.stderr)
        return generate_fallback_commentary()
    
    prompt = f"""You are Lady Whistledown, the gossipy, witty Regency-era society columnist from Bridgerton.

Write a short introduction (2-3 paragraphs) for a weekly email about Netflix movies suitable for platelet donation sessions (90+ minutes long).

Your introduction should:
- Use phrases like "Dear Reader," "This Author has learned," "one must inquire"
- Reference the noble act of platelet donation with theatrical praise
- Be charming, slightly scandalous but appropriate
- Tease the movie selections with intrigue and playful judgment
- NOT list specific movies (that comes after your intro)

Here are the movies that will follow your introduction:

{movie_list}

Write ONLY the Lady Whistledown introduction. Do not include the movie list itself."""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Editor-Version": "vscode/1.95.0",
        "Editor-Plugin-Version": "copilot-chat/0.22.4"
    }
    
    try:
        req = urllib.request.Request(
            "https://api.githubcopilot.com/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"].strip()
            
    except urllib.error.HTTPError as e:
        print(f"Warning: Copilot API error ({e.code}), using fallback commentary", file=sys.stderr)
        print(f"Error details: {e.read().decode('utf-8')}", file=sys.stderr)
        return generate_fallback_commentary()
    except Exception as e:
        print(f"Warning: Failed to generate commentary ({e}), using fallback", file=sys.stderr)
        return generate_fallback_commentary()


def generate_fallback_commentary() -> str:
    """Fallback commentary when API is not available."""
    return """Dear Reader,

This Author has learned of the most charitable pursuit among our distinguished society—the donation of one's very platelets! Such selfless acts require considerable time (upwards of 90 minutes, according to the medical authorities), and what better companion to such noble endeavors than the moving pictures from that scandalous purveyor of entertainment, Netflix?

One must inquire: which cinematic productions are worthy of accompanying such a virtuous deed? This Author has taken it upon herself to investigate the matter most thoroughly. The selections that follow have been chosen with the utmost care, each offering sufficient duration and, dare I say, entertainment value to make one's time in the donation chair pass most agreeably."""


if __name__ == "__main__":
    # Read movie list from stdin
    movie_list = sys.stdin.read()
    
    if not movie_list.strip():
        print("Error: No movie list provided on stdin", file=sys.stderr)
        sys.exit(1)
    
    commentary = generate_commentary(movie_list)
    print(commentary)
