#!/usr/bin/env python

import pathlib
import hashlib

def walk_source(source, dest, verbose=True):
    """
    Recursively look at all files in source and
    check the corresponding file exists in dest
    """
    source_base = pathlib.Path(source)
    assert source_base.is_dir(), "Source argument must be a directory"

    dest_base = pathlib.Path(dest)
    assert dest_base.is_dir(), "Dest argument must be a directory"

    for root, dirs, files in source_base.walk():
        if verbose:
            print(f"In {root}")
        for file in files:
            source_file = root/file
            dest_file = dest_base/source_file.relative_to(source_base)
            if verbose:
                print(f"Comparing {source_file} with {dest_file}")
            if dest_file.is_file():
                with open(source_file, "rb") as f:
                    source_digest = hashlib.file_digest(f, "sha256")
                with open(dest_file, "rb") as f:
                    dest_digest = hashlib.file_digest(f, "sha256")
                if dest_digest.hexdigest() == source_digest.hexdigest():
                    print(f"OK: {dest_file}")
                else:
                    print(f"DIFFERENT: {dest_file}")
                    if verbose:
                        print(f"{source_file}: {source_digest.hexdigest()}")
                        print(f"{dest_file}: {dest_digest.hexdigest()}")
            else:
                print(f"MISSING: {dest_file}")         

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("dest")
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    walk_source(args.source, args.dest, args.verbose)