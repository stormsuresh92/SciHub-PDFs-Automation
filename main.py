from pathlib import Path
from scihub import SciHub

path = Path("download")


with open ("dois.txt", "r") as file:
    dois = [line.strip() for line in file if line.strip()]


for doi in dois:
    print(f"Testing DOI: {doi}")
    scihub_instance = SciHub(doi, path)
    try:
        scihub_instance.fetch()
    except Exception as e:
        print(f"Error with DOI {doi}: {e}")