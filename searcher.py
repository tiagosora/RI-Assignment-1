import math
import argparse
import json

from collections import defaultdict

class Searcher:
    
    def __init__(self, index_folder_path):
        self.index_file_path = index_folder_path+"/index.txt"
        self.doc_lengths = self.load_docs_len(index_folder_path+"/docs_len.txt")
        self.total_docs, self.avgdl = self.load_docs_info(index_folder_path+"/docs_info.txt")
        self.doc_mapping = self.load_doc_mapping(index_folder_path+"/doc_mapping.txt")
        self.term_frequencies_path = index_folder_path+"/term_frequencies.txt"
    
    def load_docs_info(self, file_path):
        try:
            with open(file_path, "r") as file:
                lines = file.read().splitlines()
                total_docs = int(lines[0].split(':')[1])
                avgdl = float(lines[1].split(':')[1])
                return total_docs, avgdl
        except Exception as e:
            print(f"Error reading index (load_docs_info): {e}")

    def load_docs_len(self, file_path) -> dict:
        try:
            document_lengths = {}
            with open(file_path, "r") as file:
                for line in file:
                    doc_id, lenght = line.strip().split(':')
                    document_lengths[doc_id] = int(lenght)
            return document_lengths
        except Exception as e:
            print(f"Error reading index (document_lengths): {e}")

    def load_doc_mapping(self, file_path) -> dict:
        try:
            doc_mapping = {}
            with open(file_path, "r") as file:
                for line in file:
                    pmid, doc_id = line.strip().split(':')
                    doc_mapping[doc_id] = pmid
            return doc_mapping
        except Exception as e:
            print(f"Error reading index (load_doc_mapping): {e}")

    def get_term_frequency(self, expected_term) -> int:
        try:
            with open(self.term_frequencies_path, "r") as file:
                for line in file:
                    term, freq = line.strip().split(':')
                    if term == expected_term:
                        return int(freq)
            return None
        except Exception as e:
            print(f"Error reading index (get_term_frequency): {e}")

    def read_index(self):
        try:
            with open(self.index_file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split(';')
                    term = parts[0]
                    postings = []
                    for posting in parts[1:]:
                        if ':' in posting:  # Positional
                            doc_id, positions = posting.split(':')
                            positions = list(map(int, positions.split(',')))
                            postings.append((doc_id, positions, len(positions)))  # Include frequency
                        else:  # Non-positional
                            doc_id, freq = posting.split(',')
                            postings.append((doc_id, [], int(freq)))  # Empty list for positions
                    yield term, postings
                return None, None
        except Exception as e:
            print(f"Error reading index (read_index): {e}")

    def tokenize(self, text: str):
        return text.lower().split()
    
    def tf_idf_search(self, query: str, smart_notation='lnc.ltc'):
        if smart_notation == 'lnc.ltc':
            return self.tf_idf_search_lnc_ltc(query)
        elif smart_notation == 'bnn.bnc':
            return self.tf_idf_search_bnn_bnc(query)
        else:
            print(f"SMART notation {smart_notation} not recognized.")
            return []
        
    def tf_idf_search_lnc_ltc(self, query: str):
        query_terms = self.tokenize(query)
        doc_scores = defaultdict(float)
        query_weights = defaultdict(float)
        
        query_norm = 0
        for term in query_terms:
            term_freq = self.get_term_frequency(term)
            if term_freq:
                df = term_freq
                idf = math.log(self.total_docs / df)
                query_weights[term] += (1 + math.log(query_terms.count(term))) * idf
                query_norm += query_weights[term] ** 2
        query_norm = math.sqrt(query_norm)

        if query_norm == 0:
            return []

        for term, postings in self.read_index():
            if term in query_terms:
                
                for doc_id, _, freq in postings:
                    tf = 1 + math.log(freq)
                    doc_norm = math.sqrt(self.doc_lengths.get(doc_id, 1))
                    doc_scores[doc_id] += (tf / doc_norm) * (query_weights[term] / query_norm)

        return sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

    def tf_idf_search_bnn_bnc(self, query: str):
        query_terms = set(self.tokenize(query))
        query_norm = math.sqrt(len(query_terms))

        doc_scores = defaultdict(float)

        for term, postings in self.read_index():
            if term in query_terms:
                for doc_id, _, _ in postings:
                    tf = 1
                    doc_norm = math.sqrt(self.doc_lengths.get(doc_id, 1))
                    if doc_norm != 0:
                        doc_scores[doc_id] += (tf / doc_norm) / query_norm

        ranked_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return ranked_docs

    def bm25_search(self, query, k1=1.2, b=0.75):
        query_terms = self.tokenize(query)
        doc_scores = defaultdict(float)

        for term, postings in self.read_index():
            if term in query_terms:
                df = len(postings)
                idf = math.log((self.total_docs - df + 0.5) / (df + 0.5) + 1) if df > 0 else 0

                for doc_id, _, freq in postings:
                    tf = freq
                    doc_len = self.doc_lengths.get(doc_id, 1)
                    norm_tf = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / self.avgdl)))
                    doc_scores[doc_id] += idf * norm_tf

        return sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

    def interactive_mode(self, top_k, ranking_method, search_type, smart_notation, max_distance, k1, b):

        while True:
            query = input("Enter your query (or 'exit' to quit): ")
            if query.lower() == 'exit':
                break

            # Determine the set of documents to consider based on search type
            if search_type == 'phrase':
                doc_ids = self.phrase_search(query)
            elif search_type == 'proximity':
                doc_ids = self.proximity_search(query, max_distance)
            else:  # 'standard' search type
                doc_ids = None  # All documents are candidates

            # Perform the ranking
            results = []
            if ranking_method == 'tf-idf':
                results = self.tf_idf_search(query, smart_notation)[:top_k]
            elif ranking_method == 'bm25':
                results = self.bm25_search(query, k1, b)[:top_k]

            # Filter results based on doc_ids if phrase or proximity search was used
            if doc_ids is not None:
                results = [res for res in results if res[0] in doc_ids]

            # Print results
            for rank, (doc_id, score) in enumerate(results, start=1):
                print(f"{rank}. Document: {doc_id}, Score: {score}")


    def batch_mode(self, path_to_queries, output_file, top_k, ranking_method, search_type, smart_notation, max_distance, k1, b):

        with open(path_to_queries, 'r') as file:
            with open(output_file, 'w') as out:  # Open file in append mode
                pass
            for line in file:
                query_data = json.loads(line)
                query_text = query_data["query_text"]
                query_id = query_data["query_id"]

                # Determine the set of documents to consider based on search type
                if search_type == 'phrase':
                    doc_ids = self.phrase_search(query_text)
                elif search_type == 'proximity':
                    doc_ids = self.proximity_search(query_text, max_distance)
                else:
                    doc_ids = None  # All documents are candidates

                # Perform the ranking
                if ranking_method == 'tf-idf':
                    results = self.tf_idf_search(query_text, smart_notation)[:top_k]
                elif ranking_method == 'bm25':
                    results = self.bm25_search(query_text, k1, b)[:top_k]

                # Filter results based on doc_ids if phrase or proximity search was used
                if doc_ids is not None:
                    results = [res for res in results if res[0] in doc_ids]

                # Write results to output file
                with open(output_file, 'a') as out:  # Open file in append mode
                    documents = [self.doc_mapping[doc_id] for doc_id, _ in results]
                    response = json.dumps({"query_id": query_id, "documents_pmid": documents})
                    out.write(response + "\n")

    def phrase_search(self, query):
        query_terms = self.tokenize(query)
        if not query_terms:
            return []

        init_sets = []
        for term, postings in self.read_index():
            if term in query_terms:
                init_sets.append(set(doc_id for doc_id, _, freq in postings)) 

        candidate_docs = set()
        if len(init_sets) != 0:
            candidate_docs = set.intersection(*init_sets)

        results = []
        for doc_id in candidate_docs:
            term_positions = [self.get_term_positions(term, doc_id) for term in query_terms]

            if self.check_terms_in_sequence(term_positions):
                results.append(doc_id)

        return results

    def get_term_positions(self, term, doc_id):
        """Retrieve positions for a term in a specific document."""
        for _, postings in self.read_index():
            for posting in postings:
                if posting[0] == doc_id:
                    return posting[1]
        return []

    def check_terms_in_sequence(self, term_positions):
        """Check if the terms appear in sequence."""
        for i in range(len(term_positions) - 1):
            current_positions = term_positions[i]
            next_positions = term_positions[i + 1]
            if not any(npos == cpos + 1 for cpos in current_positions for npos in next_positions):
                return False
        return True

    def are_terms_within_distance(self, term_positions, max_distance):
        """Check if terms are within max_distance in a document."""
        for i in range(len(term_positions) - 1):
            for pos1 in term_positions[i]:
                for j in range(i+1, len(term_positions)):
                    if any(abs(pos2 - pos1) <= max_distance for pos2 in term_positions[j]):
                        return True
        return False

    def proximity_search(self, query, max_distance):
        query_terms = self.tokenize(query)
        if not query_terms:
            return []

        init_sets = []
        for term, postings in self.read_index():
            if term in query_terms:
                init_sets.append(set(doc_id for doc_id, _, freq in postings)) 

        candidate_docs = set()
        if len(init_sets) != 0:
            candidate_docs = set.intersection(*init_sets)
        
        results = []
        for doc_id in candidate_docs:
            term_positions = [self.get_term_positions(term, doc_id) for term in query_terms]

            if self.are_terms_within_distance(term_positions, max_distance):
                results.append(doc_id)

        return results

from time import time

if __name__ == "__main__":
    start_time = time()
    parser = argparse.ArgumentParser(description='Searcher for Indexed Documents')
    parser.add_argument('mode', type=str, choices=['interactive', 'batch'], help='Operating mode of the searcher')
    parser.add_argument('files_folder', type=str, help='Folder where the index files are located')
    parser.add_argument('--path_to_queries', type=str, help='Path to the file containing queries')
    parser.add_argument('--output_file', type=str, help='File to write the search results')
    parser.add_argument('--top_k', type=int, default=10, help='Maximum number of documents to return per query')
    parser.add_argument('--ranking_method', type=str, default='tf-idf', choices=['tf-idf', 'bm25'], help='Ranking method to use')
    parser.add_argument('--smart_notation', type=str, default='lnc.ltc', help='SMART notation for TF-IDF')
    parser.add_argument('--k1', type=float, default=1.2, help='k1 parameter for BM25')
    parser.add_argument('--b', type=float, default=0.75, help='b parameter for BM25')
    parser.add_argument('--search_type', type=str, default='standard', choices=['standard', 'phrase', 'proximity'], help='Type of search')
    parser.add_argument('--max_distance', type=int, default=0, help='Max distance for proximity search')

    args = parser.parse_args()

    searcher = Searcher(args.files_folder)

    if args.mode == 'interactive':
        searcher.interactive_mode(args.top_k,
                                  args.ranking_method,
                                  args.search_type,
                                  args.smart_notation,
                                  args.max_distance,
                                  args.k1,
                                  args.b)
    elif args.mode == 'batch':
        if not args.path_to_queries or not args.output_file:
            print("Batch mode requires path_to_queries and output_file arguments.")
        else:
            searcher.batch_mode(args.path_to_queries,
                                args.output_file,
                                args.top_k,
                                args.ranking_method,
                                args.search_type,
                                args.smart_notation,
                                args.max_distance,
                                args.k1,
                                args.b)
            
    print("Execution Time: ", time() - start_time)
