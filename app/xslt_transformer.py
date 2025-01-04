from lxml import etree

def transform_xml(xml_data, xslt_data):
    xml_tree = etree.XML(xml_data)
    xslt_tree = etree.XML(xslt_data)
    transform = etree.XSLT(xslt_tree)
    transformed_xml = transform(xml_tree)
    return str(transformed_xml)
