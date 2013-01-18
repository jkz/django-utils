import sys
import traceback

def trace():
    print sys.exc_info()[0]
    print sys.exc_info()[1]
    traceback.print_tb(sys.exc_info()[2])

