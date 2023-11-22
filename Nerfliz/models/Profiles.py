import sqlite3
import hashlib
import binascii
import os
import queue
from secrets import compare_digest
from .Profile import Profile
from PyQt5.QtGui import QPixmap
from .API_movies import MoviesAPI_selected

class Profiles():
    def __init__(self):
        self.profiles = []
        self.result_queue = queue.Queue()
        
    def addProfile(self, profile):
        sql = """INSERT INTO profiles (NAME, PASSWORD, EMAIL, IMAGE) VALUES (?,?,?,?)"""
        try:
            connection = sqlite3.connect('database/profiles.db')
            cursor = connection.cursor()
            cursor.execute(sql, (profile.name, profile.password, profile.email, profile.image))
            connection.commit()
            self.result_queue.put(True)
        except sqlite3.Error as e:
            self.result_queue.put(False)
        finally:
            connection.close()
            
    def loadProfiles(self):
        sql = """SELECT * FROM profiles"""
        try:
            connection = sqlite3.connect('database/profiles.db')
            cursor = connection.cursor()
            profiles = cursor.execute(sql).fetchall()
            for e in profiles:
                name = e[0]
                password = e[1]
                email = e[2]
                image = e[3]
                new_profile = Profile(name,password,email,image)
                self.profiles.append(new_profile)
                
        except sqlite3.Error as e:
            return False
        finally:
            connection.close()
            
    def searchPasswordProfile(self, name):
        sql = """SELECT PASSWORD FROM profiles WHERE NAME = ?"""
        try:
            connection = sqlite3.connect('database/profiles.db')
            cursor = connection.cursor()
            password = cursor.execute(sql, (name,)).fetchone()
            return password[0]
        except sqlite3.Error as e:
            return False
        finally:
            connection.close()
        
    def updateProfile(self, old_name, new_name, new_image):
        sql_update = f"""UPDATE profiles SET NAME = ?, IMAGE = ? WHERE NAME = ?"""
        
        try:
            connection = sqlite3.connect('database/profiles.db')
            cursor = connection.cursor()
            cursor.execute(sql_update, (new_name, new_image, old_name))
            connection.commit()
        except sqlite3.Error as e:
            return False
        finally:
            connection.close()
        
    def isNameInDatabase(self, new_name):
        sql_element = f"""SELECT * FROM profiles WHERE NAME = ?"""
        
        try:
            connection = sqlite3.connect('database/profiles.db')
            cursor = connection.cursor()
            return cursor.execute(sql_element, (new_name,)).fetchone()
        except sqlite3.Error as e:
            return None
        finally:
            connection.close()
        
    def removeProfile(self, name):
        sql_remove = f"""DELETE FROM profiles WHERE NAME = ?"""
        
        try:
            connection = sqlite3.connect('database/profiles.db')
            cursor = connection.cursor()
            cursor.execute(sql_remove, (name,))
            connection.commit()
        except sqlite3.Error as e:
            return None
        finally:
            connection.close()
        
    def convert_to_binary(self,photo):
        """
        this function converts a image into a binary data
        
        Parameters:
        photo = image root to the image
        
        Returns:
        blob = binary image.
        None = If there was an error during the convertion.
        """
        try:
            with open(photo, 'rb') as f:
                blob = f.read()
                
            return blob
        except:
            return None
        
    def convert_binary_to_image(self, binary_data):
        """
        This function convert a binary image to a QIcon object

        Parameters:
        binary_data (bytes): binary data from the image
        width (int): desired QIcon width
        height (int): desired QIcon height

        Returns:
        pixmap: The pixmap loaded from the binary data
        None: if there was an error during the convertion.
        """
        try:
            pixmap = QPixmap()
            pixmap.loadFromData(binary_data)
            
            return pixmap
        except:
            return None
    
    def hash_password(self, password):
        """Hash a password for storing"""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                    salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def verify_password(self, stored_password, provided_password):
        """
        Verifica si una clave suministrada es igual a una clave codificada
        
        Parameters:
        stored_password: clave codificada guardada en la base de datos
        provided_password: clave suministrada por el usuario
        """
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                    provided_password.encode('utf-8'), 
                                    salt.encode('ascii'), 
                                    100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return compare_digest(pwdhash, stored_password)