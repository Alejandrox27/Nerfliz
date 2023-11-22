import sys
from cx_Freeze import setup, Executable
import os
from PIL import Image

icon_path = os.path.abspath("images/nerfliz.png")
imagen_original = Image.open(icon_path)

nuevo_tamano = (512, 512)
imagen_redimensionada = imagen_original.resize(nuevo_tamano, Image.LANCZOS)
imagen_redimensionada.save("images/icon.ico")

imagen_original.close()
imagen_redimensionada.close()
icon_path = os.path.abspath("images/icon.ico")

base = None
if sys.platform == "win32":
    base = "Win32GUI"  

options = {
    "build_exe": {
        "packages": ["os", "io","sys", "PyQt5", "urllib", "email", "dotenv", "PIL","smtplib", "re" ,"sqlite3","threading"],
        "include_files": ["images/", "styles/", "GUI/", "models/", "database/", "movie_posters/", "profile_info_temp/", "venv/"] 
    }
}

executables = [
    Executable("main.py", base=base, icon='images/icon.ico', target_name="Nerfliz")
]

setup(
    name="Nerfliz",
    version="1.0",
    description="Nerfliz",
    options=options,
    executables=executables
)
#python setup.py build