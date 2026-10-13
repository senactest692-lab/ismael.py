
import ast
import operator as op
import flet as ft


ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.Mod: op.mod,
}


class SafeEvaluator:
    @staticmethod
    def eval_expr(expression: str) -> float:
        if len(expression) > 100:
            raise ValueError("Expressao muito longa")

        node = ast.parse(expression, mode="eval").body
        return SafeEvaluator._eval_node(node)

    @staticmethod
    def _eval_node(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp):
            operator_type = type(node.op)

            if operator_type not in ALLOWED_OPERATORS:
                raise ValueError("Operador nao permitido")

            left = SafeEvaluator._eval_node(node.left)
            right = SafeEvaluator._eval_node(node.right)

            if operator_type is ast.Pow and abs(right) > 100:
                raise ValueError("Expoente muito grande")

            result = ALLOWED_OPERATORS[operator_type](left, right)

            if abs(result) > 1e100:
                raise ValueError("Resultado muito grande")

            return result

        if isinstance(node, ast.UnaryOp):
            operator_type = type(node.op)

            if operator_type not in ALLOWED_OPERATORS:
                raise ValueError("Operador nao permitido")

            return ALLOWED_OPERATORS[operator_type](
                SafeEvaluator._eval_node(node.operand)
            )

        raise ValueError("Expressao invalida")


def main(page: ft.Page) -> None:
    page.title = "Calculadora"
    page.window.width = 380
    page.window.height = 620
    page.padding = 16
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    expression = ""

    display = ft.TextField(
        value="0",
        text_align=ft.TextAlign.RIGHT,
        read_only=True,
        text_size=34,
        border_radius=12,
        expand=True,
    )

    status = ft.Text(
        value="",
        color=ft.Colors.RED_700,
        size=12,
    )

    history = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        height=120,
        spacing=4,
    )

    def refresh() -> None:
        display.value = expression if expression else "0"
        page.update()

    def add_history(expr: str, result: str) -> None:
        history.controls.insert(
            0,
            ft.Text(f"{expr} = {result}", size=12),
        )

        if len(history.controls) > 8:
            history.controls.pop()

    def to_percent() -> None:
        nonlocal expression

        if expression:
            expression += "/100"

    def on_press(value: str):
        def handler(e: ft.ControlEvent) -> None:
            nonlocal expression

            status.value = ""

            if value == "C":
                expression = ""

            elif value == "⌫":
                expression = expression[:-1]

            elif value == "%":
                to_percent()

            elif value == "=":
                if not expression.strip():
                    return

                try:
                    normalized = (
                        expression
                        .replace("×", "*")
                        .replace("÷", "/")
                        .replace("^", "**")
                    )

                    result = SafeEvaluator.eval_expr(normalized)
                    result_text = f"{result:g}"

                    add_history(expression, result_text)
                    expression = result_text

                except ZeroDivisionError:
                    status.value = "Erro: divisao por zero."

                except (ValueError, SyntaxError, OverflowError):
                    status.value = "Expressao invalida."

            else:
                if value == ".":
                    normalized = (
                        expression
                        .replace("×", "*")
                        .replace("÷", "/")
                        .replace("^", "**")
                    )

                    # Identifica o número atual após o último operador.
                    last_number = ""
                    for char in reversed(normalized):
                        if char in "+-*/%":
                            if char == "-" and (
                                not last_number
                                or last_number[-1] in "eE"
                            ):
                                last_number += char
                                continue
                            break
                        last_number += char

                    if "." in last_number:
                        status.value = (
                            "Este numero ja possui ponto decimal."
                        )
                        refresh()
                        return

                expression += value

            refresh()

        return handler

    def key(
        label: str,
        bgcolor=ft.Colors.BLUE_GREY_100,
        color=ft.Colors.BLACK,
    ):
        return ft.Button(
            content=label,
            on_click=on_press(label),
            bgcolor=bgcolor,
            color=color,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            height=54,
            width=78,
        )

    page.add(
        ft.Text(
            "Calculadora",
            size=24,
            weight=ft.FontWeight.BOLD,
        ),
        display,
        status,
        ft.Row(
            [
                key("C", ft.Colors.RED_400, ft.Colors.WHITE),
                key("⌫", ft.Colors.ORANGE_300),
                key("%", ft.Colors.AMBER_100),
                key("÷", ft.Colors.AMBER_100),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                key("7"),
                key("8"),
                key("9"),
                key("×", ft.Colors.AMBER_100),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                key("4"),
                key("5"),
                key("6"),
                key("-", ft.Colors.AMBER_100),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                key("1"),
                key("2"),
                key("3"),
                key("+", ft.Colors.AMBER_100),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                key("0"),
                key("."),
                key("^", ft.Colors.AMBER_100),
                key("=", ft.Colors.GREEN_400, ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Divider(),
        ft.Text(
            "Historico",
            size=14,
            weight=ft.FontWeight.W_600,
        ),
        history,
    )


if __name__ == "__main__":
    ft.run(main)
