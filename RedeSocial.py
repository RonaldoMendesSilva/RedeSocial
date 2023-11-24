from neo4j import GraphDatabase
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class RedeSocial:
    def __init__(self, uri, usuario, senha):
        self._driver = GraphDatabase.driver(uri, auth=(usuario, senha))

    def fechar_conexao(self):
        self._driver.close()

    def criar_pessoa(self, nome, idade, localizacao):
        with self._driver.session() as sessao:
            sessao.write_transaction(self._criar_pessoa, nome, idade, localizacao)

    def _criar_pessoa(self, tx, nome, idade, localizacao):
        query = (
            "CREATE (p:Pessoa {nome: $nome, idade: $idade, localizacao: $localizacao})"
        )
        tx.run(query, nome=nome, idade=idade, localizacao=localizacao)

    def criar_amizade(self, nome_pessoa1, nome_pessoa2):
        with self._driver.session() as sessao:
            sessao.write_transaction(self._criar_amizade, nome_pessoa1, nome_pessoa2)

    def _criar_amizade(self, tx, nome_pessoa1, nome_pessoa2):
        query = (
            "MATCH (p1:Pessoa {nome: $nome_pessoa1}), (p2:Pessoa {nome: $nome_pessoa2})"
            "CREATE (p1)-[:AMIGO_DE]->(p2)"
        )
        tx.run(query, nome_pessoa1=nome_pessoa1, nome_pessoa2=nome_pessoa2)

    def obter_pessoas(self):
        with self._driver.session() as sessao:
            return sessao.read_transaction(self._obter_pessoas)

    def _obter_pessoas(self, tx):
        query = (
            "MATCH (p:Pessoa) RETURN ID(p) as id, p.nome as nome, p.idade as idade, p.localizacao as localizacao"
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

    def obter_amigos(self, nome_pessoa):
        with self._driver.session() as sessao:
            return sessao.read_transaction(self._obter_amigos, nome_pessoa)

    def _obter_amigos(self, tx, nome_pessoa):
        query = (
            "MATCH (p1:Pessoa {nome: $nome_pessoa})-[:AMIGO_DE]-(amigo)"
            "RETURN amigo.nome as nome"
        )
        return [record["nome"] for record in tx.run(query, nome_pessoa=nome_pessoa)]

    def remover_pessoa(self, id_pessoa):
        with self._driver.session() as sessao:
            sessao.write_transaction(self._remover_pessoa, id_pessoa)

    def _remover_pessoa(self, tx, id_pessoa):
        query = (
            "MATCH (p:Pessoa) WHERE ID(p) = $id_pessoa"
            "DETACH DELETE p"
        )
        tx.run(query, id_pessoa=id_pessoa)

    def pesquisar_pessoa(self, nome):
        with self._driver.session() as sessao:
            return sessao.read_transaction(self._pesquisar_pessoa, nome)

    def _pesquisar_pessoa(self, tx, nome):
        query = (
            "MATCH (p:Pessoa {nome: $nome}) RETURN ID(p) as id, p.nome as nome, p.idade as idade, p.localizacao as localizacao"
        )
        return [
            {
                "id": record["id"],
                "nome": record["nome"],
                "idade": record["idade"],
                "localizacao": record["localizacao"],
            }
            for record in tx.run(query, nome=nome)
        ]

    def obter_nomes_pessoas(self):
        with self._driver.session() as sessao:
            query = "MATCH (p:Pessoa) RETURN ID(p) as id, p.nome as nome, p.idade as idade, p.localizacao as localizacao"
            return [(record["id"], record["nome"], record["idade"], record["localizacao"]) for record in sessao.run(query)]

class RedeSocialGUI:
    def __init__(self, root, rede_social):
        self.root = root
        self.root.title("Rede Social")
        self.rede_social = rede_social

        # Labels
        self.label_nome = tk.Label(root, text="Nome:")
        self.label_idade = tk.Label(root, text="Idade:")
        self.label_localizacao = tk.Label(root, text="Localização:")

        # Entry Widgets
        self.entry_nome = tk.Entry(root)
        self.entry_idade = tk.Entry(root)
        self.entry_localizacao = tk.Entry(root)

        # Buttons
        self.button_adicionar_pessoa = tk.Button(root, text="1. Adicionar Pessoa", command=self.adicionar_pessoa)
        self.button_listar_pessoas = tk.Button(root, text="2. Listar Pessoas", command=self.listar_pessoas)
        self.button_adicionar_amizade = tk.Button(root, text="3. Adicionar Amizade", command=self.adicionar_amizade)
        self.button_visualizar_amigos = tk.Button(root, text="4. Visualizar Amigos", command=self.visualizar_amigos)
        self.button_remover_pessoa = tk.Button(root, text="5. Remover Pessoa", command=self.remover_pessoa)
        self.button_pesquisar_pessoa = tk.Button(root, text="6. Pesquisar Pessoa", command=self.pesquisar_pessoa)
        self.button_sair = tk.Button(root, text="0. Sair", command=root.destroy)

        # Text Widget para exibir a lista de pessoas, amigos e resultados da pesquisa
        self.text_lista_pessoas = tk.Text(root, height=10, width=50)
        self.text_lista_amigos = tk.Text(root, height=10, width=30)
        self.text_resultado_pesquisa = tk.Text(root, height=2, width=50)

        # Combobox para escolher pessoa a ser removida
        self.label_escolher_pessoa = tk.Label(root, text="Escolher Pessoa:")
        self.combobox_pessoas = ttk.Combobox(root, state="readonly", width=50)  # Ajuste o valor de width conforme necessário
        self.combobox_pessoas.bind("<<ComboboxSelected>>", self.exibir_info_pessoa)
        self.atualizar_combobox_pessoas()

        # Grid
        self.label_nome.grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        self.entry_nome.grid(row=0, column=1, pady=5, padx=10)
        self.label_idade.grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.entry_idade.grid(row=1, column=1, pady=5, padx=10)
        self.label_localizacao.grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        self.entry_localizacao.grid(row=2, column=1, pady=5, padx=10)
        self.button_adicionar_pessoa.grid(row=3, column=0, columnspan=2, pady=10)
        self.button_listar_pessoas.grid(row=4, column=0, columnspan=2, pady=10)
        self.button_adicionar_amizade.grid(row=5, column=0, columnspan=2, pady=10)
        self.button_visualizar_amigos.grid(row=6, column=0, columnspan=2, pady=10)
        self.button_remover_pessoa.grid(row=7, column=0, columnspan=2, pady=10)
        self.button_pesquisar_pessoa.grid(row=8, column=0, columnspan=2, pady=10)
        self.button_sair.grid(row=9, column=0, columnspan=2, pady=10)
        self.label_escolher_pessoa.grid(row=10, column=0, sticky=tk.W, pady=5, padx=10)
        self.combobox_pessoas.grid(row=10, column=1, pady=10, padx=30)
        self.text_lista_pessoas.grid(row=11, column=0, columnspan=2, pady=10)
        self.text_lista_amigos.grid(row=12, column=0, columnspan=2, pady=20)
        self.text_resultado_pesquisa.grid(row=13, column=0, columnspan=2, pady=10)

        # Defina a orientação da janela para o centro da tela
        largura_janela = root.winfo_reqwidth()
        altura_janela = root.winfo_reqheight()
        largura_tela = root.winfo_screenwidth()
        altura_tela = root.winfo_screenheight()
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        root.geometry(f"+{pos_x}+{pos_y}")

    def atualizar_combobox_pessoas(self):
        nomes_pessoas = self.rede_social.obter_nomes_pessoas()
        self.combobox_pessoas["values"] = nomes_pessoas

    def exibir_info_pessoa(self, event):
        # Função chamada quando o usuário seleciona um item na Combobox
        nome_selecionado = self.combobox_pessoas.get()
        pessoa_selecionada = next((pessoa for pessoa in dados_pessoas if pessoa[1] == nome_selecionado), None)

        if pessoa_selecionada:
            # Pode usar pessoa_selecionada[0] para obter o id e pessoa_selecionada[1] para obter o nome
            print(f"ID: {pessoa_selecionada[0]}, Nome: {pessoa_selecionada[1]}")
        else:
            print("Nenhuma pessoa selecionada.")

    def adicionar_pessoa(self):
        nome = self.entry_nome.get()
        idade = self.entry_idade.get()
        localizacao = self.entry_localizacao.get()

        if not nome or not idade or not localizacao:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return

        try:
            idade = int(idade)
            if idade < 0:
                raise ValueError("A idade deve ser um número inteiro não negativo.")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        self.rede_social.criar_pessoa(nome, idade, localizacao)
        self.atualizar_combobox_pessoas()
        messagebox.showinfo("Sucesso", "Pessoa adicionada com sucesso!")
        self.entry_nome.delete(0, tk.END)
        self.entry_idade.delete(0, tk.END)
        self.entry_localizacao.delete(0, tk.END)

    def listar_pessoas(self):
        lista_de_pessoas = self.rede_social.obter_pessoas()
        if lista_de_pessoas:
            pessoas_str = "\n".join([f"{pessoa['id']}: {pessoa['nome']}, {pessoa['idade']} anos, {pessoa['localizacao']}" for pessoa in lista_de_pessoas])
            self.text_lista_pessoas.delete(1.0, tk.END)
            self.text_lista_pessoas.insert(tk.END, pessoas_str)
        else:
            messagebox.showinfo("Pessoas", "Nenhuma pessoa cadastrada.")

    def adicionar_amizade(self):
        nome_pessoa1 = self.entry_nome.get()
        nome_pessoa2 = simpledialog.askstring("Adicionar Amizade", "Digite o nome da segunda pessoa:")
        if nome_pessoa2:
            self.rede_social.criar_amizade(nome_pessoa1, nome_pessoa2)
            messagebox.showinfo("Sucesso", f"Amizade entre {nome_pessoa1} e {nome_pessoa2} criada com sucesso!")

    def visualizar_amigos(self):
        nome_pessoa = self.entry_nome.get()
        lista_de_amigos = self.rede_social.obter_amigos(nome_pessoa)
        if lista_de_amigos:
            amigos_str = "\n".join(lista_de_amigos)
            self.text_lista_amigos.delete(1.0, tk.END)
            self.text_lista_amigos.insert(tk.END, f"Amigos de {nome_pessoa}:\n{amigos_str}")
        else:
            messagebox.showinfo("Amigos", f"{nome_pessoa} não tem amigos cadastrados.")

    def remover_pessoa(self):
        pessoa_selecionada = self.combobox_pessoas.get()
        if not pessoa_selecionada:
            messagebox.showerror("Erro", "Selecione uma pessoa para remover.")
            return

        id_pessoa = int(pessoa_selecionada.split(":")[0])
        resposta = messagebox.askquestion("Confirmar Remoção", f"Tem certeza que deseja remover {pessoa_selecionada}?")
        if resposta == "yes":
            self.rede_social.remover_pessoa(id_pessoa)
            self.atualizar_combobox_pessoas()
            messagebox.showinfo("Sucesso", f"{pessoa_selecionada} removido com sucesso!")
            self.entry_nome.delete(0, tk.END)
            self.entry_idade.delete(0, tk.END)
            self.entry_localizacao.delete(0, tk.END)

    def pesquisar_pessoa(self):
        nome = self.entry_nome.get()
        if not nome:
            messagebox.showerror("Erro", "O campo 'Nome' deve ser preenchido para pesquisar uma pessoa.")
            return

        resultado_pesquisa = self.rede_social.pesquisar_pessoa(nome)
        if resultado_pesquisa:
            pessoa_str = f"{resultado_pesquisa[0]['id']}: {resultado_pesquisa[0]['nome']}, {resultado_pesquisa[0]['idade']} anos, {resultado_pesquisa[0]['localizacao']}"
            self.text_resultado_pesquisa.delete(1.0, tk.END)
            self.text_resultado_pesquisa.insert(tk.END, pessoa_str)
        else:
            messagebox.showinfo("Pesquisa", f"Nenhuma pessoa encontrada com o nome {nome}.")

# Configurações do banco de dados Neo4j
uri = "bolt://localhost:7687"
usuario = "neo4j"
senha = "12345678"

# Criando uma instância da RedeSocial
rede_social = RedeSocial(uri, usuario, senha)

# Criando uma instância da interface gráfica
root = tk.Tk()
app = RedeSocialGUI(root, rede_social)

# Iniciando o loop da interface
root.mainloop()

# Certifique-se de fechar a conexão com o banco de dados ao fechar a interface
rede_social.fechar_conexao()
