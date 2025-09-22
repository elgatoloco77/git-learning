import socket

hostname = socket.gethostname()
print(f"Hostname: {hostname}")

IPAddress = socket.gethostbyname(hostname)
print(f"IP Address: {IPAddress}")

for i in range(10):
    print(i)
print("Hola")

numero_a = input("Dame el primer numero: ")
numero_b = input("Dame el segundo numero: ")
print(f"El resultado es: ")