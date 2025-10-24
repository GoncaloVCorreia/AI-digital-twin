import os, json, requests
from collections import Counter
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
import duckdb
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import duckdb
from datetime import datetime
from pathlib import Path
from typing import Union, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever

def _connect(path:str) -> duckdb.DuckDBPyConnection:
    """Create an in-memory DuckDB connection and expose a 'health' view over all parquet files."""
    con = duckdb.connect(database=":memory:")
    con.execute(f"""
        CREATE OR REPLACE VIEW health AS
        SELECT * FROM read_parquet('{Path(path)}/**/*.parquet', filename=true);
    """)
    return con

def _parse_dt(x: Union[str, datetime]) -> datetime:
    """Parse ISO date string or passthrough datetime to a datetime object."""
    if isinstance(x, datetime):
        return x
    return datetime.fromisoformat(str(x))

@tool
def get_date() -> str:
    """
    Tool that returns the current date in ISO format (YYYY-MM-DD).
    """
    return datetime.utcnow().date().isoformat()

# ---- 1) Total calories in period (and split) ----
@tool
def calories_burned(path:str, start_date: Union[str, datetime], end_date: Union[str, datetime]) -> Dict[str, float]:
    """
    Tool that returns total, active, and basal calories burned within a period.

    Args:
        path: path to health parquet data
        start_date: inclusive lower bound (ISO date string or datetime)
        end_date:   exclusive upper bound (ISO date string or datetime)

    Returns:
        Dict[str, float]: {
            "total_calories_kcal": float,
            "active_calories_kcal": float,
            "basal_calories_kcal": float
        }
    """
    start_ts = _parse_dt(start_date); end_ts = _parse_dt(end_date)
    con = _connect(path)
    q = """
    SELECT
      SUM(CASE WHEN "@type" IN (
            'HKQuantityTypeIdentifierActiveEnergyBurned',
            'HKQuantityTypeIdentifierBasalEnergyBurned'
          ) THEN CAST("@value" AS DOUBLE) ELSE 0 END) AS total_calories,
      SUM(CASE WHEN "@type"='HKQuantityTypeIdentifierActiveEnergyBurned'
               THEN CAST("@value" AS DOUBLE) ELSE 0 END) AS active_calories,
      SUM(CASE WHEN "@type"='HKQuantityTypeIdentifierBasalEnergyBurned'
               THEN CAST("@value" AS DOUBLE) ELSE 0 END) AS basal_calories
    FROM health
    WHERE "@startDate" >= ? AND "@startDate" < ?
    """
    row = con.execute(q, [start_ts, end_ts]).fetchone()
    con.close()
    return {
        "total_calories_kcal": float(row[0] or 0.0),
        "active_calories_kcal": float(row[1] or 0.0),
        "basal_calories_kcal": float(row[2] or 0.0),
    }


# ---- 1b) Average calories per day in period ----
@tool
def average_calories_per_day(path:str, start_date: Union[str, datetime], end_date: Union[str, datetime]) -> float:
    """
    Tool that returns the average calories per day (active + basal) within a period.

    Args:
        path: path to health parquet data
        start_date: inclusive lower bound (ISO string or datetime)
        end_date:   exclusive upper bound (ISO string or datetime)

    Returns:
        float: average kcal per day
    """
    start_ts = _parse_dt(start_date); end_ts = _parse_dt(end_date)
    con = _connect(path)
    q = """
    WITH daily AS (
      SELECT
        date_trunc('day', "@startDate") AS day,
        SUM(CASE WHEN "@type" IN (
            'HKQuantityTypeIdentifierActiveEnergyBurned',
            'HKQuantityTypeIdentifierBasalEnergyBurned'
        ) THEN CAST("@value" AS DOUBLE) ELSE 0 END) AS calories
      FROM health
      WHERE "@startDate" >= ? AND "@startDate" < ?
      GROUP BY 1
    )
    SELECT AVG(calories) FROM daily
    """
    row = con.execute(q, [start_ts, end_ts]).fetchone()
    con.close()
    return float(row[0] or 0.0)


# ---- 2) Max calories day in period ----
@tool
def max_daily_calories(path:str, start_date: Union[str, datetime], end_date: Union[str, datetime]) -> Dict[str, Any]:
    """
    Tool that returns the day with the maximum total calories (active + basal) and its value.

    Args:
        path: path to health parquet data
        start_date: inclusive lower bound (ISO string or datetime)
        end_date:   exclusive upper bound (ISO string or datetime)

    Returns:
        Dict[str, Any]: {"day": datetime | None, "calories_kcal": float}
    """
    start_ts = _parse_dt(start_date); end_ts = _parse_dt(end_date)
    con = _connect(path)
    q = """
    WITH daily AS (
      SELECT
        date_trunc('day', "@startDate") AS day,
        SUM(CASE WHEN "@type" IN (
              'HKQuantityTypeIdentifierActiveEnergyBurned',
              'HKQuantityTypeIdentifierBasalEnergyBurned'
            ) THEN CAST("@value" AS DOUBLE) ELSE 0 END) AS calories
      FROM health
      WHERE "@startDate" >= ? AND "@startDate" < ?
      GROUP BY 1
    )
    SELECT day, calories
    FROM daily
    ORDER BY calories DESC
    LIMIT 1
    """
    row = con.execute(q, [start_ts, end_ts]).fetchone()
    con.close()
    if not row:
        return {"day": None, "calories_kcal": 0.0}
    return {"day": row[0], "calories_kcal": float(row[1] or 0.0)}


# ---- 3) Longest run day in period ----
@tool
def longest_run(path:str, start_date: Union[str, datetime], end_date: Union[str, datetime]) -> Dict[str, Any]:
    """
    Tool that returns the day with the longest total walking/running distance (km).

    Notes:
        - Uses 'HKQuantityTypeIdentifierDistanceWalkingRunning'
        - Converts meters to km when needed and sums per day.

    Args:
        path: path to health parquet data
        start_date: inclusive lower bound (ISO string or datetime)
        end_date:   exclusive upper bound (ISO string or datetime)

    Returns:
        Dict[str, Any]: {"day": datetime | None, "distance_km": float}
    """
    start_ts = _parse_dt(start_date); end_ts = _parse_dt(end_date)
    con = _connect(path)
    q = """
    WITH runs AS (
      SELECT
        date_trunc('day', "@startDate") AS day,
        CASE
          WHEN "@type"='HKQuantityTypeIdentifierDistanceWalkingRunning' AND "@unit"='m'
            THEN CAST("@value" AS DOUBLE)/1000.0
          WHEN "@type"='HKQuantityTypeIdentifierDistanceWalkingRunning' AND "@unit"='km'
            THEN CAST("@value" AS DOUBLE)
          ELSE NULL
        END AS km
      FROM health
      WHERE "@startDate" >= ? AND "@startDate" < ?
    ),
    daily AS (
      SELECT day, SUM(km) AS day_km
      FROM runs
      WHERE km IS NOT NULL
      GROUP BY 1
    )
    SELECT day, day_km
    FROM daily
    ORDER BY day_km DESC
    LIMIT 1
    """
    row = con.execute(q, [start_ts, end_ts]).fetchone()
    con.close()
    if not row:
        return {"day": None, "distance_km": 0.0}
    return {"day": row[0], "distance_km": float(row[1] or 0.0)}


# ---- 4) Average steps per day ----
@tool
def average_steps_per_day(path:str, start_date: Union[str, datetime], end_date: Union[str, datetime]) -> float:
    """
    Tool that returns the average number of steps per day in a period.

    Args:
        path: path to health parquet data
        start_date: inclusive lower bound (ISO string or datetime)
        end_date:   exclusive upper bound (ISO string or datetime)

    Returns:
        float: average daily steps
    """
    start_ts = _parse_dt(start_date); end_ts = _parse_dt(end_date)
    con = _connect(path)
    q = """
    WITH daily AS (
      SELECT
        date_trunc('day', "@startDate") AS day,
        SUM(CASE WHEN "@type"='HKQuantityTypeIdentifierStepCount'
                 THEN CAST("@value" AS DOUBLE) ELSE 0 END) AS steps
      FROM health
      WHERE "@startDate" >= ? AND "@startDate" < ?
      GROUP BY 1
    )
    SELECT AVG(steps) AS avg_steps
    FROM daily
    """
    row = con.execute(q, [start_ts, end_ts]).fetchone()
    con.close()
    return float(row[0] or 0.0)


# ---- 4b) Day with max steps ----
@tool
def max_steps_day(path:str, start_date: Union[str, datetime], end_date: Union[str, datetime]) -> Dict[str, Any]:
    """
    Tool that returns the day with the maximum total steps and the step count.

    Args:
        path: path to health parquet data
        start_date: inclusive lower bound (ISO string or datetime)
        end_date:   exclusive upper bound (ISO string or datetime)

    Returns:
        Dict[str, Any]: {"day": datetime | None, "steps": int}
    """
    start_ts = _parse_dt(start_date); end_ts = _parse_dt(end_date)
    con = _connect(path)
    q = """
    WITH daily AS (
      SELECT
        date_trunc('day', "@startDate") AS day,
        SUM(CASE WHEN "@type"='HKQuantityTypeIdentifierStepCount'
                 THEN CAST("@value" AS DOUBLE) ELSE 0 END) AS steps
      FROM health
      WHERE "@startDate" >= ? AND "@startDate" < ?
      GROUP BY 1
    )
    SELECT day, steps
    FROM daily
    ORDER BY steps DESC
    LIMIT 1
    """
    row = con.execute(q, [start_ts, end_ts]).fetchone()
    con.close()
    if not row:
        return {"day": None, "steps": 0}
    return {"day": row[0], "steps": int(row[1] or 0)}

@tool
def get_user_repo_summary(username: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool that returns a GitHub user repository summary.
    Args:
      - username: GitHub username (required)
      - token: Optional GitHub token for higher rate limits (not required)

    Return  Dict[str, Any] summary for a GitHub user:
      - repo_count (public)
      - repos: [{name, description, language, html_url}]
      - top_languages: [{language, count, percent}]
    """
    s = requests.Session()
    s.headers.update({"Accept": "application/vnd.github+json"})
    if token:
        s.headers.update({"Authorization": f"Bearer {token}"})

    # 1) Verify user exists
    u = s.get(f"https://api.github.com/users/{username}", timeout=15)
    if u.status_code == 404:
        raise ValueError(f"GitHub user '{username}' not found")
    u.raise_for_status()

    # 2) Fetch all public repos (paginate)
    repos: List[Dict[str, Any]] = []
    page = 1
    while True:
        r = s.get(
            f"https://api.github.com/users/{username}/repos",
            params={"per_page": 100, "page": page, "type": "public", "sort": "updated"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        for repo in data:
            repos.append({
                "name": repo["name"],
                "description": repo.get("description") or "",
                "language": repo.get("language"),
                "html_url": repo["html_url"],
                "stars": repo.get("stargazers_count", 0),
                "updated_at": repo.get("updated_at"),
            })
        if "next" not in (r.links or {}):
            break
        page += 1

    # 2b) Deduplicate by html_url (defensive)
    seen = set()
    deduped: List[Dict[str, Any]] = []
    for r in repos:
        if r["html_url"] in seen:
            continue
        seen.add(r["html_url"])
        deduped.append(r)

    # Stable sort: stars desc, then name asc
    deduped.sort(key=lambda x: (-x["stars"], x["name"].lower()))

    # 3) Top languages by primary language across repos
    lang_counts = Counter(r["language"] for r in deduped if r["language"])
    total = sum(lang_counts.values()) or 1
    top_languages = [
        {"language": lang, "count": cnt, "percent": round(100 * cnt / total, 2)}
        for lang, cnt in lang_counts.most_common()
    ]

    # keep only requested fields in repos
    repos_min = [
        {k: r[k] for k in ("name", "description", "language", "html_url")}
        for r in deduped
    ]

    return {
        "user": username,
        "repo_count": len(repos_min),
        "repos": repos_min,
        "top_languages": top_languages,
    }

@tool
def query_knowledge_base_thesis(
    path: str = None,
    collection_name: str =None,
    query: str ="",
) -> List[str]:
    """
    Tool that gives information about the thesis of the user by querying a knowledge base.
    Tool that performs hybrid retrieval (BM25 + dense vector search) on a Chroma collection.
    
    Args:
        path: path to the Chroma persist directory
        collection_name: name of the collection to query
        query: what user wants to know about the thesis
    
    Returns:
        List[str]: list of document contents (page_content from each result)
    """
    if path is None:
        path ="./chroma_data"
    if collection_name is None:
        collection_name ="goncalo_thesis"
    
    EMBED_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
    
    def build_dense_retriever(k_val):
        emb = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL_NAME,
            encode_kwargs={"normalize_embeddings": True},
        )
        vs = Chroma(
            collection_name=collection_name,
            embedding_function=emb,
            persist_directory=path,
        )
        return vs.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k_val,
                "fetch_k": max(20, 4 * k_val),
                "lambda_mult": 0.75
            }
        )
    
    def build_bm25_retriever(k_val, q):
        dense = build_dense_retriever(k_val)
        docs = dense.invoke(q)
        bm25 = BM25Retriever.from_documents(docs)
        bm25.k = k_val
        return bm25
    
    def hybrid_query(q, k_val):
        bm25 = build_bm25_retriever(k_val, q)
        bm25_results = bm25.invoke(q)
        
        if bm25_results:
            dense = build_dense_retriever(k_val)
            dense_results = dense.invoke(q)
            combined_results = bm25_results + dense_results
            return combined_results[:k_val]
        
        return []
    
    # Perform the hybrid query
    results = hybrid_query(query, 5)
    
    # Return just the page_content strings
    return [doc.page_content for doc in results]