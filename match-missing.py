import hashlib
import os
import fnmatch
import pathlib
import shutil
import argparse
import pickle
import re

# Recursively read each directory
# Load existing dictionary, for each file not found in dictionary:
# Files that match steam pattern, extract SHA-1 values, add to {SHA1, filename}
# For non-steam files generate SHA-1 values, add to dictionary
# For each line is missing url file:
#   Extract SHA-1
#   Check if matching SHA-1 file is found
#   Copy and rename to destination directory

# Ignore raw files as they are created by TTS
FILES_TO_IGNORE = ['.RAWT', '.RAWM', '.TMP', '.BIN']

TTS_RAW_DIRS = {'Images Raw': '.rawt', 'Models Raw': '.rawm'}

def find_missing(root_dir, missing_file_path, backup_dir=None):

    sha_cache_path = os.path.join(root_dir, 'sha1-cache.bin')
    if os.path.exists(sha_cache_path):
        with open(sha_cache_path, 'rb') as fin:
            sha1s = pickle.load(fin)
    else:
        sha1s = {}

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
            if filepath in sha1s.values():
                continue

            file_count += 1

            print(f"{dir_name}...{file_count}", end='\r', flush=True)

            if 'httpcloud3steamusercontent' in filename :
                hexdigest = os.path.splitext(filename)[0][-40:]

                if hexdigest.upper() in sha1s:
                    duplicate_sha1s += 1
                else:
                    sha1s[hexdigest.upper()] = filepath
            else:
                with open(filepath, "rb") as f:
                    digest = hashlib.file_digest(f, "sha1")
                hexdigest = digest.hexdigest()

                # Always prioritize storing calculated sha1 values
                # to be more efficient.
                if hexdigest.upper() in sha1s:
                    duplicate_sha1s += 1
                sha1s[hexdigest.upper()] = filepath

    print(f"Found {duplicate_sha1s} duplicate sha1 files during scan.")

    with open(sha_cache_path, 'wb') as outfile:
        pickle.dump(sha1s, outfile)
            
    with open(missing_file_path, 'r') as f:
        for filename in f:
            filename = filename.strip()
            # http://cloud-3.steamusercontent.com/ugc/1014943920257914113/D6644503664E262C9C0B610A39C9AB2E98AC599C/
            if filename[-1] == '/':
                filename = filename[:-1]
            wanted_hexdigest = filename[-40:].upper()

            if wanted_hexdigest in sha1s:
                prev_filepath = sha1s[wanted_hexdigest]
                print(f"Found file matching desired SHA-1: {prev_filepath}")

                # httpcloud3steamusercontentcomugc1014943920257914113D6644503664E262C9C0B610A39C9AB2E98AC599C.png
                new_filename = re.sub('[./:-]', '', filename)
                new_ext = os.path.splitext(prev_filepath)[1]
            
                if backup_dir is not None:
                    newpath = os.path.join(backup_dir, new_filename+new_ext)
                    shutil.copy(prev_filepath, newpath)


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
    
    find_missing(args.mod_path, args.missing_url_file, args.backup_path)