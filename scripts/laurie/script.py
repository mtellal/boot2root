
begin = "Publicspeakingisveryeasy.12624120720"
p5values_i = ['0', 'P', 'p', 'x']  
p5values_a = [ '5', 'E', 'U', 'e', 'u'] 
p5values_n = [ 'K', 'k']
p5values_t = ['M', 'm', ]
p5values_s = ['1', 'A', 'Q', 'a', 'q']
end = "426135" #reverse n-2 and n-3

with open('passwds.txt', 'w') as passwd:
    for p2value in ['1b214', '2b720', '7b524']:
            for i in p5values_i:
                for a in p5values_a:
                    for n in p5values_n:
                        for t in p5values_t:
                            for s in p5values_s:
                                passwd.write(begin + p2value + "9" + "o" + i + a + n + t + s + end + "\n")