#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface de Usuário do OpenAgent usando Rich
"""

import sys
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.table import Table

# Tema Dracula / Hacker
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "hacker": "bold green",
    "user": "bold magenta",
    "ai": "bold cyan",
    "command": "bold yellow",
    "path": "italic blue",
    "dim": "grey50"
})

class UI:
    def __init__(self):
        self.console = Console(theme=custom_theme)
    
    def print_banner(self):
        banner = """
[hacker]
 ██████╗ ██████╗ ███████╗███╗   ██╗ █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
██║   ██║██████╔╝█████╗  ██╔██╗ ██║███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
╚██████╔╝██║     ███████╗██║ ╚████║██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
[/hacker]
[dim]Local AI Agent - Version 1.0.0[/dim]
"""
        self.console.print(banner, justify="center")
    
    def info(self, message):
        self.console.print(f"[info][+][/info] {message}")
    
    def success(self, message):
        self.console.print(f"[success][✓][/success] {message}")
    
    def error(self, message):
        self.console.print(f"[error][!][/error] {message}")
    
    def warning(self, message):
        self.console.print(f"[warning][?][/warning] {message}")
    
    def hacker(self, message):
        self.console.print(f"[hacker]>>>[/hacker] {message}")
    
    def print_menu(self, commands):
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Comando", style="command")
        table.add_column("Descrição", style="dim")
        
        for cmd, desc in commands.items():
            table.add_row(cmd, desc)
        
        self.console.print(Panel(table, title="[hacker]Comandos Disponíveis[/hacker]", border_style="hacker"))

    def print_ai_message(self, message):
        self.console.print(f"\n[ai]🤖 OpenAgent[/ai]")
        # Suporta markdown para a resposta da IA
        self.console.print(Markdown(message))
    
    def print_user_input_prompt(self):
        return self.console.input("\n[user]🧑 Você[/user]: ")

    def show_status(self, items):
        table = Table(show_header=False, box=None)
        for label, value in items.items():
            table.add_row(f"[info]{label}:[/info]", str(value))
        
        self.console.print(Panel(table, title="[hacker]Status do Sistema[/hacker]", border_style="cyan"))

    def print_code(self, code, language="python"):
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print(syntax)

    def progress_spinner(self, message):
        return self.console.status(f"[hacker]{message}...[/hacker]")

ui = UI()
