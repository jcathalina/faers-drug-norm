from typing import List


def list_chunker(lst: List, chunk_length: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), chunk_length):
        yield lst[i:i + chunk_length]

