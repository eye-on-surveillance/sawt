import json
import os
import logging

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from datetime import datetime

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

from langchain.retrievers import ContextualCompressionRetriever


from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
    LLMChainExtractor,
    LLMChainFilter,
)
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_openai import OpenAIEmbeddings


from helper import sort_retrieved_documents
from api import RESPONSE_TYPE_DEPTH, RESPONSE_TYPE_GENERAL

logger = logging.getLogger(__name__)


def convert_date_format(date_str):
    """Convert date from 'M-D-YYYY' or 'MM-DD-YYYY' to 'MM/DD/YYYY' format."""
    if not isinstance(date_str, str):
        return "Invalid input: not a string"

    if "/" in date_str:
        return date_str

    input_format = "%m-%d-%Y"

    try:
        date_obj = datetime.strptime(date_str, input_format)
    except ValueError:
        try:
            input_format = "%-m-%-d-%Y"
            date_obj = datetime.strptime(date_str, input_format)
        except ValueError:
            return "Invalid date format"

    return date_obj.strftime("%m/%d/%Y")


def timestamp_to_seconds(timestamp):
    if "timestamp not available" in timestamp:
        return None  # or another default value like -1 or 0

    start_time = timestamp.split("-")[0]  # Split by '-' and take the first part
    print(start_time)

    time_parts = [int(i) for i in start_time.split(":")]

    if len(time_parts) == 3:
        h, m, s = time_parts
    elif len(time_parts) == 2:
        h, m = time_parts
        s = 0
    else:
        raise ValueError("Invalid timestamp format: " + timestamp)

    return h * 3600 + m * 60 + s


def process_streamed_responses_llm(response_chunks, docs):
    final_json_object = {"card_type": "in_depth", "responses": [], "citations": []}
    unique_citations = set()

    for chunk in response_chunks:
        # Update citations for each chunk
        citations = []
        for doc in docs:
            citation_signature = (
                doc.metadata.get("title", doc.metadata.get("source", "")),
                doc.metadata.get("url", "url not available"),
                doc.metadata.get("timestamp", "timestamp not available"),
                os.path.basename(doc.metadata.get("source", "source not available")),
                doc.metadata.get("page_number"),
            )

            if citation_signature not in unique_citations:
                unique_citations.add(citation_signature)
                citation = {
                    "Title": citation_signature[0],
                    "Published": convert_date_format(
                        doc.metadata.get("publish_date", "date not available")
                    ),
                    "URL": citation_signature[1],
                    "Video timestamp": citation_signature[2],
                    "Name": citation_signature[3],
                    "Page Number": citation_signature[4],
                }
                citations.append(citation)

        # Append the current chunk and its citations to the final JSON object
        final_json_object["responses"].append({"response": chunk.strip()})
        final_json_object["citations"].extend(citations)

    return final_json_object


def extract_document_metadata(docs):
    generated_titles = [
        doc.metadata.get("title", doc.metadata.get("source", "")) for doc in docs
    ]
    page_numbers = [doc.metadata.get("page_number") for doc in docs]
    generated_sources = [
        doc.metadata.get("source", "source not available") for doc in docs
    ]
    publish_dates = [
        convert_date_format(doc.metadata.get("publish_date", "date not available"))
        for doc in docs
    ]
    timestamps = [
        doc.metadata.get("timestamp", "timestamp not available") for doc in docs
    ]
    urls = [doc.metadata.get("url", "url not available") for doc in docs]

    return (
        generated_titles,
        page_numbers,
        generated_sources,
        publish_dates,
        timestamps,
        urls,
    )


def timestamp_to_seconds(timestamp):
    if "timestamp not available" in timestamp:
        return None

    time_parts = timestamp.split(":")
    seconds = sum(
        int(part) * 60**index for index, part in enumerate(reversed(time_parts))
    )
    return seconds


def generate_response_section(
    i,
    response,
    generated_titles,
    page_numbers,
    generated_sources,
    publish_dates,
    timestamps,
    urls,
):
    section = {"response": response}
    section["source_title"] = generated_titles[i] if i < len(generated_titles) else None
    section["source_name"] = (
        os.path.basename(generated_sources[i]) if i < len(generated_sources) else None
    )
    section["source_page_number"] = page_numbers[i] if i < len(page_numbers) else None
    section["source_publish_date"] = (
        publish_dates[i] if i < len(publish_dates) else None
    )
    section["source_timestamp"] = timestamps[i] if i < len(timestamps) else None
    section["source_url"] = urls[i] if i < len(urls) else None

    if section["source_url"] and section["source_timestamp"]:
        time_in_seconds = timestamp_to_seconds(section["source_timestamp"])
        if time_in_seconds is not None:
            section["source_url"] += (
                f"&t={time_in_seconds}s"
                if "?" in section["source_url"]
                else f"?t={time_in_seconds}s"
            )

    citation = {
        key: value
        for key, value in section.items()
        if value is not None and key.startswith("source_")
    }
    return section, citation


def append_metadata_to_content(doc_list):
    updated_docs = []

    for doc_tuple in doc_list:
        doc, score = doc_tuple
        metadata = doc.metadata
        publish_date = metadata.get("publish_date")

        if publish_date is not None:
            updated_content = (
                f"Document: {doc.page_content} (Published on: {publish_date})"
            )
        else:
            updated_content = doc.page_content

        updated_doc_info = {
            "content": updated_content,
            "metadata": metadata,
            "score": score,
        }

        updated_docs.append(updated_doc_info)

    return updated_docs


def transform_query_for_date(query):
    return (
        query
        + "(SYSTEM NOTE: this query related to a specific time period, therefore, you should sort the documents by the publish dates to best answer the query)"
    )


def process_and_concat_documents(retrieved_docs):
    combined_docs_content = []
    original_documents = []

    for source, docs in retrieved_docs.items():
        for doc in docs:
            combined_docs_content.append(doc.page_content)
            original_documents.append(doc)

    combined_content = "\n\n".join(combined_docs_content)
    return combined_content, original_documents


def get_indepth_response_from_query(df, db_fc, db_cj, db_pdf, db_pc, db_news, query, k, return_context):
    logger.info("Performing in-depth summary query...")

    llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106", streaming=True)
    embeddings = OpenAIEmbeddings()


    # Initialize compressors and transformers
    splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0, separator=". ")
    redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings)
    relevant_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.76)

    # Create a compressor pipeline
    pipeline_compressor = DocumentCompressorPipeline(
        transformers=[splitter, redundant_filter, relevant_filter]
    )

    # Wrap base retrievers with the compressor pipeline
    compressed_retrievers = [
        ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=db.as_retriever()
        )
        for db in [db_fc, db_cj, db_pdf, db_pc, db_news]
    ]
    retriever_names = ["fc", "cj", "pdf",]

    # Initialize parallel retrieval with compressed retrievers
    retrieval_chains = {
        name: RunnableLambda(lambda q, db=db: db.get_relevant_documents(q, k=25))
        for name, db in zip(retriever_names, compressed_retrievers)
    }
    retrievals = RunnableParallel(retrieval_chains)

    compressed_docs = retrievals.invoke(query)

    combined_docs_content, original_documents = process_and_concat_documents(
        compressed_docs
    )
    # print(combined_docs_content)

    template = """
    ### Response Guidelines
    Your primary task is to answer the specific question: '{question}'. Extract and include information from the New Orleans city council documents provided that is directly relevant to this question. Refrain from including any additional analysis, context, or details that do not contribute to a concise and direct answer to the question.

    ### Additional Guidelines 
    Follow the guidelines below if they assist in providing a more clear answer to {question}
    If relevant, extract the key points, decisions, and actions discussed during the city council meetings relevant to {question};
    highlight any immediate shortcomings, mistakes, or negative actions by the city council relevant to {question}; 
    elaborate on the implications and broader societal or community impacts of the identified issues relevant to {question};
    investigate any underlying biases or assumptions present in the city council's discourse or actions relevant to {question}. 
    If not relevant to the question, answer the question without expanding on these points.

    ### Relevance Evaluation:
    When analyzing documents, critically assess whether each piece of information improves the response's relevance and accuracy. Include information only if it directly answers or is essential to understanding the context of the question. Disregard information that is tangential or unrelated.

    ### Bias Guidelines:
    Be mindful of biases in the document corpus. Prioritize and analyze documents that are most likely to contain direct and relevant information to the question. Avoid including details from documents that do not substantively contribute to a focused and accurate response.

    The final output should be in paragraph form without any formatting, such as prefixing your points with "a.", "b.", or "c.", "-", or "1."
    The final output should not include any reference to the model's active sorting by date.
    The final output should not include any reference to the publish date. For example, all references to "(published on mm/dd/yyyy)" should be omitted. 

    ### Documents to Analyze
    {docs}
    """

    prompt_response = ChatPromptTemplate.from_template(template)
    response_chain = prompt_response | llm | StrOutputParser()

    unique_citations = set()

    final_result = {"card_type": "in_depth", "responses": [], "citations": []}
    accumulated_text = ""
    word_count = 0

    for chunk in response_chain.stream({"question": query, "docs": combined_docs_content}):
        accumulated_text += chunk
        words = accumulated_text.split()
        
        if len(words) - word_count >= 3:  
            new_content = " ".join(words[word_count:])
            print(new_content)
            final_result["responses"].append({"response": new_content})
            word_count = len(words)

        partial_result = process_streamed_responses_llm([chunk], original_documents)
        for citation in partial_result["citations"]:
            citation_signature = (citation["Title"], citation["Published"], citation["URL"])
            if citation_signature not in unique_citations:
                unique_citations.add(citation_signature)
                final_result["citations"].append(citation)

    remaining_text = " ".join(words[word_count:])
    if remaining_text:
        final_result["responses"].append({"response": remaining_text})

    if return_context:
        # docs retrieved here
        return (final_result, combined_docs_content), template
    
    return final_result



def get_general_summary_response_from_query(db, query, k):
    logger.info("Performing general summary query...")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        As an AI assistant, your task is to provide a general response to the question "{question}", using the provided transcripts from New Orleans City Council meetings in "{docs}".

        Guidelines for AI assistant: 
        - Derive responses from factual information found within the transcripts. 
        - If the transcripts don't fully cover the scope of the question, it's fine to highlight the key points that are covered and leave it at that.  
        """,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content, temperature=0)
    response = {"response": responses_llm}
    card = {"card_type": RESPONSE_TYPE_GENERAL, "responses": [response]}
    card_json = json.dumps(card)
    return card_json


def route_question(df, db_fc, db_cj, db_pdf, db_pc, db_news, query, query_type, return_context, k=20):
    if query_type == RESPONSE_TYPE_DEPTH:
        depth_response, template = get_indepth_response_from_query(
            df, db_fc, db_cj, db_pdf, db_pc, db_news, query, k, return_context
        )

        return depth_response, template
    
    else:
        raise ValueError(
            f"Invalid query_type. Expected {RESPONSE_TYPE_DEPTH}, got: {query_type}"
        )


def answer_query(
    query: str,
    response_type: str,
    df: any,
    db_fc: any,
    db_cj: any,
    db_pdf: any,
    db_pc: any,
    db_news: any,
    return_context: any = False,
) -> str:
    final_response = route_question(
        df, db_fc, db_cj, db_pdf, db_pc, db_news, query, response_type, return_context
    )
    return final_response
