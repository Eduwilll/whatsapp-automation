import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse, Message
from pymongo import MongoClient
from datetime import datetime
from pycep-correios import get_address_from_cep, WebService, exceptions
from dotenv import load_dotenv
from functools import wraps

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

app = Flask(__name__)

# Configuração do MongoDB
MONGO_URI = os.getenv('MONGO_URI')
cluster = MongoClient(MONGO_URI)
db = cluster["salgados"]
users = db["users"]
orders = db["orders"]
complaints = db["complaint"]
chatbot = db["chatbot"]


def log_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            app.logger.error(f"Error in {func.__name__}: {str(e)}")
            raise

    return wrapper


@log_error
def send_welcome_message(res, profileName):
    msg = res.message(f"Oi *{profileName.capitalize()}*!😘, obrigado por nos contatar *Salgados S.A*\n"
                      f"Você pode escolher uma das opções abaixo\n\n *Digite* o número correspondente:\n\n"
                      f"1️⃣  Para saber nosso *endereço* e *horário*. \n"
                      f"2️⃣  Para conhecer nosso *menu*.\n"
                      f"3️⃣  Para saber nossas formas de *pagamento*. \n"
                      f"4️⃣  Para saber a taxa de *entrega*. \n"
                      f"5️⃣ Fazer uma reclamação ou obter ajuda. \n"
                      f"6️⃣ Finalizar")
    msg.media("https://i.ibb.co/tqYmh9R/1628253583441.jpg")
    return msg


@log_error
def handle_main_menu(res, number, option, profileName):
    menu_options = {
        1: lambda: res.message("*Salgados S.A*\n*CNPJ*: 71.914.849/0001-19\n\n"
                               "Você pode nos contatar por telefone ou e-mail:\n\n"
                               "*Telefone*: 1999111222\n*Email*: salgaldos@email.com.\n"
                               "*Endereço*: Av. Andrade Neves, 1992 - Centro, Campinas - SP, 13013-161\n"
                               "*Horário*: das *8:00* às *21:00*"),
        2: lambda: handle_product_menu(res, number),
        3: lambda: res.message('As formas de pagamento são:\nDinheiro\nCartão de Crédito/Débito\nPIX'),
        4: lambda: handle_delivery_fee(res, number),
        5: lambda: handle_complaint(res, number),
        6: lambda: handle_exit(res, number)
    }
    return menu_options.get(option, lambda: res.message("Por favor, digite um número válido"))()


@log_error
def handle_product_menu(res, number):
    users.update_one({"number": number}, {"$set": {"status": "main-produto"}})
    res.message("Para conhecer nossos produtos, digite:\n\n"
                "1️⃣ *Produtos*\n2️⃣ *Combos e Kits*\n"
                "3️⃣ *Promoções*\n4️⃣ *Retornar*")


@log_error
def handle_delivery_fee(res, number):
    users.update_one({"number": number}, {"$set": {"status": "address"}})
    res.message("Digite seu CEP")


@log_error
def handle_complaint(res, number):
    users.update_one({"number": number}, {"$set": {"status": "main-reclama"}})
    res.message("Digite sua dúvida e/ou reclamação.")


@log_error
def handle_exit(res, number):
    users.update_one({"number": number}, {"$set": {"status": "main-sair"}})
    res.message("Você poderia responder a algumas perguntas?\n1️⃣ *Sim*\n2️⃣ *Apenas Sair*")


@log_error
def handle_address_status(res, number, text):
    try:
        address = get_address_from_cep(text, webservice=WebService.APICEP)
        if address is None:
            return res.message("CEP não encontrado ou inválido. Por favor, verifique o CEP e tente novamente.")

        # Criando uma mensagem com as informações disponíveis
        address_parts = []
        if address.get('street'):
            address_parts.append(address['street'])
        if address.get('district'):
            address_parts.append(address['district'])
        if address.get('city'):
            address_parts.append(address['city'])
        if address.get('uf'):
            address_parts.append(address['uf'])
        if address.get('cep'):
            address_parts.append(address['cep'])
        if address.get('complement'):
            address_parts.append(address['complement'])

        if address_parts:
            address_str = " - ".join(address_parts)
            res.message(f"Seu endereço: {address_str}")
        else:
            res.message("Não foi possível obter informações detalhadas para este CEP.")

        if address.get('complemento'):
            res.message(f"Complemento: {address['complemento']}")

        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
        res.message("Digite 1 para voltar ao menu principal:")
    except exceptions.InvalidCEP as eic:
        app.logger.error(f"CEP inválido: {eic}")
        res.message("CEP inválido! Por favor, verifique o CEP e tente novamente.")
    except (exceptions.ConnectionError, exceptions.Timeout, exceptions.HTTPError) as e:
        app.logger.error(f"Erro de conexão: {e}")
        res.message("Erro de conexão. Tente novamente mais tarde.")
    except Exception as e:
        app.logger.error(f"Erro inesperado: {e}")
        res.message("Ocorreu um erro. Tente novamente mais tarde.")


@app.route("/", methods=["GET", "POST"])
@log_error
def reply():
    text = request.form.get("Body")
    number = request.form.get("From", "").replace("whatsapp:", "")
    profile_name = request.form.get("ProfileName")

    res = MessagingResponse()
    user = users.find_one({"number": number})
    print(request.values)

    if not user:
        send_welcome_message(res, profile_name)
        users.insert_one({
            "number": number,
            "ProfileName": profile_name,
            "channel": "whatsapp",
            "status": "main",
            "messages": []
        })
    elif user["status"] == "main":
        try:
            option = int(text)
            handle_main_menu(res, number, option, profile_name)
        except ValueError:
            res.message("Por favor, digite um número válido!")
    elif user["status"] == "main-produto":
        handle_product_menu_selection(res, number, text)
    elif user["status"] == "main-reclama":
        handle_complaint_submission(res, number, text, profile_name)
    elif user["status"] == "main-sair":
        handle_exit_survey(res, number, text)
    elif user["status"] == "main-sair-nota":
        handle_survey_submission(res, number, text, profile_name)
    elif user["status"] == "address":
        handle_address_status(res, number, text)
    elif user['status'] == "ordered":
        handle_reorder(res, number, profile_name)

    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})

    return str(res)


@log_error
def handle_product_menu_selection(res, number, text):
    try:
        option = int(text)
        if option == 1:
            msg = res.message("Lista dos Produtos:\n*Coxinha*\tRS6,00\n*Esfiha*\tRS6,00\n*Pastel*\tRS10,00")
            msg.media('https://i.pinimg.com/564x/72/01/06/72010685a0f1c48c4eff6e46f49f5ad6.jpg')
        elif option == 2:
            msg = res.message("Lista dos Combos e Kits::\n*Coxinha*\tRS6,00\n*Esfiha*\tRS6,00\n*Pastel*\tRS10,00")
            msg.media('https://i.pinimg.com/564x/2b/65/58/2b65582f86c3ef419f7094de4482adeb.jpg')
        elif option == 3:
            msg = res.message(
                "Lista das Promoções:\n*Coxinha* x4\tRS10,00\n*Esfiha* 4x\tRS10,00\n*Pastel* + *Refigerante 1L*\tRS10,00")
            msg.media('https://i.pinimg.com/564x/25/db/8d/25db8d6bf80f7e62906b4bd336681e4b.jpg')
        elif option == 4:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message(
                "Você pode escolher uma das opções abaixo\n\n *Digite* o numero correspodente:\n\n1️⃣  Para saber nosso *endereço* e *horário*. \n2️⃣  Para conhecer nosso *menu*.\n3️⃣  Para saber nossa formas de *pagamento*.\n4️⃣  Para saber a taxa de *entrega*. \n5️⃣ Fazer Reclamação ou Ajuda. \n6️⃣ Finalizar")
        else:
            res.message("Por Favor digite um numero válido")
    except ValueError:
        res.message("Por Favor digite um numero válido")


@log_error
def handle_complaint_submission(res, number, text, profile_name):
    complaints.insert_one({
        "number": number,
        "complaint": text,
        "name": profile_name,
        "complaint_time": datetime.now()
    })
    res.message('Sua duvida/reclamação foi registrada.')
    users.update_one({"number": number}, {"$set": {"status": "main"}})
    res.message(
        "Você pode escolher uma das opções abaixo\n\n *Digite* o numero correspodente:\n\n1️⃣  Para saber nosso *endereço* e *horário*. \n2️⃣  Para conhecer nosso *menu*.\n3️⃣  Para saber nossa formas de *pagamento*.\n4️⃣  Para saber a taxa de *entrega*. \n5️⃣ Fazer Reclamação ou Ajuda. \n6️⃣ Finalizar")


@log_error
def handle_exit_survey(res, number, text):
    try:
        option = int(text)
        if option == 1:
            users.update_one({"number": number}, {"$set": {"status": "main-sair-nota"}})
            res.message("Numa escala de 0 a 10 qual sua nota nosso atendimento via chatbot?")
        elif option == 2:
            users.delete_one({"number": number})
            res.message(
                "Obrigado por ter nos contato!😀🎈\nDe acordo com a Lei Geral de Proteção de Dados Pessoais estaremos excluindo os seus dados.")
        else:
            res.message("Por Favor digite um numero válido:")
    except ValueError:
        res.message("Por Favor digite um numero válido:")


@log_error
def handle_survey_submission(res, number, text, profile_name):
    chatbot.insert_one({
        "number": number,
        "complaint": text,
        "name": profile_name,
        "complaint_time": datetime.now()
    })
    users.delete_one({"number": number})
    res.message('Sua nota foi registrada.')
    res.message(
        "Obrigado por ter nos contato!😀🎈\n De acordo com a Lei Geral de Proteção de Dados Pessoais estaremos excluindo os seus dados.")


@log_error
def handle_reorder(res, number, profile_name):
    res.message(
        f"Oi, obrigado por nos contatar novamente *{profile_name.capitalize()}*!😘\n Você pode escolher uma das opções abaixo\n\n *Digite* o numero correspodente:\n\n1️⃣  Para saber nosso *endereço* e *horário*. \n2️⃣  Para conhecer nosso menu de *salgados*.\n3️⃣  Para saber nossa formas de *pagamento*.\n4️⃣  Para saber a taxa de *entrega*. \n5️⃣ Fazer Reclamação ou Ajuda \n6️⃣ Finalizar")
    users.update_one({"number": number}, {"$set": {"status": "main"}})


if __name__ == '__main__':
    app.run(debug=False)  # Defina como False em produção
