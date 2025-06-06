def stem(a):
    b=[]
    c=0
    a=str(a)[::-1]
    for i in a:
        b.append(i)
        c+=1
        if int(a[::-1])>999:
            if c>1 and c%3==0:
                b.append('.')
    return (str(b).replace('[','').replace(']','').replace("'","").replace(",",'').replace(' ',''))[::-1]
a=13600


def format(a):
    s=stem(a[-1])
    b=int(s)
    current=''
    if b==1:
        current='рубль'
    elif b>=2 and b<=4:
        current='рубля'
    else:
        current='рублей'
    return f"{a} {current}"


print(format(stem(a)))