"""HTML primitives shared by report sections."""

from __future__ import annotations

import textwrap
from html import escape


def _badge(level: str, text: str) -> str:
    return f'<span class="badge {escape(level)}">{escape(text, quote=False)}</span>'


def _table(headers: list[str], rows: list[list[str]]) -> str:
    ths = "".join(f"<th>{escape(h, quote=False)}</th>" for h in headers)
    trs = "".join(
        f"<tr>{''.join(f'<td>{escape(str(c), quote=False)}</td>' for c in row)}</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>"


def _kv_table(data: dict) -> str:
    return _table(["Key", "Count"], [[k, str(v)] for k, v in data.items()])


def _ul(items: list) -> str:
    return (
        "<ul>"
        + "".join(f"<li class='mono'>{escape(str(h), quote=False)}</li>" for h in items)
        + "</ul>"
    )


def _section(title: str, badge_html: str, body_html: str, auto_open: bool = False) -> str:
    open_attr = ' data-open="1"' if auto_open else ""
    return textwrap.dedent(f"""
    <div class="section">
      <div class="section-header">
        <h2>{escape(title, quote=False)}</h2>{badge_html}
      </div>
      <div class="section-body"{open_attr}>{body_html}</div>
    </div>
    """)
