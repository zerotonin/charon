import read_ivTrace_tra, cv2, time, xmlHandler, os,sys,getopt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
from tqdm import tqdm

class ivTrace_to_labelImg():

    def __init__(self,trace_position,movie_position, result_folder, image_prefix, detection_label, max_frames = 10000):
        self.trace_position  = trace_position
        self.movie_position  = movie_position
        self.result_folder   = result_folder
        self.image_prefix    = image_prefix
        self.detection_label = detection_label
        self.max_frames      = max_frames
        self.xml_handler     = xmlHandler.xmlHandler()

        #preallocate
        self.tra_df           = []
        self.detection_frames = []
        self.cap              = []
        self.frame_height     = []
        self.fps              = []


    def calc_bounding_box(self,row,edge_length=72):
        temp = [row['x_pix']-edge_length/2,row['y_pix']-edge_length/2,row['x_pix']+edge_length/2,row['y_pix']+edge_length/2]
        return [int(i) for i in temp]


    def read_tra_file(self):
        rivtt = read_ivTrace_tra.read_ivTrace_tra(self.trace_position)
        self.tra_df = rivtt.read_tra_file()
    
    def get_detection_frames(self):
        self.detection_frames = self.tra_df.frame_number.unique()
        if self.detection_frames.shape[0] > self.max_frames:
            idx = np.round(np.linspace(0, len(self.detection_frames) - 1, self.max_frames)).astype(int)   
            self.detection_frames = self.detection_frames[idx]
    
    def get_bounding_boxes(self):
        self.tra_df['bounding_box'] = self.tra_df.apply(self.calc_bounding_box,axis=1)

    def open_video_capture(self):
        self.cap = cv2.VideoCapture(self.movie_position)
        self.frame_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    def prepare_data(self):
        self.read_tra_file()
        self.get_detection_frames()
        self.get_bounding_boxes()
       
        self.open_video_capture()
    
    def show_examples(self):
        self.prepare_data()
        #prepare figure
        plt.ion()
        figure, ax = plt.subplots(figsize=(10, 8))
        #main loop
        for i in tqdm(range(0,self.detection_frames[-1]),desc='iterate through movie'):
            ret,frame = self.cap.read()
            if i in self.detection_frames:
                ax.clear()
                subset = self.tra_df.loc[self.tra_df['frame_number'] == i]        
                for delete_me,row in subset.iterrows():
                    xmin,ymin,xmax,ymax=row.bounding_box
                    frame = cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (255,0,0), 2)

                ax.imshow(frame)
                # drawing updated values
                figure.canvas.draw()
                figure.canvas.flush_events()
                time.sleep(0.001)
        self.cap.release()

    def create_new_filename(self,frame_number):
        return str(os.path.join(self.result_folder,self.image_prefix+'__'+str(frame_number)))

    def write_out_frame(self,frame,filename):
        cv2.imwrite(filename+'.png',frame)
    
    def write_out_xml(self,subset,filename,frame):
        object_list = list()
        for delete_me,row in subset.iterrows():
            object_list.append((self.detection_label,row.bounding_box))
        self.xml_handler.create_xml(filename+'.png', frame.shape, object_list, self.result_folder,datasourceText= 'ivTrace')
    
    def write_out_data(self,frame,subset,frame_number):

        if os.path.isdir(self.result_folder) == False:
            os.makedirs(self.result_folder, exist_ok=True)

        filename = self.create_new_filename(frame_number)
        self.write_out_frame(frame,filename)
        self.write_out_xml(subset,filename,frame)

    def create_training_data(self):
        self.prepare_data()
        for i in tqdm(range(0,self.detection_frames[-1]),desc='iterate through movie'):
            ret,frame = self.cap.read()
            if i in self.detection_frames:
                subset = self.tra_df.loc[self.tra_df['frame_number'] == i]
                self.write_out_data(frame,subset,i)   
        self.cap.release()
 




if __name__ == '__main__':
    
    # get input variables
    usageStr = 'usage: ivTrace_to_training.py -t <FilePositionOfInputTraFile> -m <FilePositionOfInputMovie> -r <result_folder> -p <image_prefix> -l <detection_label> -f <max_number_frames>'
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ht:m:r:p:l:f:",['trace_position','movie_position','result_folder','image_prefix','detection_label','max_frames'])
        #print(sys.argv)
    except getopt.GetoptError:
        print(usageStr)
        sys.exit(2)

    #parse Inputs
        trace_position  = False
        movie_position  = False
        result_folder   = False
        image_prefix    = False
        detection_label = False
        max_frames      = False

    #print(opts)
    for o, a in opts:
        # if user asks for help 
        if o == '-h':
            print(usageStr)
            sys.exit(2)
        elif o == '-t':
            trace_position = a
        elif o == '-m':
            movie_position = a
        elif o == '-r':
            result_folder = a
        elif o == '-p':
            image_prefix = a
        elif o == '-l':
            detection_label = a
        elif o == '-f':
            max_frames = int(a)

    if os.path.isfile(trace_position) == False:
        raise ValueError(f'-i is not an existing file: {trace_position} ')

    if os.path.isfile(movie_position) == False:
        raise ValueError(f'-i is not an existing file: {movie_position} ')

    iTli =ivTrace_to_labelImg(trace_position, movie_position,result_folder,image_prefix,detection_label,max_frames)
    iTli.create_training_data()

# /home/bgeurten/anaconda3/envs/charon/bin/python /home/bgeurten/PyProjects/charon/read_ivTrace/ivTrace_to_labelImg.py -t /home/bgeurten/PyProjects/charon/read_ivTrace/full.txt -m /home/bgeurten/OneDrive/AI_SWAP/JohnHopkins_Otago/2-human/03-05-2020/human1_pos7/full.mp4 -r /home/bgeurten/test/ -p 03-05-2020_human1_pos7 -l mosquito -f 20000

