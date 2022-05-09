import os
import re
from pathlib import Path


def read_vault(vault_dir, include_trash=False, verbose=False):
    vault_dir = Path(vault_dir)

    # First pass to read all notes in the vault

    notes = []
    for dirpath, _, filenames in os.walk(vault_dir):
        if dirpath.endswith(".trash") and not include_trash:
            continue
        for filename in filenames:
            path = vault_dir / dirpath / filename
            if path.suffix != ".md":
                continue

            name = str(path.relative_to(vault_dir))[:-3]
            with open(path) as f:
                lines = f.read().splitlines()
            links = []
            for line_number, line in enumerate(lines):
                link_pattern = r"\[\[([^\]]*)\]\]"
                for match in re.finditer(link_pattern, line):
                    link = {
                        "from": name,
                        "to": match.groups()[0],
                        "span": match.span(),
                        "line_number": line_number,
                    }
                    links.append(link)

            note = {
                "name": name,
                "vault_dir": vault_dir,
                "path": path,
                "lines": lines,
                "links": links,
                "references": [],
            }
            notes.append(note)

    assert len([x["name"] for x in notes]) == len(
        set(x["name"] for x in notes)
    ), "Unexpected error: note names should be unique."

    # Second pass to update note['links'] and note['references'] to replace
    # note names to pointers to note objects

    notes_map = {note["name"]: note for note in notes}
    for from_ in notes:
        for link in from_["links"]:
            to_name = link["to"]
            to = notes_map.get(to_name)
            is_valid = to is not None
            if is_valid:
                assert to is not None, "make lsp happy"
                to["references"].append(from_["name"])
            else:
                if verbose:
                    print(f"Invalid link: {from_['name']} -> {to_name}")

            link["is_valid"] = is_valid

    return notes


def trash_empty_notes(notes, dry_run=True):
    nonempty_notes = []
    for note in notes:
        if note["lines"]:
            nonempty_notes.append(note)
            continue
        if dry_run:
            print(f"Dry run. Would trash note: {note}.")
        else:
            print(f"Trashing note: {note}.")
            trash_note(note)
    return nonempty_notes


def remove_invalid_links(notes):
    new_notes = []
    for from_ in notes:
        links = []
        new_from = from_
        for link in from_["links"]:
            if link["is_valid"]:
                links.append(link)
            else:
                lines = from_["lines"]
                line_number = link["line_number"]
                start, end = link["span"]

                before = lines[:line_number]
                line = lines[line_number]
                after = lines[line_number + 1:]
                new_line = line[:start] + line[start+2:end-2] + line[end:]
                new_lines = before + [new_line] + after

                new_from = {**new_from, "lines": new_lines}
        new_from = {**new_from, "links": links}
        new_notes.append(new_from)
    return new_notes


def trash_note(note):
    return {
        **note,
        "path": note["path"].rename(note["vault_dir"] / ".trash" / note["path"].name),
    }
