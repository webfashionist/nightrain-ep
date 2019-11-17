__author__ = 'naetech'

import sys
import os
import shutil
import urllib
import ntpath
from urllib.request import urlopen

import zipfile
from .Settings import Settings
from .Configurations import Configurations
import module_locator

import subprocess
from subprocess import run


class Compiler:
    php_version = ""
    application_name = ""

    build_dir = "./build"
    output_dir = "./dist"
    tmp_dir = "./nrtmp"
    resources_dir = "./Resources"

    php_download_url = "https://www.php.net/distributions/php-%s.tar.gz" % php_version
    php_downloaded_folder_name = ntpath.basename(php_download_url)
    php_tmp_folder = "php-%s" % php_version

    php_linux_binary_dir = "/home/naetech/php"  # @TODO replace
    php_windows_binary_dir = "C:\\nightrain_php"  # @TODO replace
    php_mac_binary_dir = "./nrtmp/%s/%s/" % (php_tmp_folder, php_tmp_folder)

    pyinstaller_path_mac = "./venv/bin/pyinstaller"  # PyInstaller from PyCharm
    pyinstaller_path_windows = "./venv/bin/pyinstaller"  # PyInstaller from PyCharm
    pyinstaller_path_linux = "./venv/bin/pyinstaller"  # PyInstaller from PyCharm

    def __init__(self, output_dir, tmp_dir, resources_dir, argv):
        self.output_dir = output_dir
        self.tmp_dir = tmp_dir
        self.resources_dir = resources_dir

        program_settings = Settings()
        program_path = module_locator.module_path()
        program_settings.load_settings("%s/%s/%s" % (program_path, "Resources", "settings.ini"))

        self.application_name = program_settings.read_setting("application_name")
        self.php_version = program_settings.read_setting("php_version")

    def get_application_name(self):
        return self.application_name

    @staticmethod
    def is_linux():

        platform = sys.platform
        if "linux" in platform:
            return True
        else:
            return False

    @staticmethod
    def is_windows():
        if "win" in sys.platform and "darwin" not in sys.platform:
            return True
        else:
            return False

    @staticmethod
    def is_mac():
        if "darwin" in sys.platform:
            return True
        else:
            return False

    def compile_php_windows(self):
        # remove the old binary
        if os.path.exists(self.php_windows_binary_dir):
            shutil.rmtree(self.php_windows_binary_dir)

        # create a random tmp directory
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

        os.mkdir(self.tmp_dir)

        # download the latest version of PHP
        php_file_zip_download_link = "http://windows.php.net/downloads/releases/archives/php-5.5.12-nts-Win32-VC11-x86.zip"
        php_file_zip_dest = "%s/%s" % (self.tmp_dir, "php-5.5.12-Win32-VC11-x86.zip")
        print("Downloading %s" % php_file_zip_download_link)
        urllib.request.urlretrieve(php_file_zip_download_link, php_file_zip_dest)
        print("Finished downloading %s" % php_file_zip_download_link)

        zfile = zipfile.ZipFile(php_file_zip_dest)
        for name in zfile.namelist():
            (dirname, filename) = os.path.split(name)
            extracted_dir = "%s\\%s" % (self.php_windows_binary_dir, dirname)
            print("Decompressing " + filename + " on " + dirname)
            if not os.path.exists(extracted_dir):
                os.makedirs(extracted_dir)
            zfile.extract(name, extracted_dir)

        return True

    def compile_php_mac(self):
        # remove the old binary
        if os.path.exists(self.php_mac_binary_dir):
            shutil.rmtree(self.php_mac_binary_dir)
        return False
        # create a random tmp directory
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

        os.mkdir(self.tmp_dir)

        # download the latest version of PHP
        php_tar_file_save_location = "%s/%s" % (self.tmp_dir, self.php_downloaded_folder_name)
        # fixme add a config file so the developers can update this link without modifying the source codes
        php_tar_download_link = self.php_download_url
        self.download_file(php_tar_download_link, php_tar_file_save_location)

        php_extracted_dir = "%s/%s" % (self.tmp_dir, self.php_tmp_folder)
        os.mkdir(php_extracted_dir)
        run(["tar", "-C", php_extracted_dir, "-zxvf", php_tar_file_save_location])

        # compile PHP
        php_source_dir = "%s/%s" % (php_extracted_dir, self.php_tmp_folder)

        configure_command = "cd %s && ./configure --prefix=%s/%s " \
                            "--enable-bcmath " \
                            "--enable-calendar " \
                            "--enable-mbstring " \
                            "--with-curl " \
                            "--enable-ssl " \
                            "--with-gd " \
                            % (php_source_dir, os.getcwd(), self.php_mac_binary_dir)
        run(configure_command, shell=True)

        make_command = "cd %s && make && sudo make install" % php_source_dir
        run(make_command, shell=True)

        return True

    def compile_php_linux(self):

        # remove the old binary
        if os.path.exists(self.php_linux_binary_dir):
            shutil.rmtree(self.php_linux_binary_dir)

        # create a random tmp directory
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

        os.mkdir(self.tmp_dir)

        # download the latest version of PHP
        phpTarFile = "%s/%s" % (self.tmp_dir, self.php_downloaded_folder_name)
        run(["wget", self.php_download_url, "-O", phpTarFile])

        phpDir = "%s/%s" % (self.tmp_dir, self.php_tmp_folder)
        os.mkdir(phpDir)
        run(["tar", "-C", phpDir, "-zxvf", phpTarFile])

        # compile PHP
        phpSourceDir = "%s/%s" % (phpDir, self.php_tmp_folder)

        configureCommand = "cd %s && ./configure --prefix=%s " \
                           "--enable-bcmath " \
                           "--enable-calendar " \
                           "--enable-mbstring " \
                           "--with-curl " \
                           "--with-gd " \
                           "--with-mysql " \
                           "--with-pdo-mysql " \
                           "--with-sqlite3" \
                           % (phpSourceDir, self.php_linux_binary_dir)
        run(configureCommand, shell=True)

        makeCommand = "cd %s && make && sudo make install" % phpSourceDir
        run(makeCommand, shell=True)

        return True

    def compile_nightrain_windows(self):
        self.clean_unncessary_files()
        spec_path = "--specpath=%s/%s" % (self.build_dir, "specs")
        application_icon = "--icon=%s/%s" % (self.resources_dir, "icon.ico")
        # fixme When using the -w option, the final executable causes error
        run(["python.exe", self.pyinstaller_path_windows, "--onefile", "--clean", "-y", "-F", spec_path, application_icon, "-n",
             self.application_name, "Application.py"],
            shell=True)
        self.clean_unncessary_files()

    def compile_nightrain_linux(self):
        self.clean_unncessary_files()
        spec_path = "--specpath=%s/%s" % (self.build_dir, "specs")
        run([self.pyinstaller_path_linux, "--clean", "-y", "-F", spec_path, "-n", self.application_name,
             "Application.py"])
        self.clean_unncessary_files()

    def compile_nightrain_mac(self):
        self.clean_unncessary_files()
        spec_path = "--specpath=%s/%s" % (self.build_dir, "specs")
        application_icon = "--icon=%s/%s/%s" % (os.getcwd(), self.resources_dir, "icon.icns")
        print("Icon: %s" % application_icon)
        run([self.pyinstaller_path_mac, "--clean", "-w", "-y", "-F", spec_path, application_icon, "-n",
             self.application_name, "Application.py"])
        self.clean_unncessary_files()

    def update_info_plist(self):
        if self.is_mac():
            plist_path = "./dist/app_version/%s.app/Contents/Info.plist" % self.application_name
            conf = Configurations()
            conf.compile_plist(plist_path)
            return True
        return False

    def make_dir(self, path):
        if not os.path.exists(path):
            try:
                os.mkdir(path)
                print("Successfully created: %s" % path)
                return True
            except:
                print("Could not create %s" % path)
                return False
        else:
            return False

    def move_file(self, source, destination):
        if os.path.exists(source):
            try:
                shutil.move(source, destination)
                print("Successfully moved %s to %s" % (source, destination))
                return True
            except:
                print("Could not move %s to %s" % (source, destination))
                return False
        else:
            return False

    def copy_file(self, source, destination):
        success_msg = "Successfully copied %s to %s" % (source, destination)
        failure_msg = "Could not copy %s to %s" % (source, destination)

        if os.path.exists(source) and os.path.isdir(source):
            try:
                directory_path = os.path.dirname(os.path.abspath(destination))
                os.makedirs(directory_path, exist_ok=True)
                shutil.copytree(source, destination)
                print(success_msg)
                return True
            except:
                e = sys.exc_info()
                print("Error: %s - %s" % (failure_msg, e[1]))
                return False
        elif os.path.exists(source) and os.path.isfile(source):
            try:
                directory_path = os.path.dirname(os.path.abspath(destination))
                os.makedirs(directory_path, exist_ok=True)
                shutil.copyfile(source, destination)
                print(success_msg)
                return True
            except:
                e = sys.exc_info()
                print("Error: %s - %s" % (failure_msg, e[1]))
                return False
        else:
            return False

    def copy_resources(self, custom_output_dir=None):

        items = [
            "www",
            "icon.png",
            "LICENSE"
        ]

        for item in items:
            if item == "icon.png" and (self.is_windows() or self.is_mac()):
                continue

            source = "%s/%s" % (self.resources_dir, item)
            if not custom_output_dir:
                destination = "%s/%s" % (self.output_dir, item)
            else:
                destination = "%s/%s" % (custom_output_dir, item)
            if os.path.exists(source):
                error = "Could not copy item %s" % item
                success = "Successfully copied %s to %s" % (source, destination)
                if os.path.isfile(source):
                    try:
                        directory_path = os.path.dirname(os.path.abspath(destination))
                        os.makedirs(directory_path, exist_ok=True)
                        shutil.copyfile(source, destination)
                        print(success)
                    except:
                        print(error)
                        return False
                else:
                    try:
                        shutil.copytree(source, destination)
                        print(success)
                    except:
                        print(error)
                        return False
            else:
                print("%s does not exist" % item)
                return False

    def copy_php_windows(self):
        destination = "%s/%s/%s" % (self.output_dir, "lib", "php")
        if os.path.exists(self.php_windows_binary_dir):
            try:
                shutil.copytree(self.php_windows_binary_dir, destination)
                print("Successfully copied %s to %s" % (self.php_windows_binary_dir, destination))
                return True
            except:
                print("Could not copy %s to %s" % (self.php_windows_binary_dir, destination))
                return False
        else:
            return False

    def copy_php_mac(self, destination_dir):
        php_path = subprocess.check_output(["which", "php"])
        destination_dir = "%s/bin/php" % destination_dir
        print("Copy PHP executable from %s to %s" % (php_path.decode("utf-8").strip(), destination_dir))
        self.copy_file(php_path.decode("utf-8").strip(), destination_dir)
        run("sudo chmod 0755 %s" % destination_dir, shell=True)
        return True

    def copy_php_linux(self):
        destination = "%s/%s/%s" % (self.output_dir, "lib", "php")
        if os.path.exists(self.php_linux_binary_dir):
            try:
                shutil.copytree(self.php_linux_binary_dir, destination)
                print("Successfully copied %s to %s" % (self.php_linux_binary_dir, destination))
                return True
            except:
                print("Could not copy %s to %s" % (self.php_linux_binary_dir, destination))
                return False
        else:
            return False

    def copy_php_ini_linux(self):
        src = "%s/%s" % (self.resources_dir, "php.ini")
        destination = self.get_php_ini_dest()
        try:
            directory_path = os.path.dirname(os.path.abspath(destination))
            os.makedirs(directory_path, exist_ok=True)
            shutil.copyfile(src, destination)
            print("Successfully copied %s to %s" % (src, destination))
            return True
        except:
            return False

    def copy_php_ini_windows(self):
        php_ini_src = "%s\\%s" % (self.php_windows_binary_dir, "php.ini-production")
        php_ini_dest = self.get_php_ini_dest()
        if os.path.exists(php_ini_src):
            try:
                directory_path = os.path.dirname(os.path.abspath(php_ini_dest))
                os.makedirs(directory_path, exist_ok=True)
                shutil.copyfile(php_ini_src, php_ini_dest)
                print("Successfully copied %s to %s" % (php_ini_src, php_ini_dest))

                # replace configs
                php_ini_configs = [
                    '; extension_dir = "ext"',
                    ';extension=php_gd2.dll',
                    ';extension=php_mbstring.dll',
                    ';extension=php_sqlite3.dll'
                ]

                for config in php_ini_configs:
                    config_uncommented = config.replace(";", "").strip()
                    Settings.replace(php_ini_dest, config, config_uncommented)
                    print("Replaced %s with %s in %s" % (config, config_uncommented, php_ini_dest))
                return True
            except:
                return False
        else:
            print("Could not find %s" % php_ini_src)

    def copy_php_ini_mac(self, dest):
        source = "%s/settings.ini" % self.resources_dir
        return self.copy_file(source, dest)

    def clean_dist(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def clean_unncessary_files(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)

    def remove_file(self, file_path):
        if os.path.exists(file_path):
            shutil.rmtree(file_path)

    def get_php_ini_dest(self):
        if self.is_linux() or self.is_mac():
            return "%s/%s/%s/%s/%s" % (self.output_dir, "lib", "php", "bin", "php.ini")
        elif self.is_windows():
            return "%s/%s/%s/%s" % (self.output_dir, "lib", "php", "php.ini")
        else:
            return False

    def get_settings_ini_dest(self):
        return "%s/%s" % (self.output_dir, "settings.ini")

    def download_file(self, download_link, where_to_save_file_including_file_name):
        print("Downloading %s" % download_link)
        urllib.request.urlretrieve(download_link, where_to_save_file_including_file_name)
        print("Finished downloading %s" % download_link)
        print("File saved to %s" % download_link)
