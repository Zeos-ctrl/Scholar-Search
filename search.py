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
    global_collaborative_papers = 0
    global_collaborative_count = {}  # Dictionary to store institution counts globally

    for author in authors:
        print(f"Searching for {author}...")
        try:
            # Search for author
            search_query = scholarly.search_author(author)
            author_profile = next(search_query, None)

            if author_profile:
                # Fill in author details
                author_profile = scholarly.fill(author_profile, sections=['basics', 'indices', 'coauthors', 'publications'])
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

                # Track collaborations
                author_affiliations_count = {}  # Dictionary to track institution counts for this author
                for coauthor in author_profile.get('coauthors', []):
                    if 'affiliation' in coauthor and coauthor['affiliation']:
                        affiliation = coauthor['affiliation']
                        # Update the count for this author
                        author_affiliations_count[affiliation] = author_affiliations_count.get(affiliation, 0) + 1
                        # Update the global count for the affiliation
                        global_collaborative_count[affiliation] = global_collaborative_count.get(affiliation, 0) + 1
                        global_collaborative_papers += 1  # Increment global collaborative papers

                # Store author data
                citations = author_profile.get('citedby', 0)
                author_data[author] = {
                    "publications": recent_publications,
                    "citations": citations,
                    "citations_last_5_years": citations_last_5_years,
                    "top_paper": top_paper['bib']['title'] if top_paper else "N/A",
                    "journal_counts": author_journal_counts,
                    "affiliations": author_affiliations_count  # Store the count of affiliations for this author
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
                    "journal_counts": {},
                    "affiliations": {}
                }

        except Exception as e:
            print(f"Error fetching data for {author}: {e}")
            author_data[author] = {
                "publications": [],
                "citations": 0,
                "citations_last_5_years": 0,
                "top_paper": "N/A",
                "journal_counts": {},
                "affiliations": {}
            }

    return author_data, total_citations, total_recent_citations, global_journal_counts, global_collaborative_papers, global_collaborative_count

def save_to_file(author_data, total_citations, total_recent_citations, global_journal_counts, global_collaborative_papers, global_collaborative_count, output_file):
    # Sort authors by their total citations in descending order
    sorted_authors = sorted(author_data.items(), key=lambda x: x[1]['citations'], reverse=True)

    # Sort global journal counts by the number of publications in descending order
    sorted_global_journal_counts = sorted(global_journal_counts.items(), key=lambda x: x[1], reverse=True)

    # Sort global collaborations by the number of collaborations in descending order
    sorted_global_collaborative_count = sorted(global_collaborative_count.items(), key=lambda x: x[1], reverse=True)

    with open(output_file, 'w') as f:
        for author, data in sorted_authors:
            f.write(f"{author} (Total Citations: {data['citations']}, Citations Last 5 Years: {data['citations_last_5_years']}):\n")
            f.write(f"Top Paper: {data['top_paper']}\n")
            f.write(f"Journals Published In: {len(data['journal_counts'])}\n")
            f.write("Journals and their counts:\n")
            
            # Sort author-specific journals by their publication counts
            sorted_journals = sorted(data['journal_counts'].items(), key=lambda x: x[1], reverse=True)
            for journal, count in sorted_journals:
                f.write(f"  - {journal}: {count} publication(s)\n")
            
            f.write("Publications (Last 5 Years):\n")
            for pub in data['publications']:
                f.write(f"  - {pub['bib']['title']} ({pub['bib'].get('pub_year')})\n")
            
            # Sort and write the affiliations (collaborating institutions)
            sorted_affiliations = sorted(data['affiliations'], key=lambda x: x)
            f.write(f"Unique Affiliations: {len(data['affiliations'])}\n")
            for affiliation in sorted_affiliations:
                f.write(f"  - {affiliation}\n")
            f.write("\n")

        # Write total citations and overall journal counts
        f.write(f"Total Citations for all authors: {total_citations}\n")
        f.write(f"Total Citations in the Last 5 Years for all authors: {total_recent_citations}\n")
        f.write(f"Total Unique Journals: {len(global_journal_counts)}\n")
        f.write("Overall Journal Counts (Sorted by publication count):\n")
        for journal, count in sorted_global_journal_counts:
            f.write(f"  - {journal}: {count} publication(s)\n")

        f.write(f"Total Collaborative Papers: {global_collaborative_papers}\n")
        f.write(f"Overall Collaborating Institutions (Sorted by collaboration count):\n")
        for affiliation, count in sorted_global_collaborative_count:
            f.write(f"  - {affiliation}: {count} collaboration(s)\n")

if __name__ == "__main__":
    input_file = "authors.txt"
    output_file = "results.txt"
    
    authors = read_authors(input_file)
    author_publications, total_citations, total_recent_citations, global_journal_counts, global_collaborative_papers, global_collaborative_count = search_publications(authors)
    
    save_to_file(author_publications, total_citations, total_recent_citations, global_journal_counts, global_collaborative_papers, global_collaborative_count, output_file)
    
    print(f"Saved publication data to {output_file}")
    print(f"Total Citations for all authors: {total_citations}")
    print(f"Total Citations in the Last 5 Years for all authors: {total_recent_citations}")
    print(f"Total Unique Journals: {len(global_journal_counts)}")
    print(f"Total Collaborative Papers: {global_collaborative_papers}")
    print(f"Total Unique Collaborating Institutions: {len(global_collaborative_count)}")

