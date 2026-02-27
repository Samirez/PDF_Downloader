import pandas as pd
import requests
import os
from pathlib import Path
import FileDirectories

class FileDownloadError(Exception):
    def __init__(self, downloaded_size, total_size):
        self.downloaded_size = downloaded_size
        self.total_size = total_size
        super().__init__(self.__str__())

    def __str__(self):
        return (f"File was not completely downloaded "
                f"{self.downloaded_size/1024/1024:.1f} MB / {self.total_size/1024/1024:.1f} MB")


class AbortDownload(Exception):
    def __init__(self):
        super().__init__(self.__str__())

    def __str__(self):
        return (f"Download was aborted by user")
    
class Downloader:
    def __init__(self, url, alt_url, output_path):
        self.url = url
        self.alt_url = alt_url
        self.output_path = output_path

    def download(self):
        urls_to_try = [self.url, self.alt_url]
        last_error = None
        
        for attempt_url in urls_to_try:
            if not attempt_url or pd.isna(attempt_url):
                continue
                
            try:
                response = requests.get(attempt_url, stream=True, timeout=30)
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                with open(self.output_path, 'wb') as file:
                    for data in response.iter_content(1024):
                        downloaded_size += len(data)
                        file.write(data)
                if downloaded_size < total_size:
                    raise FileDownloadError(downloaded_size, total_size)
                return
            except Exception as e:
                # Clean up partial file on download error
                try:
                    os.remove(self.output_path)
                except OSError:
                    pass  # File may not exist or may be locked; ignore
                
                last_error = e
                continue
        
        # Both URLs failed
        if last_error:
            raise last_error
        else:
            raise Exception("No valid URLs available for download")
        
    @staticmethod
    def read_xlsx(file_path):
        # Read Excel file with specified options
        df = pd.read_excel(file_path, 
                          header=0,
                          index_col=None,
                          na_values=['missing'])
        required_columns = {'BRnum', 'Pdf_URL', 'Report Html Address'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            missing_list = ", ".join(sorted(missing_columns))
            raise ValueError(f"Missing required columns: {missing_list}")
        # Select only the columns we need
        df = df[['BRnum', 'Pdf_URL', 'Report Html Address']]
        return df
        

def get_source_path():
    return FileDirectories.get_source_path()

def get_output_directory():
    return FileDirectories.get_output_directory()


output_dir = get_output_directory()

# Read Excel file
try:
    df = Downloader.read_xlsx(get_source_path())
    
except Exception as e:
    print(f"An unexpected error occurred while reading Excel: {e}")
    exit(1)

# Process downloads
for index, row in df.iterrows():
    url = row['Pdf_URL']
    if (pd.isna(url) or not url) and (pd.isna(row['Report Html Address']) or not row['Report Html Address']):
        print(f"Skipping {row['BRnum']}: No URL provided")
        continue
    output_path = output_dir / f"{row['BRnum']}.pdf"
    if output_path.exists():
        print(f"Skipping {row['BRnum']}: Already downloaded")
        continue
    alt_url = row['Report Html Address']
    try:
        downloader = Downloader(url, alt_url, str(output_path))
        downloader.download()
    except AbortDownload:
        print("Download aborted by user")
        break
    except Exception as e:
        print(f"Error downloading {row['BRnum']}: {e}")
        continue



