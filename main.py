"""
Created by: Tiago Almeida & Sérgio Matos
Last update: 23-09-2023

Main python CLI interface for the IR class 
assigments. 

The code was tested on python version 3.9.
Older versions (until 3.6) of the python 
interpreter may run this code [No verification
was performed, yet].

"""

import argparse
from cliutils import grouping_args, shared_tokenizer, cli_debug_printer
from indexer import SPIMIIndexer
from tokenizer import Tokenizer
import time


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="CLI interface for the IR engine")
    
    # operation modes
    # - indexer
    # - searcher
    mode_subparsers = parser.add_subparsers(dest='mode', 
                                            required=True)
    
    ############################
    ## Indexer CLI interface  ##
    ############################
    indexer_parser = mode_subparsers.add_parser('indexer', 
                                                help='Indexer help')
    
    indexer_parser.add_argument('path_to_collection', 
                                type=str, 
                                help='Name of the folder or file that holds the document collection to be indexed.')
    
    indexer_parser.add_argument('index_output_folder', 
                                type=str, 
                                help='Name of the folder where all the index related files will be stored.')
    
    indexer_settings_parser = indexer_parser.add_argument_group('Indexer settings', 'This settings are related to how the inverted index is built and stored.')
    
    indexer_settings_parser.add_argument('--indexer.algorithm', 
                                    type=str, 
                                    default="SPIMI",
                                    help='Maximum limit of RAM that the program (index) should consume. (Default: SPIMI)')
    
    #indexer_settings_parser.add_argument('--indexer.posting_threshold', 
    #                                type=float, 
    #                                default=None,
    #                                help='Maximum number of postings that each index should hold. (Default: None)')
    
    indexer_settings_parser.add_argument('--indexer.memory_threshold', 
                                    type=float, 
                                    default=None,
                                    help='Maximum limit of RAM that the program (index) should consume. (Default: None)')

    indexer_settings_parser.add_argument('--indexer.storing.store_term_position',
                                         action="store_true",
                                         help='Signals if the indexer should store the term positions along side the term frequencies. (Default is False)')
    
    indexer_settings_parser.add_argument('--indexer.storing.bm25.cache_in_disk', 
                                    action="store_true",
                                    help='Signals if the index should create a cache file to store all intermediate computations of the BM25 ranking method. (Default is False)')

    indexer_settings_parser.add_argument('--indexer.storing.bm25.k1', 
                                    type=float, default=1.2,
                                    help='The k1 value of the bm25, this value will only be used if the flag --indexer.bm25.cache_in_disk is set to True. (Default=1.2)')

    indexer_settings_parser.add_argument('--indexer.storing.bm25.b', 
                                    type=float, default=0.7,
                                    help='The b value of the bm25, this value will only be used if the flag --indexer.bm25.cache_in_disk is set to True. (Default=0.7)')
    
    indexer_settings_parser.add_argument('--indexer.storing.tfidf.cache_in_disk', 
                                    action="store_true",
                                    help='Signals if the index should create a cache file to store all intermediate computations of the TFIDF ranking method. (Default is False)')

    indexer_settings_parser.add_argument('--indexer.storing.tfidf.smart',
                                    type=str,
                                    default="lnc.ltc",
                                    help='The smart notation of the tfidf, this value will only be used if the flag --indexer.tfidf.cache_in_disk is set to True. (Default=lnc.ltc)')
    
        
    indexer_doc_parser = indexer_parser.add_argument_group('Tokenizer settings', 'This settings are related to how the documents should be loaded and processed to tokens.')
    
    
    indexer_doc_parser.add_argument('--tokenizer.minL',
                                    #dest="minL",
                                    type=int, 
                                    default=None,
                                    help='Minimum token length. The absence means that will not be used (default=None).')
    
    indexer_doc_parser.add_argument('--tokenizer.stopwords_path',
                                    #dest="stopwords_path",
                                    type=str,
                                    default=None,
                                    help='Path to the file that holds the stopwords. The absence means that will not be used (default=None).')
    
    indexer_doc_parser.add_argument('--tokenizer.stemmer',
                                    #dest="stemmer",
                                    type=str, 
                                    default=None,
                                    help='Type of stemmer to be used. The absence means that will not be used (default=None).')
    
    indexer_doc_parser.add_argument('--tokenizer.regular_exp',
                                    #dest="stemmer",
                                    type=str, 
                                    default=None,
                                    help='Define a regular expression to be used to accept tokens (default=None).')

    indexer_doc_parser.add_argument('--tokenizer.lowercase',
                                    #dest="stemmer",
                                    action="store_true",
                                    default=None,
                                    help='Flag that enables the convertion of the characters to lowercase (default=False).')
        
    #######################################
    ## Searcher Interactive CLI interface ##
    ########################################
    searcher_parser = mode_subparsers.add_parser('searcher', help='Searcher help')

    # mutal exclusive searching modes
    searcher_mode_subparsers = searcher_parser.add_subparsers(dest='searcher_mode', 
                                                              required=True)
    
    searcher_interactive = searcher_mode_subparsers.add_parser('interactive', help='Indexer help')
    searcher_interactive.add_argument('index_folder', 
                                type=str, 
                                help='Folder where all the index related files will be loaded.')
    
    searcher_interactive.add_argument('--top_k', 
                                type=int,
                                default=1000,
                                help='Number maximum of documents that should be returned per question.')
    
    
    # mutual exclusive searching modes this is duplicated with batch mode, argparse does not support multiple
    # subparsers, rn let it be this way.
    searcher_modes_interactive_parser = searcher_interactive.add_subparsers(dest='ranking_mode', required=True)
    
    bm25_mode_parser = searcher_modes_interactive_parser.add_parser('ranking.bm25', help='Uses the BM25 as the searching method')
    bm25_mode_parser.add_argument("--ranking.bm25.k1", type=float, default=1.2)
    bm25_mode_parser.add_argument("--ranking.bm25.b", type=float, default=0.6)

    tfidf_mode_parser = searcher_modes_interactive_parser.add_parser('ranking.tfidf', help='Uses the TFIDF as the searching method')
    tfidf_mode_parser.add_argument("--ranking.tfidf.smart", type=str, default="lnc.ltc")
    
    searcher_batch = searcher_mode_subparsers.add_parser('batch', help='Indexer help')
    searcher_batch.add_argument('index_folder', 
                                type=str, 
                                help='Folder where all the index related files will be loaded.')
    

    searcher_batch.add_argument('path_to_questions', 
                                type=str, 
                                help='Path to the file that contains the question to be processed, one per line.')

    searcher_batch.add_argument('output_file', 
                                type=str, 
                                help='File where the found documents will be returned for each question.')

    searcher_batch.add_argument('--top_k', 
                                type=int,
                                default=1000,
                                help='Number maximum of documents that should be returned per question.')
    
    
    # mutual exclusive searching modes
    searcher_modes_batch_parser = searcher_batch.add_subparsers(dest='ranking_mode', required=True)
    
    bm25_mode_parser = searcher_modes_batch_parser.add_parser('ranking.bm25', help='Uses the BM25 as the searching method')
    bm25_mode_parser.add_argument("--ranking.bm25.k1", type=float, default=1.2)
    bm25_mode_parser.add_argument("--ranking.bm25.b", type=float, default=0.6)

    tfidf_mode_parser = searcher_modes_batch_parser.add_parser('ranking.tfidf', help='Uses the TFIDF as the searching method')
    tfidf_mode_parser.add_argument("--ranking.tfidf.smart", type=str, default="lnc.ltc")
    
    ############################
    ## Evaluator CLI interface ##
    ############################
    evaluator_parser = mode_subparsers.add_parser('evaluator', help='Evaluator help')
    
    evaluator_parser.add_argument('gold_standard_file', 
                                type=str, 
                                help='Path to the file that contains the questions and the goldstandard judments.')

    evaluator_parser.add_argument('run_file', 
                                type=str, 
                                help='Path to the file that contains the questions and the ranked list of documents')
    
    evaluator_parser.add_argument('--metrics',
                                  nargs="*",
                                  default=["F1","DCG","AP"])
    # CLI parsing
    #args = parser.parse_args()
    args = grouping_args(parser.parse_args())
    ### CLI ENDS HERE
    
    
    ### START YOUR SEARCHING ENGINE CODE HERE 

    # Read the Document and Identify the Content

    if args.mode == "indexer":

        tokenizer = Tokenizer(args)

        print("Indexing")

        indexer = SPIMIIndexer(tokenizer, args)

        start = time.time()

        indexer.index()

        print("TEMPO DE EXECUÇÃO: ", time.time() - start)

    #     indexer.finalize()

    #     print("Indexing Ended\n")
    #     print(f"Tempo em segundos: {time.time() - start}")
    #     input("Press any key to continue...")

    # elif args.mode=="searcher": 
    #     my_chatgpt_searcher(args)

    # elif args.mode=="evaluator":
    #     my_evaluator(args)
    
    ### Showcase of how to access the args variables
    # print("Showing the argparser NameSpace")
    # print(args)
    # print()
    # print("###############################")
    # print("#         Tree viewer         #")
    # print("###############################")   
    # print()
    # print(cli_debug_printer(args._get_kwargs()))
    
    # print()
    # print("###############################")
    # print("#      Example of access      #")
    # print("###############################")  
    # print() 
    # if args.mode == "indexer":
    #     print("mode:", args.mode)
    #     print("indexer parameters:", args.indexer)
    #     print("store_term_posiiton:", args.indexer.storing.store_term_position)
    #     print("tokenizer stemmer:", args.tokenizer.stemmer)
    # elif args.mode == "searcher":
    #     print("mode:", args.mode)
    #     print("Top k docs to retrieve:", args.top_k)
    #     print("ranking:", args.ranking)
    #     #print("store_term_posiiton:", args.indexer.storing.store_term_position)
    #     #print("tokenizer stemmer:", args.tokenizer.stemmer)
        