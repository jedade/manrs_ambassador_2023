import requests
import os
import bz2
from datetime import datetime
from tqdm import tqdm

# List of file URLs to download
urls = [
    # ii.as-org file
    {
        'url': 'https://raw.githubusercontent.com/InetIntel/Dataset-AS-to-Organization-Mapping/master/data/2023-01',
        'name': 'ii.as-org.v01.2023-01.json'
    },
    # categorized file
    {
        'url': 'https://asdb.stanford.edu/data',
        'name': '2023-05_categorized_ases.csv'
    },
    # as-rel file
    {
        'url': 'https://publicdata.caida.org/datasets/as-relationships/serial-1',
        'name': '20230801.as-rel.txt.bz2'
    },
    # nro file
    {
        'url': 'https://ftp.ripe.net/pub/stats/ripencc/nro-stats/latest',
        'name': 'nro-delegated-stats'
    },
]

# Function to download and save a file
def download_file(url, filename):
    # Create a directory with the current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d")
    path = f'manrs_{current_time}'
    
    if not os.path.exists(path):
        os.makedirs(path)
        
    response = requests.get(f'{url}/{filename}', stream=True)
    if response.status_code == 200:
        file_path = os.path.join(path, filename)
        with open(file_path, 'wb') as f:
            if filename.endswith('.bz2'):
                # Save the compressed content to a file with tqdm
                total_size = int(response.headers.get('content-length', 0))
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=f'Downloading {filename}') as pbar:
                    for data in response.iter_content(chunk_size=1024):
                        pbar.update(len(data))
                        f.write(data)
                # Decompress the downloaded file with tqdm
                decompressed_path = file_path.replace('.bz2', '')
                with tqdm(total=os.path.getsize(file_path), unit='B', unit_scale=True, desc=f'Decompressing {filename}') as pbar:
                    with open(decompressed_path, 'wb') as decompressed_file, bz2.BZ2File(file_path, 'rb') as compressed_file:
                        for data in iter(lambda: compressed_file.read(100 * 1024), b''):
                            pbar.update(len(data))
                            decompressed_file.write(data)
                # Clean up the compressed file
                os.remove(file_path)
            else:
                # Use tqdm to show progress bar with filename
                total_size = int(response.headers.get('content-length', 0))
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                    for data in response.iter_content(chunk_size=1024):
                        pbar.update(len(data))
                        f.write(data)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {filename}")

if __name__ == "__main__":
    for url in urls:
        # Check if it's a dictionary (with 'url' and 'name') or a string URL
        if isinstance(url, dict):
            download_file(url['url'], url['name'])
        else:
            filename = url.split('/')[-1]
            download_file(url, filename)
