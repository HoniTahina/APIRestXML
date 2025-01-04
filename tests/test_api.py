import pytest
from io import BytesIO
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    return app.test_client()

def test_upload_xml(client):
    data = {'file': (BytesIO(b'<root><element>value</element></root>'), 'test.xml')}
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"XML file uploaded successfully" in response.data

def test_transform_xml(client):
    xml_data = '<root><element>value</element></root>'
    xslt_data = '''<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                     <xsl:template match="/">
                       <transformed><xsl:value-of select="/root/element"/></transformed>
                     </xsl:template>
                   </xsl:stylesheet>'''
    data = {
        'xml': (BytesIO(xml_data.encode()), 'test.xml'),
        'xslt': (BytesIO(xslt_data.encode()), 'transform.xslt')
    }
    response = client.post('/transform', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"XML transformed successfully" in response.data
