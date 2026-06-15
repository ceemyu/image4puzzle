import os
import random
import cv2
import numpy as np

# Global variable
mouse_x, mouse_y = -1, -1
mouse_x1, mouse_y1 = -1, -1
mouse_x2, mouse_y2 = -1, -1
points = []
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 800
CELL_SIZE = 400

def get_image_file_directory():
    image_dir = input("Please enter the directory of the image file: ")

    if not os.path.isdir(image_dir):
        os.makedirs(image_dir, exist_ok=True)
    return image_dir

def resize_image_file(image_dir, image_filename):
    image_path = os.path.join(image_dir, image_filename)
    image = cv2.imread(image_path)
    target_dimensions = (CANVAS_WIDTH, CANVAS_HEIGHT)  # Define absolute dimensions: (width, height)

    img_resized = cv2.resize(image, target_dimensions) # Resize the image

    resized_image_filename = "resized_img.jpg"
    resized_image_path = os.path.join(image_dir, resized_image_filename)
    cv2.imwrite(resized_image_path, img_resized)  # Save or display
    height, width, channels = img_resized.shape

    print(f"Resized Width: {width} px")
    print(f"Resized Height: {height} px")
    print(f"Resized Channels: {channels}")


    return resized_image_path

def crop_image_file(image_dir, resized_image_path, row, col, top_y, bottom_y, left_x, right_x):

    img_resized = cv2.imread(resized_image_path)
    y1, y2 = top_y, bottom_y
    x1, x2 = left_x, right_x

    cropped_image = img_resized[y1:y2, x1:x2]     # Crop a region: [y1:y2 , x1:x2] for cell = (left_x, top_y, right_x, bottom_y)

    cropped_image_filename = f"cropped_{row}_{col}.jpg"
    cropped_image_path = os.path.join(image_dir, cropped_image_filename)

    success = cv2.imwrite(cropped_image_path, cropped_image)  # Save the file (returns True if successful)
    (height, width, channels) = cropped_image.shape
    print(f"cropped Width: {width} px")
    print(f"cropped Height: {height} px")
    print(f"cropped Channels: {channels}")

    if success:
        print(f"Image successfully saved to {cropped_image_path}")
    else:
        print("Failed to save the image.")
    return cropped_image_path

def create_white_canvas(image_dir):
    # Create a solid white canvas
    canvas = np.full((CANVAS_HEIGHT, CANVAS_WIDTH, 3), 255, dtype=np.uint8)
    canvas_path = os.path.join(image_dir, "canvas.jpg")
    success = cv2.imwrite(canvas_path, canvas)
    height, width, channels = canvas.shape
    print(f"Canvas Width: {width} px")
    print(f"Canvas Height: {height} px")
    print(f"Canvas Channels: {channels}")
    if success:
        print(f"Image successfully saved to {canvas_path}")
    else:
        print("Failed to save the image.")

        cv2.imshow("White Canvas", canvas)
        cv2.namedWindow("White Canvas", cv2.WINDOW_GUI_NORMAL)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()
    return canvas_path

def coordinates_for_cells_and_their_filenames(image_dir, resized_image_path, canvas_path):

    num_rows = CANVAS_HEIGHT // CELL_SIZE  # Figure out how many rows of cells we need
    num_cols = CANVAS_WIDTH // CELL_SIZE  # Figure out how many columns of cells we need
    print(num_cols, num_rows)

    cell_coordinates_and_matching_cropped_image_paths_dict = {}

    for row in range(num_rows):
        for col in range(num_cols):
            left_x = (col * CELL_SIZE)
            top_y = (row * CELL_SIZE)
            right_x = (left_x + CELL_SIZE)  # The right coordinate of the cell is CELL_SIZE pixels away from the left
            bottom_y = (top_y + CELL_SIZE)  # The bottom coordinate of the cell is CELL_SIZE pixels away from the top
            print(f"leftx:{left_x}, topy:{top_y}, rightx:{right_x}, bottomy:{bottom_y}")

            cropped_image_path = crop_image_file(image_dir, resized_image_path, row, col, top_y, bottom_y, left_x, right_x)
            cell_coordinates_and_matching_cropped_image_paths_dict[(left_x, top_y, right_x, bottom_y)] = cropped_image_path

            background = cv2.imread(canvas_path)  # Load the image
            foreground = cv2.imread(cropped_image_path)

            # 1. Copy: Select a Region of Interest (ROI)
            # Format: image[ymin:ymax, xmin:xmax]
            roi = foreground[0:CELL_SIZE, 0:CELL_SIZE].copy()

            # 2. Paste: Assign the copied ROI to a destination area
            # Note: The destination region MUST be the exact same size as the ROI
            background[top_y:bottom_y, left_x:right_x] = roi

            # Save and display the result
            cv2.imwrite(canvas_path, background)
            cv2.namedWindow("Canvas with image", cv2.WINDOW_GUI_NORMAL)
            cv2.imshow("Canvas with image", background)
            cv2.waitKey(1000)
            cv2.destroyAllWindows()

            #tile_cropped_image_to_canvas(canvas_path, cropped_image_path, top_y, bottom_y, left_x, right_x)

    return cell_coordinates_and_matching_cropped_image_paths_dict

def shuffle_create_puzzle(cell_coordinates_and_matching_cropped_image_paths_dict):
    keys = list(cell_coordinates_and_matching_cropped_image_paths_dict.keys()) # Extract and convert to lists
    values = list(cell_coordinates_and_matching_cropped_image_paths_dict.values()) # Extract and convert to lists
    random.shuffle(keys) # Shuffle both lists independently
    random.shuffle(values) # Shuffle both lists independently
    shuffled_positions_dict = dict(zip(keys, values)) # Recombine into a new dictionary

    print(shuffled_positions_dict)
    return shuffled_positions_dict

def puzzled_coordinates_for_cells_and_their_filenames(canvas_path, shuffled_positions_dict):

    copy_shuffled_positions_dict = {}

    copy_shuffled_positions_dict = shuffled_positions_dict

    for key in copy_shuffled_positions_dict:
        copy_key = key
        print("key", copy_key)
        path = str(copy_shuffled_positions_dict[key])
        print("path", path)
        background = cv2.imread(canvas_path)  # Load the image
        foreground = cv2.imread(shuffled_positions_dict[key])


        #for (left_x, top_y, right_x, bottom_y), path in copy_shuffled_positions_dict.items():
        left_x = int(copy_key[0])
        top_y = int(copy_key[1])
        right_x = int(copy_key[2])
        bottom_y = int(copy_key[3])
        print(left_x, top_y, right_x, bottom_y)


        height, width, channels = background.shape
        print(f"BHeight: {height}, Width: {width}, Channels: {channels}")
        height, width, channels = foreground.shape
        print(f"FHeight: {height}, Width: {width}, Channels: {channels}")


        #img[y:y + h, x:x + w].copy()
        roi = foreground[0:CELL_SIZE, 0:CELL_SIZE]
        #roi.shape
        #cv2.imshow('roi', roi)
        #cv2.waitKey(1000)
        background2 = background.copy()

        resized_roi = cv2.resize(roi, (CELL_SIZE, CELL_SIZE))
        #print(f"ROI Size: Width={roi_width}, Height={roi_height} ")
        #height, width, channels = background.shape
        #print(f"BHeight: {height}, Width: {width}, Channels: {channels}")


        #print(f"shuffled positions: leftx:{left_x}, topy:{top_y}, rightx:{right_x}, bottomy:{bottom_y}")

        background2[top_y:top_y+CELL_SIZE , left_x:left_x+CELL_SIZE] = roi
        background = background2

        height, width, channels = background.shape
        print(f"BHeight: {height}, Width: {width}, Channels: {channels}")
        cv2.imwrite(canvas_path, background)
        cv2.namedWindow("Canvas with shuffled positions image cells: Puzzle", cv2.WINDOW_GUI_NORMAL)

        cv2.imshow("Canvas with shuffled positions image cells: Puzzle", background)

        cv2.waitKey(3000)
        cv2.destroyAllWindows()
    return canvas_path




def solve_puzzle(canvas_path, cell_coordinates_and_matching_cropped_image_paths_dict, shuffled_positions_dict):
    keys_real_positions_of_cells = list(cell_coordinates_and_matching_cropped_image_paths_dict.keys()) # Extract and convert to lists
    print(keys_real_positions_of_cells)
    values_real_positions_of_cells = list(cell_coordinates_and_matching_cropped_image_paths_dict.values()) # Extract and convert to lists
    print(values_real_positions_of_cells)
    keys_shuffled_positions_of_cells = list(shuffled_positions_dict.keys())  # Extract and convert to lists
    print(keys_shuffled_positions_of_cells)
    values_shuffled_positions_of_cells = list(shuffled_positions_dict.values())  # Extract and convert to lists
    print(values_shuffled_positions_of_cells)

    clicked_points = select_two_cells_to_be_exchanged_with_mouse_left_click(canvas_path)
    print(clicked_points)

    find_position_of_the_selected_cell_to_move_to_its_right_position(keys_shuffled_positions_of_cells, values_shuffled_positions_of_cells)
    #key_of_the_selected_cell_to_move_to_its_right_position, path_of_the_selected_cell_to_move_to_its_right_position

    print(find_position_of_the_selected_cell_to_move_to_its_right_position(keys_shuffled_positions_of_cells, values_shuffled_positions_of_cells))


    find_real_position_of_the_selected_cell(keys_real_positions_of_cells, values_real_positions_of_cells)
    #real_position_key_of_the_selected_cell, real_position_path_of_the_selected_cell
    print(find_real_position_of_the_selected_cell(keys_real_positions_of_cells, values_real_positions_of_cells))
    find_the_position_of_the_selected_cell_to_move_to_other_cell_position(keys_shuffled_positions_of_cells, values_shuffled_positions_of_cells)
    #key_of_the_selected_cell_to_move_to_other_cell_position, path_of_the_selected_cell_to_move_to_other_cell_position
    print(find_the_position_of_the_selected_cell_to_move_to_other_cell_position(keys_shuffled_positions_of_cells, values_shuffled_positions_of_cells))


def find_position_of_the_selected_cell_to_move_to_its_right_position(keys_shuffled_positions_of_cells, values_shuffled_positions_of_cells):

    for i in range(len(keys_shuffled_positions_of_cells)):
        shuffled_position_key  = keys_shuffled_positions_of_cells[i]
        left_x = int(shuffled_position_key[0])
        top_y = int(shuffled_position_key[1])
        right_x = int(shuffled_position_key[2])
        bottom_y = int(shuffled_position_key[3])
        print(shuffled_position_key)
        print(left_x, top_y, right_x, bottom_y)

        #
        if (mouse_x1 > left_x) and (mouse_x1 < right_x) and (mouse_y1 > top_y) and (mouse_y1 < bottom_y):
            order_of_the_selected_cell_to_move_to_its_right_position_in_shuffled_list = i
            key_of_the_selected_cell_to_move_to_its_right_position = keys_shuffled_positions_of_cells[i]
            path_of_the_selected_cell_to_move_to_its_right_position = values_shuffled_positions_of_cells[i]
            return key_of_the_selected_cell_to_move_to_its_right_position, path_of_the_selected_cell_to_move_to_its_right_position


def find_real_position_of_the_selected_cell(keys_real_positions_of_cells, values_real_positions_of_cells):

    for i in range(len(keys_real_positions_of_cells)):
        real_position_key = keys_real_positions_of_cells[i]
        left_x = int(real_position_key[0])
        top_y = int(real_position_key[1])
        right_x = int(real_position_key[2])
        bottom_y = int(real_position_key[3])
        print(real_position_key)
        print(left_x, top_y, right_x, bottom_y)

        #
        if (mouse_x1 > left_x) and (mouse_x1 < right_x) and (mouse_y1 > top_y) and (mouse_y1 < bottom_y):
            order__of_the_selected_cell_in_real_list = i
            real_position_key_of_the_selected_cell = keys_real_positions_of_cells[i]
            real_position_path_of_the_selected_cell = values_real_positions_of_cells[i]
            return real_position_key_of_the_selected_cell, real_position_path_of_the_selected_cell

def find_the_position_of_the_selected_cell_to_move_to_other_cell_position(keys_shuffled_positions_of_cells, values_shuffled_positions_of_cells):

    for i in range(len(keys_shuffled_positions_of_cells)):
        shuffled_position_key  = keys_shuffled_positions_of_cells[i]
        left_x = int(shuffled_position_key[0])
        top_y = int(shuffled_position_key[1])
        right_x = int(shuffled_position_key[2])
        bottom_y = int(shuffled_position_key[3])
        print(shuffled_position_key)
        print(left_x, top_y, right_x, bottom_y)

        #
        if (mouse_x2 > left_x) and (mouse_x2 < right_x) and (mouse_y2 > top_y) and (mouse_y2 < bottom_y):
            order_of_the_selected_cell_to_move_to_other_position_in_shuffled_list = i
            key_of_the_selected_cell_to_move_to_other_cell_position = keys_shuffled_positions_of_cells[i]
            path_of_the_selected_cell_to_move_to_other_cell_position = values_shuffled_positions_of_cells[i]
            return key_of_the_selected_cell_to_move_to_other_cell_position, path_of_the_selected_cell_to_move_to_other_cell_position

def select_two_cells_to_be_exchanged_with_mouse_left_click(canvas_path):
    global points
    img = cv2.imread(canvas_path, cv2.IMREAD_UNCHANGED)
    cv2.imshow('Solve the Puzzle', img)
    print("left click")
    cv2.setMouseCallback("Solve the Puzzle", click_event)
    #Wait until 2 clicks are recorded
    while True:
        cv2.waitKey(100)
        if len(points) >= 2:
            print("Two clicks recorded! Exiting...")
            break
    print(f"Final coordinates: {points}")
    mouse_x1, mouse_y1 = points[0]
    mouse_x2, mouse_y2 = points[1]

    cv2.destroyAllWindows

    return mouse_x1, mouse_y1, mouse_x2, mouse_y2


# Read image
#img = cv2.imread('your_image.jpg')
#cv2.imshow('Image', img)
#cv2.setMouseCallback('Image', click_event)

# Wait until 2 clicks are recorded
while True:
    #cv2.waitKey(100)
    if len(points) >= 2:
        print("Two clicks recorded! Exiting...")
        break
print(f"Final coordinates: {points}")
cv2.destroyAllWindows()



def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Point {len(points)}: ({x}, {y})")










def main():

    image_dir = get_image_file_directory()
    print(image_dir)
    image_filename = "example.jpg"

    resized_image_path = resize_image_file(image_dir, image_filename)
    print(resized_image_path)
    canvas_path = create_white_canvas(image_dir)
    print(canvas_path)
    cell_coordinates_and_matching_cropped_image_paths_dict = coordinates_for_cells_and_their_filenames(image_dir, resized_image_path, canvas_path)

    print(cell_coordinates_and_matching_cropped_image_paths_dict)
    shuffled_positions_dict = shuffle_create_puzzle(cell_coordinates_and_matching_cropped_image_paths_dict)
    print("shuffled_positions", shuffled_positions_dict)
    #canvas_path = create_white_canvas(image_dir)
    puzzled_coordinates_for_cells_and_their_filenames(canvas_path, shuffled_positions_dict)

    solve_puzzle(canvas_path, cell_coordinates_and_matching_cropped_image_paths_dict, shuffled_positions_dict)






    #print(get_coordinates_for_grid(image_side, cell_side)) -> List[int]:
    #print(create_list_of_cells(x_coord_list, y_coord_list)) -> List[Dict[str, int]]:


if __name__ == '__main__':
    main()
