import os
import json
import argparse


def get_all_files(
    dirName, match_and=None, match_or=None, exclude_and=None, exclude_or=None
):
    """Returns a list of files found within a folder.

    Different options can be used to restrict the search to some specific
    patterns.

    Arguments
    ---------
    dirName : str
        The directory to search.
    match_and : list
        A list that contains patterns to match. The file is
        returned if it matches all the entries in `match_and`.
    match_or : list
        A list that contains patterns to match. The file is
        returned if it matches one or more of the entries in `match_or`.
    exclude_and : list
        A list that contains patterns to match. The file is
        returned if it matches none of the entries in `exclude_and`.
    exclude_or : list
        A list that contains pattern to match. The file is
        returned if it fails to match one of the entries in `exclude_or`.

    Example
    -------
    >>> get_all_files('tests/samples/RIRs', match_and=['3.wav'])
    ['tests/samples/RIRs/rir3.wav']
    """

    # Match/exclude variable initialization
    match_and_entry = True
    match_or_entry = True
    exclude_or_entry = False
    exclude_and_entry = False

    # Create a list of file and sub directories
    listOfFile = os.listdir(dirName)
    allFiles = list()

    # Iterate over all the entries
    for entry in listOfFile:

        # Create full path
        fullPath = os.path.join(dirName, entry)

        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + get_all_files(
                fullPath,
                match_and=match_and,
                match_or=match_or,
                exclude_and=exclude_and,
                exclude_or=exclude_or,
            )
        else:

            # Check match_and case
            if match_and is not None:
                match_and_entry = False
                match_found = 0

                for ele in match_and:
                    if ele in fullPath:
                        match_found = match_found + 1
                if match_found == len(match_and):
                    match_and_entry = True

            # Check match_or case
            if match_or is not None:
                match_or_entry = False
                for ele in match_or:
                    if ele in fullPath:
                        match_or_entry = True
                        break

            # Check exclude_and case
            if exclude_and is not None:
                match_found = 0

                for ele in exclude_and:
                    if ele in fullPath:
                        match_found = match_found + 1
                if match_found == len(exclude_and):
                    exclude_and_entry = True

            # Check exclude_or case
            if exclude_or is not None:
                exclude_or_entry = False
                for ele in exclude_or:
                    if ele in fullPath:
                        exclude_or_entry = True
                        break

            # If needed, append the current file to the output list
            if (
                match_and_entry
                and match_or_entry
                and not (exclude_and_entry)
                and not (exclude_or_entry)
            ):
                allFiles.append(fullPath)

    return allFiles


def text_to_list(text_lst):
    """
    This converts lines of text into a dictionary-

    Arguments
    ---------
    text_lst : str
        Path to the file containing the librispeech text transcription.

    Returns
    -------
    dict
        The dictionary containing the text transcriptions for each sentence.

    """
    # Initialization of the text dictionary
    all_text = []
    # Reading all the transcription files is text_lst
    for file in text_lst:
        with open(file, "r") as f:
            # Reading all line of the transcription file
            for line in f:
                line_lst = line.strip().split(" ")
                all_text.append(" ".join(line_lst[1:]))
    return all_text


def prepare_text_file(
    data_folder,
    save_folder,
    tr_splits=[],
    dev_splits=[],
    te_splits=[],
    merge_lst=[],
    merge_name=None,
    select_n_sentences=None,):

    data_folder = data_folder
    splits = tr_splits + dev_splits + te_splits
    save_folder = save_folder
    select_n_sentences = select_n_sentences
    conf = {
        "select_n_sentences": select_n_sentences,
    }

    # Other variables
    # Saving folder
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    for split_index in range(len(splits)):

        split = splits[split_index]
        text_lst = get_all_files(
            os.path.join(data_folder, split), match_and=["trans.txt"]
        )
        all_text = text_to_list(text_lst)
        f_src = open(os.path.join(save_folder,split+".src"), 'w'  )
        f_tgt = open(os.path.join(save_folder,split+".tgt"), 'w'  )
        for item in all_text:
            # write each item on a new line
            f_src.write("%s\n" % item)
            f_tgt.write("%s\n" % item)
        f_src.close()
        f_tgt.close()

        # json.dump(all_text, open(os.path.join(save_folder,split+".src"), 'w'  ))
        # json.dump(all_text, open(os.path.join(save_folder,split+".tgt"), 'w'  ))
        
    if merge_lst and merge_name is not None:
        merge_files = [split_libri + ".src" for split_libri in merge_lst]
        all_text =[]
        for merge_file in merge_files:
            f_src= open( os.path.join(save_folder,merge_file) , "r")
            for line in f_src:
            # remove linebreak from a current name
            # linebreak is the last character of each line
                x = line[:-1]
                # add current item to the list
                all_text.append(x)
                
                # data = json.load( open( os.path.join(save_folder,split+".src") ) )
                # all_text.extend(data)
            f_src.close()
            

        f_src = open(os.path.join(save_folder,merge_name+".src"), 'w'  )
        f_tgt = open(os.path.join(save_folder,merge_name+".tgt"), 'w'  )
        for item in all_text:
            # write each item on a new line
            f_src.write("%s\n" % item)
            f_tgt.write("%s\n" % item)
        f_src.close()
        f_tgt.close()
            
                # json.dump(all_text, open(os.path.join(save_folder,merge_name+".src"), 'w'  ))
                # json.dump(all_text, open(os.path.join(save_folder,merge_name+".tgt"), 'w'  ))    


def get_arguments():
    parser = argparse.ArgumentParser()

    # out path
    parser.add_argument('--save_folder', type=str, default='', help='output path')
    parser.add_argument('--tr_splits', type=str, nargs='+',default=[], help='train splits')
    parser.add_argument('--dev_splits', type=str, nargs='+',default=[], help='dev splits')
    parser.add_argument('--te_splits', type=str, nargs='+',default=[], help='test splits')
    parser.add_argument('--merge_lst', type=str, nargs='+',default=[], help='merge list')
    parser.add_argument('--merge_name', type=str, default='train', help='data path')
    parser.add_argument('--data_folder', type=str, default='', help='data path')


    args = parser.parse_args()
    return args




if __name__ == "__main__":
    args = get_arguments()
    prepare_text_file( data_folder=args.data_folder,
    save_folder=args.save_folder,
    tr_splits=args.tr_splits,
    dev_splits=args.dev_splits,
    te_splits=args.te_splits,
    merge_lst=args.merge_lst,
    merge_name=args.merge_name,)