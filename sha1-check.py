import hashlib
import os
import fnmatch
import pathlib
import shutil
import argparse

# Recursively read each directory
# Look for files that match steam pattern
# For each matching file:
#   Extract last X characters from filename, store as expected sha-1 value
#   Generate sha from file and compare to expected value
#   Print error if match is not found

# Ignore raw files as they are created by TTS
FILES_TO_IGNORE = ['.RAWT', '.RAWM', '.TMP']

TTS_RAW_DIRS = {'Images Raw': '.rawt', 'Models Raw': '.rawm'}

def check_sha1s(root_dir, backup_dir=None):
    file_count = 0
    for root, dirs, files in os.walk(root_dir):
        dir_name = pathlib.PurePath(root).name

        if dir_name in TTS_RAW_DIRS:
            continue

        if backup_dir is not None:
            if root.upper() == backup_dir.upper():
                continue

        print()
        print(f"{dir_name}", end='')
        steam_files = fnmatch.filter(files, 'httpcloud3steamusercontent*')
        for filename in steam_files:
            mismatch_found = False

            ext = os.path.splitext(filename)[1]
            if ext.upper() in FILES_TO_IGNORE:
                continue

            print('.', end='', flush=True)
            expected_hexdigest = os.path.splitext(filename)[0][-40:]
            filepath = os.path.join(root, filename)
            with open(filepath, "rb") as f:
                digest = hashlib.file_digest(f, "sha1")

                if expected_hexdigest.upper() != digest.hexdigest().upper():
                    print()
                    print(f"  -{filename}", end='', flush=True)
                    mismatch_found = True
                else:
                    mismatch_found = False

            # Need to do this outside of open() to prevent file from being in use
            if mismatch_found == True:
                if backup_dir is not None:
                    newpath = os.path.join(backup_dir, filename)
                    shutil.move(filepath, newpath)

                # Check if TTS already used corrupt file to create raw files
                for raw_dir in TTS_RAW_DIRS:
                    raw_filename = os.path.splitext(filename)[0] + TTS_RAW_DIRS[raw_dir]
                    raw_filepath = os.path.join(root_dir, raw_dir)
                    raw_filepath = os.path.join(raw_filepath, raw_filename)

                    if os.path.exists(raw_filepath):
                        print()
                        print(f"  -{raw_filename}", end='', flush=True)

                        if backup_dir is not None:
                            newpath = os.path.join(backup_dir, raw_filename)
                            shutil.move(raw_filepath, newpath)

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path. Do not include a trailing \\")

if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser(
        description='This script checks for corrupt TTS files downloaded from stream using the SHA1 hash'
        )
    
    parser.add_argument('mod_path', type=dir_path, help='Do not include a \ at the end of the path')
    parser.add_argument('-b', '--backup_path', type=dir_path, help='Do not include a \ at the end of the path')
    
    args = parser.parse_args()

    print("Mod dir:", args.mod_path)
    print("Backup dir:", args.backup_path)
    
    check_sha1s(args.mod_path, args.backup_path)