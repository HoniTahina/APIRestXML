from flask import Blueprint, request, jsonify
from .utils import parse_xml, modify_xml
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from lxml import etree
import os

main_blueprint = Blueprint('main', __name__)


# Point de terminaison pour soumettre un fichier XML
@main_blueprint.route('/upload', methods=['POST'])
def upload_xml():
    file = request.files.get('file')
    if not file:
        return jsonify({"message": "Aucun fichier fourni."}), 400

    if file.filename == '':
        return jsonify({"message": "Aucun fichier sélectionné."}), 400

    if not file.filename.endswith('.xml'):
        return jsonify({"message": "Format de fichier invalide. Seuls les fichiers XML sont acceptés."}), 400

    # Lire le contenu du fichier
    xml_data = file.read()
    # Enregistrer le fichier sur le disque
    file_path = f'uploads/{file.filename}'
    file.save(file_path)
    # Log du contenu pour vérifier
    print(f"XML data received: {xml_data}")

    if not xml_data.strip():
        return jsonify({"message": "Le fichier XML est vide"}), 400

    try:
        # Parser le contenu XML
        parsed_xml = parse_xml(xml_data)
        return jsonify({"message": "XML file uploaded successfully", "data": parsed_xml}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# Point de terminaison pour transformer un fichier XML avec XSLT
@main_blueprint.route('/transform', methods=['POST'])
def transform():
        try:
            # Vérifier si un fichier a été envoyé
            if "file" not in request.files:
                return jsonify({"erreur": "Aucun fichier envoyé"}), 400

            file = request.files["file"]

            # Vérifier si le fichier a un nom valide
            if file.filename == "":
                return jsonify({"erreur": "Nom de fichier invalide"}), 400

            # Sauvegarder le fichier XML uploadé temporairement dans 'uploads'
            filename = secure_filename(file.filename)
            xml_path = os.path.join("uploads", filename)
            file.save(xml_path)

            # Spécifier le chemin de la feuille XSLT
            xslt_path = "transform.xslt"
            if not os.path.exists(xslt_path):
                return jsonify({"erreur": "La feuille XSLT est introuvable"}), 500

            # Charger et appliquer la transformation
            xml_tree = etree.parse(xml_path)
            xslt_tree = etree.parse(xslt_path)
            transform = etree.XSLT(xslt_tree)

            # Effectuer la transformation
            result_tree = transform(xml_tree)

            # Sauvegarder le fichier transformé dans 'modify'
            transformed_filename = f"transformed_{filename.rsplit('.', 1)[0]}.html"
            transformed_path = os.path.join("modify", transformed_filename)
            with open(transformed_path, "w", encoding="utf-8") as transformed_file:
                transformed_file.write(str(result_tree))

            # Retourner une réponse avec les détails du fichier transformé
            return jsonify({
                "message": "Transformation réussie",
                "fichier_transforme": transformed_filename,
                "chemin_complet": transformed_path
            }), 200
        except Exception as e:
            return jsonify({"erreur": f"Erreur lors de la transformation : {str(e)}"}), 500


# Point de terminaison pour modifier un élément XML
@main_blueprint.route('/modify', methods=['POST'])
def modify():
    xml_file = request.files.get('xml')  # Récupérer le fichier XML
    element = request.form.get('element')  # Récupérer l'élément depuis form-data
    new_value = request.form.get('value')  # Récupérer la nouvelle valeur depuis form-data

    if not xml_file or not element or not new_value:
        return jsonify({"message": "Fichier XML, élément et nouvelle valeur requis"}), 400

    xml_data = xml_file.read()
    try:
        modified_xml = modify_xml(xml_data, element, new_value)
        # Sauvegarde dans le dossier "modify"
        output_filename = f"modify/{xml_file.filename}"  # Nom du fichier modifié
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(modified_xml)

        return jsonify({"message": f"XML modifié avec succès et sauvegardé dans '{output_filename}'"}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la modification : {str(e)}"}), 500

@main_blueprint.route('/add', methods=['POST'])
def add_book():
    xml_file = request.files.get('xml')  # Fichier XML
    title = request.form.get('title')  # Titre du livre
    lang = request.form.get('lang')  # Langue
    author = request.form.get('author')  # Auteur
    price = request.form.get('price')  # Prix

    if not xml_file or not title or not lang or not author or not price:
        return jsonify({"message": "Fichier XML, titre, langue, auteur et prix requis"}), 400

    try:
        # Lire le fichier XML
        xml_data = xml_file.read()
        root = etree.fromstring(xml_data)

        # Créer un nouvel élément <book>
        new_book = etree.Element("book")
        title_element = etree.SubElement(new_book, "title", lang=lang)
        title_element.text = title
        author_element = etree.SubElement(new_book, "author")
        author_element.text = author
        price_element = etree.SubElement(new_book, "price")
        price_element.text = price

        # Ajouter le nouveau livre au catalogue
        root.append(new_book)

        # Convertir en XML
        modified_xml = etree.tostring(root, pretty_print=True, encoding="unicode")

        # Sauvegarder le fichier modifié
        output_filename = f"modify/{xml_file.filename}"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(modified_xml)

        return jsonify({"message": f"Livre ajouté avec succès et sauvegardé dans '{output_filename}'"}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de l'ajout : {str(e)}"}), 500

@main_blueprint.route('/delete', methods=['POST'])
def delete_book():
    xml_file = request.files.get('xml')  # Récupérer le fichier XML
    title_to_delete = request.form.get('title')  # Titre du livre à supprimer

    if not xml_file or not title_to_delete:
        return jsonify({"message": "Fichier XML et titre requis pour la suppression"}), 400

    try:
        # Lire le fichier XML
        xml_data = xml_file.read()
        root = etree.fromstring(xml_data)

        # Trouver et supprimer le livre avec le titre spécifié
        books = root.findall("book")
        book_found = False
        for book in books:
            title = book.find("title")
            if title is not None and title.text.strip() == title_to_delete:
                root.remove(book)
                book_found = True
                break

        if not book_found:
            return jsonify({"message": f"Livre avec le titre '{title_to_delete}' introuvable"}), 404

        # Convertir en XML
        modified_xml = etree.tostring(root, pretty_print=True, encoding="unicode")

        # Sauvegarder le fichier modifié
        output_filename = f"modify/{xml_file.filename}"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(modified_xml)

        return jsonify({"message": f"Livre '{title_to_delete}' supprimé avec succès et sauvegardé dans '{output_filename}'"}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la suppression : {str(e)}"}), 500
