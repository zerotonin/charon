import os
from lxml import etree as et
def create_xml(imgfilepath, object_list, savedir):
    """
    params:
    - imgfilepath: path of corresponding img file. only the basename will be actually used.
    - object_list: python list of objects. the format of each element is up to the user, but for this example, each element will be a tuple of (classname, [x1,y1,x2,y2])
    - savedir: output directory to save generated xml file
    """
    basename = os.path.basename(imgfilepath)
    filename, _ = os.path.splitext(basename)
    
    root = et.Element('annotation')
    fn_elem = et.SubElement(root, 'filename')
    bn = os.path.basename(imagefilepath)
    fn, _ = os.path.splitext(bn)
    img_bn = f"{fn}.png"
    fn_elem.text = img_bn
    for classname, (x1,y1,x2,y2) in object_list:
        object_elem = et.SubElement(root, 'object')
        name = et.SubElement(object_elem, 'name')
        name.text = classname
        bndbox = et.SubElement(object_elem, 'bndbox')
        xmin = et.SubElement(bndbox, 'xmin')
        xmin.text = str(x1)
        xmax = et.SubElement(bndbox, 'xmax')
        xmax.text = str(x2)
        ymin = et.SubElement(bndbox, 'ymin')
        ymin.text = str(y1)
        ymax = et.SubElement(bndbox, 'ymax')
        ymax.text = str(y2)
    out = et.tostring(root, pretty_print=True, encoding='utf8') # if element attributes contains some non ascii characters, then need to specify encoding. if not the case, then encoding doesn't need to be set
    savepath = os.path.join(savedir, f'{fn}.xml')
    with open(savepath, 'wb') as fd:
        fd.write(out)