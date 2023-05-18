from tkinter import *
from tkinter import messagebox
import random
import string
import pyperclip
import json
from cryptography.fernet import Fernet


# ------------------------------------------ PASSWORD GENERATOR -------------------------------------------- #
def generate_password():
    """Generates a random password from strings (upper and lower), characters and numbers."""
    password_entry.delete(0, 'end')
    saved_label.config(text="")
    char_list = list(string.ascii_lowercase)
    symbols_list = list(string.punctuation)
    symbols_list.remove('\\')
    symbols_list.remove('"')  # Removing python reserved syntax
    symbols_list.remove("'")
    numbers = [str(i) for i in range(1, 11)]
    password = []

    for i in range(1, 5):
        password.append(random.choice(char_list))
        password.append(random.choice(char_list).title())
        password.append(random.choice(symbols_list))
        password.append(random.choice(numbers))

    random.shuffle(password)  # Shuffle password in order to prevent password sequence predictability
    final_password = ''.join(password)  # Converts password list to a string
    password_entry.insert(0, final_password)
    pyperclip.copy(password_entry.get())  # Automatically copies the data in the text field to clipboard
    encrypt(final_password)


# ---------------------------------------- ENCRYPT PASSWORD ------------------------------------------- #
def encrypt(final_password):
    """Encrypts password using strong AES 128-bit algorithm"""
    global encrypted_password_str, key_str
    # generate a key to use for encryption/decryption
    key = Fernet.generate_key()

    # create a Fernet object using the key
    fernet = Fernet(key)

    # encrypt the message
    encrypted_password = fernet.encrypt(final_password.encode())

    # Convert the encrypted text to a string to enable it save into a json file
    encrypted_password_str = encrypted_password.decode()

    # Convert the key to a string
    key_str = key.decode()


# ------------------------------------------ SAVE PASSWORD --------------------------------------------- #
def save():
    """Saves the encrypted password to a json file. Creates the json file if unavailable"""
    new_data = {
        website_entry.get().title(): {
            "email": email_entry.get(),
            "password": encrypted_password_str,
            "key": key_str
        }
    }

    if website_entry.get() == "" or password_entry.get() == "" or email_entry.get() == 0:
        messagebox.showinfo(title="Warning", message="Please don't leave any fields empty!")
    else:
        is_ok = messagebox.askokcancel(title=website_entry.get(), message=f"These are the details entered: "
                                                                          f"\n\nEmail: {email_entry.get()}"
                                                                          f"\nPassword: {password_entry.get()} "
                                                                          f"\n\nAre you sure you want to save?")

        if is_ok:
            try:
                # TO OPEN THE FILE
                with open("data.json", "r") as file:
                    # To read the old data as a dict
                    data = json.load(file)
                # IF FILE DOES NOT EXIST, USE THIS CODE TO CREATE FILE, IF IT DOES EXIST, IT SKIPS
            except FileNotFoundError:
                with open("data.json", "w") as file:
                    json.dump(new_data, file, indent=4)
                # THIS CODE WILL CONTINUE AFTER 'TRY' IF 'TRY' WORKS, ELSE IT'S SKIPPED
            else:
                # Updating the old data
                data.update(new_data)

                with open("data.json", "w") as file:
                    # Saving the updated data
                    json.dump(data, file, indent=4)

                # THIS CODE DOES NOT CARE, AND WILL RUN, NO MATTER WHAT
            finally:
                website_entry.delete(0, 'end')
                password_entry.delete(0, 'end')
                saved_label.config(text="Saved successfully!", fg="green")


# ------------------------------------------- DECRYPT PASSWORD --------------------------------------------- #
def decrypt(data, website):
    """Converts encrypted password string back to the encrypted password bytes and then returns decrypted string"""
    the_password = data[website]['password']
    the_encrypted_password = the_password.encode()

    # Decrypt the encrypted password to normal password
    key = data[website]["key"].encode()  # Change key from string to bytes
    new_fernet = Fernet(key)
    normal_password = new_fernet.decrypt(the_encrypted_password).decode()
    return normal_password


# ------------------------------------------- SEARCH ENTRIES ---------------------------------------------- #
def search_details():
    """Searches the database for matching entries and displays the decrypted password"""
    website = website_entry.get().title()
    try:
        with open("data.json", 'r') as file:
            data = json.load(file)
            normal_password = decrypt(data, website)
            window.clipboard_clear()
            window.clipboard_append(normal_password)  # Automatically copies diplayed password to clipboard
            messagebox.showinfo(title=website, message=f"Email: {data[website]['email']}\n"
                                                       f"Password: {normal_password}")

    except FileNotFoundError:
        messagebox.showerror(title="Error", message="No data file found. Save your first website and try again.")

    except KeyError:
        messagebox.showerror(title="Error", message="No details for this website exists")


# ------------------------------------------------- UI SETUP --------------------------------------------------- #
# WINDOW
window = Tk()


def activate_button(event):
    widget = window.focus_get()
    if isinstance(widget, Button):
        widget.invoke()


window.title("Password Generator")
window.config(padx=50, pady=50)
# window.bind('<Return>', lambda event=None: add_button.invoke()) # TO USE ENTER KEY FOR ONE BUTTON ONLY
window.bind('<Return>', activate_button) # TO USE ENTER KEY ON ANY BUTTON YOU TAB TO
icon = PhotoImage(file="logo.png")  # TO CHANGE THE ICON
window.iconphoto(True, icon)

# CANVAS
canvas = Canvas(width=200, height=200)
logo = PhotoImage(file="logo.png")
canvas.create_image(100, 100, image=logo)
canvas.grid(column=1, row=0)

# LABEL1
website_label = Label(text="Website:", font=("Arial", 10, "bold"))
website_label.grid(column=0, row=1)

# LABEL2
email_label = Label(text="Email/Username:", font=("Arial", 10, "bold"))
email_label.grid(column=0, row=2)

# LABEL3
password_label = Label(text="Password:", font=("Arial", 10, "bold"))
password_label.grid(column=0, row=3)

# LABEL4
saved_label = Label(font=("Arial", 10, "bold"))
saved_label.grid(column=1, row=5)

# ENTRY1
website_entry = Entry(width=39)
website_entry.focus()
website_entry.grid(column=1, row=1, padx=10, pady=10)

# ENTRY2
email_entry = Entry(width=57)
email_entry.insert(END, "don4dolex@gmail.com")
email_entry.grid(column=1, row=2, columnspan=2, padx=10)

# ENTRY3
password_entry = Entry(width=39)
password_entry.grid(column=1, row=3, padx=10, pady=10)

# BUTTON1
generate_button = Button(text="Generate Password", width=14, command=generate_password)
generate_button.grid(column=2, row=3)

# BUTTON2
add_button = Button(text="Add", width=50, command=save)
add_button.grid(column=1, row=4, columnspan=2, padx=10)


# BUTTON3
search_button = Button(text="Search", width=14, command=search_details)
search_button.grid(column=2, row=1)

window.mainloop()
