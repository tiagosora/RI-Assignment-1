from re import match, findall
from Stemmer import Stemmer

class Tokenizer:

    def __init__(self, args) -> None:
        self.lowercase = args.tokenizer.lowercase
        self.minL = args.tokenizer.minL
        self.regular_exp = args.tokenizer.regular_exp if args.tokenizer.regular_exp != None and args.tokenizer.regular_exp != '<complete with regular expression>' else "[a-zA-Z]{1,}"
        self.stemmer = args.tokenizer.stemmer
        self.stopwords_path = args.tokenizer.stopwords_path

        self.positional = args.indexer.storing.store_term_position

        self.stopwords = []
        
        if self.stopwords_path != None:
            with open(self.stopwords_path, "r", encoding="utf-8") as f:
                self.stopwords = set([w.strip().lower() for w in f.readlines() if len(w.strip()) >= self.minL])
            f.close()

        self.stemmer = Stemmer('english') if self.stemmer == 'pystemmer' else None
        print("\nTokenizer initialized...\n")

    def tokenize(self, content : str) -> list:

        words = findall(self.regular_exp, content)

        if self.lowercase == True:
            words = [word.lower() for word in words]
        
        if self.regular_exp != '<complete with regular expression>':
            words = [word for word in words if match(self.regular_exp, word)]
        
        if self.minL != None:
            words = [word for word in words if len(word) >= int(self.minL)]
        
        
        if self.stopwords != []:
            words = [word for word in words if word not in self.stopwords]
        
        # if self.stemmer != None:
        #     words = [self.stemmer.stemWord(word) for word in words]

            
        return words
    
