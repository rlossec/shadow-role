"""CLI tool to generate the tree of a directory. """

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Iterator, Sequence


DEFAULT_IGNORED_FILES: tuple[str, ...] = (
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "node_modules",
    "uv.lock",
    "__init__.py",
)


def list_directory_content(directory: Path, ignores: Sequence[str]) -> list[Path]:
    def sort_key(element: Path) -> tuple[int, str]:
        return (0 if element.is_dir() else 1, element.name.lower())

    ignores_set = {nom.lower() for nom in ignores}

    return sorted(
        (
            entry
            for entry in directory.iterdir()
            if entry.name.lower() not in ignores_set and not entry.name.startswith(".")
        ),
        key=sort_key,
    )


def generate_tree_lines(
    directory: Path, ignores: Sequence[str], prefix: str, is_last: bool
) -> Iterator[str]:
    marker = "└──" if is_last else "├──"
    if directory.is_dir():
        yield f"{prefix}{marker} {directory.name}/"
    else:
        yield f"{prefix}{marker} {directory.name}"

    if directory.is_dir():
        children = list_directory_content(directory, ignores)
        new_prefix = f"{prefix}{'    ' if is_last else '│   '}"
        for index, child in enumerate(children):
            last_child = index == len(children) - 1
            yield from generate_tree_lines(
                child, ignores, new_prefix, last_child
            )


def build_tree(root: Path, ignores: Sequence[str]) -> str:
    lines = [f"{root.name}/"]
    children = list_directory_content(root, ignores)
    for index, child in enumerate(children):
        last_child = index == len(children) - 1
        lines.extend(generate_tree_lines(child, ignores, "", last_child))
    return "\n".join(lines)


def generate_tree(
    source: Path, destination: Path | None = None, ignores_suppl: Iterable[str] | None = None
) -> Path:
    if not source.exists() or not source.is_dir():
        raise NotADirectoryError(f"Le chemin {source} n'est pas un dossier valide.")

    ignores = list(DEFAULT_IGNORED_FILES)
    if ignores_suppl:
        ignores.extend(ignores_suppl)

    content = build_tree(source, ignores)

    if destination is None:
        scripts_dir = source / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        destination = scripts_dir / f"arborescence_{source.name}.txt"
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(content, encoding="utf-8")
    return destination


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Génère un fichier texte contenant l'arborescence d'un dossier donné."
    )
    parser.add_argument(
        "source",
        help="Chemin du dossier dont on souhaite générer l'arborescence.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Chemin du fichier de sortie. Par défaut, utilise scripts/arborescence_<nom>.txt dans le dossier source.",
    )
    parser.add_argument(
        "--ignorer",
        action="append",
        default=[],
        help="Nom de dossier ou fichier à ignorer (option répétable).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    source = Path(args.source).resolve()
    destination = Path(args.output).resolve() if args.output else None

    file = generate_tree(source, destination)
    print(f"Arborescence générée dans {file}")


if __name__ == "__main__":
    main()

