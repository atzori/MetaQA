import sys, json, argparse, os
import queryQAnswer, queryTeBaQA

if __name__ == "__main__":
    
    qanswer_supported_languages = ["en", "de", "fr", "it", "es", "pt", "nl", "zh", "ar", "ja", "ru"]
    
    parser = argparse.ArgumentParser()
    parser.add_argument("system_name", choices = ['qanswer', 'tebaqa'])
    parser.add_argument("data_source", choices = ["dbpedia", "wikidata"])
    parser.add_argument("language", choices = qanswer_supported_languages)
    parser.add_argument("question")
    
    if(len(sys.argv) != 5):
        sys.exit("Error: Wrong number of parameters! They should be 'system_name' 'data_source' 'language' 'question_string'")
    
    args = parser.parse_args()
    system = args.system_name
    db = args.data_source
    language = args.language
    question = args.question
    
    if(system == "tebaqa" and db != "dbpedia"):
        sys.exit("Error: TeBaQA only accepts 'dbpedia' as data source!")
    
    if(system == "tebaqa" and language != "en"):
        sys.exit("Error: TeBaQA only accepts 'en' as language!")
    
    if(question == ""):
        sys.exit("Error: Please enter a valid question!")
    
    formatted_question =    {
        "questions": [
            {
                "db": db,
                "id": "1",
                "question": [
                    {
                        "language": language,
                        "string": question
                    }
                ]
            }
        ]
    }
    
    with open('temp.json', 'w+') as f:
        json.dump(formatted_question, f)
    
    with open('temp.json', 'r+') as f:
        if(system == "qanswer"):
            queryQAnswer.read_and_query('temp.json', True)
        elif(system == "tebaqa"):
            queryTeBaQA.read_and_query('temp.json', True)
            
    os.remove('temp.json')
    