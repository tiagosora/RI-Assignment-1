# How to Run

## Indexer

In order to index the collections data, run the following command, take in consideration the path to corpus `collections/pubmed_tiny.jsonl`, the path to save the results `pubmed_indexer_tiny_folder` and the arguments used.

```bash
python main.py indexer collections/pubmed_tiny.jsonl \
                       pubmed_indexer_tiny_folder \
                       --tokenizer.minL 3 \
                       --tokenizer.stopwords stopw.txt \
                       --tokenizer.stemmer pystemmer \
                       --tokenizer.regular_exp "<complete with regular expression>" \
                       --tokenizer.lowercase \
                       --indexer.algorithm SPIMI 
```

In alternative, it's also possible to run:

```
./assigment1-indexer.sh
```

## Searcher

In order to search the collected data, run the following command, take in consideration the path to folder containg the data `pubmed_indexer_tiny_folder` (specified in the indexing) and the necessary arguments: the path to the queries' file `collections/question_E8B1_gs.jsonl` and the path to the save the output in a file `tiny_output.jsonl`

```bash
python3 searcher.py batch pubmed_indexer_tiny_folder \
                        --path_to_queries collections/question_E8B1_gs.jsonl \
                        --output_file tiny_output.jsonl
```

In alternative, it's also possible to run:

```
./assigment1-searcher.sh
```

## Indexer

In order to evalutor the searcher's results, run the following command, take in consideration the path to the queries' file `collections/question_E8B1_gs.jsonl` and the path to the results obtained by the searcher `tiny_output.jsonl`

```bash
python3 evaluator.py collections/question_E8B1_gs.jsonl tiny_output.jsonl
```

In alternative, it's also possible to run:

```
./assigment1-evaluator.sh
```