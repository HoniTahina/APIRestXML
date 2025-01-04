<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" indent="yes"/>

    <!-- Template de transformation de la racine -->
    <xsl:template match="/catalog">
        <html>
            <head>
                <title>Catalogue des livres</title>
            </head>
            <body>
                <h1>Catalogue des livres</h1>
                <table border="1">
                    <tr>
                        <th>Titre</th>
                        <th>Auteur</th>
                        <th>Prix</th>
                    </tr>
                    <!-- Boucle pour chaque livre -->
                    <xsl:for-each select="book">
                        <tr>
                            <td><xsl:value-of select="title"/></td>
                            <td><xsl:value-of select="author"/></td>
                            <td><xsl:value-of select="price"/></td>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
