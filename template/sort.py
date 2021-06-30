import sys
import os
import subprocess


DIR_PATH = sys.argv[1]

#   PATH/*.fits
def get_fits_in_dir(PATH):

    fits_files = []

    for file in os.listdir(PATH):
        if file.endswith('.fits'):
            fits_files.append({
                'FILE_NAME': file,
                'FILE_PATH': os.path.join(PATH, file)
            })

    # returns list of dict
    return fits_files

# creates folders for each object and moves fits files according to them
#   PATH/*.fits -> PATH/OBJECTS/*.fits
def sort_fits_to_obj_dirs(fits_files, PATH):

    for file in fits_files:

        # use 'exiftool' to get metadata for 'Object'
        command = "exiftool " + file['FILE_PATH'] + " | grep -e 'Object'"

        # speed up by parallelizing with subprocess.Popen?
        result = subprocess.run(command, stdout=subprocess.PIPE, encoding='utf-8', shell=True)
        result = result.stdout

        object_name = result.split(':')[1].lstrip().rstrip()
        object_path = os.path.join(PATH, object_name)

        # create object folder it doesn't exist yet
        if not os.path.isdir(object_path):
            os.mkdir(object_path)
            print('Folder created for:', object_name)

        # move file to object folder
        os.rename(file['FILE_PATH'], os.path.join(object_path, file['FILE_NAME']))
        print('Moved:', file['FILE_NAME'], '->', object_name)

    print()

# create images for every fits file
#   PATH/OBJECTS/{*.fits,*.png}
def generate_fits_image(PATH):

    # walk through entire directory and subdirectory
    for path, subdirs, files in os.walk(PATH):
        for name in files:

            # any filename or pathname used in shell need to be escaped
            file_path_name = os.path.join(path, name).replace(" ", "\\ ")
            image_path_name = os.path.join(path, name.split('.fits')[0] + '.png').replace(" ", "\\ ")

            # use 'ds9' to create .png images
            command = "ds9 " + file_path_name + " -zoom to fit -zscale -saveimage png " + image_path_name + " -quit"

            # speed up by parallelizing with subprocess.Popen?
            result = subprocess.run(command, stdout=subprocess.PIPE, encoding='utf-8', shell=True)
            result = result.stdout
            print('Image created for:', name)

    print()

# main script
def main():

    print("\n>>  Starting Script...\n")


    print(">>  Getting fits files...\n")
    fits_files = get_fits_in_dir(DIR_PATH)

    print(">>  Sorting files to Object folders...\n")
    sort_fits_to_obj_dirs(fits_files, DIR_PATH)

    print(">>  Creating fits images...\n")
    generate_fits_image(DIR_PATH)


    print("\n>>  Script Finished!\n")

main()


## reset back to original fits folder (might need zsh globs?)

# ```
# $ cd ROOT_DIR (e.g 20210330)

# move all fits file back to root
# $ mv */*.fits .

# remove all png images
# $ rm -r */*.png

# remove all create object dirs
# $ rmdir *
#```


# Other tools to check metadata
# exiftool * | grep 'Naxis 2' | sort | uniq -c