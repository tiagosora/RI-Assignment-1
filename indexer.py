import time
import psutil
import os
from Stemmer import Stemmer
from corpus_reader import Reader
from tokenizer import Tokenizer

class SPIMIIndexer:

    def __init__(self, tokenizer : Tokenizer, args) -> None:
        self.index_output_folder = args.index_output_folder
        if os.path.exists(self.index_output_folder):
            for file in os.listdir(self.index_output_folder):
                os.remove(os.path.join(self.index_output_folder, file))
        else:
            os.mkdir(self.index_output_folder)
        self.memory_threshold = args.indexer.memory_threshold if args.indexer.memory_threshold else 0.8
        self.positional = args.indexer.storing.store_term_position
        print("Positional: ",self.positional)
        self._inverted_index = InvertedIndex(self.index_output_folder, self.positional)
        self.reader = Reader(args.path_to_collection)
        self.tokenizer = tokenizer
        self.total_docs_lenght = 0
        self.doc_mapping = {}

    def index(self):
        print("Indexing documents...")
        
        tic = time.time()
        while 1:
            pmid, content = self.reader.read()
            if pmid == None:
                break

            if pmid in self.doc_mapping:
                continue

            doc_id = len(self.doc_mapping)
            self.doc_mapping[pmid] = doc_id
            
            terms = self.tokenizer.tokenize(content)
            
            
            doc_lenght = len(terms)
            self.total_docs_lenght += doc_lenght
            with open(os.path.join(self.index_output_folder, "docs_len.txt"), "a") as f:
                f.write(f"{doc_id}:{doc_lenght}\n")

            tokens = {}
            for i, token in enumerate(terms):
                tokens.setdefault(token, {}).setdefault(doc_id, []).append(i)
            _ = [
                self._inverted_index.add_term(
                    token,
                    doc_id,
                    positions,
                )
                for token, data in tokens.items()
                for doc_id, positions in data.items()
            ]
            
            if self.memory_threshold != None and psutil.virtual_memory().percent/100 > self.memory_threshold:
                print(psutil.virtual_memory().percent)
                self._inverted_index.write_in_disk(self.index_output_folder)
                self._inverted_index.clean_posting_list()
                print(f"\nBlock {self._inverted_index.block_counter} finished")

        self._inverted_index.write_in_disk(self.index_output_folder)
        self._inverted_index.clean_posting_list()
        print(f"\nBlock {self._inverted_index.block_counter} finished")
        toc = time.time()

        with open(os.path.join(self.index_output_folder, "docs_info.txt"), "w") as f:
            total_docs = len(self.doc_mapping)
            f.write(f"total_docs:{total_docs}\n")
            f.write(f"avgdl:{int(self.total_docs_lenght / total_docs)}\n")

        with open(os.path.join(self.index_output_folder, "doc_mapping.txt"), "w") as f:
            for doc_id, pmid in enumerate(self.doc_mapping):
                f.write(f"{pmid}:{doc_id}\n")
            self.doc_mapping = []

        tic_merge = time.time()
        self._inverted_index.merge_blocks(self.index_output_folder, self.memory_threshold)
        toc_merge = time.time()

            # write to file Index Statistics for the file
        file = os.path.join(self.index_output_folder, "index_stats.txt")
        with open(file, "w") as f:
            f.write("INDEX STATISTICS\n")
            f.write("\n")
            f.write("Total index size on disk : {0} MB\n".format(round(os.stat(os.path.join(self.index_output_folder, 'index.txt')).st_size / 1024 / 1024, 2)))
            f.write("Total Indexing time : {0} s\n".format(toc-tic))
            f.write("Number of temporary index segments written to disk (before merging) : {0}\n".format(len(self.doc_mapping)))
            f.write("Merging time (last SPIMI step) : {0} s\n".format(toc_merge - tic_merge))
            f.write("Total time : {0} s\n".format(toc_merge - tic)) 
        
class InvertedIndex:
    def __init__(self, index_output_folder, positional):
        self.index_output_folder = index_output_folder
        self.positional = positional
        self.posting_list = {}
        self.block_counter = 0
        self.temp_index = {}

    def add_term(self, term, doc_id, positions):
        if self.positional:
            if term not in self.posting_list:
                self.posting_list[term] = {doc_id: positions}
            else:
                self.posting_list[term][doc_id] = positions
        else:
            if term not in self.posting_list:
                self.posting_list[term] = {doc_id: len(positions)}
            else:
                self.posting_list[term][doc_id] = len(positions)

    def clean_posting_list(self):
        self.posting_list = {}

    def write_in_disk(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

        sorted_index = {k: self.posting_list[k] for k in sorted(self.posting_list)}
        filename = f"{folder}/block_{self.block_counter}.txt"
        with open(filename, "wb") as f:
            if self.positional:
                for term, posting in sorted_index.items():
                    line = f"{term};{';'.join([str(doc_id) + ':' + ','.join(map(str, positions)) for doc_id, positions in posting.items()])}\n"
                    f.write(line.encode("utf-8"))
            else:
                for term, posting in sorted_index.items():
                    line = f"{term};{';'.join([str(doc_id) + ',' + str(freq) for doc_id, freq in posting.items()])}\n"
                    f.write(line.encode("utf-8"))

        self.block_counter += 1

    def dump_to_disk(self, folder):
        print("Dumping index{self.index_counter}")
        with open(f"{folder}/index{self.index_counter}.txt", "w") as f:
            for term in self.temp_index:
                f.write(f"{term};{self.temp_index[term]}\n")
        # with open(f"{folder}/index_list.txt{self.index_counter}", "w") as f:
        #     for term in temp_index:
        #         f.write(f"{current_term};{temp_index[term]}\n")
        print(f"Index{self.index_counter}.txt finished")

        self.temp_index = {}
        self.index_counter += 1

    def merge_blocks(self, folder, memory_threshold):
        print("Merging blocks...")

        files_ended = 0
        
        files = {}
        for block_id, path in enumerate(os.scandir(self.index_output_folder)):
            if path.is_file() and path.name.startswith("block_"):
                files[block_id] = open(path, "rb")

        lines = {}
        for block_id, file in files.items():
            lines[block_id] = file.readline().decode("utf-8").strip()
        
        # index_start_term = None

        saved_term = None
        saved_postings = None
        current_term = None
        current_postings = None

        self.index_counter = 0

        while files_ended < len(files):

            min_index = min(lines, key=lambda x: list(lines[x])[0])
            line = lines[min_index]

            current_term, current_postings = line.split(';', 1)

            # Se for um termo novo
            if current_term != saved_term:

                freq = 0
                for posting in current_postings.split(";"):
                    if ':' in posting:
                        _, positions = posting.split(':')
                        positions = list(map(int, positions.split(',')))
                        freq += len(positions)
                    else:
                        freq += int(posting.split(',')[1])

                with open(f"{folder}/term_frequencies.txt", "a") as f:
                    f.write(f"{current_term}:{freq}\n")

                self.temp_index[current_term] = current_postings

                if memory_threshold != None and psutil.virtual_memory().percent / 100 > memory_threshold:
                    print("Memory exceeded the threshold: ",psutil.virtual_memory().percent)
                    self.dump_to_disk(folder)

                saved_term = current_term

            elif current_term:
                current_postings += f";{current_postings}"

            lines[min_index] = files[min_index].readline().decode('utf-8')[:-1]
            if lines[min_index] == None or lines[min_index] == "":
                files[min_index].close()
                files.pop(min_index)
                lines.pop(min_index)
                files_ended += 1

        self.dump_to_disk(folder)
        
        print("Deleting temporary files...")
        _ = [
                os.remove(filename) 
                for filename in os.scandir(self.index_output_folder) 
                if filename.is_file() and filename.name.startswith("block_")
            ]
        
        ########## Merging the merged_indexes ##########
        
        index_files = [
            filename 
            for filename in os.scandir(self.index_output_folder) 
            if filename.is_file() and filename.name.startswith("index")
        ]
        
        if len(index_files) == 1:
            os.rename(f'{folder}/index0.txt', f'{folder}/index.txt')
        elif len(index_files) > 1:
            # Merge files
            with open(f'{folder}/index.txt', 'w') as outfile:
                for input_file in index_files:
                    with open(input_file, 'r') as infile:
                        outfile.write(infile.read())
                    os.remove(input_file)

        print("Merge complete...")

