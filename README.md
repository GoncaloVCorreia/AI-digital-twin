## Digital Twin AI with Personas

This project explores the concept of **AI-powered digital twins** through the creation of **interactive personas** that users can interview in natural language.

Each persona represents a distinct individual with:

- Structured personal and professional metadata  
- A **5-year health dataset** collected via **Apple Watch**, stored as **Parquet files**  
- Full **master’s thesis** indexed for retrieval per persona.

The system allows users to conduct conversational interviews with a persona, while the AI agent dynamically selects the appropriate tools to answer each question.

---

## Tool Capabilities

### Health Data Reasoning
The agent can query Parquet-based health datasets to compute insights such as **average steps per year**,  **average calories burned in year X** amoing others.

### Academic RAG
Each persona’s thesis is indexed using **Retrieval-Augmented Generation (RAG)**, enabling the agent to answer detailed questions grounded strictly in the original academic content.

### Developer Profile Awareness
The agent can retrieve and reason over the persona’s **GitHub repositories** by searching their username on the internet, enriching answers with public technical contributions and project context.

---

## AI Architecture

The AI layer is built using:

- **LangChain** for agent orchestration and tool calling  
- **LangGraph** for structured, multi-step agent workflows  
- **Reactive agents** capable of reasoning, tool selection, and context-aware responses  

The system combines **tool-based reasoning**, **RAG pipelines**, and **multi-modal persona memory** to deliver grounded, explainable answers.

---

## Tech Stack

- **Frontend**: React  
- **Backend**: FastAPI  
- **AI / Agents**: LangChain, LangGraph, Langsmith (for observation)
- **Data**: Parquet (health data), vector stores for RAG  
- **Deployment**: Railway  

