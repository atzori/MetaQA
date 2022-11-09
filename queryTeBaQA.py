import sys, json, pandas, requests


""" in: file qald formato json
    out: json delle risposte """
def read_and_query(qald_file, print_answer):
    
    file = open(qald_file,"r",encoding="utf-8") #apertura del file passato da terminale in lettura
    data = json.load(file)  ##nb: load() carica il file e lo legge come json, loads() legge una stringa e la trasforma in oggetto json
    dataframe = pandas.DataFrame(data["questions"])  #restituisce la tabella con come colonne id, questions, query e answers
    risposte = []   #dizionario dove inserire tutti i dati ottenuti
    #vai = False    #dato che tebaqa dopo tot tempo crasha questa variabile permette di riprendere dalla domanda con l'id alla quale ci si era fermati
    
    try:
        for id, question in zip(dataframe["id"], dataframe["question"]):
            #if(id == "129"):   #decommentare e mandare avanti di un tab tutto sotto l'if(vai) per ripartire dall'id selezionato
                #vai = True
            #if(vai):
            if(not print_answer):
                print("Processing question " + id + "...")
            for q in question:  #dato che question è una lista con tutte le lingue dentro (il controllo della lingua serve solo per il qald9 originale)
                if q["language"] == "en":
                    domanda = q["string"]
            if(domanda == ""):  #alcune domande nel secondo file delle parafrasi del qald9 reworded non hanno il testo, vanno saltate
                print(".......................Domanda vuota")
                continue
            params = {"query": domanda, "lang":"en"}    #parametri da passare con richiesta POST
            response = requests.post('http://localhost:9080/qa', params)    #connessione e ottenimento risposta dal server
            risposta = {}
            risposta["id"] = id
            risposta["question"] = [{"language": "en", "string": domanda}]
            risposta["query"] = {"sparql": "..."}   #lo sparql non viene restituito dal server ma appare solo nella console di tebaqa (ma tanto non serve per l'f1)
            risposta["answers"] = [dict(json.loads((response.json())["questions"][0]["question"]["answers"]))]  #estrazione solo delle risposte dal json
            risposte.append(risposta)   #aggiunta dei dati della risposta alla domanda attuale al dizionario completo
            if print_answer and risposta is not None:
                for ans in risposta["answers"][0]["results"]["bindings"]:
                    print(ans)
            elif print_answer:
                print("No answer found!")
    except KeyboardInterrupt:   #ctrl+c non chiude il programma, ferma solo il ciclo
        print(" -> Processo interrotto dall'utente, nel file di output mancheranno le risposte a partire da quella sopra")
    
    
    final = {}
    final["questions"] = risposte   #formattazione finale del dizionario con domande e relative risposte per farlo poi accettare da gerbil
    
    
    if(not print_answer):
        with open('tebaqa-' + qald_file, 'w') as f:
            f.write(json.dumps(final, indent=4))
        print("Created tebaqa-" + qald_file)


if __name__ == "__main__":
    file_da_aprire = sys.argv[1]
    read_and_query(file_da_aprire, False)
