# Photo Tools
**Not Maintained:** *Code is not the best it was a project from when I was first learning python*  
  
Used to automatically convert image format or change exif date in image metadata or do both.  
  
**The script assumes that exiftool.exe is in the root level of your pictures folder.** https://exiftool.org *(the exiftool.py library is just a wrapper for this executable. I modified this but credit goes to https://github.com/smarnach/pyexiftool)*  

My scanner (Epson FastFoto FF-680W) only supported TIFF and JPEG and the JPEG compression was terrible and not adjustable. JPEG even looked bad at 1200x1200 dpi. So if you scanned all of your photos in Tiff format and found out the hard way that google photos doesn't support .tif files, like I did. Then use this to convert to any other format and change the appropriate file/image dates. The script can be used to change the EXIF dates to the dates in the folder structure. Example: /pictures/1990/08/photo.tif > 1990:08:01 00:01:01 (August 01, 1990 12:01:01am)  

PNG doesn't support EXIF and has no attribute "DateTimeOriginal" like a .jpg would. Therefore we need to set the "PNG:CreationTime" of the file. Windows uses this PNG attribute to infer the "Date Taken".    

# Usage

**Example 1:**  
You must pass the file extension of the source images and the path object to the root level of your pictures folder.  

```python

from photo_tools import DateChange
from pathlib import Path

pictures_folder = Path("C:/Users/user/OneDrive/Documents/pictures")
change_date = DateChange(from_extension="jpg", pictures_folder=pictures_folder)
change_date.mod_exif_date()

```

**Example 2:**  
You must pass the file extension of the source and output images and the path object to the root level of your pictures folder.  

```python

from photo_tools import Convert
from pathlib import Path

convert_img = Convert(from_extension="tif", to_extension="png", change_exif=True, pictures_folder=Path.cwd())
convert_img.convert_photo()

```

**Example 3:**
  
```
photo_tools.py [-h] -fe FROM_EXTENSION [-te TO_EXTENSION] [-pf PICTURES_FOLDER] [-ce] [-ci] [-cid]

Arguments:
  -h, --help            
                        show this help message and exit
  -fe, --from_extension
                        REQUIRED! Original file extension of images. Supports any image type.
  -te, --to_extension
                        Destination image type. Supports png and jpg.
  -pf, --pictures_folder
                        Location of folder containing all images. Requires full path, no relative paths. Default is current working directory.
  -ce, --change_exif    
                         Pass argument to change the exif date in image metadata.
  -ci, --convert_image  
                         Pass argument to convert images.
  -cid, --convert_image_and_date
                         Pass argument to change the exif date in image metadata.
```  
  
**Example Folder structure:**  

```tree

PictureFolder +
              |
              + exiftool.exe
              |
              + 1990 ---+ 01 + photo1.png
              |
              + 1993 ---+ 02 + photo1.tif
              |              |
              |              + photo2.tif
              |              |
              |              + photo3.tif
              |
              + 2000 ---+ 05 + photo1.png
              |    |         | 
              |    |         + photo2.png
              |    |
              |    +----+ 10 + photo1.png
              |              |
              |              + photo2.png
              |              |
              |              + photo3.png
              |              |
              |              + photo4.png
              |
              + 2006 ---+ 08 + photo1.tif
                   |         | 
                   |         + photo2.tif
                   |         | 
                   |         + photo3.tif
                   |
                   +----+ 09 + photo1.png
                             | 
                             + photo2.png
                             | 
                             + photo3.png

```
