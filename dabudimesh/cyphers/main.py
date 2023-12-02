from kyber import Kyber768
pk, sk =Kyber768.keygen()
c, key =Kyber768.enc(pk)
_key = Kyber768.dec(c,sk)
print(key)
print(_key)
