import pymongo

class Settings(dict):

    def __getattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

global_settings = Settings()
global_client = None
global_db = None

def connect(settings=None):
    global global_client

    if settings is None:
        settings = global_settings

    global_client = pymongo.MongoClient(settings.url)
    db_name = settings.url.split('/')[-1]

    global_db = global_client[db_name]

    return global_db
