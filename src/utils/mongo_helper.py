from bson import ObjectId

def serialize_mongo_data(data):
    """ Convert ObjectId to string in a MongoDB document """
    if isinstance(data, list):
        return [serialize_mongo_data(item) for item in data]
    if isinstance(data, dict):
        return {k: str(v) if isinstance(v, ObjectId) else v for k, v in data.items()}
    return data
