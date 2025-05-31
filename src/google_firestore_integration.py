from google.cloud import firestore

def get_all_prompts(credentials):
    """
    Retrieves default prompts from Google Firestore database.
    
    Args:
        credentials: Google Cloud credentials object for authentication
        
    Returns:
        list: A list of dictionaries containing prompt documents, where each dictionary
             includes the document ID and all fields from the Firestore document.
             Example: [{'id': 'doc1', 'user': 'default', 'prompt_text': '...'}]
    """
    # Initialize a Firestore client with the provided credentials
    db = firestore.Client(credentials=credentials)
    
    # Get a reference to the 'Prompts' collection in Firestore
    collection_ref = db.collection(u'Prompts')
    
    # Create a query to filter documents where 'user' field equals 'default'
    query = collection_ref.where('user', '==', 'default')
    
    # Execute the query and get a stream of matching documents
    docs = query.stream()
    
    # Create a list of dictionaries containing document data
    # For each document:
    # - doc.id gets the document's unique identifier
    # - doc.to_dict() converts the document data to a Python dictionary
    # - **doc.to_dict() unpacks the dictionary to merge with the id
    results = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    return results

def get_one_prompt(credentials, user, prompt_name):
    db = firestore.Client(credentials=credentials)
    
    # Get a reference to the 'Prompts' collection in Firestore
    collection_ref = db.collection(u'Prompts')
    
    # Create a query to filter documents where 'user' field equals 'default'
    query = collection_ref.where('prompt_name', '==', prompt_name)
    
    # Execute the query and get a stream of matching documents
    docs = query.stream()
    
    # Create a list of dictionaries containing document data
    # For each document:
    # - doc.id gets the document's unique identifier
    # - doc.to_dict() converts the document data to a Python dictionary
    # - **doc.to_dict() unpacks the dictionary to merge with the id
    results = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    prompt_value = results[0].get("prompt_value")
   
    return prompt_value

def fetch_prompts_by_name(credentials,user,name):
    db = firestore.Client(credentials=credentials)
    collection_ref = db.collection(u'Prompts')
    query = collection_ref.where('prompt_name', '==', name).where('user', '==', user)

    docs = query.stream()
    
    # Collect document IDs that match the query
    results = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    return results

def add_prompt(credentials, user, prompt_name, new_value):
    db = firestore.Client(credentials=credentials)
    collection_ref = db.collection(u'Prompts').document() 
    collection_ref.set({
        u'user': user,
        u'prompt_name': prompt_name,
        u'prompt_value': new_value
    })

def update_prompt_by_name(credentials, user, prompt_name, new_value):
    res=fetch_prompts_by_name(credentials,user,prompt_name)
    if(len(res)==0):
        add_prompt(credentials, user, prompt_name, new_value)
        return "Found no match. Adding."
    elif len(res)==1:
        document_id=res[0].get('id')
        db = firestore.Client(credentials=credentials)
        collection_ref = db.collection(u'Prompts')
        document_ref = collection_ref.document(document_id)
        document_ref.update({'prompt_value': new_value})
        return f"Found one match {res}. Document {document_id} updated: prompt to {new_value}"
    else:
        return f"Found multiple matches {res}. Not updating"
    
def add_evals(credentials, records):
    db = firestore.Client(credentials=credentials)
    for record in records:
        #timestamp = record['start_time']
        #duration = record['duration']
        #input = record['input']
        #expected = record['expected']
        collection_ref = db.collection(u'Evals').document() 
        collection_ref.set(record)
