from __future__ import annotations

import os
import sys

from dataPool import DataPool


def upload(directory: str, collection_name: str):
    """
    Uploads all the files in the directory to the database
    :param directory: a potential directory (maybe invalid)
    :param collection_name: the collection name
    :return: it will check for valid directory. If invalid it will throw an error, else it will upload the files
    """
    directory = directory.replace("\\", "/")
    if os.path.isdir(directory):
        datapool = DataPool()
        for f in os.listdir(directory):
            file_path = f"{directory}/{f}"
            if os.path.isfile(file_path):
                print(file_path)
                datapool.add_video_to_collection(collection_name=collection_name, file_dir=file_path)
    else:
        print("Invalid directory")


def main():
    try:
        flag = sys.argv[1]
        if flag == "-h":
            if len(sys.argv) > 2:
                print("Too many parameters. Should only just be -h")
                return
            print("To upload files to the database, please put in a valid file directory")
            print("Here is an example:")
            print("uploader.py -u 'C:\\Users\\testUser\\directory'".rjust(50))
        elif flag == "-u":
            directory = None
            collection_name = None
            if len(sys.argv) == 3:
                directory = sys.argv[2]
            if len(sys.argv) == 4:
                directory = sys.argv[2]
                collection_name = sys.argv[3]
            if len(sys.argv) > 4:
                print("ERROR: Too many arguments")
                return
            if directory is None:
                print("ERROR: Missing Directory")
                return

            if collection_name is None:
                collection_name = "brainrots"
            upload(directory, collection_name)
        else:
            print("Valid flags are -h and -u")
    except IndexError:
        print(f"For help, type: uploader.py -h")


if __name__ == "__main__":
    main()
