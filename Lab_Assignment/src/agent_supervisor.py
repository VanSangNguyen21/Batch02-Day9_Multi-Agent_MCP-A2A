import operator
from typing import Annotated, Any, Dict, List, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
import json

from src.task9_retrieval_pipeline import retrieve
from src.task10_generation import generate_with_citation

# Define state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

# Define tools
@tool("Search_Legal_Docs")
def search_legal_docs(query: str) -> str:
    """Search for Vietnamese legal documents regarding drugs (ma tuý) and illegal substances."""
    # Using task9 retrieval logic for legal docs
    results = retrieve(query + " legal law", top_k=3)
    return json.dumps(results, ensure_ascii=False)

@tool("Search_News")
def search_news(query: str) -> str:
    """Search for news articles related to Vietnamese artists and drugs."""
    # Using task9 retrieval logic for news
    results = retrieve(query + " news artist", top_k=3)
    return json.dumps(results, ensure_ascii=False)

@tool("Generate_Citation")
def generate_citation_answer(query: str) -> str:
    """Generate final answer with citations using retrieved context."""
    # Using task10 generation logic
    res = generate_with_citation(query)
    return res.get("answer", "")

def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)
    return executor

def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [AIMessage(content=result["output"], name=name)]}

def run_supervisor_agent(query: str):
    llm = ChatOpenAI(model="gpt-4o-mini")

    # 1. Create Workers
    legal_agent = create_agent(
        llm, 
        [search_legal_docs], 
        "You are a Legal Researcher. Your role is to find Vietnamese laws regarding drugs. Use your tool to search."
    )
    news_agent = create_agent(
        llm, 
        [search_news], 
        "You are a News Researcher. Your role is to find news about Vietnamese artists involved with drugs. Use your tool to search."
    )
    generator_agent = create_agent(
        llm, 
        [generate_citation_answer], 
        "You are a Generator. Your role is to compile research from Legal and News researchers into a final response with citations."
    )

    # Node wrappers
    def legal_node(state): return agent_node(state, legal_agent, "Legal_Worker")
    def news_node(state): return agent_node(state, news_agent, "News_Worker")
    def generator_node(state): return agent_node(state, generator_agent, "Generator_Worker")

    # 2. Create Supervisor
    members = ["Legal_Worker", "News_Worker", "Generator_Worker"]
    system_prompt = (
        "You are a supervisor managing the following workers: {members}. "
        "Given the user request, decide which worker should act next. "
        "The Legal_Worker handles law-related tasks. "
        "The News_Worker handles artist/news-related tasks. "
        "The Generator_Worker compiles the final output with citations. "
        "When finished, output 'FINISH'."
    )
    options = ["FINISH"] + members
    
    # We use OpenAI function calling to enforce the output
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {"next": {"title": "Next", "anyOf": [{"enum": options}]}},
            "required": ["next"],
        },
    }
    
    supervisor_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Given the conversation above, who should act next? Select one of: {options}")
    ]).partial(options=str(options), members=", ".join(members))

    supervisor_chain = (
        supervisor_prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        | (lambda x: json.loads(x.additional_kwargs["function_call"]["arguments"]))
    )

    # 3. Construct Graph
    workflow = StateGraph(AgentState)
    workflow.add_node("Legal_Worker", legal_node)
    workflow.add_node("News_Worker", news_node)
    workflow.add_node("Generator_Worker", generator_node)
    workflow.add_node("supervisor", supervisor_chain)

    for member in members:
        workflow.add_edge(member, "supervisor")
        
    conditional_map = {k: k for k in members}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
    workflow.set_entry_point("supervisor")

    graph = workflow.compile()
    
    # Run
    for s in graph.stream({
        "messages": [HumanMessage(content=query)]
    }):
        if "__end__" not in s:
            print(s)
            print("----")

if __name__ == "__main__":
    run_supervisor_agent("Tìm hiểu về quy định xử phạt ma tuý và các nghệ sĩ từng vi phạm.")
