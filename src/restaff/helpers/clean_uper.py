import os


def cleanup_temp_files(temporary_files):
    for file in temporary_files:
        logger.debug(f'removing temporary {file}')
        os.remove(file)
