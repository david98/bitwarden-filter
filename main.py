import json
import argparse
import logging
import re

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-v", "--vault", help="<Required> Vault file", required=True)
    argParser.add_argument("-o", "--output", help="<Required> Output file", required=True)
    argParser.add_argument("-f", "--folders", action="append", help="<Required> Folders to include", required=True)
    argParser.add_argument("-p", "--passwords", action="append", help="Passwords to filter out (can be a regex)")

    args = argParser.parse_args()

    password_regular_expressions = []

    if args.passwords:
        password_regular_expressions = list(map(lambda p: re.compile(p), args.passwords))

    with open(args.vault) as f:
        vault = json.load(f)
        filtered_vault = {'encrypted': vault['encrypted'], 'folders': [], 'items': []}
        logging.info(f"Vault loaded: {len(vault['folders'])} folders and {len(vault['items'])} items.")
        folders_to_include = list(filter(lambda fo: fo['name'] in args.folders, vault['folders']))
        filtered_vault['folders'] = folders_to_include
        ids = list(map(lambda fo: fo['id'], folders_to_include))
        items_to_include = list(filter(lambda i: i is not None and i['folderId'] in ids, vault['items']))
        if args.passwords:
            for i in items_to_include:
                if any(map(lambda r: r.match(i['login']['password']), password_regular_expressions)):
                    i['name'] += " - <PASSWORD REDACTED>"
                    i['login']['password'] = "<redacted>"
        filtered_vault['items'] = items_to_include
        logging.info("Filtering complete. Writing JSON.")
        with open(args.output, mode="w") as o:
            json.dump(filtered_vault, fp=o, indent=4, sort_keys=True)
        logging.info("JSON written. Exiting.")



