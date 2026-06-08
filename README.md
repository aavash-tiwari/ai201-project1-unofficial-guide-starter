# The Unofficial Guide — Project 1

---

## Domain

The Unofficial Guide covers student-generated reviews, neighborhood safety opinions, and unofficial advice for off-campus apartment complexes near The University of Southern Mississippi in Hattiesburg. This knowledge is highly valuable because official leasing websites use polished marketing to hide systemic issues like maintenance backlogs, unresponsive property managers, and hidden move-in fees. Authentic peer reviews are scattered across disparate web threads and map locations, making them difficult to look up without a semantic RAG pipeline.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | cedarwood_apartments.txt | Review Compilation | documents/cedarwood_apartments.txt |
| 2 | eagle_flatts.txt | Review Compilation | documents/eagle_flatts.txt |
| 3 | hub_city_lofts.txt | Review Compilation | documents/hub_city_lofts.txt |
| 4 | ivy_row_at_southern_miss.txt | Review Compilation | documents/ivy_row_at_southern_miss.txt |
| 5 | lexington_apartment_homes.txt | Review Compilation | documents/lexington_apartment_homes.txt |
| 6 | magnolia_trace.txt | Review Compilation | documents/magnolia_trace.txt |
| 7 | mcmahan_realty.txt | Review Compilation | documents/mcmahan_realty.txt |
| 8 | parkwest_apartment_homes.txt | Review Compilation | documents/parkwest_apartment_homes.txt |
| 9 | the_cottages_of_hattiesburg.txt | Review Compilation | documents/the_cottages_of_hattiesburg.txt |
| 10 | the_reserve_at_long_point.txt | Review Compilation | documents/the_reserve_at_long_point.txt |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** Our corpus consists of brief, anecdotal student reviews (typically 2–5 sentences per review). A massive chunk size would pack multiple completely unrelated student opinions into one vector, causing specific details to get lost. The 400-character window ensures each independent student review stays intact as its own standalone context unit. The 50-character sliding overlap acts as insurance, guaranteeing that sentences near boundaries are duplicated instead of mechanically sliced in half. Before chunking, we ran custom whitespace collapsing to prevent unreadable formatting.

**Sample Chunks**
1. **Source: eagle_flatts.txt** - "Overall, its a great place. It is very quiet and clean. I love the size of the apartments. Maintenance is great and very polite. The people at the front desk are very helpful with questions."
2. **Source: hub_city_lofts.txt** - "I am loving my studio loft apartment in the Carter Building in downtown Hattiesburg! The staff is awesome (management and maintenance alike), they have been great!"
3. **Source: the_reserve_at_long_point.txt** - "Been living here a while and I’ve loved it! Maintenance responds fast, especially with emergencies! The office is filled with great people and they always do their best..."
4. **Source: ivy_row_at_southern_miss.txt** - "Ivy Row is such a wonderful place to live. It has so many amenities to cater to the students such as gym, pool, and even a study room with printing."
5. **Source: lexington_apartment_homes.txt** - "I had a wonderful experience living here! The apartments are very nice—clean, well-maintained, and modern. The location is super convenient, close to everything I needed."

**Final chunk count:** 54 chunks across all 10 files.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via the `sentence-transformers` library

**Production tradeoff reflection:** If deploying this for thousands of production users with zero budget constraints, I would look into an enterprise API model like OpenAI’s `text-embedding-3-large`. A primary tradeoff is handling **domain-specific accuracy on noisy text**. Casual student reviews are loaded with local slang, campus nicknames, abbreviations (e.g., "maint", "mgmt"), and typos. Commercial models trained on wider web text can offer better contextual accuracy for slang. However, utilizing `all-MiniLM-L6-v2` locally gives us **zero hosting costs** and **sub-millisecond latency**, making it an excellent development baseline.

---

## Grounded Generation

**System prompt grounding instruction:** ```text
You are 'The Unofficial Guide' AI assistant for student housing.
Your task is to answer the user's question using ONLY the provided text documents below.
Strict Guidelines:
1. Grounding: Do not rely on your pre-trained memory or outside knowledge about apartments.
2. Out of Scope: If the provided documents do not contain the answer, reply exactly with: 'I do not have enough information in my document database to answer that question.'
3. Citations: You must mention the source document name (e.g., source: eagle_flatts.txt) whenever you state a fact from it.

**How source attribution is surfaced in the response:**
Source attribution is multi-layered. First, the LLM is strictly instructed via the system prompt to explicitly inline the document name whenever it quotes a fact. Second, the underlying Python pipeline in app.py extracts the unique collection metadata (chunk["source"]) returned by ChromaDB and programmatically appends it to a dedicated text field right next to the answer in the Gradio web UI.

**Query Interface & Example Transcripts**
**Interface Description:** The Gradio UI consists of a Textbox input for the user's question and a primary "Search & Generate" submit button. The outputs are two Textboxes: one displaying the LLM's grounded answer and another displaying the raw ChromaDB source filenames to prove retrieval.

**Example Response 1 (Showing Attribution):**
*Query:* What are the main complaints regarding management and amenities at Eagle Flatts?
*Output:* "The main complaint regarding management and amenities at Eagle Flatts is that the staff can be unfriendly at times, and the walkways in the apartment buildings need to be power washed... (source: eagle_flatts.txt)"

**Example Response 2 (Showing Relevance):**
*Query:* Are there any hidden fees or move-in condition complaints mentioned at Lexington Apartment Homes?
*Returned Chunks:* [magnolia_trace.txt, mcmahan_realty.txt, parkwest_apartment_homes.txt]
*Relevance Explanation:* These chunks are completely off-target because the retriever failed to find Lexington chunks, pulling other apartments instead. Consequently, the LLM safely output: "I do not have enough information in my document database to answer that question."

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about the maintenance response times at Cedarwood Apartments? | Summary of response speeds at Cedarwood. | System correctly refused to answer ("I do not have enough information...") because retrieval missed the Cedarwood document. | Off-target | Accurate (Grounded refusal) |
| 2 | Are there any hidden fees or move-in condition complaints mentioned at Lexington Apartment Homes? | Specific details regarding Lexington's fees or conditions. | System correctly refused to answer ("I do not have enough information...") because retrieval pulled Magnolia Trace and Parkwest instead. | Off-target | Accurate (Grounded refusal) |
| 3 | What are the main complaints regarding management and amenities at Eagle Flatts? | Overview of issues at Eagle Flatts. | Accurately summarized complaints about unfriendly staff and walkways needing power washing, properly citing `eagle_flatts.txt`. | Relevant | Accurate |
| 4 | How do students describe the safety, parking, and community environment at Parkwest Apartment Homes? | Analysis of safety and parking at Parkwest. | Summarized great community events and an unspecified safety incident, but noted missing parking info for Parkwest and erroneously referenced parking at The Reserve instead. | Partially relevant | Partially accurate |
| 5 | Does Ivy Row at Southern Miss have good proximity to campus and reasonable rent pricing? | Evaluation of Ivy Row walking distance and price. | System correctly refused to answer ("I do not have enough information...") because retrieval missed the Ivy Row document entirely. | Off-target | Accurate (Grounded refusal) |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** What do students say about the maintenance response times at Cedarwood Apartments?

**What the system returned:** "I do not have enough information in my document database to answer that question."

**Root cause (tied to a specific pipeline stage):** This is a **Retrieval Stage Failure**. The embedding model (`all-MiniLM-L6-v2`) failed to match the semantic meaning of the user's query to the actual `cedarwood_apartments.txt` chunks, pulling chunks from Parkwest and The Reserve instead. Because the correct context was completely missing from the retrieved payload, the LLM correctly followed its strict system prompt instructions and refused to hallucinate an answer. 

**What you would change to fix it:** To resolve this retrieval failure, I would modify the document ingestion pipeline to explicitly prepend the apartment's name to the beginning of every single text chunk (e.g., adding *"Apartment: Cedarwood - "* before the review text) before creating the vector embeddings. This guarantees the entity name is strongly represented in the mathematical vector space, or I would implement hard metadata filtering so users can select the apartment from a dropdown before searching.

---

## Spec Reflection

**One way the spec helped you during implementation:**
Writing out the explicit character counts and the pipeline architecture diagram in planning.md made writing the ingest.py sliding window function straightforward. It gave me a distinct, predictable format to check my data against when inspecting my text arrays.

**One way your implementation diverged from the spec, and why:**
My implementation diverged when setting up the .env configuration file. Windows environment configurations caused pathing issues with loading the keys automatically, so I overrode the spec and initialized the Groq() client by passing the API key directly into app.py to ensure the application could build and run successfully before the deadline.

---

## AI Usage

Instance 1

What I gave the AI: The ## Documents list and ## Chunking Strategy rules from my spec.

What it produced: A baseline template for ingest.py that handles looping files and mechanical character slicing.

What I changed or overrode: I overrode the loop structures to incorporate metadata fields mapping to the generic skeleton specifications, adjusting edge cases to make sure tiny text fragments didn't break bounds.

Instance 2

What I gave the AI: The nested payload specification format of ChromaDB queries.

What it produced: A retrieval function targeting results["documents"] directly.

What I changed or overrode: I corrected the indexing logic because _collection.query() outputs lists nested inside arrays (batch data). I hardcoded index [0] to safely pull the specific strings for our single query application.
