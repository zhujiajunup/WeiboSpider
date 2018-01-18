import os

root = 'D:\\chrome_downloads\\one_piece'
for f in os.listdir(root):
    file_name = f.split('.')[0]
    os.rename(root+'\\' + f, root+'\\'+file_name+'.torrent')
