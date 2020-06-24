import os


def cleanup_temp_files(temporary_files):
    for file in temporary_files:
        print(f'removing temporary {file}')
        os.remove(file)
