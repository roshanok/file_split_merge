import os, sys, re
import logging
import argparse
import time


class SplitAndCombineFiles:
    """ This is a simple class to split and merge the files

    1. Split the binary files to the smaller chunks
    2. merge the binary files into the single file
    usage :
    usage: file_split_merge [-h] [-i INPUT] [-s] [-n CHUNK] [-m]

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            Provide the File that needs to be Split
      -s, --split           To Split the File
      -n CHUNK, --chunk CHUNK
                            No. of Chunks to be created
      -m, --merge           Merge the Files

    examples :
    file_split_merge -s -i first_project.zip -n 5
    file_split_merge -s -i first_project.zip -n 5kb
    file_split_merge -s -i first_project.zip -n 2gb
    file_split_merge -s -i "c:\temp\first_project.zip" -n 5
    file_split_merge -m -i first_project.zip
    file_split_merge -m -i "c:\temp\\first_project.zip"
    """
    def __init__(self):
        self.__input_file_name = None
        self.__chunk = None
        self.__postfix = '.ros'
        self.f_size = 0
        self.check_list = ""
        self.data_read_chunk = 5

    def get_file_chunks_from_count(self):
        """ This method is to get the file chunk sizes"""
        # get the file zize
        self.f_size = os.path.getsize(self.__input_file_name)
        log("Total file Size : {}".format(str(self.f_size)))

        # get the file chunks
        f_chunk = int(float(self.f_size) / float(self.__chunk))
        log("Splitting into {} files of {} size".format(str(self.__chunk),
                                                        str(f_chunk)))
        return int(f_chunk), int(self.__chunk)

    def get_file_count_from_size(self):
        """ This method is to get the file chunk sizes"""

        size = {"b": 1, "kb": 1024, "mb": 1024 ** 2, "gb": 1024 ** 3}

        # get the file zize
        self.f_size = os.path.getsize(self.__input_file_name)
        log("Total file Size : {}".format(str(self.f_size)))

        # get the file chunks
        f_chunk = re.sub("\D", "", self.__chunk)
        size_type = self.__chunk.replace(f_chunk, "")
        f_chunk = int(f_chunk) * size[size_type]
        no_of_files = self.f_size / f_chunk
        if no_of_files > 1:
            no_of_files = int(no_of_files) + 1 if \
                no_of_files%int(no_of_files) > 0 \
                else int(no_of_files)
        else:
            no_of_files = 1

        log("Splitting into {} files of {} size".format(str(no_of_files),
                                                        str(self.__chunk)))

        return int(f_chunk), int(no_of_files)

    @staticmethod
    def read_file_in_chunks(file_obj, read_until=-1, chunk_size=5):
        """
        Lazy function to read a file piece by piece.
        Default chunk size: 5mb.
        :param file_obj : The file open object which has to be read
        :param read_until : How much of total chunk has to be read from
                            the file.
                            Default = -1 i.e read full file
        :param chunk_size : How much of chunk has to be read in one iter
                            Default chunk size: 5mb.
        :return Data Generator
        """

        tot_read = 0
        total_iter = 0
        total_count = 0
        last_chunk = False
        chunk_size = chunk_size * 1024 * 8  # convert to mb
        print(chunk_size)
        # If chunk_size is greater than the read_until, then
        # default the chunk_size to read_until
        if not read_until == -1 and \
                (read_until < chunk_size):
            chunk_size = read_until

        # if not reading full file , count total iteration required to
        # accumulate the read_until size.
        if not read_until == -1:
            total_iter = int(read_until/chunk_size)

        while True:
            # If not reading full file, then calculate the remaining chunks
            # in the last iteration
            if (total_count == total_iter - 1) and not read_until == -1:
                chunk_size = read_until - tot_read
                last_chunk = True

            data = file_obj.read(chunk_size)
            tot_read += len(data)
            total_count += 1

            # if data is present , then yiled , else break
            if data:
                yield data
            else:
                break

            # If this is a last chunk, then break
            if last_chunk:
                # print(total_count, total_iter, chunkSize)
                break

    def __split(self, input_file_name, chunk_size):
        """ Split the files
        :param input_file_name : The filename which has to be split
        :param chunk_size : Actual number of files to be split
        :return None
        """
        self.__input_file_name = input_file_name
        self.__chunk = chunk_size

        log("Splitting the File Now")

        if self.__chunk.isdigit():
            f_chunk, chunk_size = self.get_file_chunks_from_count()
        else:
            f_chunk, chunk_size = self.get_file_count_from_size()

        # read the content of the main file
        read_main_file = open(self.__input_file_name, "rb")
        tot_bytes_in_file = 0

        # Iterate through chunk size
        for i in range(int(chunk_size)):
            log(" - Splitting {}/{} files".format(str(i+1),
                                               str(int(chunk_size))))

            _chunk_file_name = "{}-{}{}".format(str(self.__input_file_name),
                                                str(i+1),
                                                str(self.__postfix))

            # Last chunk , include the remaining data
            if i == chunk_size - 1:
                f_chunk = self.f_size - tot_bytes_in_file

            # Read the chunks from the file
            # data = read_main_file.read(f_chunk)
            data = self.read_file_in_chunks(read_main_file, read_until=f_chunk,
                                            chunk_size = self.data_read_chunk)

            # collect the first chunk and last chunk of every file
            # This content is used for verification while merging
            first_check = None
            last_check = None
            with open(_chunk_file_name, "wb") as _:
                for chunks in data:
                    if not first_check:
                        first_check = chunks[5]
                    last_check = chunks[-5]
                    _.write(chunks)

            tot_bytes_in_file += f_chunk

            # crc content
            self.check_list += str(first_check) + "-" + str(last_check)

        _crc_file_name = "{}-{}{}".format(str(self.__input_file_name),
                                          "CRC", str(self.__postfix))

        # log("Creating the check file : {}".format(str(_crc_file_name)))
        with open(_crc_file_name, "w") as crc_file:
            crc_file.write(self.check_list)

        log("File split successfully")

    def __merge(self, input_file_name):
        """ Merge the Files
        :param input_file_name : filename in .zip format ex : filename.zip
        :return none"""
        log("Merging the file to {}".format(str(input_file_name)))

        _root_dir, _file_name = os.path.split(
            os.path.realpath(input_file_name))

        _file_path = os.path.join(_root_dir, _file_name)

        if os.path.exists(_file_path):
            log("File Already Exist. Please remove the {} and "
                "then re-run.".format(str(_file_path)))

            # Prompt if file need to be deleted automatically
            prompt = input("\nDo you want to remove the file [Y/N] : ")
            if prompt.strip().lower() == "y":
                os.remove(_file_path)
            else:
                return

        # get all the split files available
        file_list = self.get_split_files(_root_dir, _file_name)
        if not file_list:
            log("No Split files found")
            return

        # get the crc file
        _crc_file_name = "{}-{}{}".format(str(_file_name),
                                          "CRC", str(self.__postfix))
        _crc_file_path = os.path.join(_root_dir,_crc_file_name)
        if not os.path.exists(_crc_file_path):
            log("{} file is missing".format(str(_crc_file_path)))
            return

        _crc_data = open(_crc_file_path, "r").read()

        # Merge the files
        # Sort the file names
        log("Found {} file(s) for merging".format(len(file_list)))
        for files in sorted(file_list):
            f_name = file_list[files]
            log(" - Merging {} file".format(f_name))
            # collect the first chunk and last chunk of every file
            # This content is used for verification while merging
            first_check = None
            last_check = None
            with open(input_file_name, 'ab') as new_file:
                read_main_file = open(os.path.join(_root_dir,
                                                   f_name), 'rb')
                data = self.read_file_in_chunks(read_main_file,
                                                read_until=-1,
                                                chunk_size=
                                                self.data_read_chunk)
                for chunks in data:
                    if not first_check:
                        first_check = chunks[5]
                    last_check = chunks[-5]
                    new_file.write(chunks)

                # create the content for the file copy check
                self.check_list += str(first_check) + "-" + str(last_check)

        # check the crc data
        log("Checking if the files are merged properly")
        if _crc_data == self.check_list:
            log("File check : Passed")
        else:
            log("File check : Failed.")
            return

        log("File Merged successfully")

    def get_split_files(self, root_dir, file_name):
        """ Find out all the zip files in the folder
        :param root_dir : Directory path where files are present
        :param file_name : filename in .zip format ex : filename.zip
        :return list of the files
        """
        # Find all the files matching the format
        file_list = {}

        file_format = re.compile(file_name + '-' + '[0-9]+'+self.__postfix)
        for f in os.listdir(root_dir):
            if file_format.match(f):
                _ = f.split('-')[-1]
                _ = int(re.sub('\D', '', _))
                file_list[_] = f

        return file_list

    def split(self, input_file_name, chunk_size):
        self.__split(input_file_name, chunk_size)

    def merge(self, input_file_name):
        self.__merge(input_file_name)


def error_args(error_msg):
    """ this is just a error message for args"""
    log("\n")
    log("Error :  Arguments provided is invalid")
    log(error_msg)
    log("use -h for more details")
    exit(usage())


def log(value):
    """ This is just a print method"""
    print(value)


def usage():
    return r"""\n
    --------------------------------------------------------------
    Usage: file_split_merge [-h] [-i INPUT] [-s] [-n CHUNK] [-m]\n
    optional arguments:
    -h, --help            show this help message and exit
    -i INPUT, --input INPUT
                        Provide the File that needs to be Split
    -s, --split           To Split the File
    -n CHUNK, --chunk CHUNK
                        [n]: No. of files to be created
                        [n]kb : Split the file in nKB size
                        [n]b : Split the file in nb size
                        [n]mb : Split the file in nmb size
                        [n]gb : Split the file in ngb size

    -m, --merge           Merge the Files


    examples :
    file_split_merge -s -i first_project.zip -n 5
    file_split_merge -s -i first_project.zip -n 5kb
    file_split_merge -s -i first_project.zip -n 2gb
    file_split_merge -s -i "c:\temp\first_project.zip" -n 5
    file_split_merge -m -i first_project.zip
    file_split_merge -m -i "c:\temp\\first_project.zip"
    ----------------------------------------------------------------
    """


def main():
    start_time = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help="Provide the File that needs to be Split")
    parser.add_argument('-s', '--split', action="store_true",
                        help="To Split the File")
    parser.add_argument('-n', '--chunk',
                        help="No. of Chunks to be created")
    parser.add_argument('-m', '--merge', action="store_true",
                        help="Merge the Files")
    parser.add_argument('-r', '--read', default=5,type=int,
                        help="The speed at which data has to be read. "
                             "Higher the value , faster the process, "
                             "but possible memory leak")

    args = parser.parse_args()

    # Perform Split Operation

    if not (args.split or args.merge):
        error_args("-s or -m has to be Specified")

    if args.split:
        log("\n------------- STARTING FILE SPLIT -------------\n")
        if not(args.input and args.chunk):
            error_args("Split command requires -i and -n")
        else:
            sm = SplitAndCombineFiles()
            sm.data_read_chunk = args.read
            sm.split(args.input, args.chunk)


    # Perform Merge Operation
    if args.merge:
        log("\n------------- STARTING FILE MERGE -------------\n")
        if not args.input:
            error_args("Merge command requires -i")
        else:
            sm = SplitAndCombineFiles()
            sm.data_read_chunk = args.read
            sm.merge(args.input)

    log("Complete in {} seconds".format(str(int(time.time() - start_time))))


if __name__ == "__main__":
    main()