from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI()

embedding_model = OpenAIEmbeddings(
    model = "text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model
)


def rag_pipeline(user_query):
    # Similarity Search of user query with DB Data
    search_results = vector_db.similarity_search(query=user_query) # this will make embedding of user's query after that it will start similarity search.

    context = "\n \n \n" .join([f"page content : {result.page_content} \n page number : {result.metadata["page_label"]} \n File Location : {result.metadata["source"] }"for result in search_results])

    SYSTEM_PROMPT = f"""
        you are a helpfull assistant. you are here to resolve the user query but not from your own knowledge.
        we have a rag system so whenever user will ask a query then it will give you the related data so from that data you have to resolve the user query only use the context data which is coming from rag and use this to give the answer to the user.

        Strict : with answer you also have to mention page number of the source and information

        context :
        {context}
    """

    response = client.chat.completions.create(
        model = "gpt-4.1-nano",
        messages=[
            {"role" : "system" , "content" : SYSTEM_PROMPT},
            {"role" : "user" , "content" : user_query}
        ]
    )

    print(response.choices[0].message.content)
    return response.choices[0].message.content