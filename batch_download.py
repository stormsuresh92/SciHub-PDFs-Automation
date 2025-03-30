from pathlib import Path
from scihub_downloader import SciHub  # Import the SciHub class
from tqdm import tqdm

# Define paths
output_path = Path("downloads")
csv_file = Path("doi_pdfs.csv")
log_file = Path("scihub.log")
dois_file = Path("dois.txt")

# Ensure the output directory exists
output_path.mkdir(exist_ok=True)

# Read DOIs from the file
if dois_file.exists():
    with open(dois_file, "r") as file:
        dois = [line.strip() for line in file if line.strip()]

    # Process each DOI
    for doi in tqdm(dois):
        #print(f"Processing DOI: {doi}")
        downloader = SciHub(doi, output_path, csv_file, log_file, rate_limit=10)
        try:
            downloader.fetch()
        except Exception as e:
            print(f"Error with DOI {doi}: {e}")
else:
    print("Error: 'dois.txt' not found. Please create the file and add DOIs.")
