import json
import socket


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 9000))
server_socket.listen(5)

while True:
    client_socket, client_address = server_socket.accept()
    request = client_socket.recv(1024).decode()
    print(request)
    header, body = request.split("\r\n\r\n");
    #теперь анализ запроса
    #если запрос начинается на get
    if "GET" in header:
        response_body = "You send a GetRequest. Take our response"
        response_header = "HTTP/1.1 200 OK\r\n"
        response_header+= "Content-Type: text/html\r\n"
        response_header+= f"Content-Length: {len(response_body)}\r\n"
        response_header+= "Connection: close\r\n"
        response_header+= "\r\n"
        response_header+= response_body+"\r\n"
        client_socket.send(response_header.encode("utf-8"))
    if "POST" in header:
        #мы получили 2 числа в формате json
        #попробуем их спарсить
        try:
            json_dict = json.loads(body)
        except:
            response_header = "HTTP/1.1 400 Bad request\r\n"
            response_body = '{"error": "Invalid JSON format"}'
        #вроде спарсили мы это дело, теперь получим переменные
        a = json_dict.get("a");
        b = json_dict.get("b");
        #print(f"a: {a}, b: {b}")
        if b==0:
            response_header = "HTTP/1.1 500 Internal Server Error \r\n"
            response_body = '{"error": "Internal Server Error"}'
        else:
            div_result  = a/b
            div_result = str(div_result)
            response_header = "HTTP/1.1 200 OK\r\n"
            response_body = '{"result": "'+div_result+'"}'
        #а теперь наклепаем полноценный ответ серверу
        response_header+= "Content-Type: application/json\r\n"
        response_header+= f"Content-Length: {len(response_body)}\r\n"
        response_header+= "Connection: close\r\n"
        response_header+= "\r\n"
        response_header+= response_body+"\r\n"
        #print(response_header)
        client_socket.send(response_header.encode("utf-8"))

