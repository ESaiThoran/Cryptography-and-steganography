



def BinaryToDecimal(binary):
    return int(binary, 2)

def encode_data_txt(file_path, datae):
    l = len(datae)
    i = 0
    add = ''
    while i < l:
        t = ord(datae[i])
        if 32 <= t <= 64:
            t1 = t + 48
            t2 = t1 ^ 170
            res = bin(t2)[2:].zfill(8)
            add += "0011" + res
        else:
            t1 = t - 48
            t2 = t1 ^ 170
            res = bin(t2)[2:].zfill(8)
            add += "0110" + res
        i += 1
    res1 = add + "111111111111"
    length = len(res1)
    print("Length of binary : ", length)
    
    HM_SK = ""
    ZWC = {"00": u'\u200C', "01": u'\u202C', "11": u'\u202D', "10": u'\u200E'}

    # Open the cover file and the stego file for reading and writing
    with open(file_path, "r+", encoding="utf-8") as file1:
        newfile = "temp.txt"
        with open(newfile, "w+", encoding="utf-8") as file3:
            word = []
            for line in file1:
                word += line.split()

            i = 0
            while i < len(res1):
                s = word[int(i / 12)]
                j = 0
                x = ""
                HM_SK = ""
                while j < 12:
                    x = res1[j + i] + res1[i + j + 1]
                    HM_SK += ZWC[x]
                    j += 2
                s1 = s + HM_SK
                file3.write(s1 + " ")
                i += 12

            t = int(len(res1) / 12)
            while t < len(word):
                file3.write(word[t] + " ")
                t += 1

                return newfile
            















def BinaryToDecimal(binary):
    return int(binary, 2)

def decode_data_txt(file_path):
    ZWC_reverse={u'\u200C':"00",u'\u202C':"01",u'\u202D':"11",u'\u200E':"10"}
    file = open(file_path, "r", encoding="utf-8")
    binary_data=''
    for line in file: 
        for words in line.split():
            T1=words
            binary_dataext=""
            for letter in T1:
                if(letter in ZWC_reverse):
                     binary_dataext+=ZWC_reverse[letter]
            if binary_dataext=="111111111111":
                break
            else:
                binary_data+=binary_dataext
    lengthd = len(binary_data)
    i=0
    a=0
    b=4
    c=4
    d=12
    decoded_data=''
    while i<lengthd:
        t3=binary_data[a:b]
        a+=12
        b+=12
        i+=12
        t4=binary_data[c:d]
        c+=12
        d+=12
        if(t3=='0110'):
            decimal_data = BinaryToDecimal(t4)
            decoded_data+=chr((decimal_data ^ 170) + 48)
        elif(t3=='0011'):
            decimal_data = BinaryToDecimal(t4)
            decoded_data+=chr((decimal_data ^ 170) - 48)
    return decoded_data
         