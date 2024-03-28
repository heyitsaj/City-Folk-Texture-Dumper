import xxhash
from PIL import Image
import re
import os
MAINPATH = "./output"
PATH = "./output"
#Palette info
def getPalette(palletteBytes):
    plt = palletteBytes[64:len(palletteBytes)]
    size = int(palletteBytes[4:8].hex(),16)-64
    vals = plt[:size]
    hashB = xxhash.xxh64(vals).hexdigest()
    pform = int(palletteBytes[24:28].hex(),16)
    valarr = [None] * 16
    colorNum = int(palletteBytes[28:30].hex(),16)
    #RGB565
    if pform == 1:
        for i in range(0,colorNum):
            colorhex = vals[i*2:i*2+2].hex()
            colorint = int(colorhex,16)
            r = colorint >> 11
            g = (colorint - (r << 11)) >> 5
            b = colorint - (r << 11) - (g << 5)
            valarr.append((int(r/31 * 255),int(g/63 * 255),int(b/31 * 255)))
    elif pform == 2:
        for i in range(0,int(len(vals)/2)):
            colorhex = vals[i*2:i*2+2].hex()
            colorint = int(colorhex,16)
            a = colorint >> 15
            if a == 1:
                r = (colorint - (a << 15)) >> 10
                g = (colorint - (a << 15) - (r << 10)) >> 5
                b = (colorint - (a << 15) - (r << 10) - (g << 5))
                valarr.append((int(r/31 * 255),int(g/31 * 255),int(b/31 * 255), 255))
            else:
                a = (colorint) >> 12
                r = (colorint - (a << 12)) >> 8
                g = (colorint - (a << 12) - (r << 8)) >> 4
                b = (colorint - (a << 12) - (r << 8) - (g << 4))
                valarr.append((int(r/15 * 255),int(g/15 * 255),int(b/15 * 255), int(a/7 * 255)))
    return [hashB,valarr]

#Tex info
def makeImageFromTex(texBytes,palletteData):
    size = int(texBytes[4:8].hex(),16)
    width = int(int(texBytes[28:30].hex(),16))
    height = int(int(texBytes[30:32].hex(),16))
    formatted = int(int(texBytes[32:36].hex(),16))
    size -=64
    pos = [0,0]
    texFile = texBytes[64:len(texBytes)]
    hashA = xxhash.xxh64(texFile[:size]).hexdigest()
    im = None
    block = [0,0]
    if formatted == 0: #I4
        im = Image.new(mode="RGB",size=(width,height))
        texFile = texBytes[64:len(texBytes)]
        blockw = 8
        blockh = 8
        maxblocksw = width/blockw
        for i in texFile[:size].hex():
            bit = int(i,16) * 17
            im.putpixel(tuple([pos[0] + block[0] * blockw,pos[1] + block[1] * blockh]),tuple([bit,bit,bit]))
            pos[0] += 1
            if pos[0] >= blockw :
                pos[1] += 1
                pos[0] = 0
            if pos[1] >= blockh:
                pos[0] = 0
                pos[1] = 0
                block[0] += 1
            if block[0] >= maxblocksw :
                block[0] = 0
                block[1] += 1
        im.save(PATH + "/tex1_"+str(width)+"x"+str(height)+"_"+str(hashA)+"_"+str(palletteData[0])+"_"+str(formatted)+".png")
    elif formatted == 1: #I8
        im = Image.new(mode="RGB",size=(width,height))
        texFile = texBytes[64:len(texBytes)]
        blockw = 8
        blockh = 4
        maxblocksw = width/blockw
        for i in range(0,len(texFile[:size].hex()),2):
            byte = int(texFile.hex()[i:i+2],16)
            im.putpixel(tuple([pos[0] + block[0] * blockw,pos[1] + block[1] * blockh]),tuple([byte,byte,byte]))
            pos[0] += 1
            if pos[0] >= blockw :
                pos[1] += 1
                pos[0] = 0
            if pos[1] >= blockh:
                pos[0] = 0
                pos[1] = 0
                block[0] += 1
            if block[0] >= maxblocksw :
                block[0] = 0
                block[1] += 1
        im.save(PATH + "/tex1_"+str(width)+"x"+str(height)+"_"+str(hashA)+"_"+str(formatted)+".png")
    elif formatted == 2: #TODO: IA4
        im = Image.new(mode="RGBA",size=(width,height))
        texFile = texBytes[64:len(texBytes)]
        blockw = 8
        blockh = 4
        maxblocksw = width/blockw
        for i in range(0,len(texFile[:size].hex()),2):
            byte = int(texFile.hex()[i:i+2],16)
            im.putpixel(tuple([pos[0] + block[0] * blockw,pos[1] + block[1] * blockh]),tuple([byte,byte,byte]))
            print(c,",","(",pos[0],",",pos[1],")")
            pos[0] += 1
            if pos[0] >= blockw :
                pos[1] += 1
                pos[0] = 0
            if pos[1] >= blockh:
                pos[0] = 0
                pos[1] = 0
                block[0] += 1
            if block[0] >= maxblocksw :
                block[0] = 0
                block[1] += 1
        im.save(PATH + "/tex1_"+str(width)+"x"+str(height)+"_"+str(hashA)+"_"+str(formatted)+".png")
    elif formatted == 3: #TODO: IA8
        im = Image.new(mode="RGBA",size=(width,height))
        texFile = texBytes[64:len(texBytes)]
        for i in range(0,size,4):
            alphaBit = int(texFile[i:i+2].hex(),16)
            colorBit = int(texFile[i+2:i+4].hex(),16)
            im.putpixel(tuple([pos[0],pos[1]]),tuple([colorBit,colorBit,colorBit,alphaBit]))
            pos[0] += 1
            if pos[0] >= width:
                pos[0] = 0
                pos[1] +=1
        im.save(PATH + "/tex1_"+str(width)+"x"+str(height)+"_"+str(hashA)+"_"+str(formatted)+".png")
    elif formatted == 4: #TODO: RGB565
        return
    elif formatted == 5: #TODO: RGB5A3
        return
    elif formatted == 6: #TODO: RGBA32
        return
    elif formatted == 8: #CI4
        #palette needed
        if len(palletteData[1]) == 4:
            im = Image.new(mode="RGBA",size=(width,height))
        else:
            im = Image.new(mode="RGB",size=(width,height))
        formatted = int(texBytes[32:36].hex(),16)
        
        #Extract CI4 from tex0 8x8 block format
        blockw = 8
        blockh = 8
        maxblocksw = width/blockw
        for i in texFile[:size].hex():
            color = int(i,16)
            im.putpixel(tuple([pos[0] + block[0] * blockw,pos[1] + block[1] * blockh]),palletteData[1][color])
            pos[0] += 1
            if pos[0] >= blockw :
                pos[1] += 1
                pos[0] = 0
            if pos[1] >= blockh:
                pos[0] = 0
                pos[1] = 0
                block[0] += 1
            if block[0] >= maxblocksw :
                block[0] = 0
                block[1] += 1
        im.save(PATH + "/tex1_"+str(width)+"x"+str(height)+"_"+str(hashA)+"_"+str(palletteData[0])+"_"+str(formatted)+".png")
    elif formatted == 9: #TODO: CI8
        #palette needed
        if len(palletteData[1]) == 4:
            im = Image.new(mode="RGBA",size=(width,height))
        else:
            im = Image.new(mode="RGB",size=(width,height))
        formatted = int(texBytes[32:36].hex(),16)
        
        #Extract CI8 from tex0 8x8 block format
        blockw = 8
        blockh = 8
        maxblocksw = width/blockw
        for i in texFile[:size].hex():
            color = int(i,16)
            im.putpixel(tuple([pos[0] + block[0] * blockw,pos[1] + block[1] * blockh]),palletteData[1][color])
            pos[0] += 1
            if pos[0] >= blockw :
                pos[1] += 1
                pos[0] = 0
            if pos[1] >= blockh:
                pos[0] = 0
                pos[1] = 0
                block[0] += 1
            if block[0] >= maxblocksw :
                block[0] = 0
                block[1] += 1
        im.save(PATH + "/tex1_"+str(width)+"x"+str(height)+"_"+str(hashA)+"_"+str(palletteData[0])+"_"+str(formatted)+".png")
    else:
        print("Unsupported Texture Type Given: ",formatted)      
    
    
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
            pfinal = b[int(p):int(p)+96]
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
        format = int(int(hfinal[i][32:36].hex(),16))
        if format < 7: #I4, I8, IA4, IA8
            makeImageFromTex(hfinal[i],None)
        
        elif format > 7: #CI4, CI8
            if type(pfinal) is bytes:
                makeImageFromTex(hfinal[i],getPalette(pfinal))
            elif type(pfinal) is list:
                istr = str(i).replace("tex_","").replace("plt_","").replace(".","")

                if str(i) == 'b':
                    makeImageFromTex(hfinal[i],getPalette(pfinal["skin0"]))
                else:
                    makeImageFromTex(hfinal[i],getPalette(pfinal["skin"]))
        else: print("Texture type not yet supported: ",format)

print("Welcome to the City Folk Character dumper\nCreated by Andrew McCauley\nSupported Files: brres")
while True:
    key = input("(1): (I)ndividual file dump\n(2): (F)ull Folder dump\n(3): (Q)uit\n")
    if key == '3' or key.lower() == 'q':
        break
    if key == '2' or key.lower() == 'f':
        break
    if key == '1' or key.lower() == 'i':
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
        

