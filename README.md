# obsidian-tools

Tools for working with [Obsidian](https://obsidian.md/) vaults.

## Install

Install manually (this package is not available on PyPI yet):

```sh
git clone git@github.com:seeM/obsidian-tools.git
cd obsidian-tools
pip install -e .
```

## Read a vault

Read a vault to a list of note dictionaries.

```pycon
>>> from obsidian import read_vault
>>> notes = read_vault("./path/to/vault/")
>>> notes[0]
{'name': 'Title of my note',
 'vault_dir': PosixPath('./path/to/vault'),
 'path': PosixPath('./path/to/vault/Title of my note.md'),
 'lines': ['First line', 'A link to [[Another note]]']
 'links': ['Another note'],
 'references': ['A third note']}
```

## Trash empty notes

_**Warning:** Running this function with `dry_run=False` makes changes to your underlying note files. Don't use this if you don't have your vault backed up!_

Move empty note files (ignoring whitespace) to the Obsidian trash directory (`{vault_dir}/.trash`).

```pycon
>>> from obsidian import trash_empty_notes
>>> nonempty_notes = trash_empty_notes(notes, dry_run=False)
```

## Remove invalid links

Return a new list of notes without invalid links (a link is considered invalid if it points to a note that doesn't exist). This doesn't yet change the underlying note files.

```pycon
>>> from obsidian import remove_invalid_links
>>> notes_with_valid_links = remove_invalid_links(notes)
```

## Roadmap

Rough ideas for next steps.

- Apply the result of `remove_invalid_links` to underlying files.
- Feel like there must be some useful analysis we could do but not sure what yet.
- Given the sensitive nature of notes, it might be useful to have a staged approach to making changes to underlying files (e.g. `trash_empty_notes` and `remove_invalid_links`).
    Something like terraform's `plan` and `apply`.
    Perhaps functions like `trash_empty_notes` could return a new list of notes.
    Then we could have a function that takes a pair of notes lists and calculates a diff e.g. `[{"type": "trash", "object": "note_0"}]`.
    Our `plan` would return this diff.
    Finally, we'd have an `apply` endpoint that actually makes the changes on disk.
