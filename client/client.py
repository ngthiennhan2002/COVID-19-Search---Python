import socket                       #thư viện socket
import os                           #thư viện hệ thống
import tkinter as tk                #thư viện khởi tạo đồ họa GUI, dùng dưới dạng tk
from tkinter import messagebox      #thư viện tkinter dùng để tạo Message Box
from tkinter import *               #dùng tạo Tk trong Tkinter
from PIL import Image,ImageTk       #Thư viện dùng để truy xuất hình ảnh vào màn hình đồ họa
from tkinter import ttk             #dùng ttk trong tkinter để tạo combobox trong main window
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ".\\platform\\"
host_name = socket.gethostname()
HOST = socket.gethostbyname(host_name)

def changeOnHover(button, colorOnHover, colorOnLeave): # Hàm thay đổi màu khi di chuột vào và ra khỏi button
    # adjusting backgroung of the widget
    # background on entering widget
    button.bind("<Enter>", func=lambda e: button.config(
        background=colorOnHover))

    # background color on leving widget
    button.bind("<Leave>", func=lambda e: button.config(
        background=colorOnLeave))

def set_socket(HOST): # Hàm khởi tạo vào kết nối client với server
    try:
        PORT = 8000
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        s.connect(server_address)
        return True
    except:
        return False

def receive_initial_covid_data(): # Hàm nhận dữ liệu covid ban đầu server gửi để khởi tạo biến 'countries' trong client combobox
    data = s.recv(4096) # Nhận data từ server
    msg = data.decode("utf8") # Giải mã data
    countries = msg.split('|') # Cắt chuỗi data gửi cách nhau bởi dấu "|" để tạo thành một list chứa tên các quốc gia
    return countries # Trả về giá trị list countries cho hàm

def format_main_window(root,a,sign_in_window): # Hàm khởi tạo màn hình tra cứu thông tin COVID-19
    info_window = tk.Toplevel(root) # Tạo một widget con của widget gốc
    info_window.geometry('500x200') # Kích thước 500 x 200
    info_window.resizable(False, False) # Không cho thay đổi kích thước widget
    info_window.title("COVID-19") # Cài tên widget
    title = Label(info_window, fg='black', font=('Arial', 20, 'bold')) # 3 dòng tạo tiêu đề cho widget
    title.place(x=62, y=13)
    title.config(text='App tra cứu dữ liệu COVID-19')
    auxillary_title = Label(info_window, fg='black', font=('Arial', 10, 'underline')) # 3 dòng tạo dòng chữ "Chọn quốc gia:"
    auxillary_title.place(x=80, y=90)
    auxillary_title.config(text='Chọn quốc gia:')
    account_label = Label(info_window, fg='black', font=('Arial', 9)) # 3 dòng tạo dòng chữ "Tên đăng nhập:"
    account_label.place(x=190, y=50)
    account_label.config(text='Tên đăng nhập: ')
    name_label = Label(info_window, fg='blue', font=('Arial', 9)) # 3 dòng tạo dòng hiển thị tên đã nhập trong cửa sổ đăng nhập trước đó
    name_label.place(x=282, y=50)
    name_label.config(text=a)
    n = StringVar() # Khởi tạo biến n biểu diễn chuỗi nhập trong comboBox
    country_chosen = ttk.Combobox(info_window, state='readonly',width = 28, textvariable=n,values=countries) # 2 dòng khởi tạo comboBox
    country_chosen.place(x=177,y=92)
    def sign_out(): # Hàm thực hiện đăng xuất sau khi bấm vào nút "Đăng xuất"
        check = messagebox.askokcancel("Đăng xuất", "Bạn có xác nhận đăng xuất?") # Tạo message box hỏi xem người dùng có thật sự muốn đăng xuất hay không
        if check == True: # Nếu chọn xác nhận đăng xuất sẽ thực hiện hủy widget tra cứu covid hiện tại và hiển thị lại cửa sổ đăng nhập trước đó
            try:
                msg = '1 ' + a
                s.sendall(bytes(msg, "utf8"))  # Mã hóa và gửi data cho server
            except:
                messagebox.showwarning("Warning", "Server disconnected")  # Báo lỗi nếu mất kết nối server
                root.destroy()
                s.close()
            info_window.destroy() # Hủy cửa sổ tra cứu hiện tại
            sign_in_window.deiconify() # Tái hiện thị cửa sổ đăng nhập
    def send_country_to_server(): # Hàm gửi tên quốc gia muốn tra cứu sau khi bấm nút 'Tìm kiếm'
        msg = n.get() # Biến msg nhận giá trị nhập vào comboBox
        try:
            s.sendall(bytes(msg,"utf8")) # Gửi data cho server
        except:
            messagebox.showwarning("Warning", "Server disconnected") # Tạo box báo lỗi kết nối nếu mất kết nối
            info_window.withdraw()
            root.close()
        amount_received = 0 # Độ dài của chuỗi server gửi cho client
        amount_expected = len(msg) # Độ dài của data client gửi đi
        while amount_received < amount_expected: # Nếu client chưa nhận được data từ server
            try:
                global data
                data = s.recv(4096) # Chờ server gửi data
                msg = data.decode("utf8") # Giải mã data
                amount_received += len(data) # Tăng số lượng amount_received lên để thoát khỏi vòng lặp
                break
            except:
                messagebox.showwarning("Warning", "Server disconnected") # Tạo bảng cảnh báo server đã mất kết nối
                info_window.withdraw()
                root.close()
        if msg != '':
            msg = msg.split('|') # Cắt chuỗi data server gửi bằng cách cắt đi các dấu '|' và đưa msg về dạng list
            info_window.geometry('500x440') # Tạo lại kích thước của widget tra cứu với chiều ngang giữ nguyên còn chiều dọc tăng lên để hiển thị data
            T = Text(info_window, height=13, width=57) # 7 dòng tạo ô text box và hiển thị data bên dưới mục tra cứu
            T.place(x=20,y=200)
            T.config(state='normal')
            Information = 'Tính đến: ' + msg[12]
            Information = Information + '\nQuốc gia: ' + msg[0] + '\nSố ca: ' + msg[1] + '\nSố ca hôm nay: '+msg[2]+'\nSố người tử vong: '+msg[3]
            Information = Information +'\nSố tử vong hôm nay: '+msg[4] + '\nSố hồi phục: '+msg[5]+'\nSố người đang nhiễm: '+msg[6]
            Information = Information + '\nSố ca nặng: '+msg[7]+'\nSố ca trên 1 triệu dân: '+msg[8]+'\nSố tử vong trên 1 triệu dân: '+msg[9]
            Information = Information + '\nTổng số xét nghiệm: '+msg[10]+'\nSố xét nghiệm trên 1 triệu dân: '+msg[11]
            T.insert(tk.END, Information)
            T.config(state='disabled')
            country_chosen.set('')
        else:
            info_window.geometry('500x200')
    def create_search_button(): # Tạo nút tìm kiếm với liên kết dẫn đến hàm gửi data cho server
        search_button = Button(info_window, command=send_country_to_server, text='Tìm kiếm', activebackground='Light salmon', fg='black', font=('Arial', 9))
        search_button.place(x=390, y=130)
        changeOnHover(search_button, 'LightGoldenrod1', 'SystemButtonFace')
    def change_to_a_to_z(): # Hàm thay đổi sắp xếp lại list countries với các giá trị tăng dần
        countries[1:] = sorted(countries[1:]) # sắp xếp tăng dần
        create_z_to_a_button() # hiển thị nút sắp xếp giảm dần
        country_chosen = ttk.Combobox(info_window, width=28, state='readonly',textvariable=n, values=countries) # khởi tạo lại combobox sau khi thay đổi thứ tự
        country_chosen.place(x=177, y=92)
    def create_a_to_z_button(): # Khởi tạo nút 'A-Z' sau khi bấm vào 'Z-A'
        a_to_z_button = Button(info_window, command=change_to_a_to_z, text='A-Z',fg='black', font=('Arial', 9)) # tạo nút dẫn đến hàm sắp xếp tăng dần
        a_to_z_button.place(x=380, y=91)
        changeOnHover(a_to_z_button, 'LightGoldenrod1', 'SystemButtonFace')
    def change_to_z_to_a(): # Hàm thay đổi sắp xếp lại list countries với các giá trị giảm dần
        countries[1:] = sorted(countries[1:], reverse=True) # sắp xếp giảm dần
        create_a_to_z_button() # hiển thị nút sắp xếp tăng dần
        country_chosen = ttk.Combobox(info_window, width=28, state='readonly',textvariable=n, values=countries) # khởi tạo lại combobox sau khi thay đổi thứ tự
        country_chosen.place(x=177, y=92)
    def create_z_to_a_button(): # Khởi tạo nút 'Z-A' sau khi bấm vào 'A-Z'
        z_to_a_button = Button(info_window, command=change_to_z_to_a, text='Z-A', activebackground='Light salmon',fg='black', font=('Arial', 9)) # tạo nút dẫn đến hàm sắp xếp giảm dần
        z_to_a_button.place(x=380, y=91)
        changeOnHover(z_to_a_button, 'LightGoldenrod1', 'SystemButtonFace')
    def quit_program(): # Thực hiện thoát client sau khi chọn nút 'Thoát'
        check_quit = messagebox.askokcancel("Thoát", "Bạn có muốn thoát chương trình?") # Tạo message box hỏi xem có thật sự muốn thoát chươg trình không
        if check_quit == True: # Nếu chọn thoát thì gửi data với độ dài bằng 4 (sẽ rơi vào trường hợp (len(data)) > 3 trong hàm handle_client bên server)
            s.sendall(bytes('0',"utf8")) # gửi chuỗi cho server báo client thoát chương trình
            root.destroy() # Hủy widget root để hủy toàn bộ các cửa sổ widget
            s.close()
    def create_quit_program_button(): # Tạo nút "Thoát" trong màn hình tra cứu
        quit_button = Button(info_window, command=quit_program, text='Thoát', activebackground='Light salmon',fg='black', font=('Arial', 9))
        quit_button.place(x=174, y=130)
        changeOnHover(quit_button, 'LightGoldenrod1', 'SystemButtonFace')
    create_search_button() # Tạo nút "Tìm kiếm" khi bắt đầu khởi tạo cửa sổ tra cứu chính
    create_quit_program_button() # Tạo nút "Thoát" khi bắt đầu khởi tạo cửa sổ tra cứu chính
    sign_out_button = Button(info_window, command=sign_out, text='Đăng xuất', activebackground='Light salmon',fg='black', font=('Arial', 9)) # Khởi tạo nút "Đăng xuất"
    sign_out_button.place(x=42, y=130)
    changeOnHover(sign_out_button, 'LightGoldenrod1', 'SystemButtonFace')
    create_z_to_a_button() # Tạo nút "Z-A" khi bắt đầu khởi tạo cửa sổ tra cứu chính
    def on_closing():  # Nhận diện nút X thoát chương trình
        if messagebox.askokcancel("Thoát", "Bạn có muốn thoát chương trình?"):
            root.destroy()
    info_window.protocol("WM_DELETE_WINDOW", on_closing)

def save_account_data(a, b, choice, s): # Hàm truyền dữ liệu account cho server
    try:
        msg = a + '    ' + b + '    ' + choice # Khởi tạo chuỗi có dạng username    password    choice (với choice = 1 hoặc 2)
        s.sendall(bytes(msg, "utf8")) # Mã hóa và gửi data cho server
        amount_received = 0 # Độ dài của chuỗi server gửi cho client
        amount_expected = len(msg) # Độ dài của chuỗi client gửi đi
        while amount_received < amount_expected: # Lặp cho đến khi server gửi data cho client
            data = s.recv(4096) # Client nhận data
            msg = data.decode("utf8") # Giải mã data
            amount_received += len(data) # thay đổi độ dài của amount_received
            if msg == '0': # Nếu data nhận được = '0' thì trả hàm về 0 (Đăng kí hoặc đăng nhập không thành công)
                return 0
            elif msg == '1': # Nếu data nhận được = '1' thì trả hàm về 1 (Đăng kí hoặc đăng nhập thành công)
                return 1
    except:
        messagebox.showwarning("Warning","Server disconnected") # Báo lỗi nếu mất kết nối server
        root.destroy()
        s.close()

def firstmenu(root): # Hàm chính thực hiện các cửa sổ welcome và sign out/sign in
    global host_input
    global HOST
    host_input = StringVar() # Tạo biến nhập IP
    root.geometry('400x400') # Kích thước root: 400 x 400
    root.title("Welcome") # Tên widget là Welcome
    root.resizable(False, False) # Không cho thay đổi kích thước widget
    title = Label(root, fg='black', font=('Arial', 15)) # 3 dòng tạo tiêu đề
    title.place(x=65,y=15)
    title.config(text='App tra cứu dữ liệu COVID-19')
    load = Image.open("first_widget_image.jpg") # 4 dòng: lấy và hiển thị hình ảnh trong widget
    render = ImageTk.PhotoImage(load)
    img = Label(root, image=render)
    img.place(x=70, y=55)
    label_IP = Label(root, text='Nhập IP: ', fg='black', font=('Arial', 11)) # Tạo label hiển thị chữ "Nhập IP:"
    label_IP.place(x=170,y=290)
    textbox_IP = Entry(root, textvariable=host_input, fg='black', font=('Arial', 11)) # Tạo box entry cho nhập địa chỉ IP
    textbox_IP.place(x=120, y=320)
    def signup_menu():
        sign_in_window = tk.Toplevel(root) # Khởi tạo widget sign up/sign in
        sign_in_window.geometry('330x400') # Kích thước 330 x 500
        sign_in_window.resizable(False, False) # Không cho phép thay đổi kích thước
        sign_in_window.title("Sign up/Sign in") # Tên widget
        sign_up_username = StringVar() # 5 dòng: Khai báo tên đăng nhập, mật khẩu, xác nhận mật khẩu cho đăng ký và tên đăng nhập, mật khẩu cho mục đăng nhập
        sign_up_password = StringVar()
        sign_up_check_password = StringVar()
        sign_in_username = StringVar()
        sign_in_password = StringVar()
        label_1=Label(sign_in_window,text='Tên đăng ký ',fg='black',font=('Arial',11)) # Tạo label "Tên đăng nhập" cho việc đăng ký
        label_1.grid(row=0,column=0,padx=5,pady=10)
        textbox_1=Entry(sign_in_window, textvariable=sign_up_username,fg='black',font=('Arial',11)) # Tạo entry box điền tên đăng nhập
        textbox_1.place(x=150,y=13)
        label_2=Label(sign_in_window,text='Mật khẩu ',fg='black',font=('Arial',12)) # Tạo label "Mật khẩu" cho việc đăng ký
        label_2.grid(row=1,column=0,padx=5,pady=10)
        textbox_2=Entry(sign_in_window, textvariable=sign_up_password,fg='black',font=('Arial',11)) # Tạo entry box điền mật khẩu
        textbox_2.place(x=150,y=55)
        label_3 = Label(sign_in_window, text='Xác nhận mật khẩu ', fg='black', font=('Arial', 11)) # Tạo label "Xác nhận mật khẩu" cho việc đăng ký
        label_3.grid(row=2, column=0, padx=5, pady=10)
        textbox_3 = Entry(sign_in_window, textvariable=sign_up_check_password, fg='black', font=('Arial', 11)) # Tạo entry box điền mật khẩu xác nhận
        textbox_3.place(x=150,y=98)
        label_6 = Label(sign_in_window, text='            ', fg='black', font=('Arial', 11)) # Tạo label trống để ghi đè lên label báo hiệu đăng ký thành công hay không
        label_6.grid(row=5, column=0, padx=5, pady=10)
        label_4 = Label(sign_in_window, text='Tên đăng nhập ', fg='black', font=('Arial', 11)) # Tạo label tên đăng nhập cho việc đăng nhập
        label_4.grid(row=6, column=0, padx=5, pady=10)
        textbox_4 = Entry(sign_in_window, textvariable=sign_in_username, fg='black', font=('Arial', 11)) # Tạo entry box điền tên đăng nhập
        textbox_4.place(x=150,y=208)
        label_5 = Label(sign_in_window, text='Mật khẩu ', fg='black', font=('Arial', 11)) # Tạo label mật khẩu cho việc đăng nhập
        label_5.grid(row=7, column=0, padx=5, pady=10)
        textbox_5 = Entry(sign_in_window, textvariable=sign_in_password, fg='black', font=('Arial', 11)) # Tạo entry box cho việc điền mật khẩu
        textbox_5.place(x=150,y=253)
        def on_closing_2():  # Nhận diện nút X thoát chương trình
            if messagebox.askokcancel("Thoát", "Bạn có muốn thoát chương trình?"):
                root.destroy()
        sign_in_window.protocol("WM_DELETE_WINDOW", on_closing_2)
        def signup_function():
            choice = 1 # Truyền lệnh đăng ký cho server
            choice = str(choice) # Chuyển biến choice trên thành dạng chuỗi
            emptylabel = Label(sign_in_window, fg='red', font=('Arial', 11)) # Tạo label để thực hiện báo hiệu trong mục đăng ký
            emptylabel.grid(row=4, column=0, sticky=W)
            a = sign_up_username.get() # Nhận giá trị nhập vào "Tên đăng nhập"
            b = sign_up_password.get() # Nhận giá trị nhập vào "Mật khẩu"
            c = sign_up_check_password.get() # Nhận giá trị nhập vào "Xác nhận mật khẩu"
            if (len(a) > 50 or len(b) > 50 or len(c) > 50): # Nếu vượt quá bất kỳ chuỗi nào vượt quá 50 kí tự
                mbox = messagebox.showerror('Có lỗi xảy ra', 'Tối đa 50 kí tự!')
            if (a == ''): # Nếu tên đăng nhập trống, xuất "Thiếu tên đăng nhập"
                mbox = messagebox.showerror('Có lỗi xảy ra', 'Thiếu tên đăng nhập')
            elif (b == '' and a != ''): # Nếu mật khẩu trống, xuất "Thiếu mật khẩu
                mbox = messagebox.showerror('Có lỗi xảy ra', 'Thiếu mật khẩu')
            if(b != c and a != '' and b != ''): # Nếu mật khẩu và xác nhận mật khẩu khác nhau sẽ báo mật khẩu không khớp
                mbox = messagebox.showerror('Có lỗi xảy ra', 'Mật khẩu xác nhận không khớp')
            if (b == c and b != '' and c != '' and a != '' and len(a) <= 50 and len(b) <= 50 and len(c) <= 50): # Nếu không rơi vào bất kỳ trường hợp phía trên
                # Thực hiện truyền username và password cho server
                emptylabel = Label(sign_in_window, fg='green', font=('Arial', 11)) # Tạo label để báo hiệu trong mục đăng ký thành công hay thất bại
                create_button_1()  # Khởi động lại chức năng của nút 1 sau khi bấm
                isValid = save_account_data(a,b,choice,s) # Thực hiện hàm save_account_data() để kiểm tra xem tài khoản đã tồn tại hay chưa
                # Nếu chưa tồn tại, server trả về 1. Nếu đã tồn tại, server trả về 0
                if isValid == 1: # Tài khoản chưa tồn tại
                    emptylabel.grid(row=4, column=0, sticky=W)
                    emptylabel.config(text='Thành công            ')
                    textbox_1.delete(0, 'end')
                    textbox_2.delete(0, 'end')
                    textbox_3.delete(0, 'end')
                elif isValid == 0: # Tài khoản đã tồn tại
                    mbox = messagebox.showerror('Có lỗi xảy ra', 'Tên tài khoản đã tồn tại')
        def create_button_1(): # Tạo nút 1 với mục đích đăng ký, liên kết với hàm signup_function()
            button_1=Button(sign_in_window,command=signup_function,text='Đăng ký', activebackground='Light salmon', fg='black', font=('Arial',11))
            button_1.place(x=248,y=130)
            changeOnHover(button_1, 'LightGoldenrod1', 'SystemButtonFace')
        def create_button_2(): # Tạo nút 2 với mục đích đăng nhập, liên kết với hàm sign_in()
            button_2=Button(sign_in_window,command=sign_in,text='Đăng nhập', activebackground='Light salmon', fg='black', font=('Arial',11))
            button_2.place(x=230,y=285)
            changeOnHover(button_2, 'LightGoldenrod1', 'SystemButtonFace')
        def sign_in(): # Thực hiện lệnh đăng nhập
            choice = 2 # Truyền lệnh đăng nhập cho server
            choice = str(choice) # Biến choice thành dạng chuỗi
            emptylabel = Label(sign_in_window, fg='red', font=('Arial', 11)) # Tạo label để thực hiện báo hiệu trong mục đăng nhập
            emptylabel.grid(row=8, column=0, sticky=W)
            global a
            a = sign_in_username.get() # Nhận giá trị username nhập vào
            b = sign_in_password.get() # Nhận giá trị password nhập vào
            if (a == ''): # Nếu username trống, xuất "Thiếu tên đăng nhập"
                mbox = messagebox.showerror('Có lỗi xảy ra', 'Thiếu tên đăng nhập')
            elif (b == '' and a != ''): # Nếu password trống, xuất "Thiếu mật khẩu"
                mbox = messagebox.showerror('Có lỗi xảy ra', 'Thiếu mật khẩu')
            elif (a != '' and b != ''): # Nếu đã nhập vào một trong hai username
                # Thực hiện truyền username và password cho server
                isValid = save_account_data(a, b, choice, s) # Nếu đã tồn tại tài khoản, server trả về 1. Nếu đã tồn tại, server trả về 0
                if isValid == 1: # Nếu đã tồn tại tài khoản, đăng nhập thành công
                    emptylabel_next = Label(sign_in_window, fg='red',font=('Arial', 11)) # Tạo label báo sai tài khoản hoặc mật khẩu
                    emptylabel_next.grid(row=4, column=0, sticky=W)
                    emptylabel_next.config(text='                   ')
                    textbox_4.delete(0, 'end')
                    textbox_5.delete(0, 'end')
                    sign_in_window.withdraw() # Ẩn widget sign up/sign in đi để dùng sau đó nếu người dùng chọn đăng xuất trong widget tra cứu
                    format_main_window(root,a,sign_in_window) # Khởi động widget tra cứu với tham số a truyền vào là tên đăng nhập để hiển thị trong widget tra cứu
                elif isValid == 0: # Nếu chưa tồn tại tài khoản, đăng nhập thất bại
                    mbox = messagebox.showerror('Có lỗi xảy ra', 'Tài khoản hoặc mật khẩu không hợp lệ')
        # Tạo các label trống để đẩy label "Tên đăng nhập" và "Mật khẩu" xuống dưới mục Đăng nhập ở vị trí phù hợp
        emptylabel_1=Label(sign_in_window,fg='red',font=('Arial',11))
        emptylabel_1.grid(row=4,column=0,sticky=W)
        emptylabel_2=Label(sign_in_window,fg='red',font=('Arial',11))
        emptylabel_2.grid(row=5,column=0,sticky=W)
        create_button_1() # Khởi tạo nút "Đăng ký", nếu bấm vào sẽ thực hiện hàm signup_function()
        create_button_2() # Khởi tạo nút "Đăng nhập", nếu bấm vào sẽ thực hiện hàm sign_in()
    def check_IP(): # Hàm kiểm tra địa chỉ IP
        HOST = host_input.get() # Lấy địa chỉ IP đã nhập trong entry box
        # Dùng để biến đổi giá trị IP vừa nhập vào entry box thành dạng string vì không thể so sánh biến dạng StringVar() và string
        # Bằng cách dùng trung gian lưu vào file IP.txt và đọc nó lên lại đưa vào biến HOST
        socket_check = set_socket(HOST)
        if socket_check == True: # Nếu địa chỉ IP khớp thì thực hiện gửi data ban đầu từ server và client để khởi tạo biến countries (chỉ một lần mỗi client sau khi kết nối thành công)
            # thực hiện kết nối server
            global countries
            countries = receive_initial_covid_data() # nhập giá trị server gửi thông qua biến countries
            countries.sort() # sắp xếp tăng dần các giá trị countries
            root.withdraw() # Ẩn đi cửa sổ root Welcome
            signup_menu() # thực hiện hàm signup_menu để đăng kí hoặc đăng nhập
        else: # Nếu nhập khác địa chỉ IP của server
            wrong_IP_input = Label(root, text='Không tìm thấy server!', fg='red', font=('Arial', 11)) # tạo nhãn báo không tìm thấy địa chỉ IP
            wrong_IP_input.place(x=118, y=345)
            button_1 = Button(root, command=check_IP, text='Tiếp', fg='black', activebackground='light salmon', font=('Arial', 11)) # Khởi động lại nút "Tiếp"
            button_1.place(x=295, y=315)
            changeOnHover(button_1, 'DarkOliveGreen1', 'SystemButtonFace')
    button_1 = Button(root, command=check_IP, text='Tiếp', activebackground='light salmon', fg='black', font=('Arial', 11)) # Khởi tạo nút "Tiếp" ở widget gốc, liên kết với hàm check_IP phía trên
    button_1.place(x=295,y=315)
    changeOnHover(button_1,'DarkOliveGreen1','SystemButtonFace')
    message = Label(root, fg='black', font=('Arial', 15)) # Hiển thị thông điệp trên màn hình widget gốc
    message.place(x=15, y=250)
    message.config(text='Hãy tuân thủ thông điệp 5K của chính phủ')
    def on_closing(): # Nhận diện nút X thoát chương trình
        if messagebox.askokcancel("Thoát", "Bạn có muốn thoát chương trình?"):
            root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop() # hiển thị màn hình root

root = Tk() # Khởi tạo màn hình root
firstmenu(root) # Thực hiện định dạng root và các thứ khác sau khi tạo widget root