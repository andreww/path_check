#!/usr/bin/env python

import pathlib
import hashlib

def check_file_pair(file, root, dest_base, source_base, verbose):

    source_file = root/file
    dest_file = dest_base/source_file.relative_to(source_base)
    if dest_file.is_file():
        with open(source_file, "rb") as f:
            source_digest = hashlib.file_digest(f, "sha256")
        with open(dest_file, "rb") as f:
            dest_digest = hashlib.file_digest(f, "sha256")
        if dest_digest.hexdigest() == source_digest.hexdigest():
            if verbose:
                print(f"OK: {dest_file}")
        else:
            print(f"DIFFERENT: {dest_file}")
            print(f"---> {source_file}: {source_digest.hexdigest()}")
            print(f"---> {dest_file}: {dest_digest.hexdigest()}")
    else:
        print(f"MISSING: {dest_file}")


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
            print(f"IN: {root}")
        for file in files:
            try:
                check_file_pair(file, root, dest_base, source_base, verbose)
            except Exception as ex:
                print(f"ERROR: {root/file}")
                print(f"---> exception type: {type(ex)}")
                print(ex)


def recheck(output_file, source, dest, verbose=True):
    """
    Check files in source match files in dest but only for those marked ERROR in output_file
    
    This is for rechecking after long running jobs where the remote file server sometimes
    falls over
    """
    source_base = pathlib.Path(source)
    assert source_base.is_dir(), "Source argument must be a directory"

    dest_base = pathlib.Path(dest)
    assert dest_base.is_dir(), "Dest argument must be a directory"

    with open(output_file, "r") as f:
        for line in f:
            if line[0:3] == 'IN:':
                current_root = line.split(':')[1]
            elif line[0:6] == 'ERROR:':
                check_file = line.split(':')[1]
                try:
                    check_file_pair(check_file, current_root, dest_base, source_base, verbose)
                except Exception as ex:
                    print(f"ERROR: {root/file}")
                    print(f"---> exception type: {type(ex)}")
                    print(ex)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("dest")
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--recheck_errors', action='store',
                        help='Provide output file from previous run, only files marked ERROR are checked.')
    args = parser.parse_args()
    if args.recheck_errors is None:
        walk_source(args.source, args.dest, args.verbose)
    else:
        recheck(args.recheck_errors, args.source, args.dest, args.verbose)
