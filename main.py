import json
import os
from datetime import datetime
import flet as ft

ARQUIVO_DADOS = "lista_compras.json"


def main(page: ft.Page):
    page.title = "Lista de Compras"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 15
    page.max_width = 500

    itens_lista = []
    historico_lista = []

    # --- Salvar e Carregar Dados (JSON) ---
    def salvar_tudo():
        dados = {
            "atual": [
                {"nome": item["nome"], "concluido": item["checkbox"].value}
                for item in itens_lista
            ],
            "historico": historico_lista,
        }
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    def carregar_tudo():
        nonlocal historico_lista
        if not os.path.exists(ARQUIVO_DADOS):
            return

        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                dados = json.load(f)

                if isinstance(dados, dict):
                    itens_salvos = dados.get("atual", [])
                    historico_lista = dados.get("historico", [])
                else:
                    itens_salvos = dados

                for item in itens_salvos:
                    adicionar_item_interface(item["nome"], item["concluido"])

                atualizar_historico_ui()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")

    # --- Ações da Lista ---
    def alternar_status(e, label_texto):
        if e.control.value:
            label_texto.style = ft.TextStyle(
                decoration=ft.TextDecoration.LINE_THROUGH, color=ft.Colors.GREY
            )
        else:
            label_texto.style = ft.TextStyle(
                decoration=ft.TextDecoration.NONE, color=ft.Colors.BLACK
            )
        page.update()
        salvar_tudo()

    def remover_item(linha_container, item_dict):
        lista_view.controls.remove(linha_container)
        itens_lista.remove(item_dict)
        page.update()
        salvar_tudo()

    def adicionar_item_interface(nome, concluido=False):
        lbl = ft.Text(
            value=nome,
            size=16,
            expand=True,
            style=ft.TextStyle(
                decoration=(
                    ft.TextDecoration.LINE_THROUGH
                    if concluido
                    else ft.TextDecoration.NONE
                ),
                color=ft.Colors.GREY if concluido else ft.Colors.BLACK,
            ),
        )

        chk = ft.Checkbox(
            value=concluido,
            on_change=lambda e: alternar_status(e, lbl),
            active_color=ft.Colors.GREEN,
        )

        item_dict = {"nome": nome, "checkbox": chk}

        btn_remover = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINED,
            icon_color=ft.Colors.RED_400,
            on_click=lambda e: remover_item(linha_item, item_dict),
        )

        linha_item = ft.Container(
            content=ft.Row(
                controls=[chk, lbl, btn_remover],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=5,
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
        )

        itens_lista.append(item_dict)
        lista_view.controls.append(linha_item)
        page.update()

    def acao_adicionar(e):
        texto = entrada_texto.value.strip()
        if texto:
            adicionar_item_interface(texto)
            entrada_texto.value = ""
            page.update()
            salvar_tudo()

    # --- Finalizar e Histórico ---
    def finalizar_e_salvar_historico(e):
        if not itens_lista:
            page.snack_bar = ft.SnackBar(content=ft.Text("A lista está vazia!"))
            page.snack_bar.open = True
            page.update()
            return

        agora = datetime.now().strftime("%d/%m/%Y às %H:%M")
        itens_compra = [
            {"nome": item["nome"], "concluido": item["checkbox"].value}
            for item in itens_lista
        ]

        historico_lista.insert(0, {"data": agora, "itens": itens_compra})

        itens_lista.clear()
        lista_view.controls.clear()

        salvar_tudo()
        atualizar_historico_ui()

        # Alterna para a visualização do histórico
        mostrar_historico(None)

        page.snack_bar = ft.SnackBar(
            content=ft.Text("Compra finalizada e salva no histórico!")
        )
        page.snack_bar.open = True
        page.update()

    def atualizar_historico_ui():
        historico_view.controls.clear()

        if not historico_lista:
            historico_view.controls.append(
                ft.Text(
                    "Nenhum histórico salvo ainda.",
                    italic=True,
                    color=ft.Colors.GREY,
                )
            )
            page.update()
            return

        for compra in historico_lista:
            itens_text = []
            for item in compra["itens"]:
                status = "✅" if item["concluido"] else "❌"
                itens_text.append(f"{status} {item['nome']}")

            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"📅 Compra de {compra['data']}",
                                weight=ft.FontWeight.BOLD,
                                size=15,
                            ),
                            ft.Divider(),
                            ft.Text("\n".join(itens_text), size=14),
                        ]
                    ),
                    padding=15,
                )
            )
            historico_view.controls.append(card)

        page.update()

    # --- Elementos da Interface ---
    entrada_texto = ft.TextField(
        hint_text="O que precisa comprar?",
        expand=True,
        on_submit=acao_adicionar,
    )

    btn_add = ft.IconButton(
        icon=ft.Icons.ADD_CIRCLE,
        icon_color=ft.Colors.GREEN,
        icon_size=36,
        on_click=acao_adicionar,
    )

    lista_view = ft.ListView(expand=True, spacing=8)
    historico_view = ft.ListView(expand=True, spacing=12)

    conteudo_lista = ft.Column(
        controls=[
            ft.Row(controls=[entrada_texto, btn_add]),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            lista_view,
            ft.Button(
                content=ft.Text("Finalizar / Nova Compra"),
                icon=ft.Icons.CHECK_CIRCLE,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(padding=15),
                on_click=finalizar_e_salvar_historico,
            ),
        ],
        expand=True,
    )

    area_conteudo = ft.Container(content=conteudo_lista, expand=True)

    def mostrar_lista(e):
        area_conteudo.content = conteudo_lista
        btn_aba_lista.style = ft.ButtonStyle(color=ft.Colors.GREEN_600)
        btn_aba_historico.style = ft.ButtonStyle(color=ft.Colors.GREY)
        page.update()

    def mostrar_historico(e):
        area_conteudo.content = historico_view
        btn_aba_lista.style = ft.ButtonStyle(color=ft.Colors.GREY)
        btn_aba_historico.style = ft.ButtonStyle(color=ft.Colors.GREEN_600)
        page.update()

    btn_aba_lista = ft.TextButton(
        "🛒 Lista Atual",
        on_click=mostrar_lista,
        style=ft.ButtonStyle(color=ft.Colors.GREEN_600),
    )
    btn_aba_historico = ft.TextButton(
        "📜 Histórico",
        on_click=mostrar_historico,
        style=ft.ButtonStyle(color=ft.Colors.GREY),
    )

    barranavegacao = ft.Row(
        controls=[btn_aba_lista, btn_aba_historico],
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )

    page.add(
        ft.Text(
            "🛒 Minha Lista de Compras", size=22, weight=ft.FontWeight.BOLD
        ),
        barranavegacao,
        ft.Divider(),
        area_conteudo,
    )

    carregar_tudo()


if __name__ == "__main__":
    ft.run(main)
