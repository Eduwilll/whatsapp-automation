# Chatbot para Loja de Salgados - LLAS Coxitas S/A

Este projeto tem como objetivo desenvolver um **chatbot** para auxiliar no atendimento aos clientes de uma loja de salgados, automatizando a comunicação via WhatsApp e Telegram.

## Descrição Geral do Projeto

O chatbot otimiza o atendimento ao cliente, proporcionando uma experiência contínua e eficiente. Ele responde dúvidas frequentes, fornece informações sobre o menu, formas de pagamento, taxas de entrega, entre outros serviços, tudo de maneira automatizada.

De acordo com o levantamento realizado:

- **100%** dos clientes gostariam de usar uma aplicação para esclarecer dúvidas 24 horas por dia.
- A maioria dos usuários prefere enviar mensagens via WhatsApp e considera o atendimento via chatbot mais ágil.
  
### Principais Funcionalidades

1. **Informações gerais**: fornecimento de endereço, horário de funcionamento e meios de contato.
2. **Exibição do menu**: lista de produtos, combos e promoções.
3. **Formas de pagamento**: disponibilização das opções de pagamento aceitas.
4. **Taxa de entrega**: cálculo com base no CEP informado pelo cliente.
5. **Reclamações e ajuda**: interface para envio de dúvidas ou reclamações.
6. **Satisfação do cliente**: pesquisa rápida de satisfação após o atendimento.

### Tecnologias Utilizadas

- **Flask**: framework web para a criação das APIs do chatbot.
- **MongoDB**: banco de dados NoSQL utilizado para armazenar informações dos usuários e pedidos.
- **Twilio API**: integração para envio de mensagens via WhatsApp.
- **PyCEP Correios**: integração para consulta de CEPs e cálculo de taxas de entrega.
- **Dotenv**: gerenciamento de variáveis de ambiente.

## Arquitetura do Chatbot

O chatbot é composto por três elementos principais:

1. **Canal**: o local onde a interação ocorre, como WhatsApp.
2. **Conteúdo**: os textos, mídias e informações que compõem as respostas.
3. **Software**: o código que define as regras de interação.

## Requisitos do Projeto

### Requisitos Funcionais
- **RF01**: O chatbot deve ser capaz de fornecer o menu de salgados da loja.
- **RF02**: O chatbot deve informar o horário de funcionamento e o endereço.
- **RF03**: O chatbot deve calcular a taxa de entrega com base no CEP fornecido.
- **RF04**: O chatbot deve permitir que o cliente envie reclamações.
- **RF05**: O chatbot deve realizar uma pesquisa de satisfação ao final do atendimento.

### Requisitos Não Funcionais
- **RNF01**: O sistema deve ser capaz de atender vários clientes simultaneamente.
- **RNF02**: O sistema deve estar disponível 24 horas por dia, 7 dias por semana.
- **RNF03**: O tempo de resposta do chatbot não deve exceder 2 segundos.

## Metodologia de Levantamento de Requisitos

A metodologia escolhida foi a aplicação de questionários para o proprietário da loja e seus clientes. As respostas formaram a base para a definição do minimundo e os requisitos do sistema.

### Minimundo

A **LLAS Coxitas S/A** é uma empresa familiar que, após a pandemia, resolveu diversificar seus canais de atendimento, criando um site e buscando um chatbot que possa interagir com os clientes via WhatsApp e Telegram. O chatbot será utilizado para tirar dúvidas sobre os produtos, calcular taxas de entrega, receber reclamações e realizar pesquisas de satisfação.

## Executando o Projeto

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/chatbot-loja-salgados.git
2. Acesse o diretório do projeto:
   ```bash
   cd chatbot-loja-salgados
3. Crie e ative um ambiente virtual:
- **Windows**:
  ```bash
  python -m venv venv
  venv\Scripts\activate
- **Linux ou MacOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
4. Instale as dependências listadas no arquivo requirements.txt:
    ```bash
   pip install -r requirements.txt
5. Crie um arquivo .env para configurar as variáveis de ambiente necessárias, como as credenciais do MongoDB e Twilio:
   ```bash
   MONGO_URI=<sua_mongo_uri>
   TWILIO_ACCOUNT_SID=<seu_twilio_account_sid>
   TWILIO_AUTH_TOKEN=<seu_twilio_auth_token>
6. Execute a aplicação:
    ````bash
   flask run
## Preview do Projeto

### Interface do Chatbot
![Interface do Chatbot](https://i.imgur.com/XLv7cbL.png)

### Fluxo de Conversação
![Fluxo de Conversação](https://i.imgur.com/U94az7N.png)
![Fluxo de Conversação](https://i.imgur.com/NEiI9rm.png)
![Fluxo de Conversação](https://i.imgur.com/WuIFNzA.png)
![Fluxo de Conversação](https://i.imgur.com/UX8U9BM.jpeg)
![Fluxo de Conversação](https://i.imgur.com/s7bjNHG.jpeg)


## Futuras Melhorias
- Implementação de uma integração com sistemas de pagamento para permitir que os clientes façam compras diretamente pelo chatbot.
- Adição de um sistema de recomendações personalizadas com base no histórico de pedidos dos clientes.
- Melhoria do processamento de linguagem natural (NLP) para respostas mais dinâmicas e interativas, utilizando modelos como o GPT.
- Integração com serviços de entrega para fornecer acompanhamento em tempo real dos pedidos.

## Licença
Este projeto está licenciado sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.