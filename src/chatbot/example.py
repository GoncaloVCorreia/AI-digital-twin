import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END, START
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings


os.environ["GOOGLE_API_KEY"] = "AIzaSyCg5X640F9n7O25T8h2_3S3b-lPE6X1Wmg"

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Sample financial documents
financial_docs = [
    Document(
        page_content="""Tesla Q4 2024 Earnings Report:
        Revenue: $25.2B (up 3% YoY)
        Net Income: $2.3B (down 12% YoY)
        Vehicle Deliveries: 484,507 units
        Automotive Gross Margin: 18.9% (down from 23.8% in Q4 2023)
        Energy Storage Deployments: 3.2 GWh (record quarter)
        CEO Commentary: "We are focused on cost reduction and efficiency improvements."
        """,
        metadata={"source": "Tesla 10-K 2024", "date": "2024-12-31", "type": "earnings"}
    ),
    Document(
        page_content="""Federal Reserve Interest Rate Decision - December 2024:
        Federal Funds Rate: 4.25-4.50% (reduced by 25 basis points)
        Dot Plot Median for 2025: 3.75%
        Chair Powell Statement: "Inflation has eased but remains above our 2% target.
        Labor market shows resilience. We will continue data-dependent approach."
        Core PCE Inflation: 2.8% (November 2024)
        Unemployment Rate: 4.1%
        """,
        metadata={"source": "Federal Reserve Press Release", "date": "2024-12-18", "type": "monetary_policy"}
    ),
    Document(
        page_content="""S&P 500 Index Performance 2024:
        Year-end close: 4,783 points (up 24.2% for the year)
        Best performing sectors: Technology (+32%), Communication Services (+28%)
        Worst performing: Energy (-2%), Utilities (+1%)
        Market Cap: $43.7 trillion
        Average P/E Ratio: 19.5x (vs. historical average of 16x)
        Volatility (VIX): Average of 14.2 for the year
        """,
        metadata={"source": "S&P Dow Jones Indices", "date": "2024-12-31", "type": "market_data"}
    ),
    Document(
        page_content="""Apple Inc. Financial Metrics FY2024:
        Revenue: $391.0B (up 2% YoY)
        Services Revenue: $96.2B (up 12% YoY, now 24.6% of total revenue)
        iPhone Revenue: $201.2B (flat YoY)
        Operating Margin: 30.1%
        Cash and Marketable Securities: $162B
        R&D Spending: $31.4B (8.0% of revenue)
        Share Repurchases: $77B during fiscal year
        """,
        metadata={"source": "Apple 10-K FY2024", "date": "2024-09-30", "type": "earnings"}
    ),
    Document(
        page_content="""U.S. GDP Growth Q4 2024 (Advance Estimate):
        Real GDP: +2.3% (annualized)
        Personal Consumption: +2.8%
        Business Investment: +3.1%
        Government Spending: +2.0%
        Net Exports: Contributed -0.6 percentage points
        GDP Deflator: +2.5%
        Economist Consensus: Growth expected to moderate to 1.8% in 2025
        """,
        metadata={"source": "Bureau of Economic Analysis", "date": "2025-01-30", "type": "economic_data"}
    )
]

vectorstore = Chroma.from_documents(
    documents=financial_docs,
    embedding=embeddings,
    collection_name="financial_data"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
print(f"Created financial knowledge base with {len(financial_docs)} documents")

class VerificationState(TypedDict):
    """State for RAG with multi-agent verification."""
    # Input
    query: str

    # Retrieval
    retrieved_docs: list[Document]

    # Generation
    initial_answer: str
    claims: list[str]  # Extracted factual claims

    # Verification
    fact_check_results: list[dict]  # {claim, verified, source}
    citations: list[str]
    contradictions: list[str]
    compliance_status: Literal["pass", "fail", "warning"]
    compliance_issues: list[str]

    # Final output
    final_answer: str
    confidence: float
    
def retrieve_and_generate(state: VerificationState) -> dict:
    """Initial RAG: retrieve and generate answer."""
    query = state["query"]

    # Retrieve relevant documents
    docs = retriever.invoke(query)

    # Build context
    context = "\n\n---\n\n".join([
        f"Source: {doc.metadata['source']} ({doc.metadata['date']})\n{doc.page_content}"
        for doc in docs
    ])

    prompt = f"""You are a financial analyst. Answer this question using the provided data.

Question: {query}

Financial Data:
{context}

Provide a comprehensive answer based on the data. Include specific numbers and metrics."""

    response = llm.invoke(prompt)

    return {
        "retrieved_docs": docs,
        "initial_answer": response.content
    }

def extract_claims(state: VerificationState) -> dict:
    """Extract factual claims from the generated answer."""
    answer = state["initial_answer"]

    prompt = f"""Extract all factual claims from this financial analysis.

Analysis:
{answer}

List each verifiable factual claim separately:
- Financial figures (revenue, earnings, etc.)
- Market data (prices, percentages)
- Economic indicators
- Comparative statements

Format as numbered list. Each claim should be a single, specific fact."""

    response = llm.invoke(prompt)

    # Parse claims (simple line-based parsing)
    lines = response.content.split("\n")
    claims = []
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-")):
            claim = line.split(".", 1)[-1].split("-", 1)[-1].strip()
            if len(claim) > 10:  # Filter out empty/short lines
                claims.append(claim)

    print(f"[EXTRACTION] Found {len(claims)} claims to verify")

    return {"claims": claims[:10]}  # Limit to 10 for demo

def fact_check_claims(state: VerificationState) -> dict:
    """Verify each claim against source documents."""
    claims = state.get("claims", [])
    docs = state.get("retrieved_docs", [])

    # Build source reference
    sources_text = "\n\n".join([
        f"[{doc.metadata['source']}]: {doc.page_content}"
        for doc in docs
    ])

    fact_check_results = []

    for claim in claims:
        prompt = f"""Fact-check this claim against the provided sources.

Claim: "{claim}"

Sources:
{sources_text}

Determine:
1. VERIFIED: Is this claim supported by the sources? (yes/no/partial)
2. SOURCE: Which specific source supports this? (or "none")
3. EXACT_MATCH: Is the number/fact exactly correct? (yes/no/close)

Format:
VERIFIED: [yes/no/partial]
SOURCE: [source name]
EXACT_MATCH: [yes/no/close]
"""

        response = llm.invoke(prompt)
        content = response.content

        # Parse fact-check result
        verified = "no"
        source = "none"
        exact = "no"

        for line in content.split("\n"):
            if line.startswith("VERIFIED:"):
                verified = line.split(":")[1].strip().lower()
            elif line.startswith("SOURCE:"):
                source = line.split(":", 1)[1].strip()
            elif line.startswith("EXACT_MATCH:"):
                exact = line.split(":")[1].strip().lower()

        fact_check_results.append({
            "claim": claim,
            "verified": verified,
            "source": source,
            "exact_match": exact
        })

        print(f"[FACT-CHECK] {claim[:60]}... → {verified}")

    return {"fact_check_results": fact_check_results}

def add_citations(state: VerificationState) -> dict:
    """Add proper citations to the answer."""
    answer = state["initial_answer"]
    fact_checks = state.get("fact_check_results", [])

    # Build citation mapping
    citations = []
    for fc in fact_checks:
        if fc["verified"] in ["yes", "partial"] and fc["source"] != "none":
            if fc["source"] not in citations:
                citations.append(fc["source"])

    # Rebuild answer with citations
    prompt = f"""Add citations to this financial analysis.

Original answer:
{answer}

Available sources: {citations}

Rewrite the answer with superscript citations [1], [2], etc. after each fact.
Then add a "Sources:" section at the end listing the numbered sources."""

    response = llm.invoke(prompt)

    return {
        "citations": citations,
        "final_answer": response.content
    }

def compliance_review(state: VerificationState) -> dict:
    """Check for regulatory compliance issues."""
    answer = state.get("final_answer", state.get("initial_answer", ""))
    fact_checks = state.get("fact_check_results", [])

    # Check 1: Are all claims verified?
    unverified_count = sum(1 for fc in fact_checks if fc["verified"] == "no")

    # Check 2: Are there forward-looking statements without disclaimers?
    has_forward_looking = any(word in answer.lower()
                              for word in ["will", "expect", "forecast", "predict", "likely"])

    has_disclaimer = "past performance" in answer.lower() or "no guarantee" in answer.lower()

    # Determine compliance status
    issues = []

    if unverified_count > 0:
        issues.append(f"{unverified_count} unverified claims detected")

    if has_forward_looking and not has_disclaimer:
        issues.append("Forward-looking statements without required disclaimers")

    if len(answer) < 100:
        issues.append("Answer too brief for investment analysis")

    if not issues:
        status = "pass"
    elif unverified_count > 2 or (has_forward_looking and not has_disclaimer):
        status = "fail"
    else:
        status = "warning"

    print(f"[COMPLIANCE] Status: {status} | Issues: {len(issues)}")

    return {
        "compliance_status": status,
        "compliance_issues": issues
    }

def detect_contradictions(state: VerificationState) -> dict:
    """Detect contradictory information in sources."""
    docs = state.get("retrieved_docs", [])

    if len(docs) < 2:
        return {"contradictions": []}

    # Compare documents for contradictions
    doc_summaries = "\n\n".join([
        f"Document {i+1} ({doc.metadata['source']}):\n{doc.page_content[:300]}"
        for i, doc in enumerate(docs)
    ])

    prompt = f"""Analyze these financial documents for contradictions.

Documents:
{doc_summaries}

Identify any:
1. Conflicting numbers for the same metric
2. Contradictory statements about trends
3. Inconsistent timeframes

List contradictions found, or state "NONE" if consistent."""

    response = llm.invoke(prompt)

    contradictions = []
    if "NONE" not in response.content.upper():
        contradictions = [response.content]

    return {"contradictions": contradictions}

def should_revise(state: VerificationState) -> str:
    """Decide if answer needs revision based on compliance."""
    status = state.get("compliance_status", "pass")

    if status == "fail":
        return "revise"
    else:
        return "complete"

def revise_answer(state: VerificationState) -> dict:
    """Revise answer to address compliance issues."""
    original = state.get("initial_answer", "")
    issues = state.get("compliance_issues", [])
    fact_checks = state.get("fact_check_results", [])

    # Filter to verified claims only
    verified_claims = [fc["claim"] for fc in fact_checks if fc["verified"] == "yes"]

    prompt = f"""Revise this financial analysis to address compliance issues.

Original answer:
{original}

Issues to fix:
{chr(10).join('- ' + issue for issue in issues)}

Verified claims to include:
{chr(10).join('- ' + claim for claim in verified_claims[:5])}

Provide a compliant revision that:
1. Only includes verified facts
2. Adds appropriate disclaimers
3. Uses conservative language
4. Cites sources properly"""

    response = llm.invoke(prompt)

    return {
        "final_answer": response.content,
        "compliance_status": "pass"
    }

def create_verification_workflow():
    workflow = StateGraph(VerificationState)

    # Add all agents
    workflow.add_node("retrieve_generate", retrieve_and_generate)
    workflow.add_node("extract_claims", extract_claims)
    workflow.add_node("fact_check", fact_check_claims)
    workflow.add_node("detect_contradictions", detect_contradictions)
    workflow.add_node("compliance", compliance_review)
    workflow.add_node("citations", add_citations)
    workflow.add_node("revise", revise_answer)

    # Build pipeline
    workflow.add_edge(START, "retrieve_generate")
    workflow.add_edge("retrieve_generate", "extract_claims")
    workflow.add_edge("extract_claims", "fact_check")
    workflow.add_edge("fact_check", "detect_contradictions")
    workflow.add_edge("detect_contradictions", "compliance")

    # Conditional: revise if compliance fails
    workflow.add_conditional_edges(
        "compliance",
        should_revise,
        {
            "revise": "revise",
            "complete": "citations"
        }
    )

    workflow.add_edge("revise", "citations")
    workflow.add_edge("citations", END)

    return workflow.compile()

app = create_verification_workflow()


print("="*80)
print("TESTING MULTI-AGENT VERIFICATION SYSTEM")
print("="*80)

# Test query
result = app.invoke({
    "query": "How did Tesla's profitability change in 2024 compared to the previous year?"
})

print("\n### INITIAL ANSWER ###")
print(result["initial_answer"][:300] + "...")

print(f"\n### CLAIMS EXTRACTED ### ({len(result['claims'])})")
for i, claim in enumerate(result["claims"][:5], 1):
    print(f"{i}. {claim}")

print(f"\n### FACT-CHECK RESULTS ###")
for fc in result["fact_check_results"][:5]:
    status_icon = "✓" if fc["verified"] == "yes" else "✗" if fc["verified"] == "no" else "~"
    print(f"{status_icon} {fc['claim'][:60]}...")
    print(f"   Source: {fc['source']}")

print(f"\n### COMPLIANCE ###")
print(f"Status: {result['compliance_status']}")
if result["compliance_issues"]:
    print("Issues:")
    for issue in result["compliance_issues"]:
        print(f"  - {issue}")

print(f"\n### CONTRADICTIONS ###")
if result["contradictions"]:
    for contradiction in result["contradictions"]:
        print(f"  - {contradiction}")
else:
    print("  None detected")

print(f"\n### FINAL ANSWER (with citations) ###")
print(result["final_answer"])

print("\n" + "="*80)