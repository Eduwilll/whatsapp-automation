from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://dbBot:admin@cluster0.yn32au7.mongodb.net/?retryWrites=true&w=majority")
db = cluster["salgados"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        msg = res.message("Oi, obrigado por nos contatar *Salgados S.A*\n Você pode escolher uma das opções abaixo\n\n *Digite* o numero correspodente:\n\n1️⃣  Para nos *contatar*\n2️⃣  Para *pedir* salgados\n3️⃣  Para saber o *horário de funcionamento*\n4️⃣  Para saber nosso *endereço*")
        msg.media("https://i.ibb.co/tqYmh9R/1628253583441.jpg")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Por Favor digite um numero válido")
            return str(res)

        if option == 1:
            res.message("Você pode nos contatar por Telefone ou E-mail:\n\n*Tel*: 1999111222\n*Email*:salgaldos@email.com.")
        elif option == 2:
            users.update_one({"number": number}, {"$set":{"status": "ordering"}})
            res.message("O que você quer ordernar?\n\n1️⃣ *Coxinha*\n2️⃣ *Esfiha*\n3️⃣ *Quibe*\n0️⃣ *Voltar*")
        elif option == 3:
            res.message("Horário de funcionamento é das *8:00* às *21:00*")
        elif option == 4:
            res.message("Av. Andrade Neves, 1992 - Centro, Campinas - SP, 13013-161")
        else:
            res.message("Por Favor digite um numero válido")
            return str(res)
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Por Favor digite um numero válido")
            return str(res)
        if option == 0:
            users.update_one({"number": number}, {"$set":{"status": "main"}})
            res.message(
                "Você pode escolher uma das opções abaixo\n\n *Digite* o numero correspodente:\n\n1️⃣  Para nos *contatar*\n2️⃣  Paara *pedir* salgados\n3️⃣  Para saber o *horário de funcionamento*\n4️⃣  Para saber nosso *endereço*")
        elif 1 <= option <= 3:
            salgados = ["Coxinha", "Esfiha", "Quibe"]
            select = salgados[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": select}})
            res.message("Otima escolha!😉")
            res.message("Digite seu endereço Cidade/Bairro/rua/numero e complemento")
        else:
            res.message("Por Favor digite um numero válido")
            return str(res)
    elif user["status"] == "address":
        select = user["item"]
        res.message("Obrigado por ter comprado conosco!😀🎈s")
        res.message(f"Seu pedido de *{select}* foi *recebido* e será entregue no maximo de *1 hora*")
        res.message("https://i.ibb.co/3mZrnMt/rickroll.gif")
        orders.insert_one({"number":number,"item":select,"address":text,"order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user['status'] == "ordered":
        res.message(
            "Oi, obrigado por nos contatar novamente *Salgados S.A*\nVocê pode escolher uma das opções abaixo\n\n*Digite o numero* correspodente:\n\n1️⃣  Para nos *contatar*\n2️⃣  Para *pedir* salgados\n3️⃣  Para saber o *horário de funcionamento*\n4️⃣  Para saber nosso *endereço*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})

    return str(res)
if __name__ == "__main__":
    app.run(port=5000)
