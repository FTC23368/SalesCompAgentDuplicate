# NEXT STEPS WITH AMIT (Updated: 7/24):

- Multi-tenant capability:

Use case 1: Anonymous usage - User goes to cl3vr.ai and use it without logging in

Use case 2: Credentialed usage - User goes to cl3vr.ai and logs in with their credentials. 

Use case 3: Dedicated Enterprise - An Enterprise company becomes a cl3vr.ai customer. They get their own tenant and makes it available to their employees. Their tenant will be company.cl3vr.ai. 

Use case 4: Partner/reseller - A Consulting company sells cl3vr.ai to their Enterprise customers and creates customer accounts under their tenant. The Enterprise customer in this case will use consulting company's tenant i.e., consultingcompany.cl3vr.ai

Capabilities:

- LangSmith traces will capture org_id, account_id, and user_name in the traces.
- Security Features for Multi-tenant Enterprise solution
- RLHF: Add Thumbs-up/Thumbs-down in the Streamlit Interface to give users ability to provide feedback. The feedback gets added to LangSmith in the form of AgentState state dictionary.






1. Separate the Plan Design agent from Plan Explainer agent
2. Clean up the document database. There is a lot of duplication in Google Firestore.
3. Similar to Policy Agent, make sure that Plan Design and Plan Explainer agents are also using the full document set and not just RAG'd documents.
4. Activate log in functionality
5. Enable multi-tenant for Enterprise users
6. Update messaging on the landing page
