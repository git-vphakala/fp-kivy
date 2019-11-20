"""ws.py
"""
import asyncio
import websockets

store = {}

async def _conn():
    """_conn
    """
    # uri = "ws://192.168.10.46:8000/ws/username/"
    uri = "ws://localhost:8000/ws/username/"
    try:
        websocket = await asyncio.wait_for(websockets.connect(uri), 3)
    except asyncio.TimeoutError:
        print("conn timeout excep")
    except websockets.InvalidURI as inv_uri_e: 
        print("uri is invalid", uri, inv_uri_e)
    except websockets.InvalidHandshake as inv_hndshake_e:
        print("the opening handshake failed", uri, inv_hndshake_e)
    except websockets.WebSocketException as wse:
        print("wse", wse)
    else:
        store["ws"] = websocket
        return True

    return False

async def _send(msg):
    """_send
    """
    try:
        ws = store["ws"]
        await asyncio.wait_for(ws.send(msg), 5)
    except asyncio.TimeoutError:
        print("send failed")
        return False
    except KeyError as kee:
        print("send: KeyError", kee)
        return False

    return True

async def _recv():
    """_recv
    """
    try:
        ws = store["ws"]
        response = await asyncio.wait_for(ws.recv(), 0.1)
        # print(f"< {response}")
        store["message"] = response
    except asyncio.TimeoutError:
        # print("no message")
        return False
    except KeyError: # as kee:
        # print("recv", kee)
        return False

    return True

async def _close():
    """_close
    """
    try:
        ws = store["ws"]
        await asyncio.wait_for(ws.close(), 5)
    except asyncio.TimeoutError as toe:
        print("close failed", toe)
        return False
    except KeyError as kee:
        print("close", kee)
        return False

    return True

def conn():
    """conn
    """
    return asyncio.get_event_loop().run_until_complete(_conn())

def send(msg):
    """send
    """
    return asyncio.get_event_loop().run_until_complete(_send(msg))

def recv():
    """recv
    """
    return asyncio.get_event_loop().run_until_complete(_recv())

def close():
    """close
    """
    return asyncio.get_event_loop().run_until_complete(_close())

if __name__ == "__main__":
    ret_val = conn()
    #if ret_val:
    ret_val = send('{"type":"my-name","message":"Helmi"}')
    while ret_val:
        ret_val = recv()
    ret_val = close()
