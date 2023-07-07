from sys import platform
from class_custom import App


if __name__ == "__main__":
    if platform.startswith('linux'):
        root = '/'
    elif platform.startswith('win32'):
        root = "c:/"
    else:
        exit()
    app = App(root)
    app.mainloop()
