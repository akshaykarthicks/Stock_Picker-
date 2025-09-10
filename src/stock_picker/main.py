#!/usr/bin/env python
# SQLite workaround for cloud environments
try:
    __import__('pysqlite3')
    import sys as _sys
    _sys.modules['sqlite3'] = _sys.modules.pop('pysqlite3')
except ImportError:
    pass
import sys
import warnings
from datetime import datetime
from dotenv import load_dotenv



from stock_picker.crew import StockPicker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the Research crew.
    """
    load_dotenv()
    inputs = {
        'sector': 'AI and Machine Learning'

    }
    result=StockPicker().crew().kickoff(inputs=inputs)
    print("\n\n -------------- Result --------------------------------")
    print(result.raw)
    print("\n\n -------------- End of Result --------------------------------")

if __name__ == "__main__":
    run()
