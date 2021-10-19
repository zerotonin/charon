from PIL import Image
import numpy as np
class contrastStretcher_8bit():

    def __init__(self, image,mode = 'auto'):
        self.img = image
        self.mode = 'auto'
        self.mode_to_bpp    = {'1':1, 'L':8, 'I;16B':16, 'P':8,  'RGBA':32, 'CMYK':32,'I':32, 'F':32}
        self.mode_to_npType = {'1':bool, 'L':np.int8, 'I;16B':np.int16, 'P':np.int8, 'RGBA':np.int32, 'CMYK':np.int32, 'I':np.int32, 'F':np.int32}
        
    def max_bits(self,b):
        return (1 << b) - 1
    
    def get_output_Limits(self):
        self.maxO = self.max_bits(self.bpp)
        self.minO = 0
   
    def get_input_Limits(self):
        data = list(self.img.getdata())
        self.maxI = max(data)
        self.minI = min(data)
    
    def main(self):

        if self.mode == 'auto':
            self.bpp = self.mode_to_bpp[self.img.mode]
            self.npType = self.mode_to_npType[self.img.mode]
            self.get_input_Limits()
            self.get_output_Limits()

        mat = np.array(self.img)
        mat = 255*(((mat-self.minI)/(self.maxI-self.minI))+(self.minO/self.maxO))
    
        return Image.fromarray(mat.astype(np.uint8))
