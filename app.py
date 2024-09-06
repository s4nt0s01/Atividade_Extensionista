import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('sistema_mercado.db')
c = conn.cursor()

# Criação das tabelas no banco de dados
def criar_tabelas():
    c.execute('''CREATE TABLE IF NOT EXISTS Produtos (
                id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS Vendas (
                id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
                id_produto INTEGER,
                quantidade INTEGER NOT NULL,
                valor_total REAL NOT NULL,
                data_venda TEXT NOT NULL,
                FOREIGN KEY (id_produto) REFERENCES Produtos(id_produto))''')

criar_tabelas()

# Função para adicionar produto
def adicionar_produto():
    nome = entry_nome.get()
    quantidade = entry_quantidade.get()
    preco = entry_preco.get()

    if nome and quantidade and preco:
        c.execute("INSERT INTO Produtos (nome, quantidade, preco) VALUES (?, ?, ?)",
                  (nome, quantidade, preco))
        conn.commit()
        carregar_produtos()
        messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
    else:
        messagebox.showwarning("Erro", "Preencha todos os campos")

# Função para editar produto
def editar_produto():
    try:
        selecionado = tree_estoque.selection()[0]
        valores = tree_estoque.item(selecionado, 'values')
        id_produto = valores[0]
        novo_nome = entry_nome.get()
        nova_quantidade = entry_quantidade.get()
        novo_preco = entry_preco.get()

        c.execute("UPDATE Produtos SET nome=?, quantidade=?, preco=? WHERE id_produto=?",
                  (novo_nome, nova_quantidade, novo_preco, id_produto))
        conn.commit()
        carregar_produtos()
        messagebox.showinfo("Sucesso", "Produto editado com sucesso!")
    except:
        messagebox.showwarning("Erro", "Selecione um produto para editar")

# Função para remover produto
def remover_produto():
    try:
        selecionado = tree_estoque.selection()[0]
        valores = tree_estoque.item(selecionado, 'values')
        id_produto = valores[0]
        c.execute("DELETE FROM Produtos WHERE id_produto=?", (id_produto,))
        conn.commit()
        carregar_produtos()
        messagebox.showinfo("Sucesso", "Produto removido com sucesso!")
    except:
        messagebox.showwarning("Erro", "Selecione um produto para remover")

# Função para realizar venda
def realizar_venda():
    try:
        selecionado = tree_estoque.selection()[0]
        valores = tree_estoque.item(selecionado, 'values')
        id_produto = valores[0]
        quantidade = int(entry_quantidade_venda.get())
        data_venda = entry_data_venda.get()

        if quantidade <= int(valores[2]):  # Verifica se há estoque suficiente
            preco_venda = float(valores[3])
            valor_total = quantidade * preco_venda

            # Atualizar o estoque
            nova_quantidade = int(valores[2]) - quantidade
            c.execute("UPDATE Produtos SET quantidade=? WHERE id_produto=?",
                      (nova_quantidade, id_produto))
            
            # Registrar a venda
            c.execute("INSERT INTO Vendas (id_produto, quantidade, valor_total, data_venda) VALUES (?, ?, ?, ?)",
                      (id_produto, quantidade, valor_total, data_venda))
            conn.commit()
            carregar_produtos()
            carregar_vendas()
            messagebox.showinfo("Sucesso", f"Venda realizada! Valor total: R$ {valor_total:.2f}")
        else:
            messagebox.showwarning("Erro", "Quantidade em estoque insuficiente!")
    except:
        messagebox.showwarning("Erro", "Selecione um produto e insira a quantidade")

# Função para carregar os produtos na tabela de estoque
def carregar_produtos():
    for row in tree_estoque.get_children():
        tree_estoque.delete(row)
    c.execute("SELECT * FROM Produtos")
    rows = c.fetchall()
    for row in rows:
        tree_estoque.insert("", END, values=row)

# Função para carregar as vendas na tabela de vendidos
def carregar_vendas():
    for row in tree_vendas.get_children():
        tree_vendas.delete(row)
    c.execute("SELECT v.id_venda, p.nome, v.quantidade, v.valor_total, v.data_venda FROM Vendas v JOIN Produtos p ON v.id_produto = p.id_produto")
    rows = c.fetchall()
    for row in rows:
        tree_vendas.insert("", END, values=row)

# Interface Gráfica
root = Tk()
root.title("Sistema de Registro")
root.geometry("1280x720")

# Frame para cadastro e edição de produtos
frame_cadastro = LabelFrame(root, text="Gerenciar Produto", padx=10, pady=10)
frame_cadastro.pack(fill="x", padx=20, pady=10)

Label(frame_cadastro, text="Nome").grid(row=0, column=0)
entry_nome = Entry(frame_cadastro)
entry_nome.grid(row=0, column=1)

Label(frame_cadastro, text="Quantidade").grid(row=1, column=0)
entry_quantidade = Entry(frame_cadastro)
entry_quantidade.grid(row=1, column=1)

Label(frame_cadastro, text="Preço (R$)").grid(row=2, column=0)
entry_preco = Entry(frame_cadastro)
entry_preco.grid(row=2, column=1)

Button(frame_cadastro, text="Adicionar Produto", command=adicionar_produto).grid(row=3, column=0, pady=10)
Button(frame_cadastro, text="Editar Produto", command=editar_produto).grid(row=3, column=1, pady=10)
Button(frame_cadastro, text="Remover Produto", command=remover_produto).grid(row=3, column=2, pady=10)

# Frame para exibição do estoque atual
frame_estoque = LabelFrame(root, text="Estoque Atual", padx=10, pady=10)
frame_estoque.pack(fill="both", padx=20, pady=10)

# Tabela de produtos em estoque
tree_estoque = ttk.Treeview(frame_estoque, columns=("ID", "Nome", "Quantidade", "Preço"), show="headings")
tree_estoque.heading("ID", text="ID")
tree_estoque.heading("Nome", text="Nome")
tree_estoque.heading("Quantidade", text="Quantidade")
tree_estoque.heading("Preço", text="Preço (R$)")
tree_estoque.pack(fill="both", expand=True)

# Frame para vendas
frame_vendas = LabelFrame(root, text="Realizar Venda", padx=10, pady=10)
frame_vendas.pack(fill="x", padx=20, pady=10)

Label(frame_vendas, text="Quantidade a Vender").grid(row=0, column=0)
entry_quantidade_venda = Entry(frame_vendas)
entry_quantidade_venda.grid(row=0, column=1)

Label(frame_vendas, text="Data da Venda (DD/MM/AAAA)").grid(row=1, column=0)
entry_data_venda = Entry(frame_vendas)
entry_data_venda.grid(row=1, column=1)

Button(frame_vendas, text="Vender", command=realizar_venda).grid(row=2, column=0, columnspan=2, pady=10)

# Frame para exibição das vendas realizadas
frame_vendidos = LabelFrame(root, text="Produtos Vendidos", padx=10, pady=10)
frame_vendidos.pack(fill="both", padx=20, pady=10)

# Tabela de produtos vendidos
tree_vendas = ttk.Treeview(frame_vendidos, columns=("ID", "Nome", "Quantidade", "Valor Total", "Data Venda"), show="headings")
tree_vendas.heading("ID", text="ID Venda")
tree_vendas.heading("Nome", text="Nome do Produto")
tree_vendas.heading("Quantidade", text="Quantidade Vendida")
tree_vendas.heading("Valor Total", text="Valor Total (R$)")
tree_vendas.heading("Data Venda", text="Data da Venda")
tree_vendas.pack(fill="both", expand=True)

carregar_produtos()
carregar_vendas()

root.mainloop()

conn.close()
