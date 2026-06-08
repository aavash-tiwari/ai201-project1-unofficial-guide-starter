# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

The domain I chose is off-campus housing options for students. I chose this because I am also someone currently dealing with it, and it is difficult for students because they are gonna be staying there for years, so they would not want to select a bad housing option and keep worrying about inconveniences.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
| 1 | eagle_flatts.txt | 4-5 student reviews regarding management and amenities | Compiled from Google Maps & Apartments.com |
| 2 | the_cottages_of_hattiesburg.txt | Student reviews covering neighborhood safety and layout | Compiled from Apartments.com |
| 3 | ivy_row_at_southern_miss.txt | Reviews on proximity to campus and rent pricing | Compiled from Google Maps |
| 4 | cedarwood_apartments.txt | Student feedback on maintenance response times | Compiled from ApartmentRatings.com |
| 5 | the_reserve_at_long_point.txt | Reviews on quietness and study environments | Compiled from Google Maps |
| 6 | hub_city_lofts.txt | Student experiences with downtown living and leasing | Compiled from Google Maps |
| 7 | magnolia_trace.txt | General student reviews regarding utility costs and space | Compiled from Apartments.com |
| 8 | parkwest_apartment_homes.txt | Reviews on parking availability and community safety | Compiled from Google Maps |
| 9 | lexington_apartment_homes.txt | Feedback on move-in conditions and hidden fees | Compiled from ApartmentRatings.com |
| 10| mcmahan_realty.txt | Student reviews concerning local property management behavior | Compiled from Google Maps |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size: 400 characters**

**Overlap: 50 characters**

**Reasoning: Our document corpus consists of short, independent student reviews gathered from Google Maps and housing sites. A large chunk size (like 1,000+ characters) would group multiple completely unrelated reviews from different students together, diluting the specific complaints or praises. A 400-character window is generally the sweet spot for catching one full, detailed student review as a single standalone unit. The 50-character overlap guarantees that if a student makes a vital point at the end of a sentence, it won't be abruptly sliced in half across chunk boundaries.**

---

## Retrieval Approach

**Embedding model: all-MiniLM-L6-v2 via sentence-transformers**

**Top-k: 4**

**Production tradeoff reflection: If cost wasn't a constraint in a real production system, I would weigh upgrading to a premium API model like OpenAI’s text-embedding-3-large. The core tradeoffs would be domain-specific accuracy and context length. Student reviews are highly colloquial, filled with local campus references, abbreviations (like "mgmt" or "maint"), and typos. A commercial model trained on broader web datasets might handle this internet slang more accurately. However, our local all-MiniLM-L6-v2 model benefits from zero latency and no API costs, which is perfect for this application scale.**

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about the maintenance response times at Cedarwood Apartments? | System should retrieve cedarwood_apartments.txt and summarize student feedback on how fast maintenance responds. |
| 2 | Are there any hidden fees or move-in condition complaints mentioned at Lexington Apartment Homes? | System should retrieve lexington_apartment_homes.txt and identify mentions of extra costs or move-in issues. |
| 3 | What are the main complaints regarding management and amenities at Eagle Flatts? | System should retrieve eagle_flatts.txt and state specific problems students have faced with staff or facilities. |
| 4 | How do students describe the safety, parking, and community environment at Parkwest Apartment Homes? | System should retrieve parkwest_apartment_homes.txt and summarize safety or parking availability experiences. |
| 5 | Does Ivy Row at Southern Miss have good proximity to campus and reasonable rent pricing? | System should retrieve ivy_row_at_southern_miss.txt and answer specifically about walkability to campus and cost satisfaction. |

---

## Anticipated Challenges

1. Loss of Entity Context: Because student reviews are short, a student might write "The walls are paper thin and management ignores you" without explicitly typing the name of the apartment complex inside that specific sentence. When chunked, the vector database might fail to connect that chunk to the correct property unless our metadata tracking is perfect.

2. Noisy Text & Typos: Review text compiled from Google Maps is messy, featuring random capitalization, emoji strings, and shorthand text. This noise might cause semantic distance scores to be weaker (higher numbers) when a user searches using proper, formal language.

---

## Architecture

graph TD
    A[Document Ingestion: Local text files] --> B[Cleaning: Strip out boilerplate/extra spaces]
    B --> C[Chunking: Text split into 400 chars, 50 char overlap]
    C --> D[Embedding + Vector Store: all-MiniLM-L6-v2 stored in ChromaDB]
    E[User Query] --> F[Retrieval: Query embedded -> top-k=4 matches fetched]
    D --> F
    F --> G[Generation: LLM llama-3.3-70b-versatile builds grounded answer + citations]

---

## AI Tool Plan

graph TD
    A[Document Ingestion: Local text files] --> B[Cleaning: Strip out boilerplate/extra spaces]
    B --> C[Chunking: Text split into 400 chars, 50 char overlap]
    C --> D[Embedding + Vector Store: all-MiniLM-L6-v2 stored in ChromaDB]
    E[User Query] --> F[Retrieval: Query embedded -> top-k=4 matches fetched]
    D --> F
    F --> G[Generation: LLM llama-3.3-70b-versatile builds grounded answer + citations]

**Milestone 3 — Ingestion and chunking:**
Tool: Claude / ChatGPTInput: The ## Documents list and ## Chunking Strategy section of this file.  Expected Output: A Python script (ingest.py) that reads all 10 files from the /documents folder, cleans white spaces, splits the text into chunks of 400 characters with 50 characters of overlap, and logs the final chunk counts.  Verification: I will write a temporary print statement to look at 3 random text chunks to ensure they are complete thoughts and aren't returning empty strings.

**Milestone 4 — Embedding and retrieval:**
Tool: Claude / ChatGPTInput: My pipeline architecture section and ChromaDB initialization specs.  Expected Output: A retrieval script (retriever.py) using sentence-transformers to turn chunks into vectors, load them into a local ChromaDB collection, and attach the source filename as metadata to every single chunk.  Verification: I will query the database directly in the terminal with "Lexington fees" and print out the results to make sure it only returns chunks labeled with the lexington_apartment_homes.txt metadata.

**Milestone 5 — Generation and interface:**
Tool: Claude / ChatGPTInput: Groq client documentation and the basic Gradio UI layout code.  Expected Output: A file (generator.py or app.py) that feeds the 4 retrieved chunks into llama-3.3-70b-versatile inside a rigid system prompt that forces the model to use only the context notes and explicitly print out its file sources.  Verification: I will test a dummy question like "What is the best food in Hattiesburg?" and confirm that the system correctly refuses to answer or states it does not have that information. 
