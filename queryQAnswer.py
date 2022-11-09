# -*- coding: utf-8 -*-

"""
USAGE:

$python queryQAnswer.py [json_file] 

"""


import json, re, requests, sys
import pandas as pd


def open_qald(qald_file):
    """
    in: file qald formato json
    out: domande del dataset in entrambe le lingue
    type(out): dataframe
    """
    q = open(qald_file,"r",encoding="utf-8")
    data = json.load(q) ##nb: load() carica il file e lo legge come json, loads() legge una stringa e la trasforma in oggetto json
    df = pd.DataFrame(data["questions"])
    
    return df
        

def read_and_query(qald_file, print_answer):
    """
    - metodo che esegue le query tramite l'API
    in: file qald formattato come un json
    out: risultati delle query (ovv. elenco di query sparql + elenco risposte + altri meta-dati)
    type(out): lst[dct]
    """
    df = open_qald(qald_file)
    if "wikidata" in qald_file:
        kb = "wikidata"
    else:
        kb = "dbpedia"
    url = 'http://qanswer-core1.univ-st-etienne.fr/api/qa/full'
    token = 'INSERT TOKEN HERE'
    header = {'Authorization': token}
    out_qa = []
    
    for qid, question in zip(df["id"], df["question"]):
        #for  i, q in enumerate(question):
            #if i < 500:
        for q in question:
            params = {'question': q["string"], 'lang':q["language"],'kb': kb}
            r = requests.get(url, params, headers=header)
            if(not print_answer):
                print("Processing question " + qid)
            j = r.json() #parsifico json della risposta restituito da QAnswer
            try:
                question = j["question"]
                query = j["queries"][0]["query"]
            except KeyError:
                question = ""
                answer = ""
                query = ""
            try:
                answer = j["qaContexts"]["qaContext"][0]
            except (IndexError, TypeError, KeyError):
                answer = ""
            new_j = {"lang": q["language"], "id":qid, "question": question, "query": {"sparql": query}, "answers": answer}
            out_qa.append(new_j)
            if(print_answer):
                # if(answer["description"]) is not None:
                #     print(answer["description"])
                # elif(answer["label"]) is not None:
                #     print(answer["label"])
                if("uri" in answer) and (answer["uri"] is not None):
                    print(answer["uri"])
                else:
                    print("No answer found!")
         
    if(not print_answer):
        print("Queries completed!")
    return out_qa
    
    
def process_answer(out_qa, infile):
    """
    - estrae le risposte del json restituito da QAnswer, lo riconverte in json qald-compatibile e lo esporta in un nuovo file
    in: risultati delle query (ovv. elenco di query sparql -- solo la prima per ogni dom.-- + risposte -- idem -- + altri meta-dati)
    out: json 
    type(out): file
    """
    qvars= "string" #assegno string e literal come valori di default delle variabili sui tipi - se solleva un'eccezione, tengo la stringa vuota come risposta
    qtype= "literal" 
    qvalue = ""
    qald_dct = {"questions": []}
    for i, item in enumerate(out_qa):
        new_q = {"id":"", "question": [], "query":{}, "answers": []}
        new_q["id"] = item["id"]
        new_q["question"] = [{"language": item["lang"], "string": item["question"]}]
        new_q["query"] = item["query"]
        try:
            if item["answers"]['uri'] is not None:
                qvars = 'uri'
                qtype = 'uri'
                qvalue = item["answers"]['uri']
            else:
                qtype = 'literal'
                qvalue = item["answers"]['literal']
                weekdays = ("Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday")
                if qvalue in weekdays:
                    qvars = "date"
                    qvalue = convert_date(qvalue) #per convertire le date quando hanno formato Weekday, DD Month YYYY
                elif re.match(r'[0-9]{1,4}\-[0-9]{1,2}\-[0-9]{1,4}$', qvalue): #per trovare date in formato YYYY-MM-DD o DD-MM-YYYY 
                    qvars = "date"
                elif re.match(r'[\-|\+]?[0-9]+[\,|\.]?[0-9]*$', qvalue):#se stringa della risposta è data da un solo numero 
                    if "." in qvalue and re.search(r'[Yy]ear', item["query"]["sparql"]):
                        qvalue = qvalue.replace(".","")    ## tolgo il . dal numero se si tratta di un anno (es. QAnswer restituisce 1.798 invece di 1798)                   
                    qvars = "c"
                else:
                    qvars = "string"
        except KeyError as Argument:
            print("Handling error - ", Argument," for question:",item["question"])  
        except TypeError as Argument:
            print("Handling error - ", Argument," for question:",item["question"])  
        new_q["answers"] = [{"head": 
                                {"vars": [qvars]}, 
                            "results": {
                                    "bindings": [
                                            {qvars: 
                                                 { "type" : qtype,
                                                   "value": qvalue
                                                 }
                                            }]
                                }
                            }]
        qald_dct["questions"].append(new_q)
           
    print("Create qansw-"+infile)
    qald = open("qansw-"+infile,"w",encoding="utf-8")
    json.dump(qald_dct, qald, ensure_ascii=False, indent=4)
  
    
def convert_date(date):
    months = {"January":"01","February":"02", "March":"03", "April":"04", "May":"05","June":"06","July":"07","August":"08", "September":"09", "October":"11", "November":"11", "December":"12"}
    date = date.split(",")[1].split(" ")
    dd = date[0]
    mm = months[date[1]]
    yy = date[2]
    
    return yy+"-"+mm+"-"+dd    



#-------------------------------------------------------------------------------
if __name__ == "__main__":
    
    q = read_and_query(sys.argv[1], False)
    process_answer(q, sys.argv[1])
    
    