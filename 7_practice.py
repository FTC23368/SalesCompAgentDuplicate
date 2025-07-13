def get_full_policy_content(self):
        files = list_files()
        policy_files = [f for f in files if "Policy" in (f.get("doc_category") or [])]
        #st.write(f"{files=}, {policy_files=}")
        #st.dataframe(policy_files)

        total_content = []

        for files in policy_files:
            content_filename = files["file_name"]
            #st.write(f"# {content_filename=}")
            content = get_text_content(content_filename)
            #st.write(content)
            total_content.append(content)
        return "\n".join(total_content)
    

    def retrieve_documents(self, query: str) -> List[str]:
        """
        Retrieve relevant documents based on the given query.
        
        :param query: User's query string
        :return: List of relevant document contents
        """
        # Generate an embedding for the query and retrieve relevant documents from Pinecone.
        embedding = self.client.embeddings.create(model=st.secrets['EMBEDDING_MODEL'], input=query).data[0].embedding
        results = self.index.query(vector=embedding, top_k=3, namespace="", include_metadata=True)
        
        retrieved_content = [r['metadata']['text'] for r in results['matches']]
        full_content = self.get_full_policy_content()
        retrieved_content.append(full_content)
        print(f"{query=},{retrieved_content=}")
        return retrieved_content