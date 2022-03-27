import socket # thư viện socket
from urllib.request import urlopen  # thư viện để web scraping dùng third party
import json # thư viện dùng JSON
import time # thư viện thời gian
import threading # thư viện thread
from tkinter import * # 4 dòng dùng thư viện tkinter
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from PIL import Image,ImageTk # Hình ảnh
from datetime import datetime # Thời gian theo ngày
HOST = ''
PORT = 8000
ADDR = (HOST, PORT)
date_time = ''

def changeOnHover(button, colorOnHover, colorOnLeave): # Hàm thay đổi màu khi di chuột vào và ra khỏi button
    # adjusting background of the widget
    # background on entering widget
    button.bind("<Enter>", func=lambda e: button.config(
        background=colorOnHover))

    # background color on leving widget
    button.bind("<Leave>", func=lambda e: button.config(
        background=colorOnLeave))

def update_data_every_1hour(): # Hàm cập nhật data mỗi 60 phút
    start_time = time.time() # Lấy thời gian bắt đầu chương trình
    while True: # Vòng lặp đếm khoảng thời gian
        end_time = time.time() #Lấy thời chương trình lúc sau
        if round(end_time - start_time) % 3600 == 0:
            # Nếu khoảng thời gian giữa start và end (làm tròn) chia hết cho 3600 giây thì sẽ cập nhật data 1 lần
            # Trường hợp này bao hàm cả cập nhật data lúc vừa khởi tạo (giây thứ 0) giúp server lấy thông tin mới nhất khi vừa chạy chương trình
            # Sau đó cứ mỗi 3600 giây sẽ cập nhật data từ web xuống file JSON một lần
            url = "https://coronavirus-19-api.herokuapp.com/countries" # 3 dòng: mở web,đọc data vào biến data_json
            response = urlopen(url)
            data_json = json.loads(response.read())
            with open('DataCovid19.json', 'w') as outfile: # 2 dòng mở file và lưu data dưới dạng JSON
                json.dump(data_json, outfile, indent=2) # indent = 2 giúp thụt đầu dòng đến đầu dòng thứ 2
            print('Đã cập nhật dữ liệu lần thứ', int(round(end_time-start_time)/3600)+1)
            now = datetime.now()
            global date_time
            date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

def send_initial_covid_data_to_client(): # Hàm thực hiện gửi data đã lưu vào file JSON cho client để client khởi tạo 'countries' dùng trong comboBox
    json_file = open('DataCovid19.json', 'r') # 3 dòng mở file JSON và đọc dữ liệu lên biến data
    jsondata = json_file.read()
    data = json.loads(jsondata)
    countries = ''
    for p in data: # Vòng lặp với chạy biến p lần lượt là các giá trị trong file:
        countries = countries + '|' + p['country']# Cộng dồn các giá trị country trong file dưới dạng countries = 'country1|country2|...'
    return countries # Giá trị trả về của hàm là chuỗi countries đã tạo

def handle_client(conn,addr): # Hàm chính để thực hiện trao đổi thông tin giữa server và client
    isFirstSend = True # Dùng để kiểm tra xem đã gửi dữ liệu ban đầu để khởi tạo 'countries' cho client chưa
    while True:
        try:
            if isFirstSend == True:
                isFirstSend = False # Nếu đã gửi dữ liệu ban đầu cho client để khởi tạo 'countries' thì biến này sẽ là False không thay đổi xuyên suốt chương trình
                initial_msg = send_initial_covid_data_to_client() # Thực hiện hàm đọc data ban đầu để gửi cho client
                conn.sendall(bytes(initial_msg, "utf8")) # Gửi data 'countries' cho client
            else: # Sau khi đã gửi data ban đầu
                msg = conn.recv(4096) # Chờ đợi nhận data từ client
                msg = msg.decode("utf8") # Giải mã data client gửi
                data = msg.split() # Cắt các dấu khoảng cách trong chuỗi data client gửi và đưa các giá trị về dạng list
                case = '' #data = ['MC', 'MC', '1']
                if data[0] == '':
                    conn.sendall(bytes('0', "utf8"))
                elif len(data) == 3 and (data[2] == '1' or data[2] == '2'): # Trường hợp đăng nhập và đăng ký
                    case = 1
                elif (len(data) == 1 and data[0] != '0') or (len(data) == 2 and data[0] != '1'): # Trường hợp quốc gia một và hai từ
                    case = 2
                elif len(data) == 3 and data[2] != '1' and data[2] != '2': # Trường hợp quốc gia 3 từ, thêm điều kiện chữ cuối không rơi vào case 1
                    case = 2
                elif len(data) >= 4: # Trường hợp quốc gia 4 từ trở lên
                    case = 2
                elif len(data) == 1 and data[0] == '0': # Trường hợp thoát chương trình
                    case = 3
                elif len(data) == 2 and data[0] == '1': # Trường hợp client đăng xuất
                    case = 4
                if case == 1: # Trường hợp gửi data dạng "username     password     'choice'" với choice = 1 hoặc 2
                    # Cấu trúc chuỗi trên được sử dụng cho cả đăng ký và đăng nhập, server chỉ cần split một lần
                    choice = data[2] # Lấy giá trị choice là biến thứ 3 trong list
                    def create_account(): # Hàm kiểm tra để tạo tài khoản
                        check = 1 # 1: không trùng usernames, 0: trùng usernames
                        signup_username = data[0] # Phần tử thứ 0 của list là username
                        signup_password = data[1] # Phần tử thứ 1 của list là password
                        usernames = ['user',] # Khởi tạo một list usernames để lưu các giá trị username đã tồn tại trong dữ liệu server
                        passwords = ['pass',] # Khởi tạo một list passwords để lưu các giá trị password đã tồn tại trong dữ liệu server
                        with open("Account.txt", 'r') as infile: # Mở file chứa thông tin các tài khoản đã tồn tại
                            try:
                                for line in infile: # Đọc các dòng trong file
                                    if not line: # Nếu không còn dòng thì ngưng vòng lặp
                                        break
                                    line1 = infile.readline(200) # line1 sẽ là dữ liệu dòng tương ứng với các username
                                    line2 = infile.readline(200) # line2 sẽ là dữ liệu dòng tương ứng với các password
                                    usernames.append(line1) # Thêm giá trị line1 vào list usernames
                                    passwords.append(line2) # Thêm giá trị line2 vào list passwords
                            except:
                                caution = "Errors in appending occurred"
                                txtbox_2.insert(tk.END, caution) # Thêm thông báo lỗi lệnh vào box 2
                        for name in usernames: # chạy vòng lặp tìm tên trong list usernames
                            name = name.strip('\n') # Cắt đi giá trị \n ở cuối chuỗi của phần tử đang được đọc (nếu có '\n')
                            if name == signup_username: # Nếu phần tử đó trùng với giá trị username mà client đã nhập thì trả check về 0
                                check = 0   # Trùng, đã có username
                                break
                        try:
                            with open('Account.txt', 'a') as file: # Mở file để ghi lại dữ liệu account mới
                                if check == 0: # Nếu check = 0 thì gửi '0' về client để client báo tên đăng ký đã tồn tại
                                    msg = '0'
                                    conn.sendall(bytes(msg, "utf8"))
                                elif check == 1:
                                    # Nếu check = 1 thì gửi '1' về client để client báo tạo tài khoản thành công và
                                    # server sẽ lưu thêm username và password đã nhập ở cuối file
                                    txtbox.config(state='normal')
                                    txtbox.insert(tk.END,str(addr) + ' created account: ' + signup_username + '\n')  # Thêm thông báo đăng nhập vào box 1
                                    txtbox.config(state='disabled')
                                    msg = '1'
                                    conn.sendall(bytes(msg, "utf8"))
                                    file.write('\n' + signup_username)
                                    file.write('\n' + signup_password)
                                    file.write('\n-----')
                        except:
                            caution = "Error in writing data"
                            txtbox_2.insert(tk.END, caution) # Thêm thông báo lỗi lệnh vào box 2
                    def check_to_sign_in(): # Hàm kiểm tra để đăng nhập tài khoản
                        pos = 0 # Biến vị trí của username trong list
                        check = 0 # 1: trùng account, 0: không trùng account
                        signin_username = data[0] # Phần tử thứ 0 của list đã được split là username
                        signin_password = data[1] # Phần tử thứ 1 của list đã được split là password
                        usernames = ['user',] # tạo list usernames
                        passwords = ['pass',] # tạo list passwords
                        with open("Account.txt", 'r') as infile: # Đọc file
                            try:
                                for line in infile:
                                    if not line: # Nếu cuối file thì thoát vòng lặp
                                        break
                                    line1 = infile.readline(200) # line1 sẽ là dữ liệu dòng tương ứng với các username
                                    line2 = infile.readline(200) # line2 sẽ là dữ liệu dòng tương ứng với các password
                                    usernames.append(line1) # thêm line1 vào list usernames
                                    passwords.append(line2) # thêm line2 vào list passwords
                            except:
                                caution = "Errors in appending occurred"
                                txtbox_2.config(state='normal')
                                txtbox_2.insert(tk.END, caution)  # Thêm thông báo lệnh thất bại vào box 2
                                txtbox_2.config(state='disabled')
                        for name in usernames: # với tên trong list usernames
                            name = name.strip('\n') # # Cắt đi giá trị \n ở cuối chuỗi của phần tử đang được đọc (nếu có '\n')
                            if name == signin_username: # nếu trùng username thì thoát vòng lặp
                                break
                            pos += 1 # Qua mỗi vòng lặp biến 'pos' sẽ tăng lên một đơn vị biểu thị vị trí hiện tại của signin_username trong list
                        if pos < len(passwords)-1: # Nếu 'pos' không vượt quá giá trị thứ n-1 của list thì đã tồn tại username mà client nhập
                            try:
                                temp = 0 # biểu thị vị trí của biến name trong passwords
                                for name in passwords: # Kiểm tra password tương tự cách của username như trên
                                    name = name.strip('\n')
                                    if name == signin_password and pos == temp: # Nếu mật khẩuđã tồn tại và khớp với vị trí của username thì biến check bằng 1 và thoát loop
                                        check = 1
                                        break
                                    temp += 1 # Qua mỗi vòng lặp biến 'temp' sẽ tăng lên một đơn vị biểu thị vị trí hiện tại của signin_password trong list
                                if check == 1: # Nếu biến check = 1 thì gửi về cho client để báo đăng nhập thành công
                                    msg = '1'
                                    txtbox.config(state='normal')
                                    txtbox.insert(tk.END, str(addr) + ' signed in to '+ signin_username + '\n')  # Thêm thông báo đăng nhập vào box 1
                                    txtbox.config(state='disabled')
                                    conn.sendall(bytes(msg, "utf8"))
                                elif check == 0: # Nếu biến check = 0 thì gửi về cho client để báo sai tài khoản hoặc mật khẩu
                                    msg = '0'
                                    conn.sendall(bytes(msg, "utf8"))
                            except:
                                caution = 'Sign-in errors'
                                txtbox_2.config(state='normal')
                                txtbox_2.insert(tk.END, caution)  # Thêm thông báo lệnh thất bại vào box 2
                                txtbox_2.config(state='disabled')
                        else: # Trường hợp 'pos' lớn hơn yêu cầu sẽ gửi về cho client báo sai tài khoản hoặc mật khẩu
                            check = 0
                            msg = '0'
                            conn.sendall(bytes(msg, "utf8"))
                    if choice == '1': # Nếu lựa chọn của client bằng 1 sẽ thực hiện việc đăng ký tài khoản
                        create_account()
                    elif choice == '2': # Nếu lựa chọn của client bằng 2 sẽ thực hiện việc đăng nhập tài khoản
                        check_to_sign_in()
                elif case == 2: # Nếu độ dài của data sau khi split mà client gửi bằng 1 thì sẽ thực hiện việc truyền data covid cho client
                    country_name = ''
                    for name in data:
                        country_name = country_name + ' ' + name
                    country_name = country_name.lstrip().rstrip()
                    json_file = open('DataCovid19.json', 'r') # 3 dòng đọc file JSON
                    jsondata = json_file.read()
                    filedata = json.loads(jsondata)
                    info = '' # Khởi tạo biến tạo chuỗi gửi cho client
                    for p in filedata: # Cho vòng lặp chạy trong data JSON
                        country = p['country'].strip('\n') # tạo biến country bằng với giá trị 'country' lưu trong json bỏ đi '\n' (nếu có)
                        if country == country_name: # Nếu quốc gia đã nhập khớp với quốc gia có trong list sẽ thực hiện lệnh sau
                            try:
                                info = p['country'] + "|"
                                info = info + str(p['cases']) + "|"
                                info = info + str(p['todayCases']) + "|"
                                info = info + str(p['deaths']) + "|"
                                info = info + str(p['todayDeaths']) + "|"
                                info = info + str(p['recovered']) + "|"
                                info = info + str(p['active']) + "|"
                                info = info + str(p['critical']) + "|"
                                info = info + str(p['casesPerOneMillion']) + "|"
                                info = info + str(p['deathsPerOneMillion']) + "|"
                                info = info + str(p['totalTests']) + "|"
                                info = info + str(p['testsPerOneMillion'])+ "|"
                                global date_time
                                info = info + date_time
                                # Chuỗi info có dạng: country|World|cases|3500000|todayCases|...
                            except:
                                caution = 'Fail to connect data\n'
                                txtbox_2.config(state='normal')
                                txtbox_2.insert(tk.END, caution)  # Thêm thông báo lệnh thất bại vào box 2
                                txtbox_2.config(state='disabled')
                            break
                    msg = info
                    conn.sendall(bytes(msg, "utf8")) # gửi chuỗi về cho client
                elif case == 3: # nếu số phần tử của biến data > 3 biểu thị việc kết thúc dữ liệu (do chỉ có chuỗi client có nhiều hơn 3 từ)
                    caution = 'Disconnected to' + str(addr) + '\n'  # Báo client đã ngắt kết nối với server và thoát vòng lặp của client
                    txtbox_2.config(state='normal')
                    txtbox_2.insert(tk.END, caution)  # Thêm thông báo lệnh thất bại vào box 2
                    txtbox_2.config(state='disabled')
                    break
                elif case == 4:
                    caution = str(addr) + ' sign out of ' + str(data[1]) +'\n'  # Báo client đã ngắt kết nối với server và thoát vòng lặp của client
                    txtbox_2.config(state='normal')
                    txtbox_2.insert(tk.END, caution)  # Thêm thông báo lệnh thất bại vào box 2
                    txtbox_2.config(state='disabled')
        except:
            caution = 'Disconnected to' + str(addr) + '\n' # Báo client đã ngắt kết nối với server và thoát vòng lặp của client
            txtbox_2.config(state='normal')
            txtbox_2.insert(tk.END, caution) # Thêm thông báo lệnh thất bại vào box 2
            txtbox_2.config(state='disabled')
            break
    conn.close()

def ask_if_exit(exit_button):
    check_quit = messagebox.askokcancel("Thoát", "Bạn có muốn thoát chương trình?")
    # Tạo message box hỏi xem có thật sự muốn thoát chươg trình không
    if check_quit == True:  # Nếu chọn thoát thì gửi data với độ dài bằng 4 (sẽ rơi vào trường hợp (len(data)) > 3 trong hàm handle_client bên server)
        root.destroy()
        exit()

def create_exit_button(): # Hàm tạo nút thoát khỏi widget server
    exit_button = Button(root, command=lambda: ask_if_exit(exit_button), text='Exit', activebackground='Light salmon', fg='black', font=('Arial', 9))
    exit_button.place(x=362, y=533)
    changeOnHover(exit_button, 'DarkOliveGreen1', 'SystemButtonFace')

def main_function(): # Hàm dùng thread để kết nối với các client khi địa chỉ IP client nhập là hợp lệ
    global root
    global txtbox
    global txtbox_2
    root = tk.Tk() # 4 dòng khởi tạo widget server
    root.geometry('405x585')  # Kích thước root: 400 x 520
    root.title("Server")  # Tên widget là Welcome
    root.resizable(False, False)
    load = Image.open("covid_outbreak.jpg")  # 5 dòng: lấy và hiển thị hình ảnh trong widget
    load = load.resize((410,600))
    render = ImageTk.PhotoImage(load)
    img = Label(root, image=render)
    img.place(x=-5, y=0)
    title = tk.Label(root, fg='black', bg='white', font=('Arial', 15, 'bold'))  # 3 dòng tạo tiêu đề
    title.place(x=130, y=15)
    title.config(text='Quản lý kết nối')
    group1 = LabelFrame(root, text="Kết nối", padx=5, pady=5) # 2 dòng tạo Frame thứ 1
    group1.grid(row=1, column=0, columnspan=3, padx=15, pady=70, sticky=E + W + N + S)
    txtbox = scrolledtext.ScrolledText(group1, width=43, height=10) # 2 dòng tạo text box thứ 1 với thanh scroll bar
    txtbox.grid(row=1, column=0, sticky=E + W + N + S)
    txtbox.config(state='disabled')
    group2 = LabelFrame(root, text="Mất kết nối", padx=5, pady=5) # 2 dòng tạo Frame thứ 2
    group2.grid(row=2, column=0, columnspan=3, padx=15, pady=0, sticky=E + W + N + S)
    txtbox_2 = scrolledtext.ScrolledText(group2, width=43, height=10) # 2 dòng tạo text box thứ 2 với thanh scroll bar
    txtbox_2.grid(row=2, column=0, sticky=E + W + N + S)
    txtbox_2.config(state='disabled')
    thread_timer = threading.Thread(target=update_data_every_1hour, daemon = True)  # Cho thread đầu tiên với hàm cập nhật data mỗi 60 phút
    thread_timer.start()  # Khởi động thread đầu tiên
    print('Đã kết nối bộ đếm giờ')
    def start_socket():
        txtbox.config(state='normal')
        txtbox.insert(tk.END, "Waiting for clients...\n")  # In ra trạng thái chờ client
        txtbox.config(state='disabled')
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 3 dòng khởi tạo socket
        s.bind(ADDR)
        s.listen()
        while True:
            conn, addr = s.accept()  # Chờ đợi đến khi có một client kết nối
            thread = threading.Thread(target=handle_client, args=(conn, addr))  # Tạo thread với mỗi client
            thread.start()  # Khởi động thread của server đã kết nối
            info = 'Connected by' + str(addr) + '\n'  # In ra thông báo kết nối với client với địa chỉ tương ứng
            txtbox.config(state='normal')
            txtbox.insert(tk.END, info) # Thêm thông báo kết nổi vào cuối của text box thứ 1
            txtbox.config(state='disabled')
    def start_thread_socket(): # Tạo thread để khởi động socket (do bị lồng vòng lặp với mainloop nên không dùng chung thread được)
        start_button.config(state='disabled')
        changeOnHover(start_button, 'SystemButtonFace', 'SystemButtonFace')
        thread1 = threading.Thread(target=start_socket, daemon = True)
        thread1.start()
    def create_start_button(): # Tạo nút bắt đầu khởi động socket
        global start_button
        start_button = Button(root, command=start_thread_socket, text='Start', activebackground='Light salmon',fg='black', font=('Arial', 9))
        start_button.place(x=356, y=270)
        changeOnHover(start_button, 'DarkOliveGreen1', 'SystemButtonFace')
    create_start_button()
    create_exit_button()
    def on_closing():  # Nhận diện nút X thoát chương trình
        check = messagebox.askokcancel("Thoát", "Bạn có muốn thoát chương trình?")
        if check == True:
            root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

main_function()