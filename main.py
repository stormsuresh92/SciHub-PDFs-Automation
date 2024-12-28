from pathlib import Path
from scihub import SciHub

path = Path("./Downloaded PDFs")
path.mkdir(exist_ok=True)

with open ("dois.txt", "r") as file:
    dois = [line.strip() for line in file if line.strip()]

for doi in dois:
    print(f"Testing DOI: {doi}")
    downloder = SciHub(doi, path)
    try:
        downloader.fetch()
    except Exception as e:
        print(f"Error with DOI {doi}: {e}")
