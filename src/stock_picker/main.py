#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

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
    inputs = {
        'sector': 'AI and Machine Learning'

    }
    result=StockPicker().crew().kickoff(inputs=inputs)
    print("\n\n -------------- Result --------------------------------")
    print(result.raw)
    print("\n\n -------------- End of Result --------------------------------")

if __name__ == "__main__":
    run()
