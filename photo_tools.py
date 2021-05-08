"""
Used to convert photo format, and change the 'date taken' of photo automatically for pictures seperated into folders based on date like year/month/photo.tif

The file names are determined by the folder structure. See README for details.

REQUIRES:
exiftool.exe found @ https://exiftool.org (the pyexiftool library is just a wrapper for this executable)
"""

import argparse
from pathlib import Path
from glob import glob
from multiprocessing import Pool
from random import randint
from tqdm import tqdm
from PIL import Image
import exiftool
from colorama import Fore


class _Collection:
    """Class is used to collect image files and returns list of dicts with dates and photo paths."""

    def __init__(self, from_extension, pictures_folder):
        """Initialize variables."""
        self.date_file = []
        self.pictures_folder = pictures_folder
        self.paths = glob(f'{str(pictures_folder)}**/**/**')
        self.photo_count = 0
        self.from_extension = from_extension

    def _collect_photos(self):
        """Collect image files and store in a dictionary."""
        print(Fore.BLUE + '\nCollecting Images...')
        for path in self.paths:
            picture_paths = glob(f"{path}/*.{self.from_extension}")
            if len(picture_paths) > 0:
                file_list = {
                    'file_name_date': str.replace(path.strip(str(self.pictures_folder)), '\\', '_'),
                    'exif_date': ("{}:01 00:01:01".format(str.replace(path.strip(str(self.pictures_folder)), '\\', ':'))).encode(),
                    'pictures': [self.pictures_folder.joinpath(pic) for pic in picture_paths]
                }
                self.date_file.append(file_list)
                self.photo_count += len(picture_paths)
        if len(self.date_file) < 1:
            print(Fore.RED + f"No image files found in the directory '{str(self.pictures_folder)}' with the specified file extension '{self.from_extension}'\n")
            return False
        else:
            print(Fore.GREEN + f"Collected {self.photo_count} Images\n")
            return self.date_file


class Convert:
    """Class used to loop through image files and convert to desired image format and change the date taken.\n
        Required(from_extension=string,to_extension=string), Optional(change_exif=boolean (default is True), path=pathlib.Path object (default is Path.cwd()). \n
        Requires exiftool.exe to be in your pictures folder. https://exiftool.org
    """

    def __init__(self, from_extension, to_extension, change_exif=True, pictures_folder=Path.cwd()):
        """Initialize variables."""

        self.date_file = _Collection(from_extension, pictures_folder)._collect_photos()
        self.to_extension = to_extension
        self.change_exif = change_exif
        self.file_name_date = ""
        self.exif_date = b""
        self.exif_tool = str(pictures_folder.joinpath('exiftool.exe'))
        self.et = exiftool.ExifTool(self.exif_tool)

    def convert_photo(self):
        """Convert image format."""

        if self.date_file is False:
            return
        #   Suppress the the "Decompression Bomb Warning" for large image files.
        Image.warnings.simplefilter('ignore', Image.DecompressionBombWarning)
        p = Pool()
        for file_list in self.date_file:
            self.file_name_date = file_list['file_name_date']
            self.exif_date = file_list['exif_date']
            p.map(
                self._save_img_file,
                tqdm(
                    file_list['pictures'],
                    desc=Fore.YELLOW + f"Proccessing Images in Folder: {self.file_name_date}" + Fore.GREEN,
                    ncols=100,
                    maxinterval=0.1,
                    bar_format='{desc} - {percentage:3.0f}%|{bar}| [{n_fmt}/{total_fmt}]'
                ),
                1
            )
        p.terminate()
        print(Fore.GREEN + '\nCompleted image conversion and date changes.\n')

    def _save_img_file(self, pic_file):
        """Save as desired image format."""

        try:
            img = Image.open(pic_file)
            #   Example name would be 1990_08_01.jpg if path variable in collect_photos() is 1990\\08. The last number is random to keep filenames unique.
            name = f"{self.file_name_date}_{str(randint(0, 1000))}.{self.to_extension}"
            save_path = pic_file.with_name(name)
            while save_path.is_file():
                name = f"{self.file_name_date}_{str(randint(0, 1000))}.{self.to_extension}"
                save_path = pic_file.with_name(name)
            #   see: https://pillow.readthedocs.io/en/3.1.x/handbook/image-file-formats.html#fully-supported-formats.
            if self.to_extension == "png":
                img.save(save_path, 'png', compress_level=0)
            elif self.to_extension == "jpg":
                img.save(save_path, 'jpeg', quality=99, optimize=True, progressive=True, dpi=(1200, 1200))
            else:
                img.save(save_path, self.to_extension)
            if self.change_exif:
                self.et.start()
                self._build_execute_EXIF_command(save_path)
                self.et.terminate()
        except PermissionError:
            print(Fore.RED + f"\nFailed to convert photo; it may be open in another program.\n    Skipping: {pic_file}")
        #   comment the below if you want to keep both the old image and new image files. Not Recommended...
        if save_path.is_file():
            try:
                pic_file.unlink()
            except PermissionError:
                print(Fore.RED + f"\nFailed to delete photo: {pic_file}")

    def _build_execute_EXIF_command(self, save_path):
        """Dynamically create the exiftool arguments needed to change the date and Execute full command. EXIF tool expects bytes objects."""

        save_path = exiftool.fsencode(str(save_path))
        overwrite_original = b'-overwrite_original'
        mod_create_date = b'-FileCreateDate=' + self.exif_date
        if self.to_extension == "png":
            all_date = b'-PNG:CreationTime='
        else:
            all_date = b'-AllDates='
        self.et.execute(overwrite_original, all_date, mod_create_date, save_path)


class DateChange:
    """Class used to loop through files and change the date.\n
        Required(from_extension=string), Optional(path=pathlib.Path object (default is Path.cwd())). \n
        Requires exiftool.exe to be in your pictures folder. https://exiftool.org
    """

    def __init__(self, from_extension, pictures_folder=Path.cwd()):
        """Initialize variables. EXIF tool expects bytes objects."""

        self.date_file = _Collection(from_extension, pictures_folder)._collect_photos()
        self.exif_date = b''
        self.overwrite_og = b'-overwrite_original'
        if from_extension == "png":
            self.all_date = b'-PNG:CreationTime='
        else:
            self.all_date = b'-AllDates='
        self.create_date = b'-FileCreateDate='
        self.exif_tool = str(pictures_folder.joinpath('exiftool.exe'))
        self.et = exiftool.ExifTool(self.exif_tool)

    def mod_exif_date(self):
        """Dynamically create the exiftool arguments. Then Execute full command."""

        if self.date_file is False:
            return
        p = Pool()
        for file_list in self.date_file:
            file_name_date = file_list['file_name_date']
            self.exif_date = file_list['exif_date']
            p.map(
                self._exif_tool,
                tqdm(
                    file_list['pictures'],
                    desc=Fore.YELLOW + f"Proccessing Images in Folder: {file_name_date}" + Fore.GREEN,
                    ncols=100,
                    maxinterval=0.1,
                    bar_format='{desc} - {percentage:3.0f}%|{bar}| [{n_fmt}/{total_fmt}]'
                ),
                1
            )
        p.terminate()
        print(Fore.GREEN + '\nCompleted date changes.\n')

    def _exif_tool(self, pic_file):
        pic_file = exiftool.fsencode(str(pic_file))
        mod_all_date = self.all_date + self.exif_date
        mod_create_date = self.create_date + self.exif_date
        self.et.start()
        self.et.execute(self.overwrite_og, mod_all_date, mod_create_date, pic_file)
        self.et.terminate()

def main():
    parser = argparse.ArgumentParser(
                        description='Used to convert image format or change exif date in image metadata or do both.')
    parser.add_argument("-fe", "--from_extension", 
                        required=True, 
                        type=str, 
                        help="REQUIRED! Original file extension of images. Supports any image type.")
    parser.add_argument("-te", "--to_extension", 
                        required=False, 
                        type=str, 
                        help="Destination image type. Supports png and jpg.")
    parser.add_argument("-pf", "--pictures_folder", 
                        required=False, 
                        default=Path.cwd(), 
                        type=str, 
                        help="Location of folder containing all images. Requires full path, no relative paths. Default is current working directory.")
    parser.add_argument("-ce", "--change_exif", 
                        required=False, 
                        action='store_true', 
                        help="Pass argument to change the exif date in image metadata.")
    parser.add_argument("-ci", "--convert_image", 
                        required=False, 
                        action='store_true', 
                        help="Pass argument to convert images.")
    parser.add_argument("-cid", "--convert_image_and_date", 
                        required=False, 
                        action='store_true', 
                        help="Pass argument to change the exif date in image metadata.")
    args = parser.parse_args()
    pictures_folder = str(args.pictures_folder)
    if args.convert_image_and_date or (args.change_exif and args.convert_image):
        if args.to_extension not in ["jpg", "png"]:
            parser.error("The script only supports conversion to jpg and png image format.")
        convert_img = Convert(from_extension=args.from_extension, to_extension=args.to_extension, change_exif=True, pictures_folder=Path(pictures_folder))
        convert_img.convert_photo()
    elif args.change_exif:
        change_date = DateChange(from_extension=args.from_extension, pictures_folder=Path(pictures_folder))
        change_date.mod_exif_date()
    elif args.convert_image:
        if args.to_extension not in ["jpg", "png"]:
            parser.error("The script only supports conversion to jpg and png image format.")
        convert_img = Convert(from_extension=args.from_extension, to_extension=args.to_extension, change_exif=False, pictures_folder=Path(pictures_folder))
        convert_img.convert_photo()
    else:
        parser.error("You have not chosen an option. You must supply one of the following arguments: --change_exif, --convert_image, --convert_image_and_date. See help: --help")


if __name__ == "__main__": 
    main()
