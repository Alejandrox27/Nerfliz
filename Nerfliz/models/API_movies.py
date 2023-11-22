import requests
import random
from PyQt5.QtCore import pyqtSignal, QThread
from dotenv import load_dotenv
import os

class MoviesAPI_selected(QThread) :
    result_ready = pyqtSignal(dict)
    result_error = pyqtSignal(str)
    def __init__(self, movie_name):
        super().__init__()
        
        load_dotenv()
        
        self.url = f"https://www.omdbapi.com/?apikey={os.getenv('APIKEY')}&t="
        self.movie_name = movie_name
    
    def run(self):
        url = f'{self.url}{self.movie_name}'

        try:
            response = requests.get(url)

            result = response.json()
            self.result_ready.emit(result)
        except requests.exceptions.ConnectionError as error:
            self.result_error.emit('Connection Error!')
        except requests.exceptions.JSONDecodeError as error:
            self.result_error.emit('Error')
        except:
            self.result_error.emit('Error')