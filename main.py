from setup import setup_faers, category_table_to_csv, get_ascii_files_of_category
import dask.distributed as dd

if __name__ == '__main__':

    do_setup = False
    if do_setup:
        setup_faers()

    category_files = get_ascii_files_of_category()
    category_table_to_csv(category_files=category_files)



