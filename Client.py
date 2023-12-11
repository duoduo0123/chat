import socket
import threading

# 用於存儲身份驗證狀態的全域變數
auth_status = None

# 用於發送訊息給伺服器的函式
def send(msg):
    client.send(msg.encode('utf-8'))

# 用於接收伺服器訊息的函式
def receive():
    global auth_status
    while True:
        try:
            # 接收伺服器發來的訊息
            message = client.recv(1024).decode('utf-8')
            # 如果訊息為 "Registration successful" 或 "Login successful"，將 auth_status 設為該訊息
            if message in ["Registration successful", "Login successful"]:
                auth_status = message
            print(message)
        except:
            print("An error occurred.")
            client.close()
            break

# 用於處理登入或註冊的函式
def login_or_register():
    global username, auth_status
    while True:
        print("\nOptions:")
        print("1. Login")
        print("2. Register")
        option = input("Enter your choice: ")

        if option == '1':
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            send(f"LOGIN {username} {password}")
        elif option == '2':
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            send(f"REGISTER {username} {password}")

        # 等待 auth_status 被設置為非 None，即等待伺服器的回應
        while auth_status is None:
            pass  # Wait for the response

        # 如果 auth_status 為 "Registration successful" 或 "Login successful"，則重置 auth_status 並返回用戶名稱
        if auth_status in ["Registration successful", "Login successful"]:
            auth_status = None  # Reset the status
            return username

# 用於發送訊息的函式
def send_message(msg, username):
    client.send(f"{username}: {msg}".encode('utf-8'))

# 主選單函式
def main_menu(username):
    while True:
        msg = input("Enter your message (or 'menu' to show the menu): ")
        if msg == 'menu':
            print("\nMain Menu:")
            print("1. Send a message")
            print("2. Send a private message")
            print("3. Logout")
            option = input("Enter your choice: ")

            if option == '1':
                msg = input("Enter your message: ")
                send_message(msg, username)
            elif option == '2':
                recipient = input("Enter the recipient's username: ")
                msg = input("Enter your message: ")
                send_message(f"PRIVATE {recipient} {msg}", username)
            elif option == '3':
                send_message("LOGOUT", username)
                break
        else:
            send_message(msg, username)

# 主程式
def main():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 6667))

    # 啟動接收伺服器訊息的線程
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    # 進行登入或註冊，獲得用戶名稱
    username = login_or_register()

    # 如果成功登入或註冊，進入主選單
    if username:
        main_menu(username)

    # 等待接收線程結束
    receive_thread.join()

# 程式進入點
if __name__ == "__main__":
    main()
