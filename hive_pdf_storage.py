from pyhive import hive
import base64
import os
import FileDirectories
from pathlib import Path

def pdf_to_bytes(pdf_path: Path) -> bytes:
    with open(pdf_path, "rb") as f:
        return f.read()


def main():
    # Get output directory
    output_dir = FileDirectories.get_output_directory()
    pdf_files = sorted(Path(output_dir).glob('*.pdf'))
    
    if not pdf_files:
        print("No PDF files found.")
        return
    
    # Read Hive connection settings from environment variables
    hive_host = os.getenv('HIVE_HOST', 'localhost')
    hive_port = int(os.getenv('HIVE_PORT', '10000'))
    hive_user = os.getenv('HIVE_USER', 'default')
    hive_database = os.getenv('HIVE_DATABASE', 'default')
    hive_auth = os.getenv('HIVE_AUTH_MECHANISM', 'NONE')
    
    # Validate required environment variables
    if not hive_user or hive_user == 'default':
        print("Warning: HIVE_USER not set. Using 'default'.")
    
    # Connect to Hive once before the loop
    try:
        conn = hive.connect(
            host=hive_host,
            port=hive_port,
            username=hive_user,
            database=hive_database,
            auth=hive_auth,
        )
        cursor = conn.cursor()
        
        # Process each PDF file
        for pdf_file in pdf_files:
            try:
                pdf_bytes = pdf_to_bytes(pdf_file)
                encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                filename = pdf_file.name
                
                # Insert encoded PDF into Hive
                insert_query = "INSERT INTO pdf_storage (filename, pdf_binary) VALUES (%s, %s)"
                cursor.execute(insert_query, (filename, encoded_pdf))
                print(f"Inserted {filename} into Hive successfully.")
                
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")
                continue
        
        # Commit transaction and close connection
        conn.commit()
        
    except Exception as e:
        print(f"Error connecting to Hive: {e}")
    finally:
        # Ensure cursor and connection are closed
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass


if __name__ == "__main__":
    main()