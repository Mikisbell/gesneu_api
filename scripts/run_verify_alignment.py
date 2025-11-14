#!/usr/bin/env python3
"""
Script de conveniencia para verificar la alineación de modelos SQLModel
contra el esquema PostgreSQL documentado en ESQUEMA_COMPLETO_BD.md.

Uso:
  poetry run python scripts/run_verify_alignment.py
  # o si se configuró el script en Poetry
  poetry run verify-alignment
"""
from __future__ import annotations

import sys
from typing import Any, Dict, TypedDict, List, Callable, cast

try:
    import verify_complete_alignment as v
except Exception as e:
    print(f"❌ No se pudo importar verify_complete_alignment: {e}")
    sys.exit(2)


def main() -> int:
    class AlignmentResult(TypedDict):
        alignment_score: float
        missing_tables: List[str]
        extra_tables: List[str]
        total_real_tables: int
        total_code_tables: int

    # Tipar explícitamente la función importada para evitar no-untyped-call de mypy
    verify_alignment_func: Callable[[], AlignmentResult | None] = cast(
        Callable[[], AlignmentResult | None], v.verify_alignment
    )

    result: AlignmentResult | None = verify_alignment_func()
    if not result:
        return 1
    ok = (
        result.get("alignment_score") == 100
        and not result.get("extra_tables")
        and not result.get("missing_tables")
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
