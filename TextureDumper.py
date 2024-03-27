import xxhash
from PIL import Image
import re
import os
MAINPATH = "./output"
PATH = "./output"
#Palette info
def getPalette(palletteBytes):
    plt = palletteBytes[64:len(palletteBytes)]
    vals = plt[:32]
    hashB = xxhash.xxh64(vals).hexdigest()
    pform = int(palletteBytes[24:28].hex(),16)
    valarr = [None] * 16
    #RGB565
    if pform == 1:
        for i in range(0,int(len(vals)/2)):
            colorhex = vals[i*2:i*2+2].hex()
            colorint = int(colorhex,16)
            r = colorint >> 11
            g = (colorint - (r << 11)) >> 5
            b = colorint - (r << 11) - (g << 5)
            valarr[i] = (int(r/31 * 255),int(g/63 * 255),int(b/31 * 255))
    elif pform == 2:
        for i in range(0,int(len(vals)/2)):
            colorhex = vals[i*2:i*2+2].hex()
            colorint = int(colorhex,16)
            a = colorint >> 15
            if a == 1:
                r = (colorint - (a << 15)) >> 10
                g = (colorint - (a << 15) - (r << 10)) >> 5
                b = (colorint - (a << 15) - (r << 10) - (g << 5))
                valarr[i] = (int(r/31 * 255),int(g/31 * 255),int(b/31 * 255), 255)
            else:
                a = (colorint) >> 12
                r = (colorint - (a << 12)) >> 8
                g = (colorint - (a << 12) - (r << 8)) >> 4
                b = (colorint - (a << 12) - (r << 8) - (g << 4))
                valarr[i] = (int(r/15 * 255),int(g/15 * 255),int(b/15 * 255), int(a/7 * 255))
    return [hashB,valarr]

#Tex info
def makeImageFromTex(texBytes,palletteData):
    size = int(texBytes[4:8].hex(),16)
    width = int(int(texBytes[28:30].hex(),16))
    height = int(int(texBytes[30:32].hex(),16))
    formatted = int(int(texBytes[32:36].hex(),16))
    im = None
    if len(palletteData[1]) == 4:
        im = Image.new(mode="RGBA",size=(width,height))
    else:
        im = Image.new(mode="RGB",size=(width,height))
    size -=64
    id = 0
    blocksize = 8
    pos = [0,0]
    block = [0,0]
    texFile = texBytes[64:len(texBytes)]
    hashA = xxhash.xxh64(texFile[:size]).hexdigest()
    maxblocksw = width/8
    #Extract CI4 from tex0 8x8 block format
    for i in texFile[:size].hex():
        color = int(i,16)
        im.putpixel(tuple([pos[0] + block[0] * 8,pos[1] + block[1] * 8]),palletteData[1][color])
        pos[0] += 1
        if pos[0] >= blocksize :
            pos[1] += 1
            pos[0] = 0
        if pos[1] >= blocksize :
            pos[0] = 0
            pos[1] = 0
            block[0] += 1
        if block[0] >= maxblocksw :
            block[0] = 0
            block[1] += 1
        id += 1
    
    im.save(PATH + "/tex1_"+str(width)+"x"+str(height)+"_"+str(hashA)+"_"+str(palletteData[0])+"_"+str(formatted)+".png")
    return
def getIndices(str1 : str,str2 : str):
    arr = []
    for m in re.finditer(str2,str1):
        arr.append(m.start())
    return arr

        



def extract(b):
    hexv = b.hex()
    hs = getIndices(hexv,bytes("TEX0", 'utf-8').hex())
    hs = list(map(lambda x : int(x/2) ,hs))
    ps = getIndices(hexv,bytes("PLT0", 'utf-8').hex())
    ps = list(map(lambda x : int(x/2) ,ps))
    pfinal= {}
    if len(ps) == 1:
        for p in ps:
            pfinal["skin"] = b[int(p):int(p)+96]
    else:
        for p in ps:
            offset = int(b[int(p+20):int(p+24)].hex(),16)
            id = b[int(p) + offset:len(b)].hex()
            twos = [id[i:i+2] for i in range(0, len(id), 2)]
            newId = twos.index("00")
            val = b[int(p) + offset:int(p) + offset + newId].hex()
            bytes_obj = bytes.fromhex(val)
            result_string = bytes_obj.decode('utf-8')
            pfinal[result_string] = b[int(p):int(p)+96]
    hfinal = {}
    for h in hs:
        offset = int(b[int(h+20):int(h+24)].hex(),16)
        id = b[int(h) + offset:len(b)].hex()
        twos = [id[i:i+2] for i in range(0, len(id), 2)]
        newId = twos.index("00")
        val = b[int(h) + offset:int(h) + offset + newId].hex()
        bytes_obj = bytes.fromhex(val)
        result_string = bytes_obj.decode('utf-8')
        size = int(b[h + 4:h+8].hex(),16)
        hfinal[result_string] = b[int(h):int(h)+size]
    print("Textures found:")    
    for i in hfinal:
        print(i)
        if str(i).find("b")>-1:
            makeImageFromTex(hfinal[i],getPalette(pfinal["skin0"]))
        else:
            makeImageFromTex(hfinal[i],getPalette(pfinal["skin"]))

print("Welcome to the City Folk Character dumper\nCreated by Andrew McCauley\nSupported Files: brres")
while True:
    key = input("(1): (I)ndividual file dump\n(2): (F)ull Folder dump\n(3): (Q)uit\n")
    if key == '3' or key.lower() == 'q':
        break
    if key == '2' or key.lower() == 'f':
        break
    if key == '1' or key.lower() == 'I':
        fp = input("File Path: ")
        file = None
        try:
            file = open(fp.replace("\"",""),'rb')
        except:
            print("Unable to open file!")
            continue
        print(file.name)
        namePath = file.name.replace("\\","/").split("/")
        print(namePath)
        PATH = MAINPATH + "/"+namePath[-1].replace(".","_")
        ext = namePath[-1].split(".")[-1]
        if ext == "brres":
            fileD = file.read()
            os.makedirs(PATH, exist_ok=True)
            
            extract(fileD)
            
        else:
            "File must be brres"
        file.close()
    print("")
        

