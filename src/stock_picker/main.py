#!/usr/bin/env python
# import sys
import warnings

from datetime import datetime
from zoneinfo import ZoneInfo

from stock_picker.crew import StockPicker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    tz = ZoneInfo("Asia/Kolkata")
    localized_time = str(datetime.now(tz)) + " IST"
    inputs = {
        'sector': 'Banking',
        'current_time': localized_time
    }

    try:
        results = StockPicker().crew().kickoff(inputs=inputs)
        print(results.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")