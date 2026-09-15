from agents import build_research_agent, build_reader_agent, writer_chain, critic_chain 

def run_research_pipeline(topic: str) -> dict:

    state ={}


    #search agent working

    print("\n"+ " ==" *50)
    print("step1: RESEARCH AGENT WORKING..." )
    print(" =" *50)
    

    search_agent = build_research_agent()
    search_result = search_agent.invoke(
        {"messages": [('user', f'Find recent, reliable and detailed information on: {topic}')]}
    )

    state["search_results"] = search_result['messages'][-1].content

    print("\n search result:\n", state["search_results"])

    #reader agent working 

    print("\n"+ "==" *50)
    print("step2:READER AGENT is scraping...")
    print(" ==" *50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke(
        {"messages": [('user',
            f"Based on the following search results about '{topic}', "
            f"pick the most relevent URL and scrap it for deeper content:\n"
            f"{state['search_results'][:800]}")]}
    )
    
    state['scraped_content'] = reader_result['messages'][-1].content

    print('\n scraped content:\n', state['scraped_content'])

    #writer chain
    print("\n"+ "==" *50)
    print("step3:WRITER AGENT is WRITING...")
    print(" ==" *50)

    research_combined = (
        f"SEARCH RESULTS: \n {state['search_results']}"
        f"\n\n SCRAPED CONTENT: \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "facts": research_combined
    })

    print(state["report"])

    #critic report
    print("\n"+ "==" *50)
    print("step4:CRITIC AGENT is REVIEWING...")
    print(" ==" *50)

    state["critique"] = critic_chain.invoke({
        "report": state["report"]
    })

    print(state["critique"])

    return state


if __name__ == "__main__":
    topic = input("\n Enter a Topic: ")
    result = run_research_pipeline(topic)
