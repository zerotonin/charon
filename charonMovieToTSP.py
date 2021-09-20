import charon,os,tqdm,shutil,sys, getopt

class charonMovieToTSP():
    def __init__(self,movieFile,AIstring,detectionThresh=0.95,writeDetMov=False):  
        self.movieFile = movieFile
        self.AIstring = AIstring
        self.detectionThresh = detectionThresh
        self.writeDetMov = writeDetMov
        # initialize charon video AI
        self.charon = charon.charon(self.AIstring)
        self.charon.DETECTION_THRESH = detectionThresh 

    def main(self):
        self.charon.analyseMovie(self.movieFile, #moviePos
                                 self.movieFile[0:-4]+'_ana.avi', #anaPath out
                                 self.movieFile[0:-3]+'tra', writeDetectionMov=self.writeDetMov) # xlsx file

if __name__ == '__main__':
    
    # get input variables
    usageStr = 'usage: charonMovTSP.py -i <FilePositionOfInputMovie> -a <AI_identSting> -d <detectionThreshhold> -o <writeResultMovieFlag>'
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:a:d:o",["movieFile=","AIstring=","detectionThresh=","writeDetMov"])
        print(sys.argv)
    except getopt.GetoptError:
        print(usageStr)
        sys.exit(2)

    #parse Inputs
    movieFile       = False
    AIstring        = False
    detectionThresh = False
    writeDetMov     = False

    for o, a in opts:
        # if user asks for help 
        if o == '-h':
            print(usageStr)
            sys.exit(2)
        elif o == '-i':
            movieFile = a
        elif o == '-a':
            AIstring = a
        elif o == '-d':
            detectionThresh = float(a)
        elif o == '-o':
            writeDetMov = bool(a)

    if os.path.isfile(movieFile) == False:
        raise ValueError(f'-i is not an existing file: {movieFile} ')


    charonObj = charonMovieToTSP(movieFile,AIstring,detectionThresh,writeDetMov)
    charonObj.main()