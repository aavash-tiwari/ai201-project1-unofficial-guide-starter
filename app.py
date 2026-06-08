import os
from dotenv import load_dotenv
from groq import Groq
import gradio as gr
from retriever import retrieve

# This line forces Python to read your .env file!
load_dotenv()

# Initialize the Groq client
client = Groq()

def generate_response(query, retrieved_chunks):
    """Feeds the query and context chunks into Llama 3.3 to get a grounded answer."""
    
    # Format the retrieved text chunks cleanly for the LLM
    context_text = ""
    for idx, chunk in enumerate(retrieved_chunks):
        context_text += f"\nDocument [{idx+1}]: {chunk['source']}\nContent: {chunk['text']}\n"
        context_text += "-"*20 + "\n"

    # CRUCIAL: Our strict grounding system prompt to stop hallucinations
    system_prompt = (
        "You are 'The Unofficial Guide' AI assistant for student housing.\n"
        "Your task is to answer the user's question using ONLY the provided text documents below.\n"
        "Strict Guidelines:\n"
        "1. Grounding: Do not rely on your pre-trained memory or outside knowledge about apartments.\n"
        "2. Out of Scope: If the provided documents do not contain the answer, reply exactly with: "
        "'I do not have enough information in my document database to answer that question.'\n"
        "3. Citations: You must mention the source document name (e.g., source: eagle_flatts.txt) "
        "whenever you state a fact from it."
    )

    user_prompt = f"Context Documents:\n{context_text}\n\nUser Question: {query}"

    try:
        # Request completion from Groq free-tier Llama-3.3-70b
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0 # Force zero temperature for highly deterministic, non-creative facts
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error communicating with LLM API: {str(e)}"

def handle_query(question):
    """Pipeline orchestration: User Question -> Search DB -> LLM Answer"""
    if not question.strip():
        return "Please enter a valid question.", ""
        
    # 1. Fetch top-k relevant chunks from ChromaDB
    chunks = retrieve(question, top_k=4)
    
    # 2. Extract unique source names for the UI metadata box
    sources_set = set([chunk["source"] for chunk in chunks])
    sources_list = "\n".join(f"- {s}" for s in sources_set)
    
    # 3. Generate the final grounded text answer
    answer = generate_response(question, chunks)
    
    return answer, sources_list

# Build the Gradio Web Browser Interface
with gr.Blocks(title="The Unofficial Student Housing Guide") as demo:
    gr.Markdown("# 🏢 The Unofficial Guide: USM Student Housing Assistant")
    gr.Markdown("Ask plain-language questions about local apartments based on peer-generated reviews.")
    
    with gr.Row():
        with gr.Column():
            inp = gr.Textbox(label="Your Question", placeholder="e.g., What are the complaints about Eagle Flatts?")
            btn = gr.Button("Search & Generate", variant="primary")
        
        with gr.Column():
            answer = gr.Textbox(label="Grounded Answer (LLM)", lines=8)
            sources = gr.Textbox(label="Retrieved Source Files (ChromaDB)", lines=3)
            
    # Hook up both clicking the button and pressing Enter in the text box
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    print("Launching Unofficial Guide Gradio Interface...")
    demo.launch()