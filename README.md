# Scholar-Search

This project is a Python-based web scraper that automates the retrieval of academic publication data from Google Scholar. Given a list of author names, the scraper collects the following information:

- Author's total citation count
- Journals in which the author has published
- Total number of publications per journal
- A list of all publications within the last 5 years, including their titles and publication years
- Global count of journals and the total number of publications for each journal across all authors

The results are saved to a text file in a readable format, displaying per-author statistics and global journal counts. This tool is particularly useful for research analysts, academics, or any institution that needs to collect and organize academic data in bulk.
## Key Features:

- Automatically searches for authors on Google Scholar
- Filters publications within the last 5 years
- Cleans and organizes journal names for readability
- Outputs results to a text file, including detailed author and global journal statistics

## Installation Instructions
Prerequisites:
- Python 3.7 or higher
- pip for Python package management

### Steps to Install:

Clone the Repository:

```bash
git clone https://github.com/Zeos-ctrl/Scholar-Search.git
cd Scholar-Search
```

Set Up a Virtual Environment (Recommended): Create and activate a virtual environment to keep dependencies isolated:

```bash

python -m venv venv
source venv/bin/activate   # For macOS/Linux
.\venv\Scripts\activate    # For Windows
```

The project uses a few Python libraries to interact with Google Scholar and manage the data. Run the following command to install them:

```bash

pip install scholarly
```

After setting up the environment and installing the dependencies, you can run the script:

```bash
python3 scraper.py
```

Make sure to provide a text file (authors.txt) containing the list of author names to search. Each author should be on a separate line.

## Usage Instructions

Prepare the Input File: Create a text file named authors.txt and list the author names you want to search for, one name per line.

Example:

```txt
John Doe
Jane Smith
Alice Johnson
```

Simply run the Python script, and it will search Google Scholar for each author, filter their publications, and save the results to a file called author_publications.txt in the current directory.

Once the script finishes running, check the author_publications.txt file for the results. You will see detailed statistics for each author as well as global journal publication counts.

The output will look something like this:

```plaintext

John Doe (Citations: 2000):
Journals Published In: 3
Journals and their counts:
  - Journal of Neural Engineering: 2 publication(s)
  - IEEE Transactions on Biomedical Engineering: 1 publication(s)
Publications (Last 5 Years):
  - Neural Signal Processing (2022)
  - Deep Learning in Biomedical Imaging (2021)

Total Citations for all authors: 5000
Total Unique Journals: 10
Overall Journal Counts:
  - Journal of Neural Engineering: 6 publication(s)
  - IEEE Transactions on Biomedical Engineering: 5 publication(s)
  - NeuroImage: 3 publication(s)
```

## Future Enhancements:

- Support for other citation data sources
- Extended filtering options for journals, publication types, and specific years 
- Output to other formats (CSV, JSON)

Feel free to contribute or raise any issues!
