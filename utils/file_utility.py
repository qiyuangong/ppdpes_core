import ftplib


def ftp_upload(filename, filepath):
    print "Begin Upload File to FTP"
    ftpfile = open("ftp",'rU')
    ftp = ftpfile.read().strip().split(' ')
    # print ftp
    session = ftplib.FTP(ftp[0], ftp[1], ftp[2])
    filein = open(filepath+filename,'rb')
    session.set_pasv(0)
    session.cwd("JSSEC/QYGong")
    session.storbinary("STOR " + filename, filein)
    filein.close()
    session.quit()
    print "Upload Complete!"

def ftp_download(filename, filepath):
    print "Begin Download File to FTP"
    ftpfile = open("ftp", 'rU')
    ftp = ftpfile.read().strip().split(' ')
    # print ftp
    session = ftplib.FTP(ftp[0], ftp[1], ftp[2])
    fileout = open(filepath + filename, 'wb')
    session.set_pasv(0)
    session.cwd("JSSEC/QYGong")
    session.retrbinary("RETR " + filename, fileout.write)
    fileout.close()
    session.quit()
    print "Download Complete!"


if __name__ == '__main__':
    ftp_upload('README.md','')