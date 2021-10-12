import gravityFunnel
import pandas as pd
import numpy as np
from scipy.interpolate import griddata

class analysePupaePosition():

    def __init__(self,pupaeData,funnelType='large'):
        self.gravFunnel = gravityFunnel.gravityFunnel(funnelType)
        self.pupaeData = pupaeData
        self.getInterpYawData()
    

    def getInterpYawData(self):
        # coordinate dictionary to transform x,y in bounding box to  funnel yaw 
        #
        # 0,0-------------------1,0
        #  |     tensorflow      |
        #  |    bounding box     |
        #  |                     |
        # 0,1-------------------1,0

        # The large funnel opening is 40mm the small one ten    
        
        # view =[(bb_x, bb_y, yaw), (bb_x, bb_y, yaw),...(bb_x, bb_y, yaw)]
        
        # view 2 looking on the shallow slope of the funnel
        #  top is 90° yaw, middle is 180° yaw, down is 270° yaw
        #  large opening is left        
        view2 = [(0.0,0.0  ,90.0),(0.0,0.5,180.0),(0.0,1.0, 270.0), #large opening
                 (1.0,0.375,90.0),(1.0,0.5,180.0),(0.0,0.625,270.0)] # small opening
        #3 looking on the steep slope of the funnel
        #  top is 90° yaw, middle is 0°/360° yaw, down is 270° yaw
        #  large opening is right
        #  ATTENTION! we are going over 360° to avoid problems with interpolation over
        #  the circle origin.        
        view3 = [(0.0,0.375,450.0),(0.0,0.5,360.0),(0.0,0.625,270.0), # small opening
                 (1.0,0.0  ,450.0),(1.0,0.5,360.0),(1.0,1.0, 270.0)] #large opening
        #4 steep slope up shallow slope down
        #  top is 360° yaw, down is 180° yaw
        #  large opening is right
        view4 = [(0.0,0.0,360.0),(0.0,0.125,270.0),(0.0,0.25,180.0), # small opening
                 (1.0,0.0,360.0),(1.0,0.5  ,270.0),(1.0,1.0 ,180.0)] #large opening
        #5 steep slope down shallow slope up
        #  top is 180° yaw, down is 0° yaw
        #  large opening is right
        view5 = [(0.0,0.75,180.0),(0.0,0.875,90.0),(0.0,1.0,0.0), # small opening
                 (1.0,0.0 ,180.0),(1.0,0.5  ,90.0),(1.0,1.0,0.0)] #large opening
        
        self.boundingBoxYawCoords['slope'] = view2
        self.boundingBoxYawCoords['ortho'] = view3
        self.boundingBoxYawCoords['left']  = view4
        self.boundingBoxYawCoords['right'] = view5

    def pixelPos2FunnelPos(self):
        if 'top' == self.pupaeData['imgPosStr']:
            self.pixel2FunnelPos_top()
        elif 'slope' == self.pupaeData['imgPosStr']:
            self.pixel2FunnelPos_slope()
        elif 'ortho' == self.pupaeData['imgPosStr']:
            self.pixel2FunnelPos_ortho()
        elif 'left' == self.pupaeData['imgPosStr']:
            self.pixel2FunnelPos_left()
        elif 'right' == self.pupaeData['imgPosStr']:
            self.pixel2FunnelPos_right()
        elif 'bottom' == self.pupaeData['imgPosStr']:
            self.pixel2FunnelPos_bottom()
        else:
            raise ValueError(f'gravityFunnel:pixelPos2FunnelPos: imgPosStr illdefined: {imgPosStr}')    

    def pixel2FunnelPos_top(self):
        #1 from the top looking on the short end of the funnel
        #  steep slope is right 0° yaw , shallow slope is left 180° yaw
        raise NotImplementedError

    def pixel2FunnelPos_slope(self):
        #2 looking on the shallow slope of the funnel
        #  top is 90° yaw, middle is 180° yaw, down is 270° yaw
        yaw = self.interpolateYaw()

    def pixel2FunnelPos_ortho(self):
        #3 looking on the steep slope of the funnel
        #  top is 90° yaw, middle is 0°/360° yaw, down is 270° yaw
        yaw = self.interpolateYaw()

    def pixel2FunnelPos_left(self):
        #4 steep slope up shallow slope down
        #  top is 360° yaw, down is 180° yaw
        yaw = self.interpolateYaw()

    def pixel2FunnelPos_right(self):
        #5 steep slope down shallow slope up
        #  top is 180° yaw, down is 0° yaw
        yaw = self.interpolateYaw()

    def pixel2FunnelPos_bottom(self):
        #6 looking into the funnel from the large oppening
        #  steep slope is left 0° yaw , shallow slope is right 180° yaw
        raise NotImplementedError

    def interpolateYawPos(self):
        bb_yaw = self.boundingBoxYawCoords[self.pupaeData['imgPosStr']]