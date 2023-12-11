import socket
import threading
import json
from datetime import datetime
import os

# 存儲在線用戶的信息
online_users = {}
USER_DATA = 'User_data.json'
ONLINE_USERS = 'online_users.json'

# 處理客戶端連線
def handle_client(client, username):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "LOGOUT":
                # 如果客戶端發送 "LOGOUT" 訊息，則從在線用戶中刪除該用戶
                online_users.pop(username)
                save_online_users()
                client.close()
                break
            else:
                # 廣播用戶的訊息給所有在線用戶
                broadcast(f"{message}", username)
                # 儲存訊息
                save_message(username, message)
        except:
            # 發生錯誤時，從在線用戶中刪除該用戶
            online_users.pop(username)
            save_online_users()
            client.close()
            break

# 處理身份驗證（登入或註冊）
def handle_auth(msg, client):
    auth_type, username, password = msg.split()
    if auth_type == "LOGIN":
        if login(username, password):
            # 登入成功，回傳 "Login successful" 並將用戶添加到在線用戶列表
            print(f"Login successful for {username}")
            client.send("Login successful".encode('utf-8'))
            online_users[username] = client
            save_online_users()
            return username
        else:
            # 登入失敗，回傳 "Login failed"
            print(f"Login failed for {username}")
            client.send("Login failed".encode('utf-8'))
    elif auth_type == "REGISTER":
        if register(username, password):
            # 註冊成功，回傳 "Registration successful" 並將用戶添加到在線用戶列表
            print(f"Registration successful for {username}")
            client.send("Registration successful".encode('utf-8'))
            online_users[username] = client
            save_online_users()
            return username
        else:
            # 註冊失敗，回傳 "Registration failed"
            print(f"Registration failed for {username}")
            client.send("Registration failed".encode('utf-8'))

# 儲存在線用戶列表到文件
def save_online_users():
    with open(ONLINE_USERS, 'w') as wfp:
        json.dump(list(online_users.keys()), wfp)

# 登入函數
def login(username, password):
    try:
        with open(USER_DATA, 'r') as rfp:
            users = json.load(rfp)
            if users.get(username) == password:
                return True
    except FileNotFoundError:
        pass
    return False

# 註冊函數
def register(username, password):
    try:
        with open(USER_DATA, 'r') as rfp:
            users = json.load(rfp)
    except FileNotFoundError:
        users = {}
    if username in users:
        return False
    users[username] = password
    with open(USER_DATA, 'w') as wfp:
        json.dump(users, wfp)
    return True

# 廣播訊息給所有在線用戶
def broadcast(message, sender):
    for username, client in online_users.items():
        if username != sender:
            client.send(message.encode('utf-8'))

# 儲存用戶的訊息到文件
def save_message(username, message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_message = {
        "username": username,
        "content": message,
        "message_at": current_time
    }
    with open('message.json', 'a') as wfp:
        json.dump(new_message, wfp)
        wfp.write('\n')

# 主程式
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 6667))
    server.listen()

    # 檢查 message.json 和 online_users.json 是否存在，如果不存在則建立它們
    if not os.path.exists('message.json'):
        with open('message.json', 'w') as wfp:
            json.dump([], wfp)
    if not os.path.exists(ONLINE_USERS):
        with open(ONLINE_USERS, 'w') as wfp:
            json.dump([], wfp)

    while True:
        client, addr = server.accept()
        # 處理身份驗證，並獲得用戶名稱
        username = handle_auth(client.recv(1024).decode('utf-8'), client)
        if username:
            # 如果身份驗證成功，則啟動處理客戶端的線程
            thread = threading.Thread(target=handle_client, args=(client, username))
            thread.start()
            print(f"Connection from {addr} has been established!")

if __name__ == "__main__":
    main()
