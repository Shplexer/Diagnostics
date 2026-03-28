
import tkinter as tk
import API
import admin
from tkinter import ttk, messagebox

def open_role_window(role, user_id):
    root.destroy()
    print(user_id, role)
    admin.open_admin_window(user_id, role)
    # match(role):
    #     case 'Администратор':
    #         admin.open_admin_window(user_id, role)
    #         print('opening admin window')
    #     case 'Пациент':
    #         print('opening patient window', user_id)
    #         admin.open_admin_window(user_id, role)
    #         # patient.open_patient_window(user_id)
    #     case 'Врач':
    #         print('opening doctor window')
    #     case 'Инженер по знаниям':
    #         admin.open_admin_window(user_id, role)
    #         print('opening data engineer window')
    #     case _:
    #         print('closing window')


def check_auth(username, password):
    result = False
    try:
        # Add your validation logic here
        if not username or not password:
            messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля")
            # Return early but don't run finally block for this case
            submit_btn.config(state='normal', text='Войти')
            return

        result, user_id = API.auth(username, password)
        print("===", result)
        print("==", user_id)
        if result:
            open_role_window(result, user_id)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
            # Clear fields on failed attempt
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            username_entry.focus_set()

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    finally:
        # Only reset button state here, handle messages in try block
        submit_btn.config(state='normal', text='Войти')



def submit():
    submit_btn.config(state='disabled', text='Вход...')
    root.update()  # Force UI update
    check_auth(username_entry.get(), password_entry.get())


# Create main window
root = tk.Tk()
root.geometry("500x600")
root.title("Вход в систему")
root.configure(bg='#F5F5F5')
root.resizable(False, False)

# Center the window on screen
window_width = 500
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f'{window_width}x{window_height}+{x}+{y}')

# Style configuration
style = ttk.Style()
style.theme_use('clam')

# Colors
bg_color = '#F5F5F5'
accent_color = '#3498DB'
entry_bg = '#FFFFFF'
text_color = '#2C3E50'

# Main container with padding
main_frame = tk.Frame(root, bg=bg_color, padx=40, pady=40)
main_frame.pack(expand=True, fill='both')

# Header
header_frame = tk.Frame(main_frame, bg=bg_color)
header_frame.pack(pady=(0, 40))

title_label = tk.Label(header_frame,
                       text="Авторизация",
                       font=('Segoe UI', 28, 'bold'),
                       bg=bg_color,
                       fg=text_color)
title_label.pack()

subtitle_label = tk.Label(header_frame,
                          text="Введите ваши учетные данные",
                          font=('Segoe UI', 12),
                          bg=bg_color,
                          fg='#7F8C8D')
subtitle_label.pack(pady=(10, 0))

# Login form container
form_frame = tk.Frame(main_frame, bg=bg_color)
form_frame.pack(fill='x', padx=20)

# Username field
username_frame = tk.Frame(form_frame, bg=bg_color)
username_frame.pack(fill='x', pady=(0, 20))

username_label = tk.Label(username_frame,
                          text="Логин",
                          font=('Segoe UI', 11, 'bold'),
                          bg=bg_color,
                          fg=text_color,
                          anchor='w')
username_label.pack(fill='x')

username_entry = tk.Entry(username_frame,
                          font=('Segoe UI', 12),
                          bg=entry_bg,
                          fg=text_color,
                          relief='flat',
                          insertbackground=accent_color)
username_entry.pack(fill='x', pady=(8, 0), ipady=10)
username_entry.config(highlightbackground='#BDC3C7', highlightthickness=1)

# Password field with icon and show/hide button
password_frame = tk.Frame(form_frame, bg=bg_color)
password_frame.pack(fill='x', pady=(0, 25))

password_label = tk.Label(password_frame,
                          text="Пароль",
                          font=('Segoe UI', 11, 'bold'),
                          bg=bg_color,
                          fg=text_color,
                          anchor='w')
password_label.pack(fill='x')

password_inner_frame = tk.Frame(password_frame, bg=entry_bg)
password_inner_frame.pack(fill='x', pady=(8, 0))

password_entry = tk.Entry(password_inner_frame,
                          font=('Segoe UI', 12),
                          bg=entry_bg,
                          fg=text_color,
                          relief='flat',
                          show='•',
                          insertbackground=accent_color)
password_entry.pack(side='left', fill='x', expand=True, ipady=10)

password_inner_frame.config(highlightbackground='#BDC3C7', highlightthickness=1)

# Submit button
submit_btn = tk.Button(form_frame,
                       text="Войти",
                       font=('Segoe UI', 12, 'bold'),
                       bg=accent_color,
                       fg='white',
                       relief='flat',
                       command=submit,
                       cursor='hand2',
                       padx=30,
                       pady=12)
submit_btn.pack(fill='x', pady=(10, 0))

# Footer with additional options
footer_frame = tk.Frame(main_frame, bg=bg_color)
footer_frame.pack(fill='x', pady=(30, 0))

# Bind Enter key to submit
root.bind('<Return>', lambda event: submit())

# Set focus to username field
username_entry.focus_set()

# Start the application
root.mainloop()