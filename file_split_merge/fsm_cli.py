from file_split_merge import SplitAndCombineFiles
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help="Provide the File that needs to be Split")
    parser.add_argument('-s', '--split', action="store_true",
                        help="To Split the File")
    parser.add_argument('-n', '--chunk',
                        help="No. of Chunks to be created")
    parser.add_argument('-m', '--merge', action="store_true",
                        help="Merge the Files")

    args = parser.parse_args()

    # Perform Split Operation
    if not (args.split or args.merge):
        error_args("-s or -m has to be Specified")

    if args.split:
        if not(args.input and args.chunk):
            error_args("Split command requires -i and -n")
        else:
            sm = SplitAndCombineFiles()
            sm.split(args.input, args.chunk)

    # Perform Merge Operation
    if args.merge:
        if not args.input:
            error_args("Merge command requires -i")
        else:
            sm = SplitAndCombineFiles()
            sm.merge(args.input)