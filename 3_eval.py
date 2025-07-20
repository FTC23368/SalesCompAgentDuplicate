import os
import streamlit as st
from langsmith import Client
from langchain_openai import ChatOpenAI
from typing_extensions import Annotated
from typing import TypedDict
from instructor import patch
from src.graph import salesCompAgent
import pandas as pd
from langchain_core.messages import HumanMessage

# Set environment variables for LangSmith
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "sales-comp-eval"  

DEBUGGING = 0

# Initialization with ChatOpenAI
client = ChatOpenAI(model=st.secrets['OPENAI_MODEL'], temperature=0, api_key=st.secrets['OPENAI_API_KEY'])

def eval():
    """Main evaluation function that:
    1. Sets up the testing environment
    2. Creates test datasets
    3. Runs evaluations
    4. Displays results"""

    # Initialize chat history in Streamlit session
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    st.title("Sales Compensation Agent Evaluation")
    
    # Initialize LangSmith client for evaluation tracking
    langsmith_client = Client()

    # Define test cases with questions and expected responses
    examples = [
        [{
            "question": "What would be my commission when I close a $2M deal?",
            "category": "commission",
            "response": "In order to calculate your expected commission, please provide OTI and annual quota? Once I have this information, I'll be able to calculate your commission.",
        },],
        [{
            "question": "I can't access the commission system",
            "category": "ticket",
            "response": "I need your full name and a valid email address. This will allow me to create a support ticket for our Sales Compensation team.",
        },]
    ]
    
    dataset_name = "Sales Compensation Agent Evaluation"

    # Always create/recreate the dataset
    st.write("Creating new dataset...")  # Debug print
    try:
        # Delete existing dataset if it exists
        if langsmith_client.has_dataset(dataset_name=dataset_name):
            existing_dataset = langsmith_client.read_dataset(dataset_name=dataset_name)
            langsmith_client.delete_dataset(dataset_id=existing_dataset.id)
        
        # Create new dataset
        dataset = langsmith_client.create_dataset(dataset_name=dataset_name)
        
        # Format examples correctly for LangSmith API
        for example in examples:
            ex = example[0]
            langsmith_client.create_example(
                inputs={"question": ex["question"]},
                outputs={"response": ex["response"]},
                dataset_id=dataset.id
            )
            
        # Verify examples were created
        created_examples = list(langsmith_client.list_examples(dataset_id=dataset.id))
        st.write(f"Created {len(created_examples)} examples")  # Debug print
        
    except Exception as e:
        st.error(f"Error creating dataset: {str(e)}")
        raise

    def run_graph(question: str):
        """Runs a single test through the Sales Compensation Agent"""
        agent = salesCompAgent(st.secrets['OPENAI_API_KEY'])
        response_text = None
        
        try:
            # Add the user's question to session history
            st.session_state.messages.append({"role": "user", "content": question})
            message_history = []
            message_history.append(HumanMessage(content=question))
            
            response = agent.graph.invoke({
                'initialMessage': question, 
                #'sessionState': st.session_state, 
                #'sessionHistory': st.session_state.messages,
                'message_history': message_history
            })
            
            # Handle different response formats
            if isinstance(response, dict):
                # Define all possible response categories
                categories = ["policy", "commission", "contest", "ticket", "smalltalk", "clarify", "planexplainer", "feedbackcollector"]
                
                # Try all possible response locations
                for cat in categories:
                    if cat in response and 'responseToUser' in response[cat]:
                        response_text = response[cat]['responseToUser']
                        break
                
                # If not found in categories, try direct access
                if not response_text:
                    response_text = response.get('responseToUser') or response.get('content')
            
            if not response_text:
                raise ValueError("No response received from agent")
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            return {"response": response_text}
            
        except Exception as e:
            st.error(f"Error in run_graph: {str(e)}")
            return {"response": f"Error: {str(e)}"}

    class Grade(TypedDict):
        """Defines the structure for evaluation results"""
        reasoning: Annotated[str, "Detailed analysis of the agent's response quality and appropriateness"]
        is_correct: Annotated[bool, "Whether the response meets sales compensation query handling standards"]

    # Instructions for GPT-4 on how to evaluate responses
    eval_instructions = """You are evaluating a Sales Compensation Agent's responses to user queries.

    Context: This agent handles questions about sales commissions, quotas, bonuses, and related systems.

    You will analyze:
    QUERY: The user's sales compensation related question
    EXPECTED RESPONSE: The standard correct response
    ACTUAL RESPONSE: The agent's response to evaluate

    Evaluation Criteria:

    1. Commission/Bonus Calculations:
       - Verifies all required input data is requested
       - Asks for specific sales performance metrics
       - Maintains accuracy in calculation prerequisites

    2. System Access Issues:
       - Requests appropriate user identification
       - Follows security protocols
       - Provides clear next steps

    3. Information Requests:
       - Asks for relevant data only
       - Provides clear guidance
       - Maintains professional tone

    4. Response Quality:
       - Clear and concise communication
       - No contradictory information
       - Appropriate level of detail

    Score as:
    - True: Response fully meets criteria and effectively handles the query
    - False: Response is incomplete, incorrect, or inappropriate"""

    def final_answer_correct(inputs: dict, outputs: dict, reference_outputs: dict) -> Grade:
        """Evaluates if the agent's response is correct using GPT-4"""
        
        user = f"""QUERY: {inputs['question']}
        EXPECTED RESPONSE: {reference_outputs['response']}
        ACTUAL RESPONSE: {outputs['response']}"""

        try:
            # Use client.invoke directly instead of patched version
            response = client.invoke([
                {"role": "system", "content": eval_instructions},
                {"role": "user", "content": user}
            ])
            
            # Extract content from the response
            content = response.content
            
            # Parse the content into our Grade format
            is_correct = "true" in content.lower() or "correct" in content.lower()
            reasoning = content
            
            return Grade(
                reasoning=reasoning,
                is_correct=is_correct
            )
            
        except Exception as e:
            st.error(f"Error in evaluation: {str(e)}")
            return Grade(
                reasoning="Error during evaluation",
                is_correct=False
            )

    # Create button to start evaluation
    if st.button("Start Sales Comp Agent Evaluation"):
        with st.spinner("Evaluating agent responses..."):
            # Initialize evaluation run in LangSmith
            #run = langsmith_client.create_run(
            #    project_name="sales-comp-eval",
            #    name="Sales Comp Agent Evaluation",
            #    inputs={"evaluation": "Sales Compensation Agent"},
            #    run_type="chain",
            #)
            
            # Get test examples from dataset and debug print
            dataset = langsmith_client.read_dataset(dataset_name=dataset_name)
            examples = list(langsmith_client.list_examples(dataset_id=dataset.id))
            st.write("Number of examples found:", len(examples))  # Debug print
            
            # Run evaluation for each test case
            results = []
            for example in examples:
                #st.write("Processing example:", example.inputs)  # Debug print
                try:
                    response = run_graph(example.inputs["question"])
                    eval_result = final_answer_correct(
                        example.inputs,
                        response,
                        example.outputs
                    )
                    
                    result_dict = {
                        "question": example.inputs["question"],
                        "expected": example.outputs["response"],
                        "actual": response["response"],
                        "reasoning": eval_result["reasoning"],
                        "is_correct": eval_result["is_correct"]
                    }
                    
                    #st.write("Result dict:", result_dict)  # Debug print
                    results.append(result_dict)
                except Exception as e:
                    st.error(f"Error processing example: {str(e)}")
                    continue
            
            st.write("All results:", results)
            
            if results:  # Only create DataFrame if we have results
                df = pd.DataFrame(results)
                st.write("DataFrame head:", df.head())
                #st.write("DataFrame columns:", df.columns.tolist())

# Entry point of the script
if __name__ == '__main__':
    eval()