indexMapping = {
    "properties":{
        
        "Type":{
            "type":"text"
        },
        "Session":{
            "type":"text"
        },
        "Content":{
            "type":"text"
        },
        "Summary":{
            "type":"text"
        },
        "SummaryVector":{
            "type":"dense_vector",
            "dims": 768,
            "index":True,
            "similarity": "l2_norm"
        }

    }
}