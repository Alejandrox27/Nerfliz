import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QPushButton, QLabel, QFrame
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt5 import QtCore, QtWidgets, QtGui

from GUI.homepage import Ui_MainWindow
from GUI.signup import Ui_SignUp
from GUI.terms_and_conditions import Ui_Terms_and_conditions
from GUI.py_messagebox import MessageBox_UI, MessageBox_confirmation

from models.API_movies import MoviesAPI_selected
import urllib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

from PIL import Image, ImageDraw
from io import BytesIO
import re
import os
import threading

from models.Profile import Profile
from models.Profiles import Profiles

class TermsAndConditions(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.profiles = Profiles()
        
        self.thread = threading.Thread(target=self.profiles.loadProfiles)
        self.thread.start()
        
        with open('styles/terms_and_conditions_style.css', 'r') as f:
            stylesheet = f.read()
        self.setStyleSheet(stylesheet)
        
        self.initializeGui()
        
    def initializeGui(self):
        self.ui = Ui_Terms_and_conditions()
        self.ui.setupUi(self)
        
        self.ui.btn_agree.clicked.connect(lambda: self.open_homepage(self.thread))
        self.ui.btn_close_terms_conditions.clicked.connect(self.closeAnimation)
        self.ui.btn_dont_agree.clicked.connect(self.closeAnimation)
        
    def open_homepage(self, thread):
        """
        id thread (load profiles) is not alive then it opens
        the homepage window
        
        PARAMETERS:
        thread: the asinc function self.profiles.loadProfiles to load the profiles
                from the database
        """
        if thread.is_alive():
            self.after(100, lambda: self.monitorear_descarga(thread))
        else:
            self.close()
            self.mainwindow = HomePage(self.profiles)
            self.mainwindow.show()
        
    def showEvent(self, event):
        super().showEvent(event)

        self.animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        
    def closeAnimation(self):
        self.fade_out_animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.fade_out_animation.setDuration(200)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.finished.connect(self.close)
        self.fade_out_animation.start()
        
class HomePage(QMainWindow):
    def __init__(self, profiles):
        super().__init__()
        
        self.profiles = profiles
        self.buttons = []
        
        self.num_profiles = 1
        self.drag_position = None
        self.storedPassword = None
        self.confirmation_ob = False
            
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.initializeGui()
        
    def initializeGui(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        with open('styles/homepage_style.css', 'r') as f:
            stylesheet = f.read()
        self.setStyleSheet(stylesheet)
        
        for profile in self.profiles.profiles:
            image = self.profiles.convert_binary_to_image(profile.image)
            self.append_new_profiles_from_database(profile.name, image)
        
        self.ui.btn_breaking_bad.installEventFilter(self)
        self.ui.btn_mr_robot.installEventFilter(self)
        self.ui.btn_american_psycho.installEventFilter(self)
        self.ui.btn_narcos.installEventFilter(self)
        self.ui.btn_shrek.installEventFilter(self)
        self.ui.btn_the_godfather.installEventFilter(self)
        self.ui.btn_the_sopranos.installEventFilter(self)
        self.ui.btn_you.installEventFilter(self)
        self.ui.btn_shrek_2.installEventFilter(self)
        self.ui.btn_cobra_kai.installEventFilter(self)
        self.ui.btn_the_witcher.installEventFilter(self)
        self.ui.btn_the_social_network.installEventFilter(self)
        self.ui.btn_stranger_things.installEventFilter(self)
        self.ui.btn_black_mirror.installEventFilter(self)
        self.ui.btn_adventure_time.installEventFilter(self)
        
        self.ui.btn_breaking_bad.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_mr_robot.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_american_psycho.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_narcos.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_shrek.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_the_godfather.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_the_sopranos.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_you.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_shrek_2.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_cobra_kai.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_the_witcher.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_the_social_network.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_stranger_things.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_black_mirror.clicked.connect(self.seeInfoMovieFromCatalog)
        self.ui.btn_adventure_time.clicked.connect(self.seeInfoMovieFromCatalog)
        
        self.ui.btn_github.clicked.connect(self.goToWebpage)
        self.ui.btn_instagram.clicked.connect(self.goToWebpage)
        self.ui.btn_facebook.clicked.connect(self.goToWebpage)
        self.ui.btn_email.clicked.connect(self.goToWebpage)
        
        self.ui.btn_nerfliz_logo_home.clicked.connect(self.returnToInitialPage)
        
        self.ui.btn_menu.clicked.connect(self.open_menu)
        self.ui.btn_restaure.clicked.connect(self.restaure)
        self.ui.btn_minimize.clicked.connect(self.minimize)
        self.ui.btn_exit.clicked.connect(self.closeAnimation)
        
        self.ui.btn_new_profile.clicked.connect(self.new_profile)
        self.ui.btn_new_profile_text.clicked.connect(self.new_profile)
        
        self.ui.btn_return_to_initial_page.clicked.connect(self.returnToInitialPage)
        
        self.ui.btn_see_password.clicked.connect(self.see_password)
        self.ui.btn_enter_homepage.clicked.connect(lambda: self.verifyPassword(self.storedPassword))
        self.ui.txt_password_login.textChanged.connect(lambda: self.ui.txt_password_login.setStyleSheet('border-color:white;') if self.ui.txt_password_login.text().strip()[:-1] == '' else None)
        
        self.ui.txt_search_movie.returnPressed.connect(lambda: self.movieSearch(self.ui.txt_search_movie.text().strip()))
        
        self.ui.btn_back_movies.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        
        self.ui.btn_go_back_from_edit.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.btn_cancel.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        
        self.ui.btn_image_profile_edit.clicked.connect(self.edit_image)
        
        self.ui.btn_remove_profile.clicked.connect(lambda: self.remove_profile())
        self.ui.btn_save_edit_profile.clicked.connect(lambda: self.save_profile())
        
        self.ui.cbx_category.currentIndexChanged.connect(self.watch_category)
        
    # Window functions    
        
    def returnToInitialPage(self):
        """
        this function returns to the initial page from the
        stacked widget (0) and refresh all the values to default.
        """
        self.ui.lbl_profile_name_information.setText('Profile')
        self.ui.lbl_profile_image_information.setPixmap(QPixmap('images/profile.png'))
        self.delete_recent_searched_movie()
        self.show_movies_catalogue()
        self.ui.txt_search_movie.setText('')
        self.ui.lbl_hello_user.setText('Hello _!\n Insert your password to enter.')
        self.ui.stackedWidget.setCurrentIndex(0) 
        
    def eventFilter(self, obj, event):
        """
        this function adds an animation to a button so
        when you pass over it the mouse is activated.
        
        PARAMETERS:
        obj: the button object to animate
        event: the animation activation event 
        """
        if obj not in self.buttons:
            if event.type() == event.Enter:
                self.start_animation_movies(obj)
            elif event.type() == event.Leave:
                self.stop_animation_movies(obj)
            return super().eventFilter(obj, event)
        else:
            if event.type() == event.Enter:
                self.start_animation_profiles(obj)
            elif event.type() == event.Leave:
                self.stop_animation_profiles(obj)
            return super().eventFilter(obj, event)
        
    def start_animation_movies(self, button):
        """
        This function adds a start animation for the posters
        """
        animation = QPropertyAnimation(button, b'iconSize')
        animation.setDuration(800)
        animation.setEasingCurve(QEasingCurve.Type.OutBack)
        
        if animation.state() == QPropertyAnimation.Running:
            animation.stop()
            geometry = button.iconSize()
            animation.setStartValue(geometry)
            animation.setEndValue(QSize(200,270))
        else:
            animation.setStartValue(QSize(250,300))
            animation.setEndValue(QSize(200,270))
        animation.start()    
        
    def stop_animation_movies(self, button):
        """
        this function adds a stop animation for a poster
        """
        animation = QPropertyAnimation(button, b'iconSize')
        animation.setDuration(800)
        animation.setEasingCurve(QEasingCurve.Type.OutBack)
        
        if animation.state() == QPropertyAnimation.Running:
            animation.stop()
            geometry = button.iconSize()
            animation.setStartValue(geometry)
            animation.setEndValue(QSize(250,300))
        else:
            animation.setStartValue(QSize(200,270))
            animation.setEndValue(QSize(250,300))
        animation.start()           
        
    def windowLoading(self):
        """
        this function is a loading screen while loading the 
        movies information
        """
        self.loadingScreen = QDialog(self)
        self.loadingScreen.setWindowTitle("loading...")
        self.loadingScreen.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.loadingScreen.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.loadingScreen.setGeometry(0, 0, self.width(), self.height())
        
        frame_loading = QtWidgets.QFrame()
        frame_loading.setStyleSheet('QFrame {background-color: rgba(0,0,0,100);}')
        layout = QtWidgets.QVBoxLayout(frame_loading)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        loadingScreenLayout = QtWidgets.QVBoxLayout(self.loadingScreen)
        loadingScreenLayout.setContentsMargins(0,0,0,0)
        loadingScreenLayout.addWidget(frame_loading)
        
        label = QLabel()
        label.setMaximumSize(QtCore.QSize(70,70))
        label.setScaledContents(True)
        movie = QtGui.QMovie("images/loading.gif")
        label.setMovie(movie)
        layout.addWidget(label)
        movie.start()
        
    def open_menu(self):
        width = self.ui.frm_menu.width()
        
        if width == 0:
            newWidth =250
        else:
            newWidth = 0
            
        self.animation = QtCore.QPropertyAnimation(self.ui.frm_menu, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuart)
        self.animation.start()
        
    def restaure(self):
        """
        This function maximizes or restores the window.
        """
        if self.isMaximized():
            self.showNormal()
            self.ui.btn_restaure.setIcon(QtGui.QIcon(u"images/square.svg"))
        else:
            self.showMaximized()
            self.ui.btn_restaure.setIcon(QtGui.QIcon(u"images/copy.svg"))
    
    def minimize(self):
        self.showMinimized()    
        
    def showEvent(self, event):
        super().showEvent(event)

        self.animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        
    def closeAnimation(self):
        self.fade_out_animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.fade_out_animation.setDuration(200)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.finished.connect(self.close)
        self.fade_out_animation.start()
    
    def mousePressEvent(self, event):
        if not self.isMaximized():
            if event.buttons() == Qt.LeftButton:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if not self.isMaximized():
            if self.drag_position:
                self.move(event.globalPos() - self.drag_position)
                event.accept()

    def mouseReleaseEvent(self, event):
        if not self.isMaximized():
            self.drag_position = None
            
    # Movie functions:    
        
    def seeInfoMovieFromCatalog(self):
        """
        this function searches the information of a movie
        from the initial catalog in the background.
        """
        self.windowLoading()
        
        icon = self.sender().icon()
        pixmap = icon.pixmap(icon.availableSizes()[0])
        root = "profile_info_temp/poster_img_tmp.png"
        pixmap.save(root, "PNG")
        
        movie = self.sender().objectName()
        movie = movie[4:].replace('_',' ')
        self.movie = MoviesAPI_selected(movie)
        self.movie.result_ready.connect(self.result_movie_search_catalogue)
        self.movie.result_error.connect(self.result_movie_search_catalogue)
        self.movie.start()
        
        self.loadingScreen.exec_()
    
    def result_movie_search_catalogue(self, result):
        """
        this function loads the poster from poster_img_tmp.png
        and then analizes if there is no error in the result, finally
        it goes to the function see_movie_search.
        """
        movie_poster = QPixmap('profile_info_temp/poster_img_tmp.png')
        if self.loadingScreen:
            self.loadingScreen.close()
        
        if result == 'Error':
            self.show_movies_catalogue()
            self.ui.txt_search_movie.setText('Error, try again')
            return
        elif result == 'Connection Error!':
            self.show_movies_catalogue()
            self.ui.txt_search_movie.setText(result)
            return
        
        self.see_movie_info(result, movie_poster)
        
    def result_movie_search(self, result):
        """
        this function analizes if there is no error in the result of the searched movie,
        then it creates a new button with the new searched movie that goes to the function
        see_movie_info.
        """
        self.loadingScreen.close()
        
        if result == 'Error':
            self.delete_recent_searched_movie()
            buttons = self.ui.frm_movies.findChildren(QPushButton)
            for button in buttons:
                button.show()
            self.ui.txt_search_movie.setText('Error, try again')
            return
        elif result == 'Connection Error!':
            self.delete_recent_searched_movie()
            self.show_movies_catalogue()
            self.ui.txt_search_movie.setText(result)
            return
        elif self.ui.txt_search_movie.text().strip() == '':
            self.delete_recent_searched_movie()
            self.show_movies_catalogue()
            return
        elif result['Response'] == 'False':
            self.delete_recent_searched_movie()
            self.show_movies_catalogue()
            self.ui.txt_search_movie.setText('Movie not found!')
            return
        
        buttons = self.ui.frm_movies.findChildren(QPushButton)

        try:
            self.delete_recent_searched_movie()
            urllib.request.urlretrieve(result['Poster'], 'profile_info_temp/poster_img_tmp.png')
            for button in buttons:
                button.hide()
            btn_movie_found = QPushButton(self.ui.scrollAreaWidgetContents)
            btn_movie_found.setIcon(QIcon('profile_info_temp/poster_img_tmp.png'))
            btn_movie_found.setMinimumSize(QtCore.QSize(200, 300))
            btn_movie_found.setMaximumSize(QtCore.QSize(200, 16777215))
            btn_movie_found.setIconSize(QtCore.QSize(200, 270))
            btn_movie_found.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn_movie_found.installEventFilter(self)
            self.ui.gridLayout_3.addWidget(btn_movie_found, 5, 0, 1, 1)
            btn_movie_found.clicked.connect(lambda: self.see_movie_info(result, QPixmap('profile_info_temp/poster_img_tmp.png')))
        except ValueError as e:
            self.delete_recent_searched_movie()
            self.ui.txt_search_movie.setText('Value Error!')
            self.show_movies_catalogue()
            return
        except urllib.error.HTTPError as error:
            self.delete_recent_searched_movie()
            self.ui.txt_search_movie.setText('Error 404: not found.')
            self.show_movies_catalogue()
            return
        
    def watch_category(self):
        """
        this function only changes the content available.
        """
        if self.ui.cbx_category.currentText() == '10+':
            self.ui.lbl_content_available.setText('Watch only kids content')
            self.ui.lbl_profile_public.setText('Kids')
        else:
            self.ui.lbl_content_available.setText('Watch all contents')
            self.ui.lbl_profile_public.setText('All')
        
    def show_movies_catalogue(self):
        """
        this function shows all thee posters (buttons) from the QFrame
        self.ui.frm_movies.
        """
        buttons = self.ui.frm_movies.findChildren(QPushButton)

        for button in buttons:
            button.show()
         
    def delete_recent_searched_movie(self):
        """
        this function deletes the recent searched movie when the user
        searches a movie or when there is an error during the search.
        """
        widget_button = self.ui.gridLayout_3.itemAtPosition(5, 0)

        if widget_button is not None and widget_button is not None:
            widget_button = widget_button.widget()
            if widget_button is not None:
                self.ui.gridLayout_3.removeWidget(widget_button)
                widget_button.deleteLater()
                
    def see_movie_info(self, result_json, poster: QPixmap):
        """
        this function extracts the information from the result_json, changes
        the stackedWidget current index to 4
        and adds a pixmap with the poster of the movie.
        
        PARAMETERS:
        result_json: the json result of the movie
        poster: a QPixmaap of the poster
        """
        self.ui.stackedWidget.setCurrentIndex(4)
        self.ui.lbl_image_poster.setPixmap(poster)
        self.ui.lbl_movie_title.setText(result_json['Title'])
        self.ui.lbl_movie_plot.setText(result_json['Plot'])
        self.ui.lbl_movie_year_edit.setText(result_json['Year'])
        self.ui.lbl_movie_released_edit.setText(result_json['Released'])
        self.ui.lbl_movie_genre_edit.setText(result_json['Genre'])
        self.ui.lbl_movie_writer_edit.setText(result_json['Writer'])
        self.ui.lbl_imdvrating_edit.setText(result_json['imdbRating'])
        self.ui.lbl_imdvvotes_edit.setText(result_json['imdbVotes'])
        
    def movieSearch(self, movie):
        """
        this function searches the information or a movie.
        """
        self.windowLoading()
        self.movie = MoviesAPI_selected(movie)
        self.movie.result_ready.connect(self.result_movie_search)
        self.movie.result_error.connect(self.result_movie_search)
        self.movie.start()
        
        self.loadingScreen.exec_()
        
    # Profile functions:
    
    def new_profile(self):
        """
        this function goest o the window SignUp.
        """
        self.signup = SignUp(self.profiles)
        self.signup.ui.btn_create.clicked.connect(self.append_new_profile)
        self.signup.exec_()
            
    def append_new_profiles_from_database(self, name, image):
        """
        this function appends a new profile from the database.
        
        PARAMETERS:
        name: the name of the user
        image: the image of the user
        """
        self.ui.gridLayout.addWidget(self.ui.btn_new_profile,0,self.num_profiles + 1,1,1)
        self.ui.gridLayout.addWidget(self.ui.btn_new_profile_text,1,self.num_profiles + 1,1,1)
        
        btn_profile = QPushButton()
        btn_profile.setMaximumSize(100,100)
        btn_profile.setMinimumSize(100,100)
        btn_profile.setIcon(QIcon(image))
        btn_profile.setIconSize(QtCore.QSize(100,100))
        btn_profile.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_profile.setObjectName(name)
        btn_profile.clicked.connect(lambda: self.changePageLogin(btn_profile.objectName()))
        
        frm_edit_profile = QFrame()
        frm_edit_profile.setObjectName(f'{name}_frm')
        
        lay_hor_edit_profile = QtWidgets.QHBoxLayout(frm_edit_profile)
        
        btn_edit_profile = QPushButton()
        btn_edit_profile.setIcon(QIcon('images/edit.svg'))
        btn_edit_profile.setIconSize(QSize(14,14))
        btn_edit_profile.setFixedSize(QSize(14,14))
        btn_edit_profile.setObjectName(f'{name}_edit')
        btn_edit_profile.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_edit_profile.clicked.connect(lambda: self.edit_profile(btn_edit_profile.objectName()[:-5]))
        
        btn_profile_text = QPushButton()
        btn_profile_text.setText(f'{name}')
        font = QtGui.QFont()
        font.setPointSize(12)
        btn_profile_text.setFont(font)
        btn_profile_text.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        btn_profile_text.setSizePolicy(sizePolicy)
        btn_profile_text.clicked.connect(lambda: self.changePageLogin(btn_profile_text.text()))
        btn_profile_text.setObjectName(f'{name}_txt')
        
        lay_hor_edit_profile.addWidget(btn_edit_profile)
        lay_hor_edit_profile.addWidget(btn_profile_text)
        
        self.ui.gridLayout.addWidget(btn_profile,0,self.num_profiles,1,1)
        self.ui.gridLayout.addWidget(frm_edit_profile,1,self.num_profiles,1,1)
        self.num_profiles += 1
        self.hide_button()
    
    def append_new_profile(self):
        """
        this function appends a recently created user.
        """
        with open('profile_info_temp/info_profile_tmp.txt','rt', encoding='utf-8') as f:
            name = f.readline()
        if name == 'Error':
            return
            
        self.ui.gridLayout.addWidget(self.ui.btn_new_profile,0,self.num_profiles + 1,1,1)
        self.ui.gridLayout.addWidget(self.ui.btn_new_profile_text,1,self.num_profiles + 1,1,1)
        
        btn_profile = QPushButton()
        btn_profile.setMaximumSize(100,100)
        btn_profile.setMinimumSize(100,100)
        btn_profile.setIcon(QIcon('profile_info_temp/profile_img_tmp.png'))
        btn_profile.setIconSize(QtCore.QSize(100,100))
        btn_profile.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_profile.setObjectName(name)
        btn_profile.clicked.connect(lambda: self.changePageLogin(btn_profile.objectName()))
        
        frm_edit_profile = QFrame()
        frm_edit_profile.setObjectName(f'{name}_frm')
        
        lay_hor_edit_profile = QtWidgets.QHBoxLayout(frm_edit_profile)
        
        btn_profile_text = QPushButton()
        btn_profile_text.setText(f'{name}')
        font = QtGui.QFont()
        font.setPointSize(12)
        btn_profile_text.setFont(font)
        btn_profile_text.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        btn_profile_text.setSizePolicy(sizePolicy)
        btn_profile_text.clicked.connect(lambda: self.changePageLogin(btn_profile_text.text()))
        btn_profile_text.setObjectName(f'{name}_txt')
        
        btn_edit_profile = QPushButton()
        btn_edit_profile.setIcon(QIcon('images/edit.svg'))
        btn_edit_profile.setIconSize(QSize(14,14))
        btn_edit_profile.setFixedSize(QSize(14,14))
        btn_edit_profile.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_edit_profile.setObjectName(f'{name}_edit')
        btn_edit_profile.clicked.connect(lambda: self.edit_profile(btn_edit_profile.objectName()[:-5]))
        
        lay_hor_edit_profile.addWidget(btn_edit_profile)
        lay_hor_edit_profile.addWidget(btn_profile_text)
        
        self.ui.gridLayout.addWidget(btn_profile,0,self.num_profiles,1,1)
        self.ui.gridLayout.addWidget(frm_edit_profile,1,self.num_profiles,1,1)
        self.num_profiles += 1
        
        self.hide_button()
        
    def edit_profile(self, name):
        """
        this function goes to the index 2 and extracts the information
        of the user to edit.
        """
        self.name = name
        self.ui.stackedWidget.setCurrentIndex(2)
        profile_btn = self.findChild(QPushButton, self.name)
        profile_image = profile_btn.icon()
        self.ui.btn_image_profile_edit.setIcon(profile_image)
        self.ui.txt_profile_name_edit.setText(self.name)
        
    def edit_image(self):
        """
        this function adds a new image fron a file of the user and 
        then transforms it into a circular image.
        """
        try:
            root, ok = QFileDialog.getOpenFileName(self, 'Select image file...', 'C:\\','Image File (*.jpg *.png)')
            
            if ok:
                original_image = Image.open(root)

                width, height = original_image.size
                mask = Image.new("L", (width, height), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, width, height), fill=255)

                circular_image = Image.new("RGBA", (width, height))
                circular_image.paste(original_image, (0, 0), mask)
                
                with BytesIO() as buffer:
                    circular_image.save(buffer, format="PNG")
                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())
                    pixmap.save('profile_info_temp/profile_img_tmp.png','PNG')
            
                self.ui.btn_image_profile_edit.setIcon(QIcon(pixmap))  
        except:
            return 'Error'
        
    def remove_profile(self):
        """
        This function removes a profile from the gridLayout profiles and
        from the database
        """
        self.messagebox_confirmation = MessageBox_confirmation(message = 'Do you want to remove this profile?', icon = 'images/alert_triangle_white.png')
        self.messagebox_confirmation.ui.yesBtn.clicked.connect(self.confirmation)
        self.messagebox_confirmation.ui.noBtn.clicked.connect(self.confirmation)
        self.messagebox_confirmation.exec_()
        
        if not self.confirmation_ob is True:
            return
                    
        profile_btn = self.findChild(QPushButton, self.name)
        profile_frm = self.findChild(QFrame, f'{self.name}_frm')
        
        position = self.ui.gridLayout.getItemPosition(self.ui.gridLayout.indexOf(profile_btn))
        for e in range(position[1] + 1,6):
            item = self.ui.gridLayout.itemAtPosition(0, e)
            item_text = self.ui.gridLayout.itemAtPosition(1, e)
            if item and item_text:
                button = item.widget()
                button_text = item_text.widget()
                self.ui.gridLayout.addWidget(button,0,e - 1,1,1)
                self.ui.gridLayout.addWidget(button_text,1,e - 1,1,1)
        
        profile_btn.deleteLater()
        profile_frm.deleteLater()
        
        self.profiles.removeProfile(self.name)
        
        if self.ui.btn_new_profile.isHidden():
            self.ui.btn_new_profile.show()
            self.ui.btn_new_profile_text.show()
            
        self.num_profiles -= 1
        
        self.ui.stackedWidget.setCurrentIndex(0)
        
    def confirmation(self):
        """
        this function is a confirmation for the 'MessageBox_confirmation'
        it confirms if the buttton selected in the MessageBox is yes (True)
        or no (False)
        """
        button = self.sender()
        if button.text().lower() == 'yes':
            self.confirmation_ob = True
        else:
            self.confirmation_ob = False
        
    def save_profile(self):
        """
        This function saves the edited information of the user
        to edit.
        """
        new_name = self.ui.txt_profile_name_edit.text()
        new_image = self.ui.btn_image_profile_edit.icon()
        
        iselement = self.profiles.isNameInDatabase(new_name)
        if iselement and iselement[0] != self.name:
            self.messagebox = MessageBox_UI(message = 'that profile is already created')
            self.messagebox.exec_()
            return
        
        profile_btn = self.findChild(QPushButton, self.name)
        profile_btn_txt = self.findChild(QPushButton, f'{self.name}_txt')
        profile_btn_edit = self.findChild(QPushButton, f'{self.name}_edit')
        profile_frm = self.findChild(QFrame, f'{self.name}_frm')
        
        profile_btn.setIcon(new_image)
        profile_btn.setObjectName(new_name)
        
        profile_btn_txt.setText(new_name)
        profile_btn_txt.setObjectName(f'{new_name}_txt')
        
        profile_btn_edit.setObjectName(f'{new_name}_edit')
        
        profile_frm.setObjectName(f'{new_name}_frm')
        
        new_image = new_image.pixmap(QSize(100,100))
        new_image.save('profile_info_temp/profile_img_tmp.png','PNG')
        new_image = self.profiles.convert_to_binary('profile_info_temp/profile_img_tmp.png')
        
        self.profiles.updateProfile(self.name, new_name, new_image)
        self.ui.stackedWidget.setCurrentIndex(0)
        
    def hide_button(self):
        """
        this function hides the new_profile button if there
        are 5 profiles.
        """
        if self.num_profiles == 6:
            self.ui.btn_new_profile.hide()    
            self.ui.btn_new_profile_text.hide()
        
    def changePageLogin(self, buttonName):
        """
        this function changes the page to index1 (login)
        """
        self.ui.txt_password_login.setText('')
        self.ui.txt_password_login.setStyleSheet('border-color:white;')
        
        self.storedPassword = self.profiles.searchPasswordProfile(buttonName)
        self.ui.lbl_hello_user.setText(self.ui.lbl_hello_user.text().replace('_', buttonName))
        self.ui.stackedWidget.setCurrentIndex(1)
        
    def see_password(self):
        if self.ui.txt_password_login.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
            self.ui.txt_password_login.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.ui.btn_see_password.setIcon(QIcon('images/eye-off.svg'))
        elif self.ui.txt_password_login.echoMode() == QtWidgets.QLineEdit.EchoMode.Normal:
            self.ui.txt_password_login.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.ui.btn_see_password.setIcon(QIcon('images/eye.svg'))
    
    def verifyPassword(self, storedPassword):
        """
        this funcction analizes the provided password to see if it is equial to the stored password
        """
        entered_password = self.ui.txt_password_login.text().strip()
        verified_password = self.profiles.verify_password(storedPassword, entered_password)
        if not verified_password:
            self.ui.txt_password_login.setText('')
            self.ui.txt_password_login.setStyleSheet('border-color:red;')
            return
        button = self.findChild(QPushButton, self.ui.lbl_hello_user.text()[6:-33])
        icon = button.icon()
        pixmap = icon.pixmap(QSize(100,100))
        
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.lbl_profile_name_information.setText(self.ui.lbl_hello_user.text()[6:-33])
        self.ui.lbl_profile_image_information.setPixmap(pixmap)
        self.ui.lbl_hello_user.setText('Hello _!\n Insert your password to enter.')
        
    def goToWebpage(self):
        """
        my webpages
        """
        if self.sender().objectName() == 'btn_github':
            url = QtCore.QUrl('https://github.com/Alejandrox27')
            QtGui.QDesktopServices.openUrl(url)
        if self.sender().objectName() == 'btn_facebook':
            url = QtCore.QUrl('https://www.facebook.com/didier.mejia.50746/')
            QtGui.QDesktopServices.openUrl(url)
        if self.sender().objectName() == 'btn_instagram':
            url = QtCore.QUrl('https:///www.instagram.com/_alejandro_829/')
            QtGui.QDesktopServices.openUrl(url)
        if self.sender().objectName() == 'btn_email':
            url = QtCore.QUrl('https://mail.google.com/mail/u/0/?fs=1&to=alej.mejia89@gmail.com&su&body&tf=cm')
            QtGui.QDesktopServices.openUrl(url)
             
class SignUp(QDialog):
    def __init__(self, profiles):
        super().__init__()
        
        self.profiles = profiles
        
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        with open('styles/signup_style.css', 'r') as f:
            stylesheet = f.read()
        self.setStyleSheet(stylesheet)
        
        self.initializeGui()
        
    def initializeGui(self):
        self.ui = Ui_SignUp()
        self.ui.setupUi(self)
        
        self.defaultIcon = self.ui.btn_image_register.icon().pixmap(100,100)
        
        self.ui.btn_close_signup.clicked.connect(self.closeAnimation)
        
        self.ui.btn_see_password_register.clicked.connect(self.see_password)
        self.ui.btn_see_password_register_2.clicked.connect(self.see_password)
        
        self.ui.btn_image_register.clicked.connect(self.select_image)
        
        self.ui.btn_create.clicked.connect(self.create_profile)
        self.ui.txt_password_register.textChanged.connect(self.password_verify)
        self.ui.txt_repeat_password_register.textChanged.connect(self.password_verify)
        self.ui.txt_email_register.textChanged.connect(self.email_verify)
        
    def select_image(self):
        """
        this function extracts a new image from files
        and converts it into a circular image
        """
        try:
            self.root, ok = QFileDialog.getOpenFileName(self, 'Select image file...', 'C:\\','Image File (*.jpg *.png)')
            
            if ok:
                icon = QIcon(self.root)
                icon_p = icon.pixmap(100,100)
                if self.defaultIcon.toImage() == icon_p.toImage():
                    return
                
                original_image = Image.open(self.root)

                width, height = original_image.size
                mask = Image.new("L", (width, height), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, width, height), fill=255)

                circular_image = Image.new("RGBA", (width, height))
                circular_image.paste(original_image, (0, 0), mask)
                
                with BytesIO() as buffer:
                    circular_image.save(buffer, format="PNG")
                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())
                    pixmap.save('profile_info_temp/profile_img_tmp.png','PNG')
            
                self.ui.btn_image_register.setIcon(QIcon(pixmap))  
        except:
            return
        
    def see_password(self):
        button = self.sender().objectName()
    
        if button == 'btn_see_password_register' and self.ui.txt_password_register.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
            self.ui.txt_password_register.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.ui.btn_see_password_register.setIcon(QIcon('images/eye-off.svg'))
        elif button == 'btn_see_password_register' and self.ui.txt_password_register.echoMode() == QtWidgets.QLineEdit.EchoMode.Normal:
            self.ui.txt_password_register.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.ui.btn_see_password_register.setIcon(QIcon('images/eye.svg'))
        elif button == 'btn_see_password_register_2' and self.ui.txt_repeat_password_register.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
            self.ui.txt_repeat_password_register.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.ui.btn_see_password_register_2.setIcon(QIcon('images/eye-off.svg'))
        elif button == 'btn_see_password_register_2' and self.ui.txt_repeat_password_register.echoMode() == QtWidgets.QLineEdit.EchoMode.Normal:
            self.ui.txt_repeat_password_register.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.ui.btn_see_password_register_2.setIcon(QIcon('images/eye.svg'))
    
    def password_verify(self):
        """
        this function adds a red stylesheet if the password is wrong
        """
        password_regex = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=\w{8,})\w*$')
        sender = self.sender()
        if sender == self.ui.txt_password_register:
            text = self.ui.txt_password_register.text().strip()
            if not password_regex.match(text):
                self.ui.txt_password_register.setStyleSheet('border-color:red;')
            else:
                self.ui.txt_password_register.setStyleSheet('border-color:white;')   
        else:
            text = self.ui.txt_repeat_password_register.text().strip()
            if not password_regex.match(text):
                self.ui.txt_repeat_password_register.setStyleSheet('border-color:red;')
            else:
                self.ui.txt_repeat_password_register.setStyleSheet('border-color:white;') 
    
    def email_verify(self):
        """
        this function adds a red stylesheet if the email is wrong
        """
        email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        text = self.ui.txt_email_register.text().strip()
        if not email_regex.fullmatch(text):
            self.ui.txt_email_register.setStyleSheet('border-color:red;')
        else:
            self.ui.txt_email_register.setStyleSheet('border-color:white;')
    
    def create_profile(self):
        """
        this function creates a new profile and adds it into the database
        """
        name = self.ui.txt_name_register.text().strip()
        password = self.ui.txt_password_register.text().strip()
        password_repeat = self.ui.txt_repeat_password_register.text().strip()
        email = self.ui.txt_email_register.text().strip()
        image = self.ui.btn_image_register.icon().pixmap(100,100)
        
        password_regex = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=\w{8,})\w*$')
        email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        
        if len(name) == 0:
            self.writeErrorProfileTxt()
            self.message = MessageBox_UI(message = 'Write a name for your profile')
            self.message.exec_()
            return
        
        if not password_regex.match(password):
            self.writeErrorProfileTxt()
            self.message = MessageBox_UI(message = 'Write a correct password \n-min 8 caracters\n-at least one mayus letter\n-at least one number)')
            self.message.exec_()
            return
        
        if not re.match(password_regex, password_repeat):
            self.writeErrorProfileTxt()
            self.message = MessageBox_UI(message = 'Write a correct password \n-min 8 caracters\n-at least one mayus letter\n-at least one number)')
            self.message.exec_()
            return
        
        if password != password_repeat:
            self.writeErrorProfileTxt()
            self.message = MessageBox_UI(message = "The passwords must be the same.")
            self.message.exec_()
            return
        
        if not re.fullmatch(email_regex, email):
            self.writeErrorProfileTxt()
            self.message = MessageBox_UI(message = 'Write a valid e-mail')
            self.message.exec_()
            return
        
        if image.toImage() == self.defaultIcon.toImage():
            self.writeErrorProfileTxt()
            self.message = MessageBox_UI(message = 'set an image for your profile')
            self.message.exec_()
            return
        
        if os.path.exists('profile_info_temp/info_profile_tmp.txt'):   
            os.remove('profile_info_temp/info_profile_tmp.txt')
            
        with open('profile_info_temp/info_profile_tmp.txt', 'at', encoding='utf-8') as f:
            f.write(f'{name}')
            
        image = self.profiles.convert_to_binary('profile_info_temp/profile_img_tmp.png')
        
        password = self.profiles.hash_password(password)
        profile = Profile(name, password, email, image)
        thread = threading.Thread(target=self.profiles.addProfile, args=(profile,))
        thread.start()
        thread.join()
        
        thread = threading.Thread(target=self.sendEmail, args=(email,))
        thread.start()
        
        if self.profiles.result_queue.get():
            self.closeAnimation()
        else:
            self.writeErrorProfileTxt()
            self.message = MessageBox_UI(message = 'The Profile name must be UNIQUE')
            self.message.exec_()
            
    def writeErrorProfileTxt(self):
        """
        this function writes a error if the profile is not ok
        """
        if os.path.exists('profile_info_temp/info_profile_tmp.txt'):   
            os.remove('profile_info_temp/info_profile_tmp.txt')
            
        with open('profile_info_temp/info_profile_tmp.txt', 'at', encoding='utf-8') as f:
            f.write(f'Error')
        
    def sendEmail(self, email):
        """
        this function sends a mail to my gmail if you want to leave a review or a question
        """
        load_dotenv()
        
        msg = MIMEMultipart()
        msg['From'] = os.getenv('USER_EMAIL')
        msg['To'] = email
        msg['Subject'] = 'Nerfliz'
        
        tMessage = f'''Thanks for downloading Nerfliz.
I am so proud of this program and i would be really
grateful to see your reviews or contributions.
\n
\n
If my program Nerfliz has some errors feel free to let me know
and give me some tips on how to improve my code, that would help me to improve.
\n
\n
Alejandro Mejía:\n
Email: alej.mejia89@gmail.com\n
github: www.github.com/Alejandrox27\n
instagram: www.instagram.com/_alejandro_829/\n
facebook: www.facebook.com/didier.mejia.50746/\n'''
        
        email = MIMEText(tMessage,"plain")
        
        msg.attach(email)
        
        mailServer = smtplib.SMTP(os.getenv('SMTP_SSL'), 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(os.getenv('USER_EMAIL'), os.getenv('PASSWORD_EMAIL'))
        
        mailServer.sendmail(os.getenv('USER_EMAIL'), os.getenv('USER_EMAIL'),msg.as_string())
        
        mailServer.close()
        
    def showEvent(self, event):
        super().showEvent(event)

        self.animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        
    def closeAnimation(self):
        self.fade_out_animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.fade_out_animation.setDuration(200)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.finished.connect(self.close)
        self.fade_out_animation.start()
    
if __name__ == '__main__':
    root = QApplication(sys.argv)
    window = TermsAndConditions()
    window.show()
    sys.exit(root.exec_())
    