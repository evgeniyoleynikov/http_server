import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import json
#----------------------------------------------------------------------------
#тут у нас будут глобальные переменные
server_socket = None
server_working = False;
#----------------------------------------------------------------------------
def start_server():
    global server_socket
    global server_working
    server_working = True
    mm_out.delete("1.0", tk.END)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", 9000))
    server_socket.listen()
    mm_out.insert("1.0", "Сервер запущен и ждет подключений.\n")
    mm_out.insert(tk.END, "Слушаем порт 9000 на localhost\n")
    server_status.set("Сервер запущен")
    bt_start.config(state=tk.DISABLED)
    bt_stop.config(state=tk.NORMAL)

    while True:
        if server_working==False:
            #выход из цикла, сервер останавливант работу
            break;

        client_socket, client_address = server_socket.accept()
        request = client_socket.recv(1024).decode()
        mm_out.insert(tk.END, request+"\n")
        header, body = request.split("\r\n\r\n");
        # теперь анализ запроса
        # если запрос начинается на get
        if "GET" in header:
            response_body = "You send a GetRequest. Take our response"
            response_header = "HTTP/1.1 200 OK\r\n"
            response_header += "Content-Type: text/html\r\n"
            response_header += f"Content-Length: {len(response_body)}\r\n"
            response_header += "Connection: close\r\n"
            response_header += "\r\n"
            response_header += response_body + "\r\n"
            client_socket.send(response_header.encode("utf-8"))
        if "POST" in header:
            # мы получили 2 числа в формате json
            # попробуем их спарсить
            try:
                json_dict = json.loads(body)
            except:
                response_header = "HTTP/1.1 400 Bad request\r\n"
                response_body = '{"error": "Invalid JSON format"}'
            # вроде спарсили мы это дело, теперь получим переменные
            a = json_dict.get("a");
            b = json_dict.get("b");
            # print(f"a: {a}, b: {b}")
            if b == 0:
                response_header = "HTTP/1.1 500 Internal Server Error \r\n"
                response_body = '{"error": "Internal Server Error"}'
            else:
                div_result = a / b
                div_result = str(div_result)
                response_header = "HTTP/1.1 200 OK\r\n"
                response_body = '{"result": "' + div_result + '"}'
            # а теперь наклепаем полноценный ответ серверу
            response_header += "Content-Type: application/json\r\n"
            response_header += f"Content-Length: {len(response_body)}\r\n"
            response_header += "Connection: close\r\n"
            response_header += "\r\n"
            response_header += response_body + "\r\n"
            # print(response_header)
            client_socket.send(response_header.encode("utf-8"))
        #мы вышли из цикла, сервер останавливает свою работу
    mm_out.insert(tk.END, "Сервер остановил работу!\n")
    server_status.set("Сервер не активен")
    bt_start.config(state=tk.NORMAL)
    bt_stop.config(state=tk.DISABLED)
    server_socket.close()
#----------------------------------------------------------------------------
def stop_server():
    global server_socket
    global server_working
    server_working = False
#----------------------------------------------------------------------------
#Запуск сервера не в потоке основного приложения
def launch_server():
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
#----------------------------------------------------------------------------

root = tk.Tk()
root.resizable(False, False)
root.title("HTTP Server")
frame = tk.Frame(root)
frame.pack()
#----------------------------------------------------------------------
#тут будут 2 кнопки - запуск сервера и остановка сервера
bt_start = tk.Button(frame, text="Запуск сервера", state=tk.NORMAL, command=launch_server)
bt_start.grid(row=0, column=0, padx=10, pady=10)
#кнопка остановить сервер
bt_stop = tk.Button(frame, text = "Стоп сервер", state=tk.DISABLED, command=stop_server)
bt_stop.grid(row=0, column=1, padx=10, pady=10)
#теперь текстовая метка со статусом сервера
server_status = tk.StringVar(value="Сервер не активен")
lb_status = tk.Label(frame, textvariable=server_status)
lb_status.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
#теперь текстовое поле для выведения сообщений от сервера
mm_out = tk.scrolledtext.ScrolledText(frame, width=100, height=20)
mm_out.delete("1.0", tk.END);
mm_out.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

#----------------------------------------------------------------------
root.mainloop()
