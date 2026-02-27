from pathlib import Path
import pandas as pd
import FileDirectories
import pypdf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Named constant for corrupted PDF value
CORRUPTED = 'CORRUPTED'


def read_pdf_file_name(file_path):
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            if len(pdf_reader.pages) > 0:
                return Path(file_path).name
            else:
                return None  # Empty PDF
    except Exception as e:
        logging.error(f"Error reading {file_path}: {type(e).__name__}: {e}")
        return None


def get_pdf_file(brnum, pdf_mapping):
    """Get the filename for a given BRnum from the pdf_mapping."""
    if str(brnum) not in pdf_mapping:
        return None  # Not Found - no file
    elif pdf_mapping[str(brnum)] == CORRUPTED:
        return f"{brnum}.pdf"  # Show the corrupted filename
    else:
        return pdf_mapping[str(brnum)]  # Downloaded - return filename


def get_status(brnum, pdf_mapping):
    """Determine the download status for a given BRnum from the pdf_mapping."""
    if str(brnum) not in pdf_mapping:
        return 'Not Found'
    elif pdf_mapping[str(brnum)] == CORRUPTED:
        return 'Corrupted'
    else:
        return 'Downloaded'


def main():
    # Get paths
    filePath = FileDirectories.get_output_directory()
    xlsx_path = FileDirectories.get_source_path()
    
    logging.info(f"Looking for PDF files in: {filePath}")
    
    # Get all PDF files and create a mapping of BRnum to filename
    pdf_files = sorted(filePath.glob('*.pdf'))
    logging.info(f"Found {len(pdf_files)} PDF files")
    
    # Create a dictionary mapping BRnum to filename or status
    pdf_mapping = {}
    for file in pdf_files:
        file_name = read_pdf_file_name(file)
        brnum = file.stem
        # Store either the filename (valid) or CORRUPTED (invalid)
        pdf_mapping[brnum] = file_name if file_name else CORRUPTED
        logging.info(f"File: {file.name}, Valid: {file_name is not None}")

    try:
        # Read the same way as Downloader.py - first 10 rows with headers
        df = pd.read_excel(xlsx_path, 
                 header=0, 
                 index_col=None,
                 na_values=['missing'])
        
        # Select only the columns we need
        df = df[['BRnum', 'Pdf_URL', 'Report Html Address']]
        
        # Apply helper functions with pdf_mapping as parameter
        df['File Name'] = df['BRnum'].apply(lambda brnum: get_pdf_file(brnum, pdf_mapping))
        df['Pdf Download Status'] = df['BRnum'].apply(lambda brnum: get_status(brnum, pdf_mapping))        
        output_metadata_path = filePath / "metadata_with_filenames.xlsx"
        
        # Compute value counts once for efficiency
        counts = df['Pdf Download Status'].value_counts()
        downloaded_count = counts.get('Downloaded', 0)
        corrupted_count = counts.get('Corrupted', 0)
        not_found_count = counts.get('Not Found', 0)
        logging.info(
            f"Status summary: {downloaded_count} Downloaded, {corrupted_count} Corrupted, {not_found_count} Not Found"
        )

        df.to_excel(output_metadata_path, index=False)
        logging.info(f"Metadata with file names saved to: {output_metadata_path}")

    except FileNotFoundError as e:
        logging.error(f"Excel file not found: {e}")
    except pd.errors.EmptyDataError as e:
        logging.error(f"Excel file is empty or corrupted: {e}")
    except ValueError as e:
        logging.error(f"Validation error: {e}")
    except PermissionError as e:
        logging.error(f"Permission denied while reading or writing files: {e}")
    except Exception:
        logging.exception("An unexpected error occurred while processing metadata")


if __name__ == "__main__":
    main()

