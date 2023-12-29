import json
import math
import argparse

class Evaluator:
    def __init__(self, gold_standard_file, run_file):
        self.gold_standard_file = self.parse_files(gold_standard_file)
        self.run_file = self.parse_files(run_file)
        self.evaluation_results = self.evaluate_queries()

    def parse_files(self, file_path):
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON on line: {line}. Error: {e}")
        return data

    def calculate_precision(self, retrieved_documents, relevant_documents):
        relevant_retrieved = set(retrieved_documents).intersection(relevant_documents)
        return len(relevant_retrieved) / len(retrieved_documents) if retrieved_documents else 0

    def calculate_recall(self, retrieved_documents, relevant_documents):
        relevant_retrieved = set(retrieved_documents).intersection(relevant_documents)
        return len(relevant_retrieved) / len(relevant_documents) if relevant_documents else 0

    def calculate_f_measure(self, precision, recall):
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0

    def calculate_average_precision(self, retrieved_documents, relevant_documents):
        ap_sum = 0
        num_relevant_retrieved = 0

        for i, doc in enumerate(retrieved_documents):
            if doc in relevant_documents:
                num_relevant_retrieved += 1
                precision_at_i = num_relevant_retrieved / (i + 1)
                ap_sum += precision_at_i

        return ap_sum / len(relevant_documents) if relevant_documents else 0

    def calculate_dcg(self, retrieved_documents, relevant_documents):
        dcg = 0
        for i, doc in enumerate(retrieved_documents):
            if doc in relevant_documents:
                relevance = 1  # assuming binary relevance; modify as needed
                dcg += relevance / math.log2(i + 2)  # i + 2 because log2(1) is zero and indexing starts at 0
        return dcg
    
    def evaluate_queries(self):
        total_precision, total_recall, total_f_measure, total_avg_precision, total_dcg = 0, 0, 0, 0, 0
        n_queries = len(self.gold_standard_file)
        print(n_queries)

        for query in self.gold_standard_file:
            query_id = query["query_id"]
            relevant_documents = query["documents_pmid"]

            # Find the corresponding retrieved documents
            retrieved_documents = next((item['documents_pmid'] for item in self.run_file if item['query_id'] == query_id), [])

            print("\nRetrieved Documents: ", retrieved_documents)
            print("Relevant Documents: ", relevant_documents)
            # Calculate evaluation metrics
            precision = self.calculate_precision(retrieved_documents, relevant_documents)
            recall = self.calculate_recall(retrieved_documents, relevant_documents)
            f_measure = self.calculate_f_measure(precision, recall)
            average_precision = self.calculate_average_precision(retrieved_documents, relevant_documents)
            discounted_cumulative_gain = self.calculate_dcg(retrieved_documents, relevant_documents)

            # Accumulate evaluation results
            total_precision += precision
            total_recall += recall
            total_f_measure += f_measure
            total_avg_precision += average_precision
            total_dcg += discounted_cumulative_gain

        print("\nTotal Precision: ", total_precision)
        print("Total Recall: ", total_recall)
        print("Total F-Measure: ", total_f_measure)
        print("Total Average Precision: ", total_avg_precision)
        print("Total DCG: ", total_dcg)

        avg_precision = total_precision / n_queries
        avg_recall = total_recall / n_queries
        avg_f_measure = total_f_measure / n_queries
        avg_avg_precision = total_avg_precision / n_queries
        avg_dcg = total_dcg / n_queries

        return {
            "average_precision": avg_precision,
            "average_recall": avg_recall,
            "average_f_measure": avg_f_measure,
            "average_avg_precision": avg_avg_precision,
            "average_dcg": avg_dcg
        }
    
    def get_evaluation_results(self):
        return self.evaluation_results

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Evaluate Information Retrieval System")
    parser.add_argument("gold_standard_file", type=str, help="File path for the gold standard data")
    parser.add_argument("results_file", type=str, help="File path for the results data")
    parser.add_argument("--precision", action="store_true", help="Display precision")
    parser.add_argument("--recall", action="store_true", help="Display recall")
    parser.add_argument("--f1", action="store_true", default=True, help="Display F1 measure")
    parser.add_argument("--average_precision", action="store_true", default=True, help="Display average precision")
    parser.add_argument("--dcg", action="store_true", default=True, help="Display discounted cumulative gain")

    # Parse arguments
    args = parser.parse_args()

    # Initialize the evaluator
    evaluator = Evaluator(args.gold_standard_file, args.results_file)
    results = evaluator.get_evaluation_results()

    # Display requested metrics
    if args.precision:
        print(f"Average Precision: {results['average_precision']}")
    if args.recall:
        print(f"Average Recall: {results['average_recall']}")
    if args.f1:
        print(f"Average F-Measure: {results['average_f_measure']}")
    if args.average_precision:
        print(f"Average Average Precision: {results['average_avg_precision']}")
    if args.dcg:
        print(f"Average DCG: {results['average_dcg']}")

if __name__ == "__main__":
    main()
