import os 


def recursiveFindFiles(source_dir,file_extension):
    '''
    Find all files with a user defined extension in folder recursively.
    '''
    os.system('clear')
    print('Finding Files!')
    file_list =  [os.path.join(dp, f) for dp, dn, filenames in os.walk(source_dir) for f  in filenames if f.endswith(file_extension)]
    file_list.sort()
    return file_list

def sendDirToTSP(source_dir,file_extension,result_folder,detection_label,max_frames,python_pos='/home/bgeurten/anaconda3/envs/charon/bin/python',scritpt_pos = '/home/bgeurten/PyProjects/charon/read_ivTrace/ivTrace_to_labelImg.py'):
    file_list = recursiveFindFiles(source_dir,file_extension)
    file_list2 = [x[0:-3]+'mp4' for x in file_list]
    combi_list =list(zip(file_list,file_list2))
    for c in combi_list:
        foldername = os.path.basename(os.path.dirname(c[0]))
        date_str = os.path.basename(os.path.dirname(os.path.dirname(c[0])))
        image_prefix = f'{date_str}_{foldername}'
        result_subfolder = os.path.join(result_folder,image_prefix)
        
        os.system(f'tsp {python_pos} {scritpt_pos} -t {c[0]} -m {c[1]} -r {result_subfolder} -p {image_prefix} -l {detection_label} -f {max_frames}')

# Mosquitos
source_directory   = '/home/bgeurten/OneDrive/AI_SWAP/JohnHopkins_Otago/2-human/'
tra_file_extension = 'full.txt'
result_folder      = '/home/bgeurten/OneDrive/AI_SWAP/JohnHopkins_Otago/training_data/'
detection_label    = 'mosquito'
max_frames         = 20000


sendDirToTSP(source_directory,tra_file_extension,result_folder,detection_label,max_frames)

#   -r /home/bgeurten/test/ -p 03-05-2020_human1_pos7 -l mosquito -f 20000

