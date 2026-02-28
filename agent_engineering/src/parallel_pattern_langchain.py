import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from dotenv import load_dotenv

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

if __name__ == "__main__":
    # ---------------------------------------------------------
    # The Parallelization Pattern (Fan-out / Fan-in) 
    # ---------------------------------------------------------
    
    # 1. FAN-OUT (Parallel Tasks)
    # Task A: Analyze pros of the topic
    pros_prompt = ChatPromptTemplate.from_template("What are the main advantages of {topic}? List 3 points briefly.")
    pros_chain = pros_prompt | llm | StrOutputParser()

    # Task B: Analyze cons of the topic
    cons_prompt = ChatPromptTemplate.from_template("What are the main disadvantages of {topic}? List 3 points briefly.")
    cons_chain = cons_prompt | llm | StrOutputParser()
    
    # Combine them to run concurrently using RunnableParallel
    parallel_analysis = RunnableParallel(
        pros=pros_chain,
        cons=cons_chain
    )
    
    # 2. FAN-IN (Aggregation Task)
    # The final step takes the output of the parallel step (a dict with 'pros' and 'cons')
    summary_prompt = ChatPromptTemplate.from_template(
        "You are an objective reviewer. Based on the following pros and cons, write a short final verdict.\n\n"
        "PROS:\n{pros}\n\n"
        "CONS:\n{cons}\n\n"
        "VERDICT:"
    )
    
    # Combine into the full pipeline
    full_chain = parallel_analysis | summary_prompt | llm | StrOutputParser()
    
    # --- Run the Chain ---
    topic = "remote work"
    print(f"--- Analyzing: {topic} ---")
    
    # The invoke call will run the `pros_chain` and `cons_chain` AT THE SAME TIME.
    final_verdict = full_chain.invoke({"topic": topic})
    
    print("\n--- Final Verdict Output ---")
    print(final_verdict)
