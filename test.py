def workDict():
    return {'200231':1,'200237':2,'200238':3,'280010':4,'220009':5}

def writeProductId(qrcode:str)->int:
    '''
        extract the work type code from QRCODE
        return the Product ID
    '''
    qrcode = '200238-1:2311379270:D:G601'
    wdict = workDict()
    
    qrwork = qrcode[:6]
    if qrwork in wdict.keys():
        id = wdict[qrwork]
        print(id)
    
writeProductId('123')