import threading
from socket import *
from customtkinter import *
# • threading — щоб працювати з окремим потоком, щоб отримувати повідомлення від сервера без "заморозки" інтерфейсу.
# • socket – стандартний модуль для мережної взаємодії.
# • customtkinter – сучасна версія Tkinter з темною темою та кастомними віджетами.


class MainWindow(CTk):
   def __init__(self):
       super().__init__()
#        • Створюємо головне вікно чату.
# • CTk – це основне вікно CustomTkinter.


#  Налаштування інтерфейсу
       self.geometry('400x300')
       self.label = None
       # • Меню-слайдер зліва (вузька панель 30px).
       self.menu_frame = CTkFrame(self, width=30, height=300)
       self.menu_frame.pack_propagate(False)
       self.menu_frame.place(x=0, y=0)
       self.is_show_menu = False
       self.speed_animate_menu = -5
    #    Кнопка для меню
       self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
       self.btn.place(x=0, y=0)
       # Основні віджети чату
       self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable')
       self.chat_field.place(x=0, y=0)
       self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
       self.message_entry.place(x=0, y=0)
       self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
       self.send_button.place(x=0, y=0)

       self.username = 'Svitlana'

    #    Підключення до сервера
       try:
           self.sock = socket(AF_INET, SOCK_STREAM)
            # Створюємо TCP-сокет та підключаємося до локального сервера на порту 8080.
           self.sock.connect(('4.tcp.eu.ngrok.io', 17090))
           hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
        #    Надсилаємо повідомлення про приєднання.

           self.sock.send(hello.encode('utf-8'))
        #    Створюємо окремий потік для отримання повідомлень, щоб GUI залишався чуйним.

           threading.Thread(target=self.recv_message, daemon=True).start()
       except Exception as e:
           self.add_message(f"Не вдалося підключитися до сервера: {e}")

       self.adaptive_ui()



# Меню-слайдер

# логіка відкриття/закриття меню
# • Змінює ширину меню поступово (анімація).
# • Додає віджети в меню (ім'я користувача).

   def toggle_show_menu(self):
       if self.is_show_menu:
           self.is_show_menu = False
           self.speed_animate_menu *= -1
           self.btn.configure(text='▶️')
           self.show_menu()
       else:
           self.is_show_menu = True
           self.speed_animate_menu *= -1
           self.btn.configure(text='◀️')
           self.show_menu()
           # setting menu widgets
           self.label = CTkLabel(self.menu_frame, text='Імʼя')
           self.label.pack(pady=30)
           self.entry = CTkEntry(self.menu_frame, placeholder_text=self.username, height=40)
           self.entry.pack()



# анімація зміни ширини
#  Викликається рекурсивно через after кожні 10 мс, щоб плавно розширювати чи стискати меню

   def show_menu(self):
       self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
       if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
           self.after(10, self.show_menu)
       elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
           self.after(10, self.show_menu)
           if self.label and self.entry:
               self.label.destroy()
               self.entry.destroy()

# Адаптивний інтерфейс

# підганяє розміри chat_field, message_entry та send_button під розміри вікна 

# • Інтерфейс підлаштовується при зміні розмірів вікна.
# • after(50, …) – викликає саму себе кожні 50 мс.
   def adaptive_ui(self):
       self.menu_frame.configure(height=self.winfo_height())
       self.chat_field.place(x=self.menu_frame.winfo_width())
       self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                 height=self.winfo_height() - 40)
       self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
       self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
       self.message_entry.configure(
           width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

       self.after(50, self.adaptive_ui)
# Робота з повідомленнями
# • Вставляє текст у полі чату.
# • Тимчасово вмикає редагування, щоб програма могла вставити текст.

   def add_message(self, text):
       self.chat_field.configure(state='normal')
       self.chat_field.insert(END, 'Я: ' + text + '\n')
       self.chat_field.configure(state='disable')

# Бере текст із message_entry та надсилає серверу.
   def send_message(self):
       message = self.message_entry.get()
       if message:
           self.add_message(f"{self.username}: {message}")
           data = f"TEXT@{self.username}@{message}\n"
           try:
               self.sock.sendall(data.encode())
           except:
               pass
       self.message_entry.delete(0, END)
# Отримання повідомлень
# • Постійно отримує дані від сервера.
# • Розділяє їх рядками (\n) і передає для обробки.

# Це метод класу  отримує мережеві дані по сокету і послідовно обробляє кожен рядок повідомлення, розділений символом нового рядка.

   def recv_message(self):
       buffer = ""
       while True:
           try:
               chunk = self.sock.recv(4096)
               if not chunk:
                   break
               buffer += chunk.decode()

               while "\n" in buffer:
                   line, buffer = buffer.split("\n", 1)
                   self.handle_line(line.strip())
           except:
               break
       self.sock.close()
# обробляє текстові повідомлення
# • Якщо повідомлення починається з TEXT@, виводить його як звичайний текст.
# • Якщо не розпізнає - то виводит як є.
   def handle_line(self, line):
       if not line:
           return
       parts = line.split("@", 3)
       msg_type = parts[0]

       if msg_type == "TEXT":
           if len(parts) >= 3:
               author = parts[1]
               message = parts[2]
               self.add_message(f"{author}: {message}")
       elif msg_type == "IMAGE":
           if len(parts) >= 4:
               author = parts[1]
               filename = parts[2]

               self.add_message(f"{author} надіслав(ла) зображення: {filename}")

       else:
           self.add_message(line)

print("MainWindow об'єкт буде створено")
win = MainWindow()
win.mainloop()



