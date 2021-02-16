# main server 

import asyncio
import websockets
import json
import function
import sys


STATE = 0
STATE_band = [1,1,1,1,1]
device_state = True

async def main(websocket,path):
    global STATE    
    global STATE_band
    print("web connected")
    async for message in websocket:
        if device_state==False:
            sys.exit(-1)
        data = json.loads(message)
        if data["action"] == "connect" and STATE==0:
            #some code to connect
            STATE = 1
            function.connect()
            if device_state:
                print("connected")
                await websocket.send(json.dumps({"type":"connect","connect_state":STATE}))
            else:
                await websocket.send(json.dumps({"type":"err"}))
                sys.exit(-1)
        elif data["action"] == "connect" and STATE==1:
            #some code to disconnect
            STATE = 0;
            print("disconnected")
            await websocket.send(json.dumps({"type":"connect","connect_state":STATE}))
            sys.exit(0)
        elif data["action"] == "timer":
            #some code to send data
            '''
            d = json.dumps({"type":"data_raw","data_raw":function.data_raw.tolist()})
            with open("a.json",'w',encoding='utf-8') as json_file:
                json.dump(d,json_file,ensure_ascii=False)
            '''
            await websocket.send(json.dumps({"type":"packet",
                                             "fig_raw":function.draw_raw(),
                                             "fig_band":function.draw_band(),
                                             "fig_pre":function.draw_pre()}))
            #await websocket.send(json.dumps({"type":"data_raw","data_raw":function.data_raw.tolist()}))
        
        elif data["action"] == "change_state":
            STATE_band = data["state_checkbox"]
def start_server():    
    server = websockets.serve(main, "127.0.0.1", 5678)
    asyncio.get_event_loop().run_until_complete(server)
    print("start server successfully")
    print("server serve at ws://127.0.0.1:5678/")
    asyncio.get_event_loop().run_forever()
