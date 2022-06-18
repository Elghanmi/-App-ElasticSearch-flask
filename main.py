import json
from elasticsearch import Elasticsearch, helpers, ApiError
#from elasticsearch_dsl import Search
from flask import Flask, render_template, request
app = Flask(__name__)
es = Elasticsearch("http://localhost:9200")





#il faut taper a la 1ere fois
#cette route fais seulement la creation d'index
#et remplire par les document qui sont dans le fichier movies.json


#http://localhost:9200/index
@app.route("/index")
def index():
    # Opening JSON file
    f = open('D:/app-search-flask-app/movies.json', )
    documents = []
    for i in f.readlines():
        documents.append(i)
    # on utilise helpers.bulk pour creer et estocker plusieurs documents a une seule fois
    data = helpers.bulk(
        es,
        documents,
        index="movies",

    )
    return render_template("about.html", data=data)



#cette route fais la recuperation de toutes les documents d'index movies
# et les envoyer au index.html
#pour les afficher

#http://localhost:9200/
@app.route("/")
def home():
    data = ""
    es_error = ""
    try:
        data = es.search(index="movies", body={"query": {"match_all": {}}})
    except ApiError as e:
        es_error = "Configure cluster credentials in \"config.json\" and Index data with by calling \"/index\" endpoint"
        print(es_error)
    movies_list = []
    if data:
        for i in data['hits']['hits']:
            movies_list.append(i['_source'])
    return render_template("index.html", data=movies_list, es_error=es_error)


#cette route fais la rechereche
#et fais un trie soit d'apres year ou rate
#




#http://localhost:9200/search
@app.route("/search", methods=['POST'])
def search_es():
    se=None
    se1=None
    if request.method == 'POST':
        query =  request.form['search']
        sorted = request.form['sorted']
    if query and sorted!="None":

        se=query
        se1=sorted
        req={"query": {
            "multi_match": {
                "query": query,
                "fields": ["title.prefix", "info.plot.prefix"]
            }
        } ,
          "sort": [
            {
                sorted: {
                    "order": "asc"
                }
            }
        ]
           }
    elif query:
        se=query
        req={"query": {
            "multi_match": {
                "query": query,
                "fields": ["title.prefix", "info.plot.prefix"]
            }
        }  }
    else:
        req ={
            "sort": [
                {
                    sorted: {
                        "order": "asc"
                    }
                }
            ]
        }
    data = es.search(index="movies", body=req)
    movies_list = []
    for i in data['hits']['hits']:
        movies_list.append(i['_source'])
    if sorted == "year":
        year,rate="selected",None
    elif sorted == "info.rating":
        rate,year="selected",None
    else:
        rate, year = None, None
    return render_template("index.html", data=movies_list,se=se,year=year,rate=rate)



if __name__ == "__main__":
    app.run(debug=False)
