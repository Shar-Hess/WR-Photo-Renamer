# WR-Photo-Renamer
Used Pyinstaller to create .app file
pyinstaller --onefile --windowed rename-gui.py

created a dmg file in the disk utilities, which compressed the file. 

- This takes in a csv file that has the Image number and names as well as grades of everyone in the school.
- It compares the image number to the csv and renames the image as the last and first name... Or whatever you tell it to rename it by.
- It also tells you errors. For example if there was an image number that was a duplicate it will only do one and then tell you there was a duplicate. 
