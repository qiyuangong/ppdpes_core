import ftplib
import os, shutil


def ftp_upload(filename, filepath):
    print "Begin Upload File to FTP"
    ftpfile = open("ftp",'rU')
    ftp = ftpfile.read().strip().split(' ')
    # print ftp
    session = ftplib.FTP(ftp[0], ftp[1], ftp[2])
    filein = open(filepath + filename, 'rb')
    session.set_pasv(0)
    session.cwd("FTP/QYGong")
    session.storbinary("STOR " + filename, filein)
    filein.close()
    session.quit()
    print "Upload Complete!"

def ftp_download(filename, filepath, flag=True):
    print "Begin Download File to FTP"
    ftpfile = open("ftp", 'rU')
    ftp = ftpfile.read().strip().split(' ')
    # print ftp
    session = ftplib.FTP(ftp[0], ftp[1], ftp[2])
    session.set_pasv(0)
    session.cwd("FTP/QYGong")
    if flag:
        fileout = open(filepath + filename, 'wb')
        session.retrbinary("RETR " + filename, fileout.write)
        fileout.close()
    else:
        gh_list = [t for t in session.nlst() if filename in t]
        for temp in gh_list:
            fileout = open(filepath + temp, 'wb')
            session.retrbinary("RETR " + temp, fileout.write)
            fileout.close()
    session.quit()
    print "Download Complete!"


def clear_dir(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        # print file_path
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print e

def remove_file(file, path):
    file_path = os.path.join(path, file)
    # print file_path
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print e

if __name__ == '__main__':
    ftp_upload('README.md','')