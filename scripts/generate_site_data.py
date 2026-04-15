#!/usr/bin/env python3
"""Generate data.json for the static website."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_command(cmd: list[str]) -> str:
    """Run a command and return its output.
    
    Args:
        cmd: Command and arguments as list
        
    Returns:
        Command output as string
        
    Raises:
        subprocess.CalledProcessError: If command fails
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e.stderr}", file=sys.stderr)
        raise


def get_movie_data() -> dict:
    """Get movie data from platelet-movie CLI.
    
    Returns:
        Parsed JSON data with movies
        
    Raises:
        subprocess.CalledProcessError: If CLI fails
        json.JSONDecodeError: If output is not valid JSON
    """
    print("Fetching movie data from TMDB...", file=sys.stderr)
    # Use the installed entry point instead of -m
    output = run_command(["platelet-movie", "--format", "json", "--min-minutes", "90", "--max-minutes", "160", "--max-pages", "50"])
    return json.loads(output)


def get_commentary(movie_data: list[dict] | str) -> str:
    """Get Lady Whistledown commentary for the movies.
    
    Args:
        movie_data: Either a list of movie dicts or a markdown string
        
    Returns:
        Lady Whistledown commentary
        
    Raises:
        subprocess.CalledProcessError: If lady_whistledown.py fails
    """
    print("Generating Lady Whistledown commentary...", file=sys.stderr)
    
    # Format movies as markdown for the lady_whistledown script
    if isinstance(movie_data, str):
        # Already in markdown format
        markdown_movies = movie_data
    else:
        # Convert list of movies to markdown
        markdown_movies = "Movies:\n"
        for movie in movie_data:
            title = movie.get("title", "Unknown")
            runtime = movie.get("runtime_minutes", "?")
            year = movie.get("year", "")
            markdown_movies += f"- {title} ({runtime}m, {year})\n"
    
    # Run lady_whistledown script
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "lady_whistledown.py")],
        input=markdown_movies,
        capture_output=True,
        text=True,
        check=True,
    )
    
    return result.stdout.strip()


def generate_site_data() -> None:
    """Generate and save site/data.json with current movie data and commentary."""
    try:
        # Get movie data
        movies = get_movie_data()
        
        # Get commentary
        movie_markdown = "\n".join(
            f"- {m.get('title', 'Unknown')} ({m.get('runtime_minutes', '?')}m, {m.get('year', '')})"
            for m in (movies if isinstance(movies, list) else [])
        )
        commentary = get_commentary(movie_markdown)
        
        # Prepare combined data
        site_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "commentary": commentary,
            "movies": movies if isinstance(movies, list) else movies.get("movies", []),
        }
        
        # Save to site/data.json
        output_path = Path(__file__).parent.parent / "site" / "data.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(site_data, f, indent=2)
        
        print(f"✓ Generated {output_path} with {len(site_data['movies'])} movies", file=sys.stderr)
        
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to generate site data: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in response: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error during site generation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    generate_site_data()
