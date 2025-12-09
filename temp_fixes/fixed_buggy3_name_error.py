def show_name():
    print("Hello", end=" ")
    print(username)

username = try:
    input("Please enter your name: ")
except EOFError:
    input("Please enter your name: ") = 'DefaultUser'
show_name()