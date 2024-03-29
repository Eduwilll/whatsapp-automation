from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse,Message
from pymongo import MongoClient
from datetime import datetime
from pycep_correios import get_address_from_cep, WebService, exceptions

app = Flask(__name__)


cluster = MongoClient("mongodb+srv://dbBot:admin@cluster0.yn32au7.mongodb.net/?retryWrites=true&w=majority") # endereço do mangodb
db = cluster["salgados"] #Banco de dados
users = db["users"] #Colletion user
orders = db["orders"] #Colletion Orders
complaints = db["complaint"]#Colletion complaint
chatbot = db["chatbot"]#Colletion complaint

def send_welcome_message(res, profileName):
    msg = res.message(f"Oi *{profileName.capitalize()}*!😘, obrigado por nos contatar *Salgados S.A*\nVocê pode escolher uma das opções abaixo\n\n *Digite* o número correspondente:\n\n1️⃣  Para saber nosso *endereço* e *horário*. \n2️⃣  Para conhecer nosso *menu*.\n3️⃣  Para saber nossas formas de *pagamento*. \n4️⃣  Para saber a taxa de *entrega*. \n5️⃣ Fazer uma reclamação ou obter ajuda. \n6️⃣ Finalizar")
    msg.media("https://i.ibb.co/tqYmh9R/1628253583441.jpg")
    return msg

def handle_main_menu(res, number, option, profileName):
    if option == 1:
        res.message("*Salgados S.A*\n*CNPJ*: 71.914.849/0001-19\n\nVocê pode nos contatar por telefone ou e-mail:\n\n*Telefone*: 1999111222\n*Email*: salgaldos@email.com.\n*Endereço*: Av. Andrade Neves, 1992 - Centro, Campinas - SP, 13013-161\n*Horário*: das *8:00* às *21:00*")
    elif option == 2:
        users.update_one({"number": number}, {"$set": {"status": "main-produto"}})
        res.message("Para conhecer nossos produtos, digite:\n\n1️⃣ *Produtos*\n2️⃣ *Combos e Kits*\n3️⃣ *Promoções*\n4️⃣ *Retornar*")
    elif option == 3:
        res.message('As formas de pagamento são:\nDinheiro\nCartão de Crédito/Débito\nPIX')
    elif option == 4:
        users.update_one({"number": number}, {"$set": {"status": "address"}})
        res.message("Digite seu CEP")
    elif option == 5:
        users.update_one({"number": number}, {"$set": {"status": "main-reclama"}})
        res.message("Digite sua dúvida e/ou reclamação.")
    elif option == 6:
        users.update_one({"number": number}, {"$set": {"status": "main-sair"}})
        res.message("Você poderia responder a algumas perguntas?\n1️⃣ *Sim*\n2️⃣ *Apenas Sair*")
    else:
        res.message("Por favor, digite um número válido")
    return res

def handle_address_status(res, number, text):
    try:
        option = int(text)
        address = get_address_from_cep(text, webservice=WebService.APICEP)
        if address is None:
            res.message("CEP não encontrado ou inválido. Por favor, verifique o CEP e tente novamente.")
        else:
            res.message(
                f"Seu endereço: {address['logradouro']} - {address['bairro']}, {address['cidade']} - {address['uf']}, {address['cep']} \n {address['complemento']}")
            users.update_one({"number": number}, {"$set": {"status": "ordered"}})
            res.message("Digite 1 para voltar ao menu principal:")

    except exceptions.InvalidCEP as eic:
        print(eic)
        res.message("CEP inválido! Por favor, verifique o CEP e tente novamente.")
    except exceptions.ConnectionError as errc:
        print(errc)
        res.message("Erro de conexão. Tente novamente mais tarde.")
    except exceptions.Timeout as errt:
        print(errt)
        res.message("Tempo de conexão expirado. Tente novamente mais tarde.")
    except exceptions.HTTPError as errh:
        print(errh)
        res.message("Erro de conexão. Tente novamente mais tarde.")
    except ValueError:
        res.message("Por favor, digite um número válido")
    except Exception as e:
        print(e)
        res.message("Ocorreu um erro. Tente novamente mais tarde.")


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body") #Pegando todos os inputs do user
    number = request.form.get("From")# pegando o numero de celular do cliente
    number = number.replace("whatsapp:", "") # Retirando a Palavra whatsapp.
    profileName = request.form.get("ProfileName")
    res = MessagingResponse() #Criando um objeto de MessagingResponse
    user = users.find_one({"number": number}) # atibuindo user o numero do user
    order = orders.find_one({"number": number})#
    complaint = complaints.find_one({"number": number})
    #print(f"Request values: {request.values}")

    #Caso não é encontrado o numero é acionado
    if bool(user) == False:
        send_welcome_message(res, profileName)
        users.insert_one({"number": number,"ProfileName":profileName ,"channel":"whatsapp" ,"status": "main", "messages": []})

    #Chegando o Status do user, estados possiveis para user = main, ordering, address, ordered.
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Por Favor digite um numero válido!")
            return str(res)
        handle_main_menu(res, number, option, profileName)

    elif user["status"] == "main-produto":
        try:
            option = int(text)
        except:
            res.message("Por Favor digite um numero válido")
            return str(res)
        if option == 1:
            msg = res.message("Lista dos Produtos:\n*Coxinha*\tRS6,00\n*Esfiha*\tRS6,00\n*Pastel*\tRS10,00")
            msg.media('https://i.pinimg.com/564x/72/01/06/72010685a0f1c48c4eff6e46f49f5ad6.jpg')
        elif option == 2:
            msg1 = res.message("Lista dos Combos e Kits::\n*Coxinha*\tRS6,00\n*Esfiha*\tRS6,00\n*Pastel*\tRS10,00")
            msg1.media('https://i.pinimg.com/564x/2b/65/58/2b65582f86c3ef419f7094de4482adeb.jpg')
        elif option == 3:
            msg2 = res.message("Lista das Promoções:\n*Coxinha* x4\tRS10,00\n*Esfiha* 4x\tRS10,00\n*Pastel* + *Refigerante 1L*\tRS10,00")
            msg2.media('https://i.pinimg.com/564x/25/db/8d/25db8d6bf80f7e62906b4bd336681e4b.jpg')
        elif option == 4:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("Você pode escolher uma das opções abaixo\n\n *Digite* o numero correspodente:\n\n1️⃣  Para saber nosso *endereço* e *horário*. \n2️⃣  Para conhecer nosso *menu*.\n3️⃣  Para saber nossa formas de *pagamento*.\n4️⃣  Para saber a taxa de *entrega*. \n5️⃣ Fazer Reclamação ou Ajuda. \n6️⃣ Finalizar")
        else:
            res.message("Por Favor digite um numero válido")
            return str(res)

    elif user["status"] == "main-reclama":
        complaints.insert_one({"number": number, "complaint": text, "name": profileName, "complaint_time": datetime.now()})
        res.message('Sua duvida/reclamação foi registrada.')
        users.update_one({"number": number}, {"$set": {"status": "main"}})
        res.message(
            "Você pode escolher uma das opções abaixo\n\n *Digite* o numero correspodente:\n\n1️⃣  Para saber nosso *endereço* e *horário*. \n2️⃣  Para conhecer nosso *menu*.\n3️⃣  Para saber nossa formas de *pagamento*.\n4️⃣  Para saber a taxa de *entrega*. \n5️⃣ Fazer Reclamação ou Ajuda. \n6️⃣ Finalizar")

    elif user["status"] == "main-sair":
        try:
            option = int(text)
        except:
            res.message("Por Favor digite um numero válido:")
            return str(res)
        if option == 1:
            users.update_one({"number": number}, {"$set": {"status": "main-sair-nota"}})
            res.message("Numa escala de 0 a 10 qual sua nota nosso atendimento via chatbot?")
        elif option == 2:
            users.delete_one({"number": number})
            res.message("Obrigado por ter nos contato!😀🎈\nDe acordo com a Lei Geral de Proteção de Dados Pessoais estaremos excluindo os seus dados.")
        else:
            res.message("Por Favor digite um numero válido:")

    elif user["status"] == "main-sair-nota":
        chatbot.insert_one({"number": number, "complaint": text, "name": profileName, "complaint_time": datetime.now()})
        users.delete_one({"number": number})
        res.message('Sua nota foi registrada.')
        res.message("Obrigado por ter nos contato!😀🎈\n De acordo com a Lei Geral de Proteção de Dados Pessoais estaremos excluindo os seus dados.")

    elif user["status"] == "address":
        handle_address_status(res, number, text)

    elif user['status'] == "ordered":
        res.message(f"Oi, obrigado por nos contatar novamente *{profileName.capitalize()}*!😘\n Você pode escolher uma das opções abaixo\n\n *Digite* o numero correspodente:\n\n1️⃣  Para saber nosso *endereço* e *horário*. \n2️⃣  Para conhecer nosso menu de *salgados*.\n3️⃣  Para saber nossa formas de *pagamento*.\n4️⃣  Para saber a taxa de *entrega*. \n5️⃣ Fazer Reclamação ou Ajuda \n6️⃣ Finalizar")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})

    return str(res)

if __name__ == '__main__':
    app.run(debug=True)
