from elasticsearch import Elasticsearch

def init_and_check():
    
  es = Elasticsearch(
      "http://localhost:9200",
  #     basic_auth=("elastic","LQym+efHnUy9DbT-jtD2"),
  #     ca_certs="/Users/abidsaudagar/Personal/yt1_semantic_search/elasticsearch-8.9.1/config/certs/http_ca.crt"
  )
  return es.ping()

def create_index(name):
  try:
    if es.indices.exists(index=index_name):
      es.indices.delete(index=index_name)
      print(f"Index '{index_name}' deleted.")

    # Now, recreate the index
    es.indices.create(index=index_name)
    print(f"Index '{index_name}' created.")
    return True
  except Exception:
    return False


def add_to_index(sessions, types, datas, summarizes, vector_summarizes):
    try:
        for session, typeD, data, summary, vector in zip(sessions, types, datas, summarizes, vector_summarizes):
            document = {
                "session": session,
                "type": typeD,
                "data": data,
                "summary": summary,
                "vector_summary": vector
            }

            es.index(index=index_name, document=document)
        
        return True  # Return True if successful

    except exceptions.ConnectionError:
        print("Error: Unable to connect to Elasticsearch.")
    except exceptions.RequestError as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return False  # Return False if there was an error


def query_extract(input_keyword_encode):
  # input_keyword = "Blue Shoes"
  # vector_of_input_keyword = model.encode(input_keyword)
  count_index = es.count(index="all_products")
  
  query = {
      "field" : "DescriptionVector",
      "query_vector" : input_keyword_encode,
      "k" : 2,
      "num_candidates" : count_index, 
  }

  res = es.knn_search(index="all_products", knn=query , source=["ProductName","Description"])
  return res["hits"]["hits"]