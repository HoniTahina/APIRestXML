from lxml import etree

def parse_xml(xml_data):
    try:
        tree = etree.XML(xml_data)
        return etree.tostring(tree, pretty_print=True).decode()
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid XML: {str(e)}")

def modify_xml(xml_data, element, new_value):
    try:
        tree = etree.XML(xml_data)
        nodes = tree.xpath(f"//{element}")
        if nodes:
            nodes[0].text = new_value
            return etree.tostring(tree, pretty_print=True).decode()
        else:
            raise ValueError(f"Element '{element}' not found.")
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid XML: {str(e)}")
