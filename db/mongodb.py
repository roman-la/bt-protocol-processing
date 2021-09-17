import pymongo


class MongoDB:
    def __init__(self):
        self.connection = pymongo.MongoClient('mongodb://user:pw@141.45.146.163:27017')
        self.database = self.connection['protocols']

    def __del__(self):
        self.connection.close()

    def get_collection_documents(self, collection='19'):
        documents = []
        for document in self.database[collection].find({}):
            documents.append(document)
        return documents