from xata.client import XataClient
from langchain_openai import OpenAIEmbeddings
import json

# Свой модуль.
from common.settings import db_url_xata

# Создание клиента Xata и подключение его к БД.
xata = XataClient(db_url=db_url_xata)


def vector_search(query='', k=4, filter={}, filter_chunk=[]):
    """Функция векторного поиска."""
    embeddings = OpenAIEmbeddings()
    query_emb = embeddings.embed_query(query)

    if filter_chunk:
        filter_chunk_list = filter_chunk
    else:
        filter_chunk_list = ['0']

    results = xata.data().vector_search("capilot_db", {
        "queryVector": query_emb,
        "column": "embedding",
        "size": k,
        "filter": {"$not": {"$any": {"chunk": filter_chunk_list}},
                   filter["operand"]: {"topic": filter["list"]}}
    })
    if not results.is_success():
        raise Exception(f"Vector search failed: {results.json()}")
    return results


def keyword_search(query='', k=4, filter={}, filter_chunk=[]):
    """Функция поиска по ключевым словам."""
    if filter_chunk:
        filter_chunk_list = filter_chunk
    else:
        filter_chunk_list = ['0']

    results = xata.data().search_table("capilot_db", {
        "query": query,
        "fuzziness": 1,
        "prefix": "phrase",  # phrase|disabled
        "page": {"size": k},
        "filter": {"$not": {"$any": {"chunk": filter_chunk_list}},
                   filter["operand"]: {"topic": filter["list"]}}
    })
    if not results.is_success():
        raise Exception(f"Keyword search failed: {results.json()}")

    return results

# Функция гибридного поиска основанная на методе ранжирования 'Reciprocal rank fusion (RRF)'.


def rerank_with_rrf(keyword_results, vector_results, k=60):
    """Computes the reciprocal rank fusion of two search results."""
    # Combine and initialize scores
    unique_results = {
        result["id"]: result for result in keyword_results + vector_results}
    scores = {result_id: 0 for result_id in unique_results.keys()}

    # Helper to update scores based on RRF formula
    def update_scores(results_list, scores, k):
        for rank, result in enumerate(results_list, start=1):
            result_id = result['id']
            if result_id in scores:
                scores[result_id] += 1 / (k + rank)

    # Update scores for both sets of results
    update_scores(keyword_results, scores, k)
    update_scores(vector_results, scores, k)

    # Sort results by their RRF score in descending order
    sorted_result_ids = sorted(
        scores.keys(), key=lambda id: scores[id], reverse=True)

    # Extract the sorted result objects
    sorted_results = [unique_results[result_id]
                      for result_id in sorted_result_ids]

    return sorted_results


def retriever_xata(query, type_search, top_k, filter_agent, subquery_id):
    """Функция ретривера."""
    def save_docs(docs, subquery_id):
        """Функция записи чанка в Xata"""
        # Если есть id то записать в Xata данные чанка в формате JSON.
        if subquery_id:
            chunk_number = ''  # Список номеров чанков
            chunk_context = ''  # Контекст из документов для поиска информации.
            for i, doc in enumerate(docs):
                chunk = {"content": doc.get("content"),
                         "chunk": doc.get("chunk"),
                         "len": doc.get("len"),
                         "topic": doc.get("topic"),
                         "topic_full": doc.get("topic_full"),
                         "H1": doc.get("H1"),
                         "H2": doc.get("H2"),
                         "H3": doc.get("H3"),
                         "H4": doc.get("H4"),
                         }
                chunk_number += f"{doc.get('chunk')},"
                chunk_context += f"Document #{i+1} (Chunk #{doc.get('chunk')})\n{doc.get('content').strip()}\n\n"

                # Ограничение на 5 чанков в Xata
                if i < 6:
                    record_subquery = xata.records().update("subquerys", subquery_id, {
                        f"chunk_{i+1}": json.dumps(chunk),
                        "chunk_number": chunk_number,
                    })
            record_subquery = xata.records().update("subquerys", subquery_id, {
                "chunk_context": chunk_context
            })
        return docs

    filter = filter_agent['filter_data']
    filter_chunk = filter_agent['filter_chunk']

    if type_search == 'hybrid':
        vector_results = vector_search(query, top_k, filter, filter_chunk)
        keyword_results = keyword_search(query, top_k, filter, filter_chunk)
        docs = rerank_with_rrf(keyword_results["records"],
                               vector_results["records"])[:top_k]
        return save_docs(docs, subquery_id)
    elif type_search == 'vector':
        vector_results = vector_search(query, top_k, filter, filter_chunk)
        docs = vector_results["records"]
        return save_docs(docs, subquery_id)
    elif type_search == 'keyword':
        keyword_results = keyword_search(query, top_k, filter, filter_chunk)
        docs = keyword_results["records"]
        return save_docs(docs, subquery_id)
