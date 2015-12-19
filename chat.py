#! /usr/bin/env python3

import socket
import threading
from tkinter import *

MAXLEN = 10000
SERVER_PORT = 3000
USER_NAME = "abc"

def message_encode(method, name, text):
	data = "{} {} {}\r\n{}".format(method, len(text), USER_NAME, text)
	return data.encode()

def message_decode(message):
	items = message.split(" ")
	return (items[0], int(items[1]), " ".join(items[2:]))

def response_encode(state, reason):
	data = "RESPONSE {} {}\r\n".format(state, reason)
	return data.encode()

def response_decode(response):
	items = response.split(" ")
	return (items[0], int(items[1]), " ".join(items[2:]))

def server_doit(conn):
	message = ""
	while True:
		message += conn.recv(1024).decode()
		pos = message.find("\r\n")
		if pos!=-1:
			(method, length, name) = message_decode(message[:pos])
			text = message[pos+2:]
			break

	while len(text)<length:
		text += conn.recv(1024).decode()
	
	if method=="SEND":
		msg_box = Message(msg_frame, background="lightgreen", width=320, font="Arial", text=name+": "+text, anchor=W)
		msg_box.pack(pady=5, fill=X, expand=1)
		conn.sendall(response_encode(100, "OK"))
	else:
		conn.sendall(response_encode(202, "Bad Request"))
	conn.close()

def client_doit(text):
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client.connect((remote_host, remote_port))
		client.sendall(message_encode("SEND", USER_NAME, text))
		response = ""
		while True:
			response += client.recv(1024).decode()
			pos = response.find("\r\n")
			if pos!=-1:
				(mask, state, reason) = response_decode(response[:pos])
				break
		client.close()
		msg_box = Message(msg_frame, background="lightblue", width=320, font="Arial", text=text, anchor=E)
		msg_box.pack(pady=5, fill=X, expand=1)
		text_area.delete("1.0", END)
		state_bar["text"] = "State: {} {}".format(state, reason)
		state_bar["background"] = "green"
	except socket.error:
		state_bar["text"] = "State: 201 Connection refused"
		state_bar["background"] = "red"

def start_server():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(("", SERVER_PORT))
	server.listen(1)
	while not quit:
		conn, addr = server.accept()
		server_doit(conn)
		conn.close()

remote_host, remote_port = input("Enter remote address: ").split(":")
remote_port = int(remote_port)
server_thread = threading.Thread(target=start_server)
server_thread.start()
quit = False

# build GUI
app = Tk(className="socketChat")
app.config(padx=10, pady=10)
top_bar = Label(app, text=USER_NAME, font="Arial 15 bold")
top_bar.pack()

middle_frame = Frame(app)
middle_frame.pack(pady=10)

msg_frame = Frame(middle_frame)
msg_frame.pack(pady=5, fill=X, expand=1)

text_frame = Frame(middle_frame)
text_frame.pack(pady=5)
text_area = Text(text_frame, height=3, width=50, font="Arial")
text_area.pack(fill=Y, side="left")
text_scroll = Scrollbar(text_frame, command=text_area.yview)
text_scroll.pack(fill=Y, side="right")
text_area.config(yscrollcommand=text_scroll.set)

send_btn = Button(middle_frame, text="Send", font="Arial", command=lambda: client_doit(text_area.get("1.0", "end-1c")))
send_btn.pack()

state_bar = Message(app, text="Ready to send a message.", font="Arial", background="grey", width=300, foreground="white", anchor=W)
state_bar.pack(fill=X, expand=1)
app.mainloop()

server_thread.join()

