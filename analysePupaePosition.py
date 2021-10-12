import gravityFunnel


class analysePupaePosition():

    def __init__(self,pupaeCoords,funnelType='large'):
        self.gravFunnel = gravityFunnel.gravityFunnel(funnelType)
        self.pupaeCoords = pupaeCoords
        self.interpYawData()
    

    def interpYawData(self):
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
    def pixelPos2FunnelPos(self,larvaePos,imgPosStr):
        if 'top' == imgPosStr:
            self.pixel2FunnelPos_top(larvaePos)
        elif 'slope' == imgPosStr:
            self.pixel2FunnelPos_slope(larvaePos)
        elif 'ortho' == imgPosStr:
            self.pixel2FunnelPos_ortho(larvaePos)
        elif 'left' == imgPosStr:
            self.pixel2FunnelPos_left(larvaePos)
        elif 'right' == imgPosStr:
            self.pixel2FunnelPos_right(larvaePos)
        elif 'bottom' == imgPosStr:
            self.pixel2FunnelPos_bottom(larvaePos)
        else:
            raise ValueError(f'gravityFunnel:pixelPos2FunnelPos: imgPosStr illdefined: {imgPosStr}')    

    def pixel2FunnelPos_top(self,larvaePos):
        #1 from the top looking on the short end of the funnel
        #  steep slope is right 0° yaw , shallow slope is left 180° yaw
        pass
    def pixel2FunnelPos_slope(self,larvaePos):
        #2 looking on the shallow slope of the funnel
        #  top is 90° yaw, middle is 180° yaw, down is 270° yaw

        # getting yaw

        bb_yaw = self.boundingBoxYawCoords['slope']

    def pixel2FunnelPos_ortho(self,larvaePos):
        #3 looking on the steep slope of the funnel
        #  top is 90° yaw, middle is 0°/360° yaw, down is 270° yaw
        bb_yaw = self.boundingBoxYawCoords['ortho']
    def pixel2FunnelPos_left(self,larvaePos):
        #4 steep slope up shallow slope down
        #  top is 360° yaw, down is 180° yaw
        bb_yaw = self.boundingBoxYawCoords['left']
    def pixel2FunnelPos_right(self,larvaePos):
        #5 steep slope down shallow slope up
        #  top is 180° yaw, down is 0° yaw
        bb_yaw = self.boundingBoxYawCoords['right']
    def pixel2FunnelPos_bottom(self,larvaePos):
        #6 looking into the funnel from the large oppening
        #  steep slope is left 0° yaw , shallow slope is right 180° yaw
        pass

