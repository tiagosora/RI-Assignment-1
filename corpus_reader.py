from json import loads


class Reader:

    def __init__(self, path_to_collection: str) -> None:
        self.path_to_collection = path_to_collection
        self.file = open(self.path_to_collection, 'rb')
        print("\nReader initialized...\n")

    def read(self):
        line = self.file.readline()

        if not line:    
            self.file.close()
            return None, None
        
        result = loads(line)
        return int(result['pmid']), " ".join([result['title'], result['abstract']])