# NEXT STEPS WITH AMIT (Updated: 2/8):

1. Complete Eval setup - COMPLETED

2. Embeddings migration plan - Save documents in Firestore and include the entire doucment in the prompt.

3. I have to consider on how to reduce the response time. Currently, it is taking very long. Plus, if possible, I'd like the agent to start streaming the response and not take the entire time thinking..

3. contest agent RAG setup





1) Now that we have moved prompts outside of the code, point to Firestore for prompts instead of prompt_store.py. But keep it easy to revert back to prompt_store.py - Done

2) Google Firestore integration should do a two step search for prompts. First look for a custom prompt from the user. If it doesn't exist get the default prompt for that prompt_name.

3) Set up for multi-tenancy so that prompts can be modified by organization

a) Setup Authentication
b) Define user table with roles (admin and user) and populate with one user
c) Process to add users

4) Modify eval.py so that eval can be done for entire conversation instead of just one statement at a time.

5) Self-assessment and Continuous Improvement Loop:
Assess every user conversation for it's effectiveness and provide feedback to your developers on how to improve either the prompt or RAG documents or the flow. 

6) Check if we can move to o3-mini or not (COMPLETED)

7) Create a lighter version of Sales Comp Agent: Remove complex tasks like booking appointment which are dependent on calendar integration. Create something which a Sales Comp Leader can deploy in their company by simply signing up for a company account (free version with no ability to do RAG or a paid version with their own instance of sales comp agent with ability to do RAG) -- Tag line: Reduce your ticket volume by 30%.

8) Modify the app for multi-tenant environment, which includes deploying it on a URL and ability to create a company account. Company employees would be able to access their own version.

9) Host it on a hosting service. (COMPLETED)


# NEXT STEPS FOR JAHANGIR (Updated: 2/8):

1) Complete UAT for all sub-agents. Based on the outcome, refine the RAG document and prompts. Note that in the main prompt where you have examples, you might want to add examples using Claude.

2) Exception request: 
    a. Ask the user to fill out an intake form (Google Form) -- https://forms.gle/zBp6H4ApLRmAT2Cx8
    b. Inform them the rough timeline for approval workflow i.e., roughly how long it takes to get SCRC decision.

3) Plan Explainer: 
    Sometimes reps ask questions about how their plan works. These questions are simply to get clarity on the mechanics of the comp plan. This sub-agent has leanred all plan constructs in the company and has deep understanding of how they work. Note: We will use RAG to upload descriptions of all comp plans by role. 

4) Feedback Collector: (Narrative generator based on email responses)
    Sometimes sales leaders want to share their feedback about what's working and what's not working in the current sales comp plan design. They may have ideas from their past experiences. The sub-agent understands all current sales comp plans, and is also an expert researcher and has the ability to go deeper and ask intriguing questions to understand exactly what problem are they trying to solve.

5) Test with Multiple LLMs: Test Sales Comp Agent using newer ChatGPT models (4o, 4o mini, o1 or o1 mini) and other LLMs, like Grok, Claude etc. Compare the time it takes for them versus ChatGPT