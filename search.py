from scholarly import scholarly
from datetime import datetime
import re

def clean_journal_name(journal_entry):
    # Match patterns like arXiv preprint, and keep only 'arXiv'
    arxiv_pattern = re.compile(r"arXiv preprint arXiv")
    if arxiv_pattern.match(journal_entry):
        return "arXiv"
    
    # Remove common patterns like volume, issue, page numbers, and years
    cleaned_entry = re.sub(r'(\d{4})', '', journal_entry)  # Remove years (four digits)
    cleaned_entry = re.sub(r'(\d+\s*\(\d+\))', '', cleaned_entry)  # Remove volume and issue (e.g., 19 (1))
    cleaned_entry = re.sub(r'(\d+,\s*\d+|\d+-\d+)', '', cleaned_entry)  # Remove page numbers or ranges
    cleaned_entry = re.sub(r'(\d+)', '', cleaned_entry)  # Remove any remaining numbers
    cleaned_entry = re.sub(r'[\s,-:]+$', '', cleaned_entry)
    cleaned_entry = cleaned_entry.strip()  # Remove any extra spaces
    
    return cleaned_entry

def read_authors(file_path):
    with open(file_path, 'r') as f:
        authors = [line.strip() for line in f.readlines() if line.strip()]  # Extract non-empty lines
    return authors

def filter_recent_publications(publications):
    current_year = datetime.now().year
    recent_publications = []
    journal_counts = {}  # Dictionary to count journals
    for pub in publications:
        pub_year = pub['bib'].get('pub_year')
        unsanitised_journal = pub['bib']['citation']
        journal = clean_journal_name(unsanitised_journal)

        if pub_year and (current_year - int(pub_year) <= 5):  # Only consider publications within the last 5 years
            recent_publications.append(pub)

            if journal:
                # Count journals for global statistics
                journal_counts[journal] = journal_counts.get(journal, 0) + 1

    return recent_publications, journal_counts

def get_top_paper(publications):
    if not publications:
        return None
    # Find the publication with the highest citations
    return max(publications, key=lambda pub: pub.get('num_citations', 0))

def search_publications(authors):
    author_data = {}
    total_citations = 0  # Initialize total citations count
    total_recent_citations = 0
    global_journal_counts = {}  # Dictionary to store overall journal counts

    for author in authors:
        print(f"Searching for {author}...")
        try:
            # Search for author
            search_query = scholarly.search_author(author)
            author_profile = next(search_query, None)

            if author_profile:
                # Fill in author details
                author_profile = scholarly.fill(author_profile)
                print(f"Found {author}: {author_profile.get('name')}")

                # Get all publications
                all_publications = author_profile['publications']
                recent_publications, author_journal_counts = filter_recent_publications(all_publications)

                # Get the top paper by citations
                top_paper = get_top_paper(all_publications)

                # Update global journal counts
                for journal, count in author_journal_counts.items():
                    global_journal_counts[journal] = global_journal_counts.get(journal, 0) + count

                # Citations in the last 5 years (if available)
                citations_last_5_years = author_profile.get('citedby5y', 0)

                # Store author data
                citations = author_profile.get('citedby', 0)
                author_data[author] = {
                    "publications": recent_publications,
                    "citations": citations,
                    "citations_last_5_years": citations_last_5_years,
                    "top_paper": top_paper['bib']['title'] if top_paper else "N/A",
                    "journal_counts": author_journal_counts
                }

                # Update total citation counts
                total_citations += citations
                total_recent_citations += citations_last_5_years
            else:
                print(f"No results found for {author}.")
                author_data[author] = {
                    "publications": [],
                    "citations": 0,
                    "citations_last_5_years": 0,
                    "top_paper": "N/A",
                    "journal_counts": {}
                }

        except Exception as e:
            print(f"Error fetching data for {author}: {e}")
            author_data[author] = {
                "publications": [],
                "citations": 0,
                "citations_last_5_years": 0,
                "top_paper": "N/A",
                "journal_counts": {}
            }

    return author_data, total_citations, total_recent_citations, global_journal_counts

def save_to_file(author_data, total_citations, total_recent_citations, global_journal_counts, output_file):
    with open(output_file, 'w') as f:
        for author, data in author_data.items():
            f.write(f"{author} (Total Citations: {data['citations']}, Citations Last 5 Years: {data['citations_last_5_years']}):\n")
            f.write(f"Top Paper: {data['top_paper']}\n")
            f.write(f"Journals Published In: {len(data['journal_counts'])}\n")
            f.write("Journals and their counts:\n")
            for journal, count in data['journal_counts'].items():
                f.write(f"  - {journal}: {count} publication(s)\n")
            f.write("Publications (Last 5 Years):\n")
            for pub in data['publications']:
                f.write(f"  - {pub['bib']['title']} ({pub['bib'].get('pub_year')})\n")
            f.write("\n")

        # Write total citations and overall journal counts
        f.write(f"Total Citations for all authors: {total_citations}\n")
        f.write(f"Total Citations in the Last 5 Years for all authors: {total_recent_citations}\n")
        f.write(f"Total Unique Journals: {len(global_journal_counts)}\n")
        f.write("Overall Journal Counts:\n")
        for journal, count in global_journal_counts.items():
            f.write(f"  - {journal}: {count} publication(s)\n")

if __name__ == "__main__":
    input_file = "authors.txt"
    output_file = "author_publications.txt"
    
    authors = read_authors(input_file)
    author_publications, total_citations, total_recent_citations, global_journal_counts = search_publications(authors)
    save_to_file(author_publications, total_citations, total_recent_citations, global_journal_counts, output_file)
    
    print(f"Saved publication data to {output_file}")
    print(f"Total Citations for all authors: {total_citations}")
    print(f"Total Citations in the Last 5 Years for all authors: {total_recent_citations}")
    print(f"Total Unique Journals: {len(global_journal_counts)}")
