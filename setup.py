# -*- coding: utf-8 -*-
import json
import os
import random
from pprint import pprint

# ---------- Fonctions de sélection de fichiers ----------
def get_json_files(dossier='.'):
    """Retourne la liste des fichiers .json dans le dossier donné."""
    if not os.path.isdir(dossier):
        print(f"❌ Le dossier '{dossier}' n'existe pas.")
        return []
    fichiers = [f for f in os.listdir(dossier) if f.endswith('.json') and os.path.isfile(os.path.join(dossier, f))]
    return sorted(fichiers)

def afficher_liste_fichiers(fichiers, dossier='.'):
    """Affiche une liste numérotée des fichiers."""
    if not fichiers:
        print("Aucun fichier JSON trouvé.")
        return
    print("\nFichiers JSON disponibles :")
    for i, f in enumerate(fichiers, 1):
        print(f"  {i}. {f}")

def choisir_fichier(question, dossier='.', multi=False, obligatoire=True):
    """
    Permet de sélectionner un ou plusieurs fichiers JSON par numéro.
    - question : message affiché à l'utilisateur.
    - dossier : dossier à scanner.
    - multi : si True, retourne une liste de chemins ; sinon un seul chemin.
    - obligatoire : si True, redemande tant qu'aucun choix valide n'est fait.
    Retourne : chemin (str) ou liste de chemins.
    """
    fichiers = get_json_files(dossier)
    if not fichiers:
        print("❌ Aucun fichier JSON disponible.")
        return None if not multi else []

    afficher_liste_fichiers(fichiers, dossier)
    
    while True:
        saisie = input(f"{question} (entrez le numéro" + ("(x) ou plage (ex: 1-3,5)" if multi else "") + ") : ").strip()
        if not saisie and not obligatoire:
            return None if not multi else []
        
        if not multi:
            try:
                idx = int(saisie) - 1
                if 0 <= idx < len(fichiers):
                    return os.path.join(dossier, fichiers[idx])
                else:
                    print(f"❌ Numéro invalide. Choisissez entre 1 et {len(fichiers)}.")
            except ValueError:
                print("❌ Veuillez entrer un nombre valide.")
        else:
            # Sélection multiple : on accepte des numéros séparés par des virgules ou des plages (ex: 1-3,5)
            indices = []
            parts = saisie.replace(' ', '').split(',')
            valide = True
            for part in parts:
                if '-' in part:
                    try:
                        deb, fin = map(int, part.split('-'))
                        if deb < 1 or fin > len(fichiers) or deb > fin:
                            print(f"❌ Plage invalide : {part}")
                            valide = False
                            break
                        indices.extend(range(deb-1, fin))
                    except:
                        print(f"❌ Plage mal formatée : {part}")
                        valide = False
                        break
                else:
                    try:
                        idx = int(part) - 1
                        if 0 <= idx < len(fichiers):
                            indices.append(idx)
                        else:
                            print(f"❌ Numéro {part} hors plage.")
                            valide = False
                            break
                    except ValueError:
                        print(f"❌ '{part}' n'est pas un nombre valide.")
                        valide = False
                        break
            if valide and indices:
                # Supprimer les doublons et trier
                indices = sorted(set(indices))
                return [os.path.join(dossier, fichiers[i]) for i in indices]
            else:
                print("Veuillez réessayer.")
                continue

# ---------- Fonctions existantes (légèrement adaptées) ----------
def load_json_file(filepath):
    try:
        with open(filepath, 'r', encoding="utf-8", errors="ignore") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors de la lecture de {filepath} : {e}")
        return []

def save_json_file(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Fichier sauvegardé : {filepath}")
    except Exception as e:
        print(f"Erreur lors de l'écriture de {filepath} : {e}")

def find_duplicates(data):
    seen = set()
    duplicates = []
    unique = []
    for entry in data:
        uid = entry.get('uid')
        if uid is None:
            continue  # ou gérer autrement
        if uid in seen:
            duplicates.append(entry)
        else:
            seen.add(uid)
            unique.append(entry)
    return unique, duplicates

def compare_files(file1, file2):
    data1 = load_json_file(file1)
    data2 = load_json_file(file2)
    if not data1 or not data2:
        print("❌ Un des fichiers est vide ou invalide.")
        return

    uids1 = {entry['uid'] for entry in data1 if 'uid' in entry}
    uids2 = {entry['uid'] for entry in data2 if 'uid' in entry}

    common = uids1.intersection(uids2)
    unique_uids1 = uids1 - uids2
    unique_uids2 = uids2 - uids1

    print(f"\nComparaison entre {file1} et {file2}")
    print(f"Total fichier 1 : {len(data1)} {[file1]}")
    print(f"Total fichier 2 : {len(data2)} {[file2]}")
    print(f"UIDs communs : {len(common)}")
    print(f"UIDs uniques à {file1} : {len(unique_uids1)}")
    print(f"UIDs uniques à {file2} : {len(unique_uids2)}")

    unique_entries1 = [entry for entry in data1 if entry.get('uid') in unique_uids1]
    unique_entries2 = [entry for entry in data2 if entry.get('uid') in unique_uids2]

    out1 = os.path.splitext(file1)[0] + "_unique.json"
    out2 = os.path.splitext(file2)[0] + "_unique.json"
    save_json_file(out1, unique_entries1)
    save_json_file(out2, unique_entries2)

def clean_file(file_path):
    data = load_json_file(file_path)
    unique, duplicates = find_duplicates(data)
    if duplicates:
        new_path = file_path.replace('.json', '_cleaned.json')
        save_json_file(new_path, unique)
        print(f"\n{len(duplicates)} doublon(s) supprimé(s). Fichier nettoyé : {new_path}")
    else:
        print("\nAucun doublon trouvé.")

def count_uids(file_path):
    data = load_json_file(file_path)
    unique, duplicates = find_duplicates(data)
    print(f"\nAnalyse de {file_path} :")
    print(f"Total d'entrées : {len(data)}")
    print(f"UIDs uniques   : {len(unique)}")
    print(f"Doublons       : {len(duplicates)}")
    if duplicates:
        print("Doublons trouvés :")
        for dup in duplicates:
            print(f"  {dup}")

def search_uid(uid, filepaths):
    found = False
    for path in filepaths:
        data = load_json_file(path)
        for entry in data:
            if entry.get('uid') == uid:
                print(f"✅ UID trouvé dans {path} : {entry}")
                found = True
    if not found:
        print("❌ UID non trouvé dans les fichiers sélectionnés.")

def merge_files(filepaths, output_path):
    combined = []
    for path in filepaths:
        data = load_json_file(path)
        if isinstance(data, list):
            combined.extend(data)
        else:
            print(f"⚠️ {path} n'est pas une liste JSON, ignoré.")
    unique, duplicates = find_duplicates(combined)
    save_json_file(output_path, unique)
    print(f"\nFusion terminée. {len(unique)} entrées uniques sauvegardées dans {output_path}")

def export_uids(file_path, output_txt):
    data = load_json_file(file_path)
    uids = [entry.get('uid') for entry in data if entry.get('uid')]
    try:
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(uids))
        print(f"UIDs exportés dans : {output_txt}")
    except Exception as e:
        print(f"Erreur d’export : {e}")

def find_duplicate_passwords(file_path):
    data = load_json_file(file_path)
    passwords = {}
    duplicates = []
    for entry in data:
        pwd = entry.get('password')
        if pwd is None:
            continue
        if pwd in passwords:
            duplicates.append(entry)
        else:
            passwords[pwd] = entry.get('uid')
    print(f"\nNombre de mots de passe en double : {len(duplicates)}")
    for d in duplicates:
        print(f"UID : {d.get('uid')} utilise un mot de passe déjà existant.")

def generate_custom_file(input_file, output_file, number):
    data = load_json_file(input_file)
    if not data:
        print("Le fichier source est vide ou introuvable.")
        return
    if number > len(data):
        print(f"⚠️ Le nombre demandé ({number}) est supérieur au nombre d'entrées disponibles ({len(data)}). Le fichier contiendra toutes les entrées disponibles.")
        number = len(data)
    selected_entries = random.sample(data, number)
    save_json_file(output_file, selected_entries)
    print(f"{number} comptes générés dans : {output_file}")

def merge_folder(folder_path, output_path):
    combined = []
    if not os.path.isdir(folder_path):
        print("❌ Dossier invalide.")
        return
    files = [f for f in os.listdir(folder_path) if f.endswith(".json") and os.path.isfile(os.path.join(folder_path, f))]
    if not files:
        print("❌ Aucun fichier JSON trouvé dans le dossier.")
        return
    print(f"📂 {len(files)} fichiers trouvés. Fusion en cours...")
    for file in files:
        full_path = os.path.join(folder_path, file)
        data = load_json_file(full_path)
        if isinstance(data, list):
            combined.extend(data)
        else:
            print(f"⚠️ Ignoré (format invalide) : {file}")
    unique, duplicates = find_duplicates(combined)
    save_json_file(output_path, unique)
    print(f"\n✅ Fusion terminée")
    print(f"📊 Total combiné : {len(combined)}")
    print(f"🧹 Doublons supprimés : {len(duplicates)}")
    print(f"💾 Résultat : {output_path}")

# ---------- Menu principal modifié ----------
def main():
    while True:
        print("\n===== MENU =====")
        print("1. Comparer deux fichiers JSON")
        print("2. Vérifier les doublons dans un fichier")
        print("3. Nettoyer un fichier (retirer les doublons)")
        print("4. Compter les UID uniques et doublons")
        print("5. Rechercher un UID dans plusieurs fichiers")
        print("6. Fusionner plusieurs fichiers sans doublons")
        print("7. Exporter les UIDs dans un fichier texte")
        print("8. Trouver les mots de passe en double")
        print("9. Quitter")
        print("10. Générer un fichier JSON avec un nombre choisi de comptes")
        print("11. Fusionner tous les JSON d’un dossier")

        choix = input("\nVotre choix : ").strip()

        if choix == '1':
            f1 = choisir_fichier("Choisissez le premier fichier")
            if not f1:
                continue
            f2 = choisir_fichier("Choisissez le second fichier")
            if not f2:
                continue
            compare_files(f1, f2)

        elif choix == '2':
            f = choisir_fichier("Choisissez un fichier à vérifier")
            if not f:
                continue
            data = load_json_file(f)
            _, duplicates = find_duplicates(data)
            if duplicates:
                print(f"{len(duplicates)} doublon(s) trouvé(s) dans {f}")
            else:
                print("Aucun doublon trouvé.")

        elif choix == '3':
            f = choisir_fichier("Choisissez un fichier à nettoyer")
            if not f:
                continue
            clean_file(f)

        elif choix == '4':
            f = choisir_fichier("Choisissez un fichier à analyser")
            if not f:
                continue
            count_uids(f)

        elif choix == '5':
            uid = input("UID à rechercher : ").strip()
            if not uid:
                print("UID vide, annulation.")
                continue
            fichiers = choisir_fichier("Sélectionnez les fichiers à parcourir (multi)", multi=True)
            if not fichiers:
                continue
            search_uid(uid, fichiers)

        elif choix == '6':
            fichiers = choisir_fichier("Sélectionnez les fichiers à fusionner (multi)", multi=True)
            if not fichiers:
                continue
            out = input("Nom du fichier de sortie (ex: merged.json) : ").strip()
            if not out:
                print("Nom de sortie vide, annulation.")
                continue
            merge_files(fichiers, out)

        elif choix == '7':
            f = choisir_fichier("Choisissez un fichier JSON")
            if not f:
                continue
            out = input("Fichier de sortie (.txt) : ").strip()
            if not out:
                print("Nom de sortie vide, annulation.")
                continue
            export_uids(f, out)

        elif choix == '8':
            f = choisir_fichier("Choisissez un fichier à vérifier")
            if not f:
                continue
            find_duplicate_passwords(f)

        elif choix == '9':
            print("Au revoir !")
            break

        elif choix == '10':
            f = choisir_fichier("Choisissez le fichier source")
            if not f:
                continue
            output = input("Nom du fichier de sortie (ex: generated.json) : ").strip()
            if not output:
                print("Nom de sortie vide, annulation.")
                continue
            try:
                n = int(input("Nombre de comptes à générer : ").strip())
            except ValueError:
                print("Veuillez entrer un nombre valide.")
                continue
            generate_custom_file(f, output, n)

        elif choix == '11':
            dossier = input("Chemin du dossier à scanner (vide pour le dossier courant) : ").strip()
            if not dossier:
                dossier = '.'
            out = input("Nom du fichier de sortie (ex: merged.json) : ").strip()
            if not out:
                print("Nom de sortie vide, annulation.")
                continue
            merge_folder(dossier, out)

        else:
            print("Choix invalide, réessayez.")

if __name__ == "__main__":
    main()