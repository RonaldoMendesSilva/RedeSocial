from neo4j import GraphDatabase
from datetime import datetime

class RedeSocial:

    def __init__(self, uri, usuario, senha):
        self._driver = GraphDatabase.driver(uri, auth=(usuario, senha))

    def fechar_conexao(self):
        self._driver.close()

    def adicionar_pessoa(self, nome, idade, localizacao):
        with self._driver.session() as sessao:
            sessao.write_transaction(self._criar_pessoa, nome, idade, localizacao)

    def _criar_pessoa(self, tx, nome, idade, localizacao):
        id_pessoa = int(datetime.timestamp(datetime.now()))
        query = (
            "CREATE (p:Pessoa {id: $id, nome: $nome, idade: $idade, localizacao: $localizacao})"
        )
        tx.run(query, id=id_pessoa, nome=nome, idade=idade, localizacao=localizacao)

    def listar_pessoas(self):
        with self._driver.session() as sessao:
            return sessao.read_transaction(self._obter_pessoas)

    def _obter_pessoas(self, tx):
        query = (
            "MATCH (p:Pessoa) RETURN p.id as id, p.nome as nome, p.idade as idade, p.localizacao as localizacao"
        )
        return [
            {
                "id": record["id"],
                "nome": record["nome"],
                "idade": record["idade"],
                "localizacao": record["localizacao"],
            }
            for record in tx.run(query)
        ]

    def adicionar_amizade(self, id_pessoa1, id_pessoa2):
        with self._driver.session() as sessao:
            sessao.write_transaction(self._criar_amizade, id_pessoa1, id_pessoa2)

    def _criar_amizade(self, tx, id_pessoa1, id_pessoa2):
        id_amizade = int(datetime.timestamp(datetime.now()))
        query = (
            "MATCH (p1:Pessoa), (p2:Pessoa) "
            "WHERE p1.id = $id_pessoa1 AND p2.id = $id_pessoa2 "
            "CREATE (p1)-[:AMIGO_DE {id: $id_amizade}]->(p2)"
        )
        tx.run(query, id_pessoa1=id_pessoa1, id_pessoa2=id_pessoa2, id_amizade=id_amizade)

    def visualizar_amigos(self, id_pessoa):
        with self._driver.session() as sessao:
            return sessao.read_transaction(self._obter_amigos, id_pessoa)

    def _obter_amigos(self, tx, id_pessoa):
        query = (
            "MATCH (p1:Pessoa)-[:AMIGO_DE]-(p2:Pessoa) "
            "WHERE p1.id = $id_pessoa "
            "RETURN p2.id as id, p2.nome as nome, p2.idade as idade, p2.localizacao as localizacao"
        )
        return [registro for registro in tx.run(query, id_pessoa=id_pessoa)]

    def remover_pessoa(self, id_pessoa):
        with self._driver.session() as sessao:
            sessao.write_transaction(self._excluir_pessoa, id_pessoa)

    def _excluir_pessoa(self, tx, id_pessoa):
        query = "MATCH (p:Pessoa) WHERE p.id = $id_pessoa DETACH DELETE p"
        tx.run(query, id_pessoa=id_pessoa)

# Configurações do banco de dados Neo4j
uri = "bolt://localhost:7687"
usuario = "neo4j"
senha = "12345678"

# Criando uma instância da RedeSocial
rede_social = RedeSocial(uri, usuario, senha)

while True:
    print("============================")
    print("\n### Menu ###")
    print("1. Adicionar Pessoa")
    print("2. Listar Pessoas")
    print("3. Adicionar Amizade")
    print("4. Visualizar Amigos")
    print("5. Remover Pessoa")
    print("0. Sair")
    print("============================")

    escolha = input("\nEscolha uma opção: ")

    if escolha == "1":
        # Adicionar pessoa
        print("============================")
        nome = input("Informe o nome da pessoa: ")
        print("============================")
        idade = int(input("Informe a idade da pessoa: "))
        print("============================")
        localizacao = input("Informe a localização da pessoa: ")
        print("============================")
        rede_social.adicionar_pessoa(nome, idade, localizacao)
        print("Pessoa adicionada com sucesso!")

    elif escolha == "2":
        # Listar pessoas
        lista_de_pessoas = rede_social.listar_pessoas()
        print("\nPessoas:")
        for pessoa in lista_de_pessoas:
            print("===========================================================================================================")
            print(f"ID: {pessoa['id']}, Nome: {pessoa['nome']}, Idade: {pessoa['idade']}, Localizacao: {pessoa['localizacao']}")

    elif escolha == "3":
        # Adicionar amizade
        print("============================")
        id_pessoa1 = int(input("Informe o ID da primeira pessoa: "))
        id_pessoa2 = int(input("Informe o ID da segunda pessoa: "))
        print("============================")
        rede_social.adicionar_amizade(id_pessoa1, id_pessoa2)
        print("Amizade adicionada com sucesso!")
        print("============================")

    elif escolha == "4":
        # Visualizar amigos
        id_pessoa_visualizar = int(input("Informe o ID da pessoa para visualizar os amigos: "))
        amigos_da_pessoa = rede_social.visualizar_amigos(id_pessoa_visualizar)
        print(f"\nAmigos da pessoa {id_pessoa_visualizar}:")
        for amigo in amigos_da_pessoa:
            print("============================")
            print(f"ID: {amigo['id']}, Nome: {amigo['nome']}, Idade: {amigo['idade']}, Localizacao: {amigo['localizacao']}")

    elif escolha == "5":
        # Remover pessoa
        print("============================")
        id_pessoa_remover = int(input("Informe o ID da pessoa a ser removida: "))
        rede_social.remover_pessoa(id_pessoa_remover)
        print("============================")
        print("Pessoa removida com sucesso!")

    elif escolha == "0":
        # Sair do programa
        rede_social.fechar_conexao()
        break

    else:
        print("================================")
        print("Opção inválida. Tente novamente.")
        print("================================")
