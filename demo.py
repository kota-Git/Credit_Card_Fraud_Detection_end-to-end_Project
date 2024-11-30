from Demo_project.configuration.mongo_db_connection import MongoDBClient

def main():
    try:
        # Initialize MongoDB client
        mongo_client = MongoDBClient()  # Default uses DATABASE_NAME

        # Print connection details for confirmation
        print(f"Connected to MongoDB database: {mongo_client.database_name}")
        print(f"Client: {mongo_client.client}")
        
        # Accessing a specific collection (example)
        collection_name = "fraud_data"  # Replace with your collection name
        collection = mongo_client.database[collection_name]
        print(f"Connected to collection: {collection_name}")

        # Fetching and displaying documents from the collection
        documents = collection.find()
        print("Documents in the collection:")
        for doc in documents:
            print(doc)

    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()