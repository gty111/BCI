#interface of EEG device

from mindwavemobile.MindwaveDataPointReader import MindwaveDataPointReader
from mindwavemobile.MindwaveDataPoints import RawDataPoint
import server

mindwaveDataPointReader = None

def connect():
    global mindwaveDataPointReader
    try:
        mindwaveDataPointReader = MindwaveDataPointReader("C4:64:E3:E7:D1:06")
        # connect to the mindwave mobile headset...
        mindwaveDataPointReader.start()
        device_state = True
    except Exception as e:
        print(e)
        server.device_state = False
def read():
    # read one data point, data point types are specified in  MindwaveDataPoints.py'
    try:
        dataPoint = mindwaveDataPointReader.readNextDataPoint()
        if isinstance(dataPoint,RawDataPoint): 
            return int(dataPoint.rawValue)
    except Exception as e:
        print(e)
        server.device_state = False