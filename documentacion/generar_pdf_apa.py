from __future__ import annotations

import html
import os
import re
import subprocess
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "Documentacion_Tecnica_Integral_VELANDIAX_APA.pdf"
SENA_LOGO = Path(__file__).resolve().parent / "sena_logo.png"


def register_fonts() -> tuple[str, str, str, str]:
    font_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    files = {
        "body": font_dir / "times.ttf",
        "bold": font_dir / "timesbd.ttf",
        "italic": font_dir / "timesi.ttf",
        "mono": font_dir / "consola.ttf",
    }
    if all(path.exists() for path in files.values()):
        pdfmetrics.registerFont(TTFont("TimesVX", str(files["body"])))
        pdfmetrics.registerFont(TTFont("TimesVX-Bold", str(files["bold"])))
        pdfmetrics.registerFont(TTFont("TimesVX-Italic", str(files["italic"])))
        pdfmetrics.registerFont(TTFont("ConsolasVX", str(files["mono"])))
        pdfmetrics.registerFontFamily(
            "TimesVX",
            normal="TimesVX",
            bold="TimesVX-Bold",
            italic="TimesVX-Italic",
            boldItalic="TimesVX-Bold",
        )
        return "TimesVX", "TimesVX-Bold", "TimesVX-Italic", "ConsolasVX"
    return "Times-Roman", "Times-Bold", "Times-Italic", "Courier"


BODY_FONT, BOLD_FONT, ITALIC_FONT, MONO_FONT = register_fonts()


class APADocument(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=letter,
            leftMargin=inch,
            rightMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
            title="Documentación técnica integral del proyecto VELANDIAX",
            author="Nicolás Ruiz Giraldo",
            subject="Arquitectura, base de datos, frontend, chatbot, Git y despliegue",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="apa", frames=[frame], onPage=self._page))

    def _page(self, canvas, doc):
        canvas.saveState()
        if SENA_LOGO.exists():
            canvas.drawImage(
                str(SENA_LOGO),
                letter[0] - 1.05 * inch,
                letter[1] - 0.85 * inch,
                width=0.55 * inch,
                height=0.55 * inch,
                preserveAspectRatio=True,
                mask="auto",
            )
        canvas.setFont(BODY_FONT, 12)
        canvas.drawRightString(letter[0] - inch, 0.5 * inch, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style_name = flowable.style.name
        levels = {"Heading1VX": 0, "Heading2VX": 1, "Heading3VX": 2}
        if style_name not in levels:
            return
        key = f"heading-{id(flowable)}"
        text = flowable.getPlainText()
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=levels[style_name], closed=False)
        self.notify("TOCEntry", (levels[style_name], text, self.page, key))


sample = getSampleStyleSheet()
styles = {
    "body": ParagraphStyle(
        "BodyVX",
        parent=sample["Normal"],
        fontName=BODY_FONT,
        fontSize=12,
        leading=24,
        alignment=TA_JUSTIFY,
        firstLineIndent=0.5 * inch,
        spaceAfter=0,
    ),
    "body_no_indent": ParagraphStyle(
        "BodyNoIndentVX",
        parent=sample["Normal"],
        fontName=BODY_FONT,
        fontSize=12,
        leading=24,
        alignment=TA_LEFT,
        firstLineIndent=0,
    ),
    "h1": ParagraphStyle(
        "Heading1VX",
        parent=sample["Heading1"],
        fontName=BOLD_FONT,
        fontSize=12,
        leading=24,
        alignment=TA_CENTER,
        spaceBefore=18,
        spaceAfter=6,
        keepWithNext=True,
    ),
    "h2": ParagraphStyle(
        "Heading2VX",
        parent=sample["Heading2"],
        fontName=BOLD_FONT,
        fontSize=12,
        leading=24,
        alignment=TA_LEFT,
        spaceBefore=14,
        spaceAfter=4,
        keepWithNext=True,
    ),
    "h3": ParagraphStyle(
        "Heading3VX",
        parent=sample["Heading3"],
        fontName=ITALIC_FONT,
        fontSize=12,
        leading=24,
        alignment=TA_LEFT,
        leftIndent=0.5 * inch,
        spaceBefore=8,
        keepWithNext=True,
    ),
    "title": ParagraphStyle(
        "TitleVX",
        parent=sample["Title"],
        fontName=BOLD_FONT,
        fontSize=17,
        leading=25,
        alignment=TA_CENTER,
    ),
    "subtitle": ParagraphStyle(
        "SubtitleVX",
        parent=sample["Normal"],
        fontName=BODY_FONT,
        fontSize=12,
        leading=24,
        alignment=TA_CENTER,
    ),
    "table": ParagraphStyle(
        "TableVX",
        parent=sample["Normal"],
        fontName=BODY_FONT,
        fontSize=8.2,
        leading=10,
        alignment=TA_LEFT,
    ),
    "table_header": ParagraphStyle(
        "TableHeaderVX",
        parent=sample["Normal"],
        fontName=BOLD_FONT,
        textColor=colors.white,
        fontSize=8.2,
        leading=10,
        alignment=TA_CENTER,
    ),
    "code": ParagraphStyle(
        "CodeVX",
        parent=sample["Code"],
        fontName=MONO_FONT,
        fontSize=8,
        leading=10,
        leftIndent=10,
        rightIndent=10,
        borderColor=colors.HexColor("#D1D5DB"),
        borderWidth=0.5,
        borderPadding=8,
        backColor=colors.HexColor("#F3F4F6"),
        spaceBefore=6,
        spaceAfter=8,
    ),
    "bullet": ParagraphStyle(
        "BulletVX",
        parent=sample["Normal"],
        fontName=BODY_FONT,
        fontSize=12,
        leading=24,
        leftIndent=0.5 * inch,
        firstLineIndent=-0.25 * inch,
        alignment=TA_LEFT,
    ),
    "reference": ParagraphStyle(
        "ReferenceVX",
        parent=sample["Normal"],
        fontName=BODY_FONT,
        fontSize=12,
        leading=24,
        leftIndent=0.5 * inch,
        firstLineIndent=-0.5 * inch,
        alignment=TA_LEFT,
    ),
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=False).replace("\n", "<br/>")


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(esc(text), styles[style])


def H1(text: str) -> Paragraph:
    return Paragraph(esc(text), styles["h1"])


def H2(text: str) -> Paragraph:
    return Paragraph(esc(text), styles["h2"])


def H3(text: str) -> Paragraph:
    return Paragraph(esc(text), styles["h3"])


def bullet(items: list[str], numbered: bool = False) -> list[Paragraph]:
    result = []
    for index, item in enumerate(items, start=1):
        marker = f"{index}." if numbered else "•"
        result.append(Paragraph(f"{marker} {esc(item)}", styles["bullet"]))
    return result


def code(text: str) -> Paragraph:
    clean = html.escape(text.strip()).replace(" ", "&#160;").replace("\n", "<br/>")
    return Paragraph(clean, styles["code"])


def table(headers: list[str], rows: list[list[object]], widths=None, font_size: float = 8.2):
    header_style = styles["table_header"]
    cell_style = ParagraphStyle(
        f"TableVX{font_size}",
        parent=styles["table"],
        fontSize=font_size,
        leading=font_size + 1.8,
    )
    data = [[Paragraph(esc(v), header_style) for v in headers]]
    data.extend([[Paragraph(esc(v), cell_style) for v in row] for row in rows])
    obj = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    obj.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9CA3AF")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
            ]
        )
    )
    return obj


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return completed.stdout.strip()


def git_history() -> list[list[str]]:
    raw = git("log", "--all", "--reverse", "--date=short", "--pretty=format:%ad|%h|%an|%s")
    return [line.split("|", 3) for line in raw.splitlines() if line]


def add_section(story, heading: str, paragraphs: list[str]):
    story.append(H1(heading))
    story.extend(P(text) for text in paragraphs)


story = []

# Portada institucional SENA con estructura de la evidencia suministrada.
story.append(Spacer(1, 0.2 * inch))
story.append(Paragraph("GA5-220501095-AA1-EV03", styles["subtitle"]))
story.append(Spacer(1, 0.18 * inch))
story.append(Paragraph("DOCUMENTACIÓN TÉCNICA INTEGRAL DEL PROYECTO VELANDIAX", styles["title"]))
story.append(Paragraph("ARQUITECTURA, BASE DE DATOS, API, FRONTEND, CHATBOT, GIT Y DESPLIEGUE", styles["subtitle"]))
story.append(Spacer(1, 0.16 * inch))
story.append(Paragraph("FICHA 3186657", styles["subtitle"]))
story.append(Spacer(1, 1.15 * inch))
for line in [
    "APRENDIZ",
    "NICOLÁS RUIZ GIRALDO",
]:
    story.append(Paragraph(esc(line), styles["subtitle"]))
story.append(Spacer(1, 0.75 * inch))
for line in [
    "PRESENTADO AL INSTRUCTOR",
    "JHON FAIBER CERQUERA SÁNCHEZ",
]:
    story.append(Paragraph(esc(line), styles["subtitle"]))
story.append(Spacer(1, 1.0 * inch))
for line in [
    "ANÁLISIS Y DESARROLLO DE SOFTWARE",
    "SERVICIO NACIONAL DE APRENDIZAJE",
    "SENA REGIONAL HUILA",
    "11/11/2026",
]:
    story.append(Paragraph(esc(line), styles["subtitle"]))
story.append(PageBreak())

story.append(H1("Control del documento"))
story.append(
    table(
        ["Campo", "Valor"],
        [
            ["Proyecto", "VELANDIAX"],
            ["Tipo", "Memoria técnica integral y manual de continuidad"],
            ["Presentación", "Plantilla institucional SENA y adaptación técnica de APA, 7.ª edición"],
            ["Aprendiz", "Nicolás Ruiz Giraldo"],
            ["Instructor", "Jhon Faiber Cerquera Sánchez"],
            ["Ficha", "3186657"],
            ["Repositorio", "https://github.com/Nicolas-ruizg/DISTRIBUIDORA-VELANDIAX"],
            ["Rama", "main"],
            ["HEAD local", git("rev-parse", "--short", "HEAD") or "No disponible"],
            ["Estado Git", git("status", "-sb").splitlines()[0]],
            ["Fecha de corte", "11 de noviembre de 2026"],
        ],
        [1.4 * inch, 5.1 * inch],
        9,
    )
)
story.append(H1("Resumen"))
story.append(
    P(
        "VELANDIAX es una plataforma comercial para una distribuidora de ropa que integra catálogo público, "
        "ventas por unidad y por paca, inventario por depósitos, clientes, pedidos, pagos, guías, seguimiento "
        "logístico, documentos imprimibles y atención por WhatsApp. El monorepositorio contiene una API REST "
        "en Python y FastAPI, una aplicación web en React y TypeScript, y un chatbot en Python conectado con "
        "WhatsApp Cloud API y Gemini. PostgreSQL conserva la información operativa mediante SQLAlchemy; las "
        "imágenes se cargan temporalmente a Supabase Storage. El despliegue usa Ubuntu, Nginx, systemd y HTTPS "
        "bajo velandiax.com.co. Este documento reconstruye la creación, funcionamiento y evolución del sistema "
        "a partir del código, los scripts SQL, el historial Git y el estado local pendiente de commit."
    )
)
story.append(P("Palabras clave: comercio electrónico, inventario, FastAPI, React, PostgreSQL, SQLAlchemy, WhatsApp, trazabilidad, VELANDIAX.", "body_no_indent"))
story.append(PageBreak())
story.append(H1("Tabla de contenido"))
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle("TOC0", fontName=BODY_FONT, fontSize=11, leading=18, leftIndent=0, firstLineIndent=0),
    ParagraphStyle("TOC1", fontName=BODY_FONT, fontSize=10, leading=15, leftIndent=18, firstLineIndent=0),
    ParagraphStyle("TOC2", fontName=BODY_FONT, fontSize=9, leading=13, leftIndent=36, firstLineIndent=0),
]
story.append(toc)
story.append(PageBreak())

add_section(
    story,
    "1. Introducción",
    [
        "El proyecto responde a la operación de una distribuidora de ropa con venta minorista y por paca. Su propósito es mantener una única fuente de información para productos, variantes, existencias, depósitos, usuarios, clientes, pedidos y envíos. Sobre esta base funcionan una tienda web, un panel administrativo y un chatbot de WhatsApp.",
        "El análisis se realizó sobre el monorepositorio local, la rama main, los archivos rastreados, los cambios no confirmados, los scripts SQL y la configuración de despliegue. Se excluyen secretos reales. Cuando el código actual difiere del esquema consolidado o de los README, la diferencia se registra como hallazgo.",
    ],
)
story.append(H2("1.1 Objetivo general"))
story.append(P("Documentar de forma reproducible la arquitectura, construcción, reglas, operación y evolución de VELANDIAX para facilitar mantenimiento, auditoría, instalación y continuidad técnica."))
story.append(H2("1.2 Objetivos específicos"))
story.extend(
    bullet(
        [
            "Describir el negocio, los módulos y las reglas de productos, stock, ventas, pagos y envíos.",
            "Presentar tecnologías, dependencias, patrones y decisiones de diseño.",
            "Documentar tablas, campos, relaciones, restricciones, índices y migraciones.",
            "Catalogar endpoints, pantallas, roles e integraciones externas.",
            "Reconstruir Git por commits, ramas, remoto y cambios locales.",
            "Explicar instalación local, despliegue, operación, seguridad, pruebas y riesgos.",
        ]
    )
)
story.append(H2("1.3 Alcance"))
story.append(P("La documentación cubre DISTRIBUIDORA-VELANDIAX, velandiax-admin, Velandiax-Chatbot y los archivos raíz. El repositorio registra 113 archivos. El inventario aproximado incluye 5.098 líneas TSX, 4.712 líneas Python, 570 líneas SQL y 489 líneas Markdown, sin contar dependencias o artefactos compilados."))

add_section(
    story,
    "2. Contexto del negocio y capacidades",
    [
        "VELANDIAX comercializa prendas en modalidad presencial y web. Cada producto puede tener variantes con talla, color, material u otros atributos libres; cada variante controla sus propios precios, estado, imágenes y stock. Los productos, usuarios y pedidos se relacionan con depósitos para segmentar la operación.",
        "La tienda pública permite descubrir productos, ver ofertas, armar una paca, conservar favoritos, crear pedidos y consultar seguimiento. El backoffice administra catálogo, inventario, ventas, depósitos, usuarios, pagos, envíos, facturas y guías. El chatbot replica catálogo, carrito, checkout y seguimiento en WhatsApp.",
    ],
)
story.append(H2("2.1 Capacidades funcionales"))
story.extend(
    bullet(
        [
            "Catálogo público limitado a productos y variantes activas con stock.",
            "Código comercial manual, preparado para lectura por código de barras.",
            "Atributos variables almacenados en JSONB.",
            "Imágenes de producto y variante con principal, orden, texto alternativo y estado.",
            "Venta presencial y web con reglas distintas de pago y despacho.",
            "Trazabilidad por depósito, vendedor, responsable de inventario y cliente.",
            "Estados de pago CANCELADO, PAGO_50 y PAGO_TOTAL.",
            "Generación de guía al confirmar 50 % o pago total.",
            "Simulación logística cada 30 segundos mientras la API permanece activa.",
            "PDF de detalle, factura y guía para impresión térmica de 120 mm.",
            "Chatbot con Meta, menús, favoritos, compra por volumen y Gemini.",
            "Footer comercial, dos sedes, redes, TikTok y botón flotante de WhatsApp.",
        ]
    )
)
story.append(H2("2.2 Reglas de negocio"))
story.append(
    table(
        ["Regla", "Comportamiento actual"],
        [
            ["Conservación histórica", "Productos y variantes se desactivan; no se eliminan físicamente."],
            ["Stock", "No puede ser negativo; la venta bloquea variantes y descuenta en transacción."],
            ["Depósito", "Un pedido pertenece a un depósito; el carrito no mezcla depósitos."],
            ["Alcance de usuario", "No administradores operan sobre el depósito asignado."],
            ["Pago y guía", "Solo PAGO_50 o PAGO_TOTAL habilitan guía."],
            ["Presencial", "No requiere datos de envío ni regla de anticipo del 50 %."],
            ["Público", "Se ocultan inactivos y variantes sin inventario."],
            ["Seguimiento", "Consulta por celular o guía; excluye estados finales en la vista por celular."],
            ["Por paca", "La interfaz usa Por paca; el campo técnico continúa como paquete_estatico."],
        ],
        [1.6 * inch, 4.9 * inch],
    )
)

add_section(
    story,
    "3. Metodología y control de versiones",
    [
        "La evidencia corresponde a desarrollo iterativo e incremental orientado a funcionalidades. El sistema inició como solución full stack y recibió incrementos verticales de despliegue, datos, roles, depósitos, chatbot e impresión. No existe evidencia de sprints, ceremonias o artefactos suficientes para afirmar Scrum formal.",
        "El repositorio usa una rama principal única, main, sin tags ni ramas feature registradas. Esta estrategia equivale a trunk-based simplificado y resulta viable para un equipo pequeño, siempre que se adopten commits frecuentes, revisión y protección de rama.",
    ],
)
story.append(H2("3.1 Prácticas observadas"))
story.extend(
    bullet(
        [
            "Monorepositorio para backend, frontend, chatbot y despliegue.",
            "Arquitectura por capas y módulos por capacidad.",
            "Contratos de datos con Pydantic y TypeScript.",
            "SQLAlchemy y transacciones para persistencia.",
            "Configuración por variables de entorno.",
            "RBAC aplicado en frontend y backend.",
            "Scripts SQL incrementales y esquema consolidado manual.",
            "Compilación de producción y pruebas versionadas del chatbot.",
        ]
    )
)

story.append(H1("4. Arquitectura general"))
story.append(
    code(
        "Navegador                         WhatsApp\n"
        "   |                                  |\n"
        "   | HTTPS                            | Meta Cloud API / webhook\n"
        "   v                                  v\n"
        "Nginx ----------------------> Chatbot FastAPI --------> Gemini API\n"
        "   |                                  |\n"
        "   | estáticos                         | cliente HTTP\n"
        "   v                                  v\n"
        "React + TypeScript ---------> API FastAPI + SQLAlchemy\n"
        "                                      |\n"
        "                                      v\n"
        "                                 PostgreSQL\n"
        "                                      |\n"
        "                                      +--> Supabase Storage"
    )
)
story.append(P("Nginx entrega el build de React y reenvía /api a Uvicorn en 127.0.0.1:8001. FastAPI concentra reglas y persistencia. El chatbot recibe eventos de Meta, consulta el catálogo real mediante la API y puede crear pedidos con una cuenta de ventas. Gemini interpreta lenguaje natural; SalesBot valida toda acción contra catálogo y estado conversacional."))
story.append(H2("4.1 Módulos"))
story.append(
    table(
        ["Módulo", "Responsabilidad", "Tecnologías"],
        [
            ["DISTRIBUIDORA-VELANDIAX", "API, seguridad, negocio, persistencia, envíos y SQL.", "Python, FastAPI, SQLAlchemy, PostgreSQL"],
            ["velandiax-admin", "Tienda pública y panel administrativo.", "React, TypeScript, Vite, Tailwind"],
            ["Velandiax-Chatbot", "Webhook, canal conversacional, IA y backend.", "Python, FastAPI, HTTPX, Meta, Gemini"],
            ["DEPLOYMENT.md", "Instalación y operación productiva.", "Ubuntu, Nginx, systemd, Certbot"],
            [".vscode", "Tareas para desarrollo local.", "Visual Studio Code"],
        ],
        [1.7 * inch, 2.9 * inch, 1.9 * inch],
    )
)

story.append(H1("5. Lenguajes, frameworks y dependencias"))
story.append(
    table(
        ["Capa", "Tecnología", "Versión declarada", "Uso"],
        [
            ["Backend", "Python", "3.11+", "API, negocio y automatización."],
            ["API", "FastAPI", "0.104.1", "REST, DI, OpenAPI y validación."],
            ["ORM", "SQLAlchemy", "2.0.23", "Modelos, sesiones y transacciones."],
            ["BD", "PostgreSQL", "Servidor compatible", "Relaciones, índices y JSONB."],
            ["Esquemas", "Pydantic", "2.5.0", "Entradas y salidas."],
            ["Seguridad", "PyJWT / bcrypt", "2.13.0 / 4.1.1", "JWT y hash de claves."],
            ["Frontend", "TypeScript", "~6.0.2", "Tipado del cliente."],
            ["UI", "React", "19.2.6", "Componentes y contextos."],
            ["Build", "Vite", "8.0.12", "Desarrollo y producción."],
            ["Estilos", "Tailwind CSS", "4.3.1", "Diseño responsivo."],
            ["HTTP", "Axios", "1.17.0", "Consumo e interceptores."],
            ["Documentos", "jsPDF", "4.2.1", "Factura y guía."],
            ["Chatbot", "HTTPX", "0.28.1", "Clientes HTTP asíncronos."],
            ["IA", "Gemini API", "Configurable", "Interpretación de intención."],
            ["Servidor", "Ubuntu/Nginx/systemd", "Ubuntu 24", "Hosting y supervisión."],
            ["Versiones", "Git/GitHub", "main", "Historia y colaboración."],
        ],
        [1.0 * inch, 1.35 * inch, 1.25 * inch, 2.9 * inch],
        7.5,
    )
)
story.append(H2("5.1 Backend"))
story.append(P("requirements.txt fija FastAPI, Uvicorn, psycopg2-binary, SQLAlchemy, PyJWT, bcrypt, python-dotenv, Pydantic, python-multipart, pytest y Pillow. El acceso es síncrono mediante Session de SQLAlchemy y psycopg2."))
story.append(H2("5.2 Frontend"))
story.append(P("React Router define navegación; Axios centraliza HTTP; Lucide React provee iconos; jsPDF genera documentos; Tailwind implementa el lenguaje visual blanco y negro. React Query está instalado, aunque la mayoría de cargas usa useEffect y estado local."))

story.append(H1("6. Estructura del repositorio"))
story.append(
    code(
        "VELANDIAX/\n"
        "|-- DISTRIBUIDORA-VELANDIAX/\n"
        "|   |-- database/      modelos, conexión, DDL, migraciones y seed\n"
        "|   |-- routes/        auth, catálogo, pedidos, usuarios y envíos\n"
        "|   |-- schemas/       contratos Pydantic\n"
        "|   |-- services/      simulador logístico\n"
        "|   `-- utils/         JWT\n"
        "|-- velandiax-admin/src/\n"
        "|   |-- api, context, components y features\n"
        "|-- Velandiax-Chatbot/\n"
        "|   |-- app, data y tests\n"
        "|-- DEPLOYMENT.md\n"
        "`-- README.md"
    )
)

story.append(H1("7. Construcción e instalación paso a paso"))
story.append(H2("7.1 Prerrequisitos"))
story.extend(bullet(["Git, Python 3.11+, Node.js 20/22, npm y PostgreSQL.", "Ubuntu 24, Nginx, systemd y Certbot para producción.", "Supabase Storage durante la etapa actual de imágenes.", "Aplicación Meta/WhatsApp Business y Google AI Studio para integraciones."]))
story.append(H2("7.2 Clonación"))
story.append(code("git clone https://github.com/Nicolas-ruizg/DISTRIBUIDORA-VELANDIAX.git\ncd DISTRIBUIDORA-VELANDIAX\ngit switch main\ngit status"))
story.append(H2("7.3 Base de datos"))
story.extend(bullet(["Crear base y usuario PostgreSQL.", "Ejecutar database/schema_final.sql.", "Aplicar database/add_stock_variantes.sql, todavía pendiente de integrar al esquema final.", "Renombrar DEP001 y DEP002.", "Crear usuarios mediante API para almacenar bcrypt.", "Usar seed_demo_ropa únicamente en demostración."], numbered=True))
story.append(code("psql -U postgres -d velandiax -f database/schema_final.sql\npsql -U postgres -d velandiax -f database/add_stock_variantes.sql"))
story.append(H2("7.4 Backend"))
story.append(code("cd DISTRIBUIDORA-VELANDIAX\npython -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npip install -r requirements.txt\nCopy-Item .env.example .env\npython -m uvicorn main:app --reload --host 127.0.0.1 --port 8001"))
story.append(H2("7.5 Frontend"))
story.append(code("cd velandiax-admin\nnpm install\nCopy-Item .env.example .env\nnpm run dev"))
story.append(P("VITE_API_URL usa http://127.0.0.1:8001 en local y /api en producción. Esto evita que el navegador del visitante intente consultar su propio localhost."))
story.append(H2("7.6 Chatbot"))
story.append(code("cd Velandiax-Chatbot\npython -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npip install -r requirements-dev.txt\nCopy-Item .env.example .env\nuvicorn app.main:app --reload --port 8000"))

story.append(H1("8. Base de datos"))
story.append(P("El diseño combina entidades relacionales para información estable con JSONB para atributos variables. NUMERIC se usa en dinero, salvo precio_anterior, que continúa como DOUBLE PRECISION. Los estados conservan historia de productos y variantes. Las llaves foráneas garantizan integridad entre catálogo, inventario, clientes, pedidos y envíos."))
story.append(H2("8.1 Relaciones"))
story.append(code("DEPOSITOS 1--N USUARIOS / PRODUCTO / PEDIDO\nCATEGORIA 1--N PRODUCTO 1--N VARIANTES_PRODUCTO\nPRODUCTO 1--N IMAGENES_PRODUCTO\nVARIANTES_PRODUCTO 1--N IMAGENES_VARIANTE_PRODUCTO\nCLIENTES 1--N PEDIDO 1--N ITEMS_PEDIDO N--1 VARIANTES_PRODUCTO\nPEDIDO 1--0..1 ENVIOS\nPRODUCTO N--N VARIANTES mediante PAQUETES_ESTATICOS_ITEMS"))

db_rows = [
    ["usuarios", "id_usuario", "INTEGER identity", "PK", "Identificador interno."], ["usuarios", "id_deposito", "VARCHAR(20)", "FK nullable", "Depósito asignado."], ["usuarios", "nombre", "VARCHAR(150)", "NOT NULL", "Nombre."], ["usuarios", "email", "VARCHAR(160)", "UNIQUE", "Credencial."], ["usuarios", "codigo_cuenta", "VARCHAR(20)", "UNIQUE", "VEND001/INV001."], ["usuarios", "password_hash", "VARCHAR(255)", "NOT NULL", "Hash bcrypt."], ["usuarios", "rol", "VARCHAR(30)", "CHECK", "ADMINISTRADOR/VENDEDOR/INVENTARIO."], ["usuarios", "activo", "BOOLEAN", "DEFAULT true", "Acceso."], ["usuarios", "fecha_creacion", "TIMESTAMP", "DEFAULT now", "Auditoría."], ["usuarios", "ultimo_acceso", "TIMESTAMP", "nullable", "Último login."],
    ["categoria", "id_categoria", "INTEGER identity", "PK", "Identificador."], ["categoria", "nombre", "VARCHAR(100)", "NOT NULL", "Nombre."], ["categoria", "descripcion", "TEXT", "nullable", "Descripción."],
    ["depositos", "id_deposito", "VARCHAR(20)", "PK", "Código manual."], ["depositos", "nombre", "VARCHAR(120)", "nullable", "Sede/bodega."], ["depositos", "activo", "BOOLEAN", "DEFAULT true", "Estado."], ["depositos", "fecha_creacion", "TIMESTAMP", "DEFAULT now", "Auditoría."],
    ["producto", "id_producto", "INTEGER identity", "PK", "ID técnico."], ["producto", "id_categoria", "INTEGER", "FK", "Categoría."], ["producto", "id_deposito", "VARCHAR(20)", "FK", "Depósito."], ["producto", "codigo_producto", "VARCHAR(60)", "UNIQUE", "Referencia manual."], ["producto", "nombre", "VARCHAR(200)", "NOT NULL", "Nombre."], ["producto", "descripcion", "TEXT", "nullable", "Detalle."], ["producto", "paquete_estatico", "BOOLEAN", "DEFAULT false", "Por paca."], ["producto", "en_oferta", "BOOLEAN", "DEFAULT false", "Oferta."], ["producto", "precio_anterior", "DOUBLE", "nullable", "Precio tachado."], ["producto", "estado", "VARCHAR(20)", "CHECK", "ACTIVO/INACTIVO."],
    ["variantes_producto", "id_variante", "INTEGER identity", "PK", "ID variante."], ["variantes_producto", "id_producto", "INTEGER", "FK", "Producto."], ["variantes_producto", "precio_costo", "NUMERIC(12,2)", "NOT NULL", "Costo."], ["variantes_producto", "precio_minorista", "NUMERIC(12,2)", "NOT NULL", "Precio venta."], ["variantes_producto", "precio_mayorista", "NUMERIC(12,2)", "NOT NULL", "Precio volumen heredado."], ["variantes_producto", "stock", "INTEGER", "CHECK >= 0", "Existencia."], ["variantes_producto", "peso", "NUMERIC(10,2)", "nullable", "Peso."], ["variantes_producto", "aplica_paquete", "BOOLEAN", "DEFAULT false", "Elegible para paca."], ["variantes_producto", "atributos", "JSONB", "nullable", "Talla/color/material."], ["variantes_producto", "estado", "VARCHAR(20)", "CHECK", "ACTIVO/INACTIVO."],
    ["imagenes_producto", "id_imagen", "INTEGER identity", "PK", "Identificador."], ["imagenes_producto", "id_producto", "INTEGER", "FK CASCADE", "Producto."], ["imagenes_producto", "url", "VARCHAR(500)", "NOT NULL", "URL pública."], ["imagenes_producto", "alt_text", "VARCHAR(200)", "nullable", "Accesibilidad."], ["imagenes_producto", "es_principal", "BOOLEAN", "DEFAULT false", "Portada."], ["imagenes_producto", "orden", "INTEGER", "CHECK >= 0", "Orden."], ["imagenes_producto", "estado", "VARCHAR(20)", "CHECK", "Estado."], ["imagenes_producto", "fecha_creacion", "TIMESTAMP", "DEFAULT now", "Auditoría."],
    ["imagenes_variante_producto", "id_imagen_variante", "INTEGER identity", "PK", "Identificador."], ["imagenes_variante_producto", "id_variante", "INTEGER", "FK CASCADE", "Variante."], ["imagenes_variante_producto", "url", "VARCHAR(500)", "NOT NULL", "URL."], ["imagenes_variante_producto", "alt_text", "VARCHAR(200)", "nullable", "Accesibilidad."], ["imagenes_variante_producto", "es_principal", "BOOLEAN", "DEFAULT false", "Portada."], ["imagenes_variante_producto", "orden", "INTEGER", "CHECK >= 0", "Orden."], ["imagenes_variante_producto", "estado", "VARCHAR(20)", "CHECK", "Estado."], ["imagenes_variante_producto", "fecha_creacion", "TIMESTAMP", "DEFAULT now", "Auditoría."],
    ["clientes", "id_cliente", "INTEGER identity", "PK", "Identificador."], ["clientes", "cedula", "VARCHAR(30)", "UNIQUE", "Cédula/NIT."], ["clientes", "celular", "VARCHAR(20)", "UNIQUE", "Contacto/seguimiento."], ["clientes", "nombre", "VARCHAR(200)", "NOT NULL", "Nombre."],
    ["pedido", "id_pedido", "INTEGER identity", "PK", "Número interno."], ["pedido", "id_cliente", "INTEGER", "FK", "Cliente."], ["pedido", "id_deposito", "VARCHAR(20)", "FK", "Depósito."], ["pedido", "id_usuario_venta", "INTEGER", "FK nullable", "Vendedor."], ["pedido", "id_usuario_inventario", "INTEGER", "FK nullable", "Inventario."], ["pedido", "canal_venta", "VARCHAR(20)", "CHECK", "PRESENCIAL/WEB."], ["pedido", "tipo_envio", "VARCHAR(30)", "CHECK", "CONTRAENTREGA/GRATIS."], ["pedido", "estado", "VARCHAR(30)", "NOT NULL", "Estado operativo."], ["pedido", "estado_pago", "VARCHAR(20)", "CHECK", "CANCELADO/PAGO_50/PAGO_TOTAL."], ["pedido", "total", "NUMERIC(14,2)", "DEFAULT 0", "Total."], ["pedido", "precio_envio", "NUMERIC(12,2)", "DEFAULT 0", "Envío."], ["pedido", "es_mayorista", "BOOLEAN", "DEFAULT false", "Volumen heredado."], ["pedido", "fecha", "TIMESTAMP", "DEFAULT now", "Registro."],
    ["items_pedido", "id_item_pedido", "INTEGER identity", "PK", "Detalle."], ["items_pedido", "id_pedido", "INTEGER", "FK CASCADE", "Pedido."], ["items_pedido", "id_variante", "INTEGER", "FK", "Variante."], ["items_pedido", "cantidad", "INTEGER", "CHECK > 0", "Unidades."], ["items_pedido", "precio_unitario", "NUMERIC(12,2)", "NOT NULL", "Precio congelado."],
    ["paquetes_estaticos_items", "id_paquete", "INTEGER", "PK/FK", "Producto paca."], ["paquetes_estaticos_items", "id_variante", "INTEGER", "PK/FK", "Variante incluida."], ["paquetes_estaticos_items", "cantidad", "INTEGER", "CHECK > 0", "Cantidad."],
    ["envios", "id_envio", "INTEGER identity", "PK", "ID logístico."], ["envios", "id_pedido", "INTEGER", "FK UNIQUE", "Pedido."], ["envios", "transportadora", "VARCHAR(120)", "nullable", "Operador."], ["envios", "numero_guia", "VARCHAR(120)", "UNIQUE", "Guía."], ["envios", "estado", "VARCHAR(30)", "NOT NULL", "Estado."], ["envios", "nombre_destinatario", "VARCHAR(200)", "NOT NULL", "Destinatario."], ["envios", "celular_destinatario", "VARCHAR(20)", "nullable", "Contacto."], ["envios", "direccion", "TEXT", "NOT NULL", "Dirección."], ["envios", "ciudad", "VARCHAR(100)", "NOT NULL", "Ciudad."], ["envios", "departamento", "VARCHAR(100)", "nullable", "Departamento."], ["envios", "codigo_postal", "VARCHAR(20)", "nullable", "Postal."], ["envios", "notas", "TEXT", "nullable", "Notas."], ["envios", "costo", "NUMERIC(12,2)", "CHECK >= 0", "Costo."], ["envios", "fecha_despacho", "TIMESTAMP", "nullable", "Salida."], ["envios", "fecha_entrega", "TIMESTAMP", "nullable", "Entrega."], ["envios", "fecha_creacion", "TIMESTAMP", "DEFAULT now", "Auditoría."],
]
story.append(H2("8.2 Diccionario de datos completo"))
story.append(table(["Tabla", "Campo", "Tipo", "Regla", "Propósito"], db_rows, [1.25*inch, 1.45*inch, 1.15*inch, 1.05*inch, 1.6*inch], 6.9))
story.append(H2("8.3 Índices y restricciones"))
story.append(P("Hay índices para categoría, código y depósito de producto; depósito de usuario; producto de variante; imágenes; cliente, depósito, vendedor y fecha del pedido; y detalles. UNIQUE cubre correo, código de cuenta, código de producto, cédula, celular y guía. CHECK valida roles, estados, cantidades, stock y costos."))
story.append(H2("8.4 Migraciones SQL"))
migration_rows = [[p.name, "Script incremental o esquema consolidado"] for p in sorted((ROOT / "DISTRIBUIDORA-VELANDIAX" / "database").glob("*.sql"))]
story.append(table(["Archivo", "Función"], migration_rows, [3.1*inch, 3.4*inch], 8))
story.append(P("Hallazgo: add_stock_variantes.sql no está rastreado por Git y stock no aparece todavía en schema_final.sql, aunque el modelo y la aplicación dependen de él."))

story.append(H1("9. Backend FastAPI"))
story.append(P("main.py registra CORS, routers y un lifespan que inicia el simulador. connection.py usa URL.create, pool_pre_ping y sesiones cerradas por dependencia. Los modelos siguen SQLAlchemy 2.0 y Pydantic valida longitudes, rangos y enumeraciones."))
story.append(H2("9.1 Autenticación y autorización"))
story.append(P("POST /admin/login localiza el usuario activo, compara bcrypt, valida rol, actualiza ultimo_acceso y crea un JWT con usuario, depósito, código, rol, emisión y expiración. verificar_admin, verificar_inventario y verificar_ventas aplican permisos del lado servidor."))
story.append(H2("9.2 Matriz de roles"))
story.append(table(["Función", "Administrador", "Vendedor", "Inventario"], [["Dashboard", "Sí", "No", "No"], ["Categorías", "Completo", "No", "Crear/editar"], ["Productos", "Completo", "Lectura API", "Crear/editar en depósito"], ["Registrar venta", "Sí", "Sí", "No"], ["Historial", "Sí", "No", "No"], ["Depósitos", "Administrar", "Asignado", "Asignado"], ["Usuarios", "Administrar", "No", "No"], ["Envíos", "Administrar", "No", "No"]], [2.1*inch, 1.45*inch, 1.4*inch, 1.55*inch]))
story.append(H2("9.3 Inventario y concurrencia"))
story.append(P("Al crear un pedido la API consulta variantes activas, bloquea sus filas con SELECT FOR UPDATE, valida depósito y existencia, descuenta stock y crea items en una transacción. El cambio local limita el bloqueo a VarianteProducto y usa selectinload para Producto, corrigiendo el error de PostgreSQL sobre FOR UPDATE en el lado anulable de un outer join."))
story.append(H2("9.4 Pagos, guía y simulación"))
story.append(P("CANCELADO significa pago no confirmado. PAGO_50 o PAGO_TOTAL permiten crear guía si existen datos de entrega. El simulador avanza PENDIENTE, PREPARANDO, DESPACHADO, EN_TRANSITO y ENTREGADO; registra fechas de despacho y entrega. Al ejecutarse dentro de la API puede duplicarse con varios workers."))
story.append(H2("9.5 Imágenes"))
story.append(P("Los endpoints multipart admiten JPG, PNG, WebP y GIF, controlan tamaño y suben a Supabase Storage. PostgreSQL almacena URL, alt, principal, orden y estado. La capa pública filtra imágenes inactivas."))

api_rows = [
    ["GET", "/", "Público", "Salud."], ["POST", "/admin/login", "Público", "JWT."], ["GET", "/admin/dashboard", "Admin", "Métricas y filtros."],
    ["GET", "/categorias", "Público", "Lista."], ["GET", "/categorias/{id}", "Público", "Detalle."], ["GET", "/admin/categorias", "Público actual", "Alias."], ["POST", "/admin/categorias", "Admin/Inventario", "Crear."], ["PUT", "/admin/categorias/{id}", "Admin/Inventario", "Editar."], ["DELETE", "/admin/categorias/{id}", "Admin/Inventario", "Eliminar."],
    ["GET", "/productos", "Público", "Activos con stock."], ["GET", "/productos/{id}", "Público", "Detalle."], ["GET", "/admin/productos", "Autenticado", "Todos según depósito."], ["GET", "/admin/productos/{id}", "Autenticado", "Detalle admin."], ["POST", "/admin/productos", "Admin/Inventario", "Crear."], ["PUT", "/admin/productos/{id}", "Admin/Inventario", "Editar/desactivar."], ["POST", "/admin/productos/{id}/variantes", "Admin/Inventario", "Crear variante."], ["PUT", "/admin/variantes/{id}", "Admin/Inventario", "Editar variante/stock."],
    ["POST", "/admin/productos/{id}/imagenes", "Admin/Inventario", "URL producto."], ["POST", "/admin/productos/{id}/imagenes/upload", "Admin/Inventario", "Subir producto."], ["PUT", "/admin/productos/imagenes/{id}", "Admin/Inventario", "Editar imagen."], ["POST", "/admin/variantes/{id}/imagenes", "Admin/Inventario", "URL variante."], ["POST", "/admin/variantes/{id}/imagenes/upload", "Admin/Inventario", "Subir variante."], ["PUT", "/admin/variantes/imagenes/{id}", "Admin/Inventario", "Editar imagen."],
    ["GET", "/admin/pedidos", "Admin", "Historial."], ["POST", "/pedidos", "Público", "Pedido web."], ["POST", "/admin/pedidos", "Admin/Vendedor", "Venta manual."], ["GET", "/admin/pedidos/{id}", "Admin", "Detalle."], ["PUT", "/admin/pedidos/{id}", "Admin", "Actualizar/pago."], ["DELETE", "/admin/pedidos/{id}", "Admin", "Eliminar."],
    ["POST", "/admin/pedidos/{id}/envio", "Admin", "Crear envío."], ["GET", "/admin/pedidos/{id}/envio", "Admin", "Consultar envío."], ["GET", "/admin/envios", "Admin", "Listar."], ["GET", "/envios/seguimiento/{guia}", "Público", "Guía."], ["GET", "/pedidos/seguimiento", "Público", "Por celular."],
    ["GET", "/admin/depositos", "Autenticado", "Listar según alcance."], ["POST", "/admin/depositos", "Admin", "Crear."], ["PUT", "/admin/depositos/{id}", "Admin", "Editar."], ["DELETE", "/admin/depositos/{id}", "Admin", "Desactivar."],
    ["GET", "/admin/usuarios", "Admin", "Listar."], ["GET", "/admin/usuarios/{id}", "Admin", "Detalle."], ["POST", "/admin/usuarios", "Admin", "Crear."], ["PUT", "/admin/usuarios/{id}", "Admin", "Editar."], ["DELETE", "/admin/usuarios/{id}", "Admin", "Desactivar."],
]
story.append(H2("9.6 Catálogo completo de endpoints"))
story.append(table(["Método", "Ruta", "Acceso", "Finalidad"], api_rows, [0.65*inch, 2.6*inch, 1.35*inch, 1.9*inch], 7))

story.append(H1("10. Frontend React"))
story.append(P("La SPA combina tienda y backoffice. StoreLayout envuelve la tienda con CartProvider y FavoritesProvider. AdminLayout organiza el panel; ProtectedRoute exige token y usuario; RoleRoute filtra por rol. Axios adjunta Bearer y limpia sesión ante 401. La paleta es blanco, negro, grises y verde de WhatsApp."))
story.append(H2("10.1 Tienda"))
story.append(table(["Vista", "Ruta", "Función"], [["HomeView", "/", "Banner, slider, recomendados, paca y TikTok."], ["ProductView", "/producto/:id", "Galería, atributos, stock, depósito y carrito."], ["CategoryView", "/categoria/:id", "Catálogo por categoría."], ["PackageBuilderView", "/arma-tu-paca", "Categorías y productos elegibles."], ["SaleView", "/sale", "Ofertas."], ["FavoritesView", "/favoritos", "Favoritos locales."], ["OrderTrackingView", "/seguimiento", "Pedidos activos por celular."], ["CartModal", "Global", "Carrito, checkout, pedido y WhatsApp."]], [1.4*inch, 1.4*inch, 3.7*inch], 8))
story.append(H2("10.2 Panel"))
story.append(table(["Vista", "Función"], [["LoginView", "Autenticación."], ["Dashboard", "Métricas por tiempo, vendedor, referencia y depósito."], ["CategoriasView", "Gestión de categorías."], ["ProductosView/Form", "Código, depósito, oferta, variantes, stock e imágenes."], ["PedidoFormView", "Venta presencial/web y búsqueda por código."], ["PedidosView/Detalle", "Historial, pago, factura y guía."], ["DepositosView", "Alta, edición y desactivación."], ["UsuariosView", "Roles, códigos y depósito."]], [2.2*inch, 4.3*inch], 8))
story.append(H2("10.3 Estado e impresión"))
story.append(P("Carrito y favoritos se conservan en localStorage. El JWT usa admin_token y el usuario admin_user. jsPDF crea detalle, factura y guía térmica. La impresión depende del controlador y diálogo del navegador; para impresión silenciosa se requeriría QZ Tray o agente local."))

story.append(H1("11. Chatbot de WhatsApp"))
story.append(P("La segunda aplicación FastAPI verifica GET /webhook y recibe POST /webhook. Valida opcionalmente HMAC SHA-256, acepta rápido y procesa en BackgroundTasks. Una cola de 2.000 IDs deduplica mensajes dentro de una instancia."))
story.append(H2("11.1 Componentes"))
story.append(table(["Archivo", "Responsabilidad"], [["main.py", "Webhook, salud, deduplicación y coordinación."], ["bot.py", "Máquina de estados, carrito y checkout."], ["catalog.py", "Carga, búsqueda, categorías y recomendación."], ["backend.py", "Catálogo, seguimiento, login y pedidos."], ["whatsapp.py", "Texto, botones, listas, imágenes y lectura."], ["gemini.py", "Intención estructurada."], ["storage.py", "Pedidos JSONL con lock."], ["config.py", "Entorno tipado."]], [1.7*inch, 4.8*inch], 8))
story.append(H2("11.2 Flujo"))
story.append(code("menú -> comprar / asesor / seguimiento\ncomprar -> categorías / ofertas / volumen\ncatálogo -> producto -> cantidad -> carrito\ncarrito -> editar / eliminar / checkout\ncheckout -> nombre -> documento -> ciudad -> dirección -> notas -> confirmar\nconfirmar -> backend -> PENDIENTE/CANCELADO -> cliente y asesor"))
story.append(P("Gemini solo interpreta intención y respuesta; SalesBot valida. Las sesiones están en memoria y los pedidos locales en JSONL, por lo que para escalar se recomienda Redis, PostgreSQL y un trabajador de colas."))

story.append(H1("12. Flujos de negocio"))
for title, steps in [
    ("12.1 Alta de producto", ["Iniciar sesión como Admin o Inventario.", "Seleccionar depósito y código manual.", "Reutilizar datos si la referencia existe en historial.", "Registrar categoría, oferta y Por paca.", "Crear variantes con stock y atributos.", "Subir imágenes.", "Confirmar validaciones."]),
    ("12.2 Pedido web", ["Agregar variantes con stock.", "Impedir mezcla de depósitos.", "Capturar nombre, documento, celular y dirección.", "Enviar POST /pedidos.", "Bloquear, validar y descontar stock.", "Crear WEB/PENDIENTE/CANCELADO.", "Abrir WhatsApp con número de pedido."]),
    ("12.3 Venta presencial", ["Vendedor abre Registrar venta.", "Selecciona PRESENCIAL.", "Busca código o referencia.", "Captura cliente.", "Backend atribuye vendedor y depósito.", "Transacción descuenta inventario."]),
    ("12.4 Pago y despacho", ["Admin abre pedido.", "Cambia a PAGO_50 o PAGO_TOTAL.", "API crea guía si hay datos.", "Simulador avanza estados.", "Se imprime factura o guía.", "Cliente consulta seguimiento."]),
]:
    story.append(H2(title))
    story.extend(bullet(steps, numbered=True))

story.append(H1("13. Despliegue productivo"))
story.append(P("El entorno conocido usa Ubuntu 24 en 199.192.19.201. velandiax.com.co y www resuelven a esa IP. Los nameservers son dns1.registrar-servers.com y dns2.registrar-servers.com. Nginx sirve /var/www/VELANDIAX/velandiax-admin/dist; velandiax-api.service ejecuta Uvicorn en 127.0.0.1:8001 y /api actúa como proxy."))
story.append(H2("13.1 DNS"))
story.append(table(["Tipo", "Host", "Destino"], [["A", "@", "199.192.19.201"], ["CNAME", "www", "velandiax.com.co"]], [1.3*inch, 1.3*inch, 3.9*inch], 9))
story.append(H2("13.2 Instalación"))
story.append(code("sudo apt update\nsudo apt install -y git nginx python3 python3-venv python3-pip certbot python3-certbot-nginx\ncd /var/www\nsudo git clone https://github.com/Nicolas-ruizg/DISTRIBUIDORA-VELANDIAX.git\ncd DISTRIBUIDORA-VELANDIAX/DISTRIBUIDORA-VELANDIAX\npython3 -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt"))
story.append(H2("13.3 Actualización"))
story.append(code("cd /var/www/VELANDIAX\ngit status\ngit pull --ff-only\ncd DISTRIBUIDORA-VELANDIAX\nsource .venv/bin/activate\npip install -r requirements.txt\nsudo systemctl restart velandiax-api.service\ncd ../velandiax-admin\nnpm ci\nnpm run build\nsudo nginx -t && sudo systemctl reload nginx"))
story.append(H2("13.4 Diagnóstico"))
story.append(code("systemctl status velandiax-api.service --no-pager\njournalctl -u velandiax-api.service -f\nnginx -t\ntail -f /var/log/nginx/error.log\ncurl https://velandiax.com.co/api/productos"))

story.append(H1("14. Historial Git"))
history = git_history()
story.append(P(f"El historial contiene {len(history)} commits en main. No se encontraron tags ni ramas adicionales. El estado exacto de sincronización se incluye en Control del documento."))
story.append(table(["Fecha", "Commit", "Autor", "Descripción"], history, [1.0*inch, 0.8*inch, 1.2*inch, 3.5*inch], 7.5))
story.append(H2("14.1 Evolución funcional"))
commit_details = [
    ("fd62280", "Base full stack: API, esquema, productos, pedidos, envíos, usuarios, tienda y panel."),
    ("71f9925", "Guía de producción para Ubuntu, Nginx, systemd y HTTPS."),
    ("46381c3", "Home, favicon, datos de demostración y Pillow."),
    ("510db09", "Roles, códigos de cuenta, códigos manuales y protección por rol."),
    ("e740262", "Depósitos, trazabilidad, canal, cédula, filtros, usuarios y depósitos."),
    ("b348c8f", "Chatbot Meta/Gemini, catálogo, carrito, checkout y pruebas."),
    ("b6b845c", "PDF, guía térmica y etiquetas Por paca."),
]
story.append(table(["Commit", "Aporte"], commit_details, [1.0*inch, 5.5*inch], 8))
story.append(H2("14.2 Cambios locales pendientes"))
status_lines = git("status", "--short").splitlines()
story.append(P(f"El directorio de trabajo contiene {sum(1 for line in status_lines if line.startswith(' M'))} archivos modificados y {sum(1 for line in status_lines if line.startswith('??'))} rutas no rastreadas. Incluye inventario, endpoint público de pedido, corrección FOR UPDATE, TikTok, footer, WhatsApp, checkout, PDF y tipos. database/add_stock_variantes.sql y routes.zip todavía no están rastreados."))

story.append(H1("15. Calidad, pruebas y validación"))
story.append(table(["Componente", "Comando", "Resultado observado"], [["Backend", "python -m compileall -q .", "Correcto; advertencias de dependencias."], ["Frontend", "npm run build", "Correcto; 2.028 módulos."], ["Frontend", "Bundle", "JS principal 874,98 kB; advertencia >500 kB."], ["Chatbot", "python -m pytest -q", "No ejecutado: pytest no instalado en Python global y sin .venv."], ["Chatbot", "tests/", "Suite versionada para bot, webhook y WhatsApp."]], [1.2*inch, 2.0*inch, 3.3*inch], 8))
story.append(H2("15.1 Cobertura recomendada"))
story.extend(bullet(["Unitarias para totales, volumen y estados.", "Integración PostgreSQL para concurrencia/stock.", "Autorización por rol y depósito.", "Contratos entre Pydantic y TypeScript.", "E2E de producto a entrega.", "CI con compileall, pytest, npm ci, lint y build."]))

story.append(H1("16. Seguridad y privacidad"))
story.append(H2("16.1 Controles"))
story.extend(bullet(["bcrypt para contraseñas.", "JWT con expiración.", "RBAC en backend.", "CORS por entorno.", "Secretos en .env.", "Pydantic y restricciones SQL.", "Firma HMAC de Meta.", "Filtrado por depósito."]))
story.append(H2("16.2 Riesgos"))
story.append(table(["Prioridad", "Riesgo", "Recomendación"], [["Alta", "POST /pedidos público descuenta stock.", "Rate limit, CAPTCHA, idempotencia y monitoreo."], ["Alta", "Seguimiento por celular.", "OTP, limitar campos y rate limit."], ["Alta", "Cambios críticos sin commit.", "Revisar, probar y confirmar."], ["Alta", "Migraciones manuales/schema sin stock.", "Alembic y reconciliación."], ["Media", "JWT en localStorage.", "CSP y evaluar cookie HttpOnly."], ["Media", "Simulador en cada worker.", "Trabajador único/cola."], ["Media", "Chatbot en memoria.", "Redis e idempotencia persistente."], ["Media", "DELETE físico de pedidos/categorías.", "Política de retención."], ["Baja", "Bundle grande.", "Lazy loading y code splitting."]], [0.7*inch, 2.4*inch, 3.4*inch], 7.5))

story.append(H1("17. Operación y mantenimiento"))
story.append(H2("17.1 Respaldo"))
story.append(code("pg_dump -Fc -U velandiax_user -h 127.0.0.1 velandiax_db > velandiax_YYYYMMDD.dump\npg_restore --clean --if-exists -U velandiax_user -d velandiax_db velandiax_YYYYMMDD.dump"))
story.append(H2("17.2 Lista de despliegue"))
story.extend(bullet(["Git limpio y commit identificado.", "Respaldo restaurable.", "Migraciones aplicadas una vez.", "Dependencias reproducibles.", "Servicios activos.", "Build con VITE_API_URL=/api.", "nginx -t y TLS correctos.", "Pruebas de login, catálogo, pedido, stock, pago, guía y seguimiento.", "Monitoreo de logs."]))

story.append(H1("18. Hallazgos y deuda técnica"))
story.extend(bullet(["schema_final.sql no incluye stock.", "precio_mayorista y es_mayorista siguen presentes.", "paquete_estatico conserva nomenclatura anterior.", "No existe Alembic.", "GET /admin/categorias reutiliza lectura pública.", "Lecturas admin de producto permiten cualquier autenticado.", "El simulador se duplicaría con múltiples workers.", "El seed puede ser destructivo.", "No hay CI/CD, tags ni releases.", "README frontend continúa como plantilla Vite.", "Persisten textos históricos con codificación incorrecta."]))

story.append(H1("19. Hoja de ruta"))
story.append(table(["Horizonte", "Acciones"], [["Inmediato", "Commit local; integrar stock; retirar routes.zip; pruebas chatbot; respaldo."], ["1-2 semanas", "Alembic, rate limit, idempotencia, auditoría y CI."], ["1 mes", "Redis, trabajador logístico, observabilidad y code splitting."], ["2-3 meses", "Facturación formal, impresión administrada, códigos de barras y movimientos."], ["Continuo", "Dependencias, OWASP, backups probados y documentación por release."]], [1.3*inch, 5.2*inch], 8))

add_section(story, "20. Conclusiones", ["VELANDIAX ya es una solución operativa y no solo una maqueta: integra dominio comercial, persistencia, inventario, roles, depósitos, canales web/WhatsApp, seguimiento e impresión. La arquitectura es comprensible y adecuada para el tamaño actual.", "El riesgo principal es operativo: funcionalidades críticas permanecen sin commit y el esquema consolidado no representa completamente el modelo vigente. La prioridad es reconciliar migraciones, confirmar cambios, endurecer endpoints públicos y automatizar validación y despliegue."])

story.append(H1("Referencias"))
references = [
    "FastAPI. (s. f.). FastAPI documentation. Recuperado el 11 de noviembre de 2026, de https://fastapi.tiangolo.com/",
    "Git. (s. f.). Git reference. https://git-scm.com/docs",
    "Google. (2026). Gemini API reference. https://ai.google.dev/api",
    "Meta Platforms, Inc. (s. f.). WhatsApp Cloud API. https://developers.facebook.com/docs/whatsapp/cloud-api/",
    "Open Worldwide Application Security Project. (2021). OWASP Top 10:2021. https://owasp.org/Top10/",
    "PostgreSQL Global Development Group. (2026). JSON types. https://www.postgresql.org/docs/current/datatype-json.html",
    "React Team. (2026). React reference overview. https://react.dev/reference/react",
    "SQLAlchemy authors. (2026). SQLAlchemy 2.0 documentation. https://docs.sqlalchemy.org/en/20/",
    "Vite contributors. (2026). Getting started. https://vite.dev/guide/",
    "Ruiz Giraldo, N. (2026). DISTRIBUIDORA-VELANDIAX [Código fuente]. GitHub. https://github.com/Nicolas-ruizg/DISTRIBUIDORA-VELANDIAX",
]
story.extend(Paragraph(esc(item), styles["reference"]) for item in references)

story.append(H1("Apéndice A. Variables de entorno"))
env_rows = [["Backend", "DB_HOST, DB_PORT, DB_NAME", "PostgreSQL."], ["Backend", "DB_USER, DB_PASSWORD, DB_SSLMODE", "Credenciales/TLS."], ["Backend", "JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS", "Tokens."], ["Backend", "CORS_ORIGINS", "Orígenes."], ["Backend", "ENVIO_INTERVALO_SEGUNDOS", "Simulador."], ["Backend", "SUPABASE_URL, BUCKET, STORAGE_KEY", "Imágenes."], ["Frontend", "VITE_API_URL", "Base API."], ["Chatbot", "WHATSAPP_TOKEN, PHONE_NUMBER_ID", "Meta."], ["Chatbot", "VERIFY_TOKEN, META_APP_SECRET", "Webhook."], ["Chatbot", "BACKEND_API_URL/EMAIL/PASSWORD", "Integración."], ["Chatbot", "BACKEND_CREATE_ORDERS", "Pedidos."], ["Chatbot", "GEMINI_API_KEY, GEMINI_MODEL", "IA."], ["Chatbot", "STORE_URL, VOLUME_MIN_QUANTITY", "Negocio."]]
story.append(table(["Módulo", "Variable", "Propósito"], env_rows, [1.1*inch, 3.5*inch, 1.9*inch], 7.5))

story.append(H1("Apéndice B. Estados"))
story.append(table(["Entidad", "Valores"], [["Producto/variante/imagen", "ACTIVO, INACTIVO"], ["Rol", "ADMINISTRADOR, VENDEDOR, INVENTARIO"], ["Canal", "PRESENCIAL, WEB"], ["Pago", "CANCELADO, PAGO_50, PAGO_TOTAL"], ["Tipo envío", "CONTRAENTREGA, GRATIS o null"], ["Logística", "PENDIENTE, PREPARANDO, DESPACHADO, EN_TRANSITO, ENTREGADO"], ["Previstos", "DEVUELTO, CANCELADO"]], [2.2*inch, 4.3*inch], 8))

story.append(H1("Apéndice C. Inventario de archivos rastreados"))
tracked = git("ls-files").splitlines()
file_rows = [[str(index), path] for index, path in enumerate(tracked, start=1)]
story.append(P(f"Git rastrea {len(file_rows)} archivos. El listado permite verificar el alcance exacto de esta versión."))
story.append(table(["N.º", "Ruta"], file_rows, [0.6*inch, 5.9*inch], 7))

document = APADocument(str(OUT))
document.multiBuild(story)
print(f"PDF={OUT}")
print(f"BYTES={OUT.stat().st_size}")
