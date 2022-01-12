import os
import numpy as np
from lxml import etree as et
import xml.etree.ElementTree as ET

class dataframe2labelImgXML:
    def __init__(self):
        pass

    def inputNum2labelImgFormat(self,num):
        if num <0:
            return '0'
        else:
            return str(int(np.round(num)))

    def readXML(self,xml_file):
        xml_list = list()
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                        int(root.find('size')[0].text),
                        int(root.find('size')[1].text),
                        member[0].text,
                        int(member[4][0].text),
                        int(member[4][1].text),
                        int(member[4][2].text),
                        int(member[4][3].text)
                        )
            xml_list.append(value)
        return xml_list
    def create_xml(self,imgfilepath, imageSize, object_list, savedir,datasourceText= 'Unknown'):
        """
        params:
        - imgfilepath: path of corresponding img file. only the basename will be actually used.
        - object_list: python list of objects. the format of each element is up to the user, but for this example, each element will be a tuple of (classname, [x1,y1,x2,y2])
        - savedir: output directory to save generated xml file
        """
        filename   = os.path.basename(imgfilepath)
        folderPos = os.path.dirname(imgfilepath)
        folderName = os.path.basename(folderPos)
        savePos    = os.path.join(folderPos,filename.rsplit('.',1)[0]+'.xml')
        
        root = et.Element('annotation')
        folderName_elem = et.SubElement(root,'folder')
        folderName_elem.text = folderName
        fn_elem = et.SubElement(root, 'filename')
        fn_elem.text = filename
        path_elem = et.SubElement(root,'path')
        path_elem.text = imgfilepath
        sourc_elem = et.SubElement(root,'source')
        data_elem = et.SubElement(sourc_elem,'database')
        data_elem.text = datasourceText
        size_elem = et.SubElement(root,'size')
        width_elem = et.SubElement(size_elem,'width')
        width_elem.text= self.inputNum2labelImgFormat(imageSize[0])
        height_elem = et.SubElement(size_elem,'height')
        height_elem.text= self.inputNum2labelImgFormat(imageSize[1])
        depth_elem = et.SubElement(size_elem,'depth')
        depth_elem.text= self.inputNum2labelImgFormat(imageSize[2])
        seg_elem = et.SubElement(root,'segmented')
        seg_elem.text = '0'

        for classname, (x1,y1,x2,y2) in object_list:
            object_elem = et.SubElement(root, 'object')
            name = et.SubElement(object_elem, 'name')
            name.text = classname
            pose_elem = et.SubElement(object_elem,'pose')
            pose_elem.text = 'Unspecified'
            trunc_elem = et.SubElement(object_elem,'truncated')
            trunc_elem.text = '1'
            diff_elem = et.SubElement(object_elem,'difficult')
            diff_elem.text = '0'




            bndbox = et.SubElement(object_elem, 'bndbox')
            xmin = et.SubElement(bndbox, 'xmin')
            xmin.text = self.inputNum2labelImgFormat(x1)
            ymin = et.SubElement(bndbox, 'ymin')
            ymin.text = self.inputNum2labelImgFormat(y1)
            xmax = et.SubElement(bndbox, 'xmax')
            xmax.text = self.inputNum2labelImgFormat(x2)
            ymax = et.SubElement(bndbox, 'ymax')
            ymax.text = self.inputNum2labelImgFormat(y2)
        out = et.tostring(root, pretty_print=True, encoding='utf8') # if element attributes contains some non ascii characters, then need to specify encoding. if not the case, then encoding doesn't need to be set
        
        with open(savePos, 'wb') as fd:
            fd.write(out)