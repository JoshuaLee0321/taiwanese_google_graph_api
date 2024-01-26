from flask import Flask, request, jsonify, render_template
from flask_restful import Resource, Api, abort, reqparse
from threading import Thread, Lock
from scripts.services import *
import time
# flask
app = Flask(__name__)
api = Api(app)
lock = Lock()

@app.errorhandler(400)
def bad_request_handler(message):
    '''
    User bad request handler
    '''
    return jsonify(error=str(message)), 400
class Search(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.zhdrv = init_driver()
        self.taidrv = init_driver()
        self.endrv = init_driver()
    
    def processLang(self, search_lang: str, search_word: str) -> dict:
        dictionary = dict()
        if search_lang == "en":
            dictionary['en'] = search_word
            dictionary['zh'] = translation(search_word, "en2zh_0416Osborn")
            dictionary['tai'] = translation(search_word, "en2tai")
        elif search_lang == "tai":
            dictionary['tai'] = search_word
            dictionary['en'] = translation(search_word, "tai2en")
            dictionary['zh'] = translation(search_word, "tai2zh")
        elif search_lang == "zh":
            dictionary['zh'] = search_word
            dictionary['en'] = translation(search_word, "zh2en_0406Osborn")
            dictionary['tai'] = translation(search_word, "zh2tai")
        return dictionary
    
    def query(self):
        pass
    
    def get(this):
        try:
            return jsonify({"post it you moron": {'post it': 'post'}})
        except Exception as e:
            abort(400, 'translation failed')
            
    def post(this):
    # parse args
        parser = reqparse.RequestParser()
        parser.add_argument('search_word', required=True)
        parser.add_argument('search_lang', required=True)
        parser.add_argument("type", required=True)
        args = parser.parse_args()
        print(args)
        queryType = args['type']
        queryDict = this.processLang(args['search_lang'], args['search_word'])

        result = dict()
        result['message'] = "success"
        
        # query it args: this.drv, queryDict["xx"], type : "xx", reference
        if queryType == "Video":
            thread_tai = Thread(target=get_queryVideo, args=(this.taidrv, queryDict['tai'], 'tai', result, lock))
            thread_en = Thread(target=get_queryVideo, args=(this.endrv, queryDict['en'], 'en', result, lock))
            thread_zh = Thread(target=get_queryVideo, args=(this.zhdrv, queryDict['zh'], 'zh', result, lock))

            thread_tai.start()
            thread_en.start()
            thread_zh.start()
            
            thread_tai.join()
            thread_en.join()
            thread_zh.join()
            
            return  jsonify(result)
        elif queryType == "Image":
            thread_tai = Thread(target=get_queryGraph, args=(this.taidrv, queryDict['tai'], 'tai', result, lock))
            thread_en = Thread(target=get_queryGraph, args=(this.endrv, queryDict['en'], 'en', result, lock))
            thread_zh = Thread(target=get_queryGraph, args=(this.zhdrv, queryDict['zh'], 'zh', result, lock))

            thread_tai.start()
            thread_en.start()
            thread_zh.start()
            
            thread_tai.join()
            thread_en.join()
            thread_zh.join()
            
            return  jsonify(result)
            
        
api.add_resource(Search, '/search')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1005, debug=True)
