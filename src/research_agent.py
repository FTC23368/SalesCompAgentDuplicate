from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.create_llm_message import create_llm_msg
from langchain_core.messages import BaseMessage
import json

# When ResearchAgent object is created, it's initialized with a client and a model. 
# The main entry point is the research_agent_agent method. 
# Note: You will have to add the nodes and edges for this sub-agent node in graph.py

class ResearchPlan(BaseModel):
    """Data model for the research plan structure."""
    sections: List[Dict[str, Any]] = Field(
        description="List of sections with titles and descriptions",
        default_factory=list
    )
    main_sections: List[str] = Field(
        description="List of main section titles that require research",
        default_factory=list
    )
    final_sections: List[str] = Field(
        description="List of final sections like intro/conclusion to write after research",
        default_factory=list
    )
    
    class Config:
        schema_extra = {
            "required": ["sections", "main_sections", "final_sections"]
        }


class ResearchSection(BaseModel):
    """Data model for a completed research section."""
    title: str = Field(description="Section title")
    content: str = Field(description="Section content")
    follow_up_questions: List[str] = Field(description="Follow-up questions for further research")


class ResearchAgent:
    """
    A class to handle comprehensive research on sales compensation topics.
    This agent generates detailed reports following a structured workflow with customizable parameters.
    """
    
    def __init__(self, client, model, search_api=None, planner_model=None, report_writer_model=None):
        """
        Initialize the ResearchAgent with necessary components.

        Args:
            client: The OpenAI client for API interactions.
            model: The default language model to use.
            search_api: The search API to use (Tavily, Perplexity, etc.)
            planner_model: Specific model for planning (defaults to main model if None)
            report_writer_model: Specific model for final report writing (defaults to main model if None)
        """
        self.client = client
        self.model = model
        self.search_api = search_api
        self.planner_model = planner_model or model
        self.report_writer_model = report_writer_model or model
        self.research_depth = 2  # Default research depth (iterations)
        self.searches_per_iteration = 3  # Default searches per iteration

    def set_research_parameters(self, research_depth: int = 2, searches_per_iteration: int = 3):
        """
        Set the research parameters.

        Args:
            research_depth: Number of iterations for each section research
            searches_per_iteration: Number of searches to run per iteration
        """
        self.research_depth = research_depth
        self.searches_per_iteration = searches_per_iteration

    def generate_research_plan(self, topic: str, messageHistory: [BaseMessage]) -> ResearchPlan:
        """
        Generate a structured research plan for the given topic.

        Args:
            topic: The research topic to create a plan for

        Returns:
            ResearchPlan: A structured plan with sections
        """
        planning_prompt = f"""
        You are an expert research planner specializing in sales compensation topics.
        
        Create a comprehensive research plan for the topic: "{topic}"
        
        Your task is to:
        1. Break down this topic into logical sections for a comprehensive report
        2. For each section, provide a brief description of what should be covered
        3. Identify which sections are "main sections" requiring research
        4. Identify which sections are "final sections" (like introduction, conclusion) to be written after research
        
        Format your response as a JSON object with the following structure:
        {{
            "sections": [
                {{"title": "Section Title", "description": "What this section should cover"}},
                ...
            ],
            "main_sections": ["Title of main section 1", "Title of main section 2", ...],
            "final_sections": ["Introduction", "Conclusion", ...]
        }}
        """

        llm_messages = create_llm_msg(planning_prompt, messageHistory)
        response = self.planner_model.invoke(llm_messages)
        
        # Parse the JSON response manually
        try:
            # Extract JSON from the response
            json_str = response.content
            # If the response contains markdown code blocks, extract the JSON
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            plan_data = json.loads(json_str)
            return ResearchPlan(
                sections=plan_data.get("sections", []),
                main_sections=plan_data.get("main_sections", []),
                final_sections=plan_data.get("final_sections", [])
            )
        except Exception as e:
            # Fallback to a basic plan if parsing fails
            print(f"Error parsing research plan: {e}")
            return ResearchPlan(
                sections=[{"title": "Overview", "description": f"General overview of {topic}"}],
                main_sections=["Overview"],
                final_sections=["Introduction", "Conclusion"]
            )

    def retrieve_documents(self, query: str, num_searches: int = 3) -> List[str]:
        """
        Retrieve relevant documents based on the query using the configured search API.

        Args:
            query: The search query
            num_searches: Number of search results to retrieve

        Returns:
            List[str]: Retrieved content from search
        """
        # This is a placeholder. In a real implementation, you would:
        # 1. Call your search API (Tavily, Perplexity, etc.)
        # 2. Process and return the results
        
        if self.search_api is None:
            # Mock response for demonstration
            return [
                f"Search result 1 for query: {query}",
                f"Search result 2 for query: {query}",
                f"Search result 3 for query: {query}"
            ][:num_searches]
        
        # Example implementation with a search API:
        # return self.search_api.search(query, num_results=num_searches)

    def research_section(self, section_title: str, section_description: str, topic: str, 
                         messageHistory: list[BaseMessage], depth: int = None) -> ResearchSection:
        """
        Research a specific section through multiple iterations of writing, reflection, and search.

        Args:
            section_title: Title of the section
            section_description: Description of what the section should cover
            topic: The overall research topic
            depth: Number of research iterations (defaults to self.research_depth)

        Returns:
            ResearchSection: The completed section with content and follow-up questions
        """
        if depth is None:
            depth = self.research_depth
            
        current_content = ""
        follow_up_questions = [
            f"What are the key aspects of {section_title} in relation to {topic}?",
            f"What are best practices for {section_title}?",
            f"What are common challenges with {section_title}?"
        ]
        
        # Iterative research process
        for iteration in range(depth):
            # Gather information through search
            search_results = []
            for question in follow_up_questions[:self.searches_per_iteration]:
                search_results.extend(self.retrieve_documents(question))
            
            # Combine all search results
            combined_search_results = "\n\n".join(search_results)
            
            # Generate or refine content based on search results
            research_prompt = f"""
            You are researching the topic: "{topic}" 
            Specifically focusing on the section: "{section_title}"
            Section description: {section_description}
            
            Current draft content: {current_content if current_content else "No content yet."}
            
            New information from research:
            {combined_search_results}
            
            Based on this information, write or improve the content for this section.
            Provide a comprehensive, well-structured section that incorporates both existing content and new information.
            
            Then, suggest 3-5 follow-up questions that would help deepen or expand this research further.
            """
            
            llm_messages = create_llm_msg(research_prompt, messageHistory)
            
            # Use structured output to get both content and follow-up questions
            section_response = self.model.with_structured_output(ResearchSection).invoke(llm_messages)
            
            # Update for next iteration
            current_content = section_response.content
            follow_up_questions = section_response.follow_up_questions
        
        return ResearchSection(
            title=section_title,
            content=current_content,
            follow_up_questions=follow_up_questions
        )

    def write_final_section(self, section_title: str, section_description: str, 
                           completed_sections: List[ResearchSection], topic: str, messageHistory: list[BaseMessage]) -> str:
        """
        Write a final section (like intro or conclusion) based on completed research.

        Args:
            section_title: Title of the section to write
            section_description: Description of what the section should cover
            completed_sections: List of already completed research sections
            topic: The overall research topic

        Returns:
            str: The content for the final section
        """
        # Extract section titles and summaries for context
        section_summaries = "\n\n".join([
            f"Section: {section.title}\nSummary: {section.content[:200]}..." 
            for section in completed_sections
        ])
        
        final_section_prompt = f"""
        You are writing the {section_title} for a comprehensive research report on "{topic}".
        
        Section description: {section_description}
        
        The report contains the following sections:
        {section_summaries}
        
        Write a compelling {section_title} that:
        1. Appropriately introduces/concludes the topic based on the research
        2. Ties together the main themes from the research
        3. Is professional, clear, and engaging
        4. Is appropriate for a business audience interested in sales compensation
        """
        
        llm_messages = create_llm_msg(final_section_prompt, messageHistory)
        response = self.report_writer_model.invoke(llm_messages)
        
        # Extract content from response
        return response.content

    def compile_final_report(self, sections: List[Dict[str, str]]) -> str:
        """
        Compile all sections into a final formatted report.

        Args:
            sections: List of dictionaries with section titles and content

        Returns:
            str: The complete formatted report
        """
        report_parts = []
        
        for section in sections:
            report_parts.append(f"# {section['title']}\n\n{section['content']}\n\n")
        
        return "\n".join(report_parts)

    def research_agent(self, state: dict) -> dict:
        """
        Process the user's request and generate a comprehensive research report.

        Args:
            state (dict): The current state of the conversation, including the initial message.

        Returns:
            dict: An updated state dictionary with the generated report.
        """
        topic = state.get('initialMessage', '')
        
        # Extract customization parameters if provided
        research_depth = state.get('researchDepth', self.research_depth)
        searches_per_iteration = state.get('searchesPerIteration', self.searches_per_iteration)
        
        # Set research parameters
        self.set_research_parameters(research_depth, searches_per_iteration)
        
        # Generate research plan
        research_plan = self.generate_research_plan(topic, state['message_history'])
        
        # For a real implementation, you would get user feedback on the plan here
        # and potentially revise it based on feedback
        
        # Research main sections
        completed_sections = []
        for section_title in research_plan.main_sections:
            # Find section description
            section_description = next(
                (s["description"] for s in research_plan.sections if s["title"] == section_title), 
                f"Research about {section_title}"
            )
            
            # Research this section
            section = self.research_section(
                section_title=section_title,
                section_description=section_description,
                topic=topic,
                depth=research_depth,
                messageHistory=state['message_history']
            )
            
            completed_sections.append(section)
        
        # Write final sections (intro, conclusion, etc.)
        final_sections = []
        for section_title in research_plan.final_sections:
            # Find section description
            section_description = next(
                (s["description"] for s in research_plan.sections if s["title"] == section_title), 
                f"Write {section_title}"
            )
            
            # Write this final section based on completed research
            content = self.write_final_section(
                section_title=section_title,
                section_description=section_description,
                completed_sections=completed_sections,
                topic=topic,
                messageHistory=state['message_history']
            )
            
            final_sections.append({"title": section_title, "content": content})
        
        # Organize all sections in the correct order
        all_sections = []
        
        # Add sections in the order specified in the plan
        for section_info in research_plan.sections:
            section_title = section_info["title"]
            
            if section_title in research_plan.final_sections:
                # Add from final sections
                matching_section = next((s for s in final_sections if s["title"] == section_title), None)
                if matching_section:
                    all_sections.append(matching_section)
            else:
                # Add from main sections
                matching_section = next((s for s in completed_sections if s.title == section_title), None)
                if matching_section:
                    all_sections.append({"title": matching_section.title, "content": matching_section.content})
        
        # Compile the final report
        final_report = self.compile_final_report(all_sections)
        
        # Return the updated state with the generated report
        return {
            "lnode": "research_agent", 
            "responseToUser": final_report,
            "category": "research"
        }
