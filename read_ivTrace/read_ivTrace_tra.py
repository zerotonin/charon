from numpy import void
import pandas as pd
import re

class read_ivTrace_tra():

    def __init__(self, filepos = False, mode = '2D') -> None:
        """
        This class reads the ivTrace trajectory format files. Currently it only works for the 2D trajectory files. 
        The trajectory files are expected in the 2011 format (see below).

        The resulting format is a pandas dataframe with as many rows as there are detections in the trajectory file.
        Columns are 
        frame_number : The frame in which the detection took place
        animal_number: The number of the detection inside the frame
        x_pix        : The x-coordinate of the detection's center of mass in pixels
        y_pix        : The y-coordinate of the detection's center of mass in pixels
        atan2_rad    : The angle against the horizontal dimension of the frame given in atan2 format and radians. 
                       This is set to zero if it is a manual detection.
        size_pix     : The surface area of the detection given in pixels. This is set to zero if it is a manual 
                       detection.
        eccentricity : The eccentricity (circularity) of the detection. 0 for a perfect circle, elipse 0->1, 
                       line =  infinity. This is set to -1 if it is a manual detection.
        
        Args:
            mode (str, optional): _description_. Defaults to '2D'.
            filepos (str, optional): _description_. Defaults to false.

        Simple Usage:
                        self.transcribe_to_hdf_dataframe(): produces a hdf file in the same folder with identical 
                                                            filename with 'df' as key ending on .hd5
                        self.read_tra_file()              : returns a pandas dataframe with the trajectory data

                        rivtt = read_ivTrace_tra(filepos='read_ivTrace/full.txt')
                        rivtt.transcribe_to_hdf_dataframe()

        
        2011 ivTrace format
        ===================

        The resulting trace file contains one line for each image of the sequence.  All the region objects detected 
        within one image arealways containg into one line. Whether there are lines not containing any data depends on 
        the parameters given for saving. Eachline starts with the 4 digit wide image index, followed by the available 
        sets of region data. Each set of region data contains of thecenter of mass (2 unsigned float coordinates with 
        four (three before October 2006) leading digits and two decimals), the directionin radiants measured against
        the horizontal direction (1 signed float value with 5 decimals), the size of the region representedas number
        of contained pixels (1 int value) and an parameter describing the excentricity of the region shape reaching 
        from 0.0(circle shape) to 1.0 (line shape) (1 unsigned float value with 2 decimals).
        """
        self.mode = mode
        self.filepos = filepos
    
    def ivTrace_row_to_dictlist(self,seq):
        """Subroutine to split the coordinates and detection data from the frame number.
           Numerical data is than type cast into integers (frame number) and floats (detection data).

        Args:
            seq (list of strings): numerical data of an ivTrace row

        Returns:
            list: list of dictionaries containing the detection data of this frame
        """
        frame_number = int(seq[1])
        detections = [float(x) for x in seq[2::]]
        return self.raw_detections_to_dict(frame_number,detections)
    
    
    def raw_detections_to_dict(self,frame_number,detections):
        """This function iterates through the detections of a frame and creates a pandas readable dictionary.
           It also creates the animal_number from the position of the detection within the detection text. 
           ivTrace numbers them after there position from the left as does this function.

        Args:
            frame_number (int): number of the frame in which the detections were made
            detections (list of floats): all detection data of the frame as returned by ivTrave_row_to_dict_list

        Returns:
            list: ist of dictionaries containing the detection data  of this frame
        """
        dict_list = []
        animal_num = 0
        for i in range(0, len(detections), 5):
            dict_list.append({"frame_number": frame_number, "animal_number":animal_num, 'x_pix':detections[i], 'y_pix':detections[i+1],
                              'atan2_rad':detections[i+2], 'size_pix':detections[i+3], 'eccentricity':detections[i+4]})
            animal_num +=1
        return dict_list

        

    def read_tra_file(self, filepos= False):
        """
        This function reads the ivTrace trajectory file and writes it into a pandas DataFrame. Therefore it is first transcribed
        into a list of dictionaries. Importantly empty frames are not transcribed and so the length of the file does not 
        represent the length of the original footage. Furthermore multiple detections in the same frame are found under specific
        animal numbers of the same frame number.

        Args:
            filepos (string, optional): This is the file position of the ivTrace trajectory file. Defaults to False.

        Returns:
            pandas.DataFrame: The resulting format is a pandas dataframe with as many rows as there are detections in the trajectory file.
                              Columns are 
                              frame_number : The frame in which the detection took place
                              animal_number: The number of the detection inside the frame
                              x_pix        : The x-coordinate of the detection's center of mass in pixels
                              y_pix        : The y-coordinate of the detection's center of mass in pixels
                              atan2_rad    : The angle against the horizontal dimension of the frame given in atan2 format and radians. 
                                          This is set to zero if it is a manual detection.
                              size_pix     : The surface area of the detection given in pixels. This is set to zero if it is a manual 
                                          detection.
                              eccentricity : The eccentricity (circularity) of the detection. 0 for a perfect circle, elipse 0->1, 
                                          line =  infinity. This is set to -1 if it is a manual detection.
        """
        if filepos != False:
            self.filepos = filepos
        
        df = pd.read_csv(self.filepos)
        tra_list_of_dicts =list()
        for i,row in df.iterrows():
            # split text row in numbers
            seq = re.split(r'\s+',row[0])
            # sequence length is 3 or 7 + n*5
            if len(seq) > 3:
                tra_list_of_dicts+=self.ivTrace_row_to_dictlist(seq)
        
        return pd.DataFrame(tra_list_of_dicts)
    
    def transcribe_to_hdf_dataframe(self, filepos= False):
        """
        Identical to read_tra_file, but the data is saved back to the source under an identical filename, with the ending .hd5. The
        file is hd5 formatted with the key 'df'

        Args:
            filepos (string, optional): This is the file position of the ivTrace trajectory file. Defaults to False.
        """

        if filepos != False:
            self.filepos = filepos
        df = self.read_tra_file(self.filepos)
        new_filepos = self.filepos.rsplit('.',1)[0]+'.hd5'
        df.to_hdf(new_filepos,key='df')
