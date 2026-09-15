from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrap_url
from dotenv import load_dotenv
import os

load_dotenv()

#model setup

llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    api_key=os.getenv("GEMINI_API_KEY"),
)

#1st agent

def build_research_agent():
    return create_agent(
        model = llm,
        tools = [web_search]
    )

#2nd agent

def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrap_url]
    )
    
#writer chain

writer_prompt = ChatPromptTemplate.from_messages(
    [('system', 'You are a expert research writer. Write clear, structured and insightful reports from the facts collected by the research agent. Make sure to credit sources and avoid plagiarism'),
    ('human', """write a detailed research report on the topic below.
    
    Topic: {topic}
    Facts Collected: {facts}

    structure the report as:
    -INTRODUCTION
    -KEY FINDINGS (minimum 3 well explained points)
    -CONCLUSION
    -DATA CITATIONS

    Be detailed, factual and professional.
    
    """)
    ])

writer_chain  = writer_prompt | llm | StrOutputParser()

#critic chain 

critic_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', 'You are a critical editor. Review the following report and provide constructive feedback to improve clarity, flow, and depth of research. Be honest and specific'),
        ('human', """Review the research report below and evaluate unbiased and strictly.
        
        Report: {report}
        
        Respond in exact format:
        Critique Score:
        
         (1-10) 
        
        Strengths:
        - ...
        - ...

        Areas of Improvement: 
        - ...
        - ...

        Final Verdict: 
        ONE LINE VERDICT

        """)
    ]
)

critic_chain =critic_prompt | llm | StrOutputParser()


