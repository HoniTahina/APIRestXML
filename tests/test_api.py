import unittest
from app import create_app  # Importer l'application Flask
from io import BytesIO

class APITestCase(unittest.TestCase):
    def setUp(self):
        """Initialiser le client Flask pour les tests."""
        self.app = create_app()  # Créer l'application Flask
        self.client = self.app.test_client()  # Client de test
        self.xml_data = b"""<?xml version="1.0"?>
        <catalog>
            <book>
                <title lang="en">Python Basics</title>
                <author>John Doe</author>
                <price>29.99</price>
            </book>
        </catalog>"""
        self.xslt_data = b"""<?xml version="1.0"?>
        <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
            <xsl:template match="/">
                <html>
                    <body>
                        <xsl:for-each select="catalog/book">
                            <div>
                                <p>Title: <xsl:value-of select="title"/></p>
                                <p>Author: <xsl:value-of select="author"/></p>
                                <p>Price: <xsl:value-of select="price"/></p>
                            </div>
                        </xsl:for-each>
                    </body>
                </html>
            </xsl:template>
        </xsl:stylesheet>"""

    def test_upload(self):
        """Tester l'upload d'un fichier XML."""
        response = self.client.post('/upload', data={
            'file': (BytesIO(self.xml_data), 'test_catalog.xml')
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Fichier XML téléchargé avec succès".encode('utf-8'), response.data)

    def test_transform(self):
        """Tester la transformation d'un fichier XML avec XSLT."""
        response = self.client.post('/transform', data={
            'xml': (BytesIO(self.xml_data), 'test_catalog.xml'),
            'xslt': (BytesIO(self.xslt_data), 'test_transform.xslt')
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<html>", response.data)

    def test_modify(self):
        """Tester la modification d'un élément dans le fichier XML."""
        response = self.client.post('/modify', data={
            'xml': (BytesIO(self.xml_data), 'test_catalog.xml'),
            'element': 'price',
            'value': '35.99'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("XML modifié avec succès".encode('utf-8'), response.data)

    def test_add_book(self):
        """Tester l'ajout d'un livre dans le fichier XML."""
        new_book = {
            "title": "New Book",
            "author": "Jane Smith",
            "price": "19.99"
        }
        response = self.client.post('/add', data={
            'xml': (BytesIO(self.xml_data), 'test_catalog.xml'),
            'title': new_book['title'],
            'author': new_book['author'],
            'price': new_book['price']
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Livre ajouté avec succès".encode('utf-8'), response.data)

    def test_delete_book(self):
        """Tester la suppression d'un livre dans le fichier XML."""
        response = self.client.post('/delete', data={
            'xml': (BytesIO(self.xml_data), 'test_catalog.xml'),
            'title': 'Python Basics'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Livre 'Python Basics' supprimé avec succès".encode('utf-8'), response.data)

    def test_delete_book_not_found(self):
        """Tester la suppression d'un livre non existant."""
        response = self.client.post('/delete', data={
            'xml': (BytesIO(self.xml_data), 'test_catalog.xml'),
            'title': 'Nonexistent Book'
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn("Livre avec le titre 'Nonexistent Book' introuvable".encode('utf-8'), response.data)

if __name__ == '__main__':
    unittest.main()
