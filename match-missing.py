import hashlib
import os
import pathlib
import shutil
import argparse
import re
import sqlite3
from contextlib import closing

# Recursively read each directory
# Load existing dictionary, for each file not found in dictionary:
# Files that match steam pattern, extract SHA-1 values, add to {SHA1, filename}
# For non-steam files generate SHA-1 values, add to dictionary
# For each line is missing url file:
#   Extract SHA-1
#   Check if matching SHA-1 file is found
#   Copy and rename to destination directory

# Ignore raw files as they are created by TTS
FILES_TO_IGNORE = ['.RAWT', '.RAWM', '.TMP', '.DB']

TTS_RAW_DIRS = {'Images Raw': '.rawt', 'Models Raw': '.rawm'}

def find_missing(root_dir, missing_file_path, cursor, backup_dir=None):

    duplicate_sha1s = 0

    for root, dirs, files in os.walk(root_dir):
        dir_name = pathlib.PurePath(root).name

        if dir_name in TTS_RAW_DIRS:
            continue

        if backup_dir is not None:
            if root.upper() == backup_dir.upper():
                continue

        print()
        print(f"{dir_name}", end='\r', flush=True)

        file_count = 0

        for filename in files:
            ext = os.path.splitext(filename)[1]
            if ext.upper() in FILES_TO_IGNORE:
                continue

            filepath = os.path.join(root, filename)

            cursor.execute("SELECT * FROM tts_files WHERE filename=?", (filename,))
            result = cursor.fetchone()
            if result:
                continue

            file_count += 1

            print(f"{dir_name}...{file_count}", end='\r', flush=True)

            if 'httpcloud3steamusercontent' in filename :
                hexdigest = os.path.splitext(filename)[0][-40:]
            else:
                with open(filepath, "rb") as f:
                    digest = hashlib.file_digest(f, "sha1")
                hexdigest = digest.hexdigest()
            
            hexdigest = hexdigest.upper()

            cursor.execute("SELECT * FROM tts_files WHERE sha1=?", (hexdigest,))
            result = cursor.fetchone()
            if result:
                duplicate_sha1s += 1
            
            cursor.execute("INSERT INTO tts_files VALUES (?, ?, ?)", (filename, hexdigest, root))

    print(f"Found {duplicate_sha1s} duplicate sha1 files during scan.")

    found_missing = 0
    with open(missing_file_path, 'r') as f:
        for filename in f:
            filename = filename.strip()
            # http://cloud-3.steamusercontent.com/ugc/1014943920257914113/D6644503664E262C9C0B610A39C9AB2E98AC599C/
            if filename[-1] == '/':
                filename = filename[:-1]
            wanted_hexdigest = filename[-40:].upper()

            cursor.execute("SELECT * FROM tts_files WHERE sha1=?", (wanted_hexdigest,))
            result = cursor.fetchone()
            if result:
                found_missing += 1
                prev_filepath = os.path.join(result[2], result[0])
                print(f"Found file matching desired SHA-1: {prev_filepath}")

                # httpcloud3steamusercontentcomugc1014943920257914113D6644503664E262C9C0B610A39C9AB2E98AC599C.png
                new_filename = re.sub('[./:-]', '', filename)
                new_ext = os.path.splitext(prev_filepath)[1]
            
                if backup_dir is not None:
                    newpath = os.path.join(backup_dir, new_filename+new_ext)
                    shutil.copy(prev_filepath, newpath)

    print(f"Found {found_missing} missing files.")

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path. Do not include a trailing \\")

def file_path(path):
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path. Do not include a trailing \\")

if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser(
        description='This script checks for corrupt TTS files downloaded from stream using the SHA1 hash'
        )
    
    parser.add_argument('mod_path', type=dir_path, help='Do not include a \ at the end of the path')
    parser.add_argument('missing_url_file', type=file_path)
    parser.add_argument('-b', '--backup_path', type=dir_path, help='Do not include a \ at the end of the path')
    
    args = parser.parse_args()

    print("Mod dir:", args.mod_path)
    print("Missing URL file:", args.missing_url_file)
    print("Backup dir:", args.backup_path)

    DB_NAME = "tts-sha1.db"

    if not os.path.exists(DB_NAME):
        init_table = True
    else:
        init_table = False

    with closing(sqlite3.connect(DB_NAME)) as conn:
        with closing(conn.cursor()) as cursor:
            if init_table:
                cursor.execute("""CREATE TABLE tts_files
                (filename TEXT, sha1 TEXT, path TEXT)
                """)
            
            find_missing(args.mod_path, args.missing_url_file, cursor, args.backup_path)